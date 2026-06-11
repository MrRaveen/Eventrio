import os
import json
import time
import requests
from celery import shared_task
from pydantic import BaseModel
from app.models.projects import Projects
from app.models.userAcc import userAcc
from app.config import getRedisClient
from app.orchestrator.channel_output import channel_output
from app.models.enum.SAGAStepStatusEnum import SAGAStepStatusEnum

class social_service:
    class req_data(BaseModel):
        owner_id: str
        event_id: str
        page_id: str
        workflow_id: str

    @shared_task(bind=True)
    def post_image_to_facebook_page_task(self, reqData: "social_service.req_data"):
        if isinstance(reqData, dict):
            reqData = social_service.req_data(**reqData)

        start_time = time.time()
        redis_client = getRedisClient()
        channel_name = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
        
        def push_status(status, payload):
            time_diff_ms = int((time.time() - start_time) * 1000)
            pushing_data = channel_output(
                return_data={
                    "status": status.value,
                    "function_name": "post_image_to_facebook_page",
                    "ms": time_diff_ms,
                    "payload": {
                        "workflowID": reqData.workflow_id,
                        "project_id": reqData.event_id,
                        **payload
                    }
                }
            )
            converted_data = json.dumps(pushing_data.return_data, default=str)
            redis_client.publish(channel_name, converted_data)

        try:
            user = userAcc.objects(sub=reqData.owner_id).first()
            if not user or not user.socialMediaTokens or not user.socialMediaTokens.facebook:
                err = {"error": "Facebook token missing for this user. Please connect Facebook in Settings."}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
            
            user_token = user.socialMediaTokens.facebook
            project = Projects.objects(id=reqData.event_id).first()
            
            image_url = None
            message = ""
            if project:
                if project.mediaLinks:
                    image_url = project.mediaLinks[0]
                message = project.fb_post or ""

            if reqData.page_id:
                #Get the Page Access Token
                accounts_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={user_token}"
                try:
                    accounts_data = requests.get(accounts_url).json()
                except Exception as e:
                    err = {"error": f"Failed: Could not reach Facebook API. {str(e)}"}
                    push_status(SAGAStepStatusEnum.FAILED, err)
                    return err

                page_token = None
                for page in accounts_data.get('data', []):
                    if page.get('id') == reqData.page_id:
                        page_token = page.get('access_token')
                        break

                if not page_token:
                    err = {"error": "Failed: Page not found or permissions missing."}
                    push_status(SAGAStepStatusEnum.FAILED, err)
                    return err

                #Publish the Photo to the Page (Note the /photos endpoint)
                post_url = f"https://graph.facebook.com/v19.0/{reqData.page_id}/photos"
                payload = {
                    'message': message,
                    'access_token': page_token
                }
                if image_url:
                    payload['url'] = image_url
                try:
                    response = requests.post(post_url, data=payload, timeout=10)
                    res_json = response.json()
                    push_status(SAGAStepStatusEnum.COMPLETED, res_json)
                    return res_json
                except Exception as e:
                    err = {"error": f"Failed to post: {str(e)}"}
                    push_status(SAGAStepStatusEnum.FAILED, err)
                    return err
            else:
                err = {"error": "No page_id provided"}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return None 
        except Exception as global_err:
            err = {"error": f"Internal task error: {str(global_err)}"}
            push_status(SAGAStepStatusEnum.FAILED, err)
            return err
