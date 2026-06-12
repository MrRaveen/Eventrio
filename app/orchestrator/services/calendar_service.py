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

class calendar_service:
    class req_data(BaseModel):
        owner_id: str
        event_name: str
        start_time: str
        end_time: str
        workflow_id: str

    @staticmethod
    @shared_task(name='schedule_real_google_calendar_task', bind=False)
    def schedule_real_google_calendar_task(reqData: dict):
        if isinstance(reqData, dict):
            reqData = calendar_service.req_data(**reqData)

        """Schedule the event directly into the user's Google Calendar natively."""
        start_time_exec = time.time()
        redis_client = getRedisClient()
        channel_name = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
        
        def push_status(status, payload):
            time_diff_ms = int((time.time() - start_time_exec) * 1000)
            pushing_data = channel_output(
                return_data={
                    "status": status.value,
                    "function_name": "schedule_real_google_calendar",
                    "ms": time_diff_ms,
                    "payload": {
                        "workflowID": reqData.workflow_id,
                        "user_id": reqData.owner_id,
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
                
            token = user.oauthToken.get('access_token')
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            cal_payload = {
                "summary": reqData.event_name,
                "start": {"dateTime": reqData.start_time},
                "end": {"dateTime": reqData.end_time}
            }
            res = requests.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", headers=headers, json=cal_payload)
            if res.status_code != 200:
                err = {"error": f"Error scheduling calendar: {res.text}"}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
                
            event_link = res.json().get('htmlLink')
            res_data = {"link": event_link, "message": f"Successfully scheduled Event in your calendar! Link: {event_link}"}
            push_status(SAGAStepStatusEnum.COMPLETED, res_data)
            return res_data
        except Exception as e:
            err = {"error": f"Internal task error: {str(e)}"}
            push_status(SAGAStepStatusEnum.FAILED, err)
            return err
