import uuid
import requests
from celery import shared_task
from app.models.projects import Projects
from app.models.userAcc import userAcc

@shared_task(bind=True)
def automate_google_meet_task(self, owner_id: str, event_details: dict, event_id: str = None):
    user = userAcc.objects(sub=owner_id).first()
    if not user or not user.oauthToken or not user.oauthToken.get('access_token'):
        return {"error": "Google authentication missing or expired for this user."}
    
    user_access_token = user.oauthToken.get('access_token')
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1"
    headers = {"Authorization": f"Bearer {user_access_token}"}

    try:
        title = event_details.get('title', 'Eventrio Meeting')
        start_time = event_details.get('start_time')
        end_time = event_details.get('end_time')

        if not start_time or not end_time:
            return {"error": "Start time and end time are required for a meeting."}

        # Google Calendar API with timeZone expects dateTime without 'Z' suffix
        if start_time.endswith('Z'):
            start_time = start_time[:-1]
        if end_time.endswith('Z'):
            end_time = end_time[:-1]

        payload = {
            "summary": title,
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
                if event_id:
                    project = Projects.objects(id=event_id).first()
                    if project:
                        project.meetingUrl = link
                        try:
                            project.save()
                        except Exception as db_err:
                            print(f"Error saving meetingUrl: {db_err}")
                return {"link": link}
            return {"error": "Google API did not return a hangout link."}
        else:
            return {"error": f"Google Calendar API Error: {response.text}"}
    except Exception as e:
        return {"error": f"Failed to automate Google Meet: {str(e)}"}
