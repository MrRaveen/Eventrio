from app.models.projects import Projects
from app.models.userAcc import userAcc
import uuid
import requests
import json
from urllib.parse import quote

#create the event in the DB
def create_event(name: str, description: str, org_id: str, owner_id: str, start_time: str = None, end_time: str = None) -> str:
    # Lookup the user to verify limits
    user = userAcc.objects(sub=owner_id).first()
    if not user:
        return f"Error: User not found with ID {owner_id}"
    if user.limits.projectsCount >= 5 and user.payments.tier == 'free':
        return "Error: Free tier limit of 5 projects reached. Please upgrade to create more."
    project = Projects(
        name=name,
        description=description,
        orgID=org_id,
        ownerID=owner_id
    )
    if start_time:
        project.startDate = start_time
    if end_time:
        project.endDate = end_time
    project.save()
    # Increment usage
    user.limits.projectsCount += 1
    user.save()
    # return f"Successfully created event '{name}' with ID: {str(project.id)}."
    return f"{str(project.id)}"

#create the media images
def generate_media_for_event(event_id: str, script_context: str) -> str:
    """Creates real media assets and links them to an event."""
    project = Projects.objects(id=event_id).first()
    if not project:
        return f"Error: Event {event_id} not found."
    # Generate a real image URL via Pollinations
    safe_prompt = quote(f"{project.name} {script_context[:100]} professional event cover art")
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&nologo=true"
    # Generate a real functional viewable text file using Data URIs for the script
    safe_script = quote(script_context)
    script_url = f"data:text/plain;charset=utf-8,{safe_script}"
    project.scriptLink = script_url
    project.mediaLinks = [image_url]
    project.save()
    return f"Media generated and linked to event {event_id} (Image & Script ready)."

#create the google doc part
def create_google_doc_for_event(owner_id: str, event_id: str, plan_text: str) -> str:
    user = userAcc.objects(sub=owner_id).first()
    if not user or not user.oauthToken: return "Error: No Google Auth token found."
    token = user.oauthToken.get('access_token')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    #Create empty document
    res = requests.post("https://docs.googleapis.com/v1/documents", headers=headers, json={"title": f"Event Plan: {event_id}"})
    if res.status_code != 200: return f"Error creating doc: {res.text}"
    doc_id = res.json().get('documentId')
    #Insert text
    insert_req = {
        "requests": [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": plan_text
                }
            }
        ]
    }
    res2 = requests.post(f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate", headers=headers, json=insert_req)
    doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
    return f"Successfully created your Google Doc: {doc_link}"

#create the google calendar part
def schedule_real_google_calendar(owner_id: str, event_name: str, start_time: str, end_time: str) -> str:
    """Schedule the event directly into the user's Google Calendar natively."""
    user = userAcc.objects(sub=owner_id).first()
    if not user or not user.oauthToken: return "Error: No Google Auth token found."
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

#save tasks to DB
def save_tasks_to_db(owner_id: str, event_id: str, tasks_data_json: str) -> str:
    project = Projects.objects(id=event_id).first()
    if not project: return "Error: Event not found."
    try:
        tasks_data = json.loads(tasks_data_json)
    except Exception as e:
        return f"Error: Invalid JSON format for tasks_data_json. {e}"

    if not isinstance(tasks_data, list):
        return "Error: tasks_data_json must be a JSON array."
    new_tasks = []
    for item in tasks_data:
        if isinstance(item, str):
            new_tasks.append({
                "id": str(uuid.uuid4()),
                "title": item,
                "isCompleted": False
            })
        elif isinstance(item, dict):
            new_tasks.append({
                "id": str(uuid.uuid4()),
                "title": item.get('title', 'Untitled Task'),
                "startDate": item.get('start_date', ''),
                "dueDate": item.get('due_date', ''),
                "isCompleted": False
            })
    project.tasks.extend(new_tasks)
    project.save()
    return f"Successfully saved {len(new_tasks)} tasks to MongoDB."

