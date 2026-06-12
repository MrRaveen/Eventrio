import uuid
import requests
import os
import json
import time
from celery import shared_task
from pydantic import BaseModel
from typing import Optional
from app.models.projects import Projects
from app.models.userAcc import userAcc
from app.config import getRedisClient
from app.orchestrator.channel_output import channel_output
from app.models.enum.SAGAStepStatusEnum import SAGAStepStatusEnum

class meet_service:
    class req_data(BaseModel):
        owner_id: str
        title: str
        start_time: str
        end_time: str
        event_id: Optional[str] = None
        workflow_id: str

    @staticmethod
    @shared_task(name='automate_google_meet_task', bind=False)
    def automate_google_meet_task(reqData: dict):
        if isinstance(reqData, dict):
            reqData = meet_service.req_data(**reqData)

        start_time_exec = time.time()
        redis_client = getRedisClient()
        channel_name = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
        
        def push_status(status, payload):
            time_diff_ms = int((time.time() - start_time_exec) * 1000)
            pushing_data = channel_output(
                return_data={
                    "status": status.value,
                    "function_name": "automate_google_meet",
                    "ms": time_diff_ms,
                    "payload": {
                        "workflowID": reqData.workflow_id,
                        "user_id": reqData.owner_id,
                        "project_id": reqData.event_id,
                        **payload
                    }
                }
            )
            converted_data = json.dumps(pushing_data.return_data, default=str)
            redis_client.publish(channel_name, converted_data)

        try:
            user = userAcc.objects(sub=reqData.owner_id).first()
            if not user or not user.oauthToken or not user.oauthToken.get('access_token'):
                err = {"error": "Google authentication missing or expired for this user."}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
            
            user_access_token = user.oauthToken.get('access_token')
            url = "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1"
            headers = {"Authorization": f"Bearer {user_access_token}"}

            if not reqData.start_time or not reqData.end_time:
                err = {"error": "Start time and end time are required for a meeting."}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err

            # Google Calendar API with timeZone expects dateTime without 'Z' suffix
            start_time = reqData.start_time
            end_time = reqData.end_time
            if start_time.endswith('Z'):
                start_time = start_time[:-1]
            if end_time.endswith('Z'):
                end_time = end_time[:-1]

            payload = {
                "summary": reqData.title,
                "start": {"dateTime": start_time, "timeZone": "Asia/Colombo"},
                "end": {"dateTime": end_time, "timeZone": "Asia/Colombo"},
                "conferenceData": {
                    "createRequest": {
                        "requestId": str(uuid.uuid4()),
                        "conferenceSolutionKey": {"type": "hangoutsMeet"}
                    }
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code in (200, 201):
                data = response.json()
                link = data.get('hangoutLink')
                if link:
                    if reqData.event_id:
                        project = Projects.objects(id=reqData.event_id).first()
                        if project:
                            project.meetingUrl = link
                            try:
                                project.save()
                            except Exception as db_err:
                                print(f"Error saving meetingUrl: {db_err}")
                    res_data = {"link": link}
                    push_status(SAGAStepStatusEnum.COMPLETED, res_data)
                    return res_data
                err = {"error": "Google API did not return a hangout link."}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
            else:
                err = {"error": f"Google Calendar API Error: {response.text}"}
                push_status(SAGAStepStatusEnum.FAILED, err)
                return err
        except Exception as str_err:
            err = {"error": f"Failed to automate Google Meet: {str(str_err)}"}
            push_status(SAGAStepStatusEnum.FAILED, err)
            return err
