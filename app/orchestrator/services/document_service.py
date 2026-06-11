import requests
import os
import json
import time
from celery import shared_task
from pydantic import BaseModel

from app.models.userAcc import userAcc
from app.config import getRedisClient
from app.orchestrator.channel_output import channel_output
from app.models.enum.SAGAStepStatusEnum import SAGAStepStatusEnum


class document_service:
    class req_data(BaseModel):
        owner_id: str
        event_id: str
        plan_text: str
        workflow_id: str
        
    @shared_task(bind=True)
    def create_google_doc_for_event_task(self, reqData: "document_service.req_data"):
        if isinstance(reqData, dict):
            reqData = document_service.req_data(**reqData)

        start_time_exec = time.time()
        redis_client = getRedisClient()
        channel_name = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
        
        def push_status(status, payload):
            time_diff_ms = int((time.time() - start_time_exec) * 1000)
            pushing_data = channel_output(
                return_data={
                    "status": status.value,
                    "function_name": "create_google_doc_for_event",
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
            if not user:
                err = {"error": "Error: User not found. Please log in again."}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
            if not user.oauthToken:
                err = {"error": "Error: Google account not connected. Please connect your Google account in Settings."}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
            if not user.oauthToken.get('access_token'):
                err = {"error": "Error: Google access token expired. Please reconnect your Google account."}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
                
            headers = {"Authorization": f"Bearer {user.oauthToken.get('access_token')}", "Content-Type": "application/json"}
            #Create empty document
            res = requests.post("https://docs.googleapis.com/v1/documents", headers=headers, json={"title": f"Event Plan: {reqData.event_id}"})
            if res.status_code != 200:
                err = {"error": f"Error creating doc: {res.text}"}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
                
            doc_id = res.json().get('documentId')
            #Insert text
            insert_req = {
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": reqData.plan_text
                        }
                    }
                ]
            }
            res2 = requests.post(f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate", headers=headers, json=insert_req)
            doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
            res_data = {"link": doc_link, "message": f"Successfully created your Google Doc: {doc_link}"}
            push_status(SAGAStepStatusEnum.COMPLETED, res_data)
            return res_data
        except Exception as e:
            err = {"error": f"Internal task error: {str(e)}"}
            push_status(SAGAStepStatusEnum.FAILED, err)
            return err
