import requests
from celery import shared_task
from app.models.userAcc import userAcc

@shared_task(bind=True)
def schedule_real_google_calendar_task(self, owner_id: str, event_name: str, start_time: str, end_time: str) -> str:
    """Schedule the event directly into the user's Google Calendar natively."""
    user = userAcc.objects(sub=owner_id).first()
    if not user:
        return "Error: User not found. Please log in again."
    if not user.oauthToken:
        return "Error: Google account not connected. Please connect your Google account in Settings."
    if not user.oauthToken.get('access_token'):
        return "Error: Google access token expired. Please reconnect your Google account."
    token = user.oauthToken.get('access_token')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "summary": event_name,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time}
    }
    res = requests.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", headers=headers, json=payload)
    if res.status_code != 200: return f"Error scheduling calendar: {res.text}"
    event_link = res.json().get('htmlLink')
    return f"Successfully scheduled Event in your calendar! Link: {event_link}"
