import io
import json
import os
import tempfile
import uuid
from urllib.parse import quote

import cloudinary
import requests
from mdtopptx import create_ppt, parse_markdown

from app.models.projects import Projects
from app.models.tasks import tasks
from app.models.userAcc import userAcc


#create the event in the DB
def create_event(name: str, description: str, org_id: str, owner_id: str, start_time: str = None, end_time: str = None) -> str:
    # Lookup the user to verify limits
    user = userAcc.objects(sub=owner_id).first()
    if not user:
        return f"Error: User not found with ID {owner_id}"
    # if user.limits.projectsCount >= 5 and user.payments.tier == 'free':
    #     return "Error: Free tier limit of 5 projects reached. Please upgrade to create more."
    project = Projects(
        name=name,
        description=description,
        orgID=org_id,
        ownerID=owner_id,
        attendeeCountExpected=100,
        industry=["IT"],
        userRole=["manager"]
    )
    if start_time:
        project.startDate = start_time
    if end_time:
        project.endDate = end_time
    try:
        project.save()
        # Increment usage
        user.limits.projectsCount += 1
        user.save()
    except Exception as e:
        return f"Error saving event to database: {str(e)}"
    
    event_id_str = str(project.id)
    return f"SUCCESS: Event created. The event_id is: {event_id_str}. You MUST use this exact event_id ({event_id_str}) in all subsequent function calls (generate_media_for_event, create_google_doc_for_event, save_tasks_to_db)."
#create media
def generate_media_for_event(event_id: str, script_context: str) -> str:
    """Creates real media assets and links them to an event."""
    import io
    import re
    from urllib.parse import quote

    import cloudinary
    import cloudinary.uploader
    import requests
    # Validate ObjectId format
    if not re.match(r'^[a-f0-9]{24}$', str(event_id)):
        return f"Error: Invalid event_id '{event_id}'. It must be a 24-character hex string from create_event."

    project = Projects.objects(id=event_id).first()
    if not project:
        return f"Error: Event {event_id} not found."
    safe_prompt = quote(f"{project.name} {script_context[:100]} professional event cover art")
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&nologo=true&model=flux"
    try:
        response = requests.get(image_url, timeout=15)
        if response.status_code == 200:
            image_bytes = response.content
            image_stream = io.BytesIO(image_bytes)
            try:
                upload_result = cloudinary.uploader.upload(
                    image_stream,
                    folder="eventrio_media"
                )
                final_cloudinary_url = upload_result.get('secure_url')
                project.mediaLinks = [final_cloudinary_url]
            except Exception as upload_error:
                print(f"Cloudinary upload failed: {upload_error}")
                project.mediaLinks = [image_url]
        else:
            project.mediaLinks = [image_url]
    except requests.exceptions.RequestException as req_error:
        print(f"Failed to fetch image from Pollinations: {req_error}")
        project.mediaLinks = [image_url]
    safe_script = quote(script_context)
    script_url = f"data:text/plain;charset=utf-8,{safe_script}"
    project.scriptLink = script_url
    try:
        project.save()
    except Exception as e:
        return f"Error linking media to event: {str(e)}"
    return f"Media generated and linked to event {event_id} (Image & Script ready)."

#create the google doc part
def create_google_doc_for_event(owner_id: str, event_id: str, plan_text: str) -> str:
    user = userAcc.objects(sub=owner_id).first()
    if not user:
        return "Error: User not found. Please log in again."
    if not user.oauthToken:
        return "Error: Google account not connected. Please connect your Google account in Settings."
    if not user.oauthToken.get('access_token'):
        return "Error: Google access token expired. Please reconnect your Google account."
    headers = {"Authorization": f"Bearer {user.oauthToken.get('access_token')}", "Content-Type": "application/json"}
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

#create google meet link
def automate_google_meet(owner_id: str, event_details: dict, event_id: str = None):
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

#post fb posts
def post_image_to_facebook_page(owner_id, page_id, message, event_id=None, image_url=None):
    user = userAcc.objects(sub=owner_id).first()
    if not user or not user.socialMediaTokens or not user.socialMediaTokens.facebook:
        return {"error": "Facebook token missing for this user. Please connect Facebook in Settings."}
    
    user_token = user.socialMediaTokens.facebook
    if not image_url and event_id:
        project = Projects.objects(id=event_id).first()
        if project and project.mediaLinks:
            image_url = project.mediaLinks[0]

    if page_id:
        #Get the Page Access Token
        accounts_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={user_token}"
        try:
            accounts_data = requests.get(accounts_url).json()
        except Exception as e:
            return {"error": f"Failed: Could not reach Facebook API. {str(e)}"}

        page_token = None
        for page in accounts_data.get('data', []):
            if page.get('id') == page_id:
                page_token = page.get('access_token')
                break

        if not page_token:
            return {"error": "Failed: Page not found or permissions missing."}

        #Publish the Photo to the Page (Note the /photos endpoint)
        post_url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

        if image_url:
            payload = {
                'message': message,
                'url': image_url,
                'access_token': page_token
            }
            try:
                response = requests.post(post_url, data=payload, timeout=10)
                return response.json()
            except Exception as e:
                return {"error": f"Failed to post: {str(e)}"}
        else:
            return {"error": "Failed: No image available for this event to post."}
    else:
        return None  # Skipped FB publishing (No Page Selected)

#create the google calendar part
def schedule_real_google_calendar(owner_id: str, event_name: str, start_time: str, end_time: str) -> str:
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

#create slides using the markdown
def create_slides(markdown_text: str,eventID : str):
    if not markdown_text:
        return {"link": None, "error": "Markdown text is empty."}

    temp_path = None
    try:
        parsed_slides = parse_markdown(markdown_text)
        if not parsed_slides:
            return {"link": None, "error": "Failed to parse markdown slides."}
    except Exception as e:
        return {"link": None, "error": f"Error parsing markdown: {str(e)}"}

    try:
        #Create the temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as temp_file:
            temp_path = temp_file.name

        #Generate the file to the temporary disk path
        create_ppt(parsed_slides, temp_path)

        #Read the file into a Python variable
        with open(temp_path, 'rb') as f:
            pptx_memory_file = io.BytesIO(f.read())

        #Reset the stream position so it can be read by other functions
        pptx_memory_file.seek(0)
        #upload the file to cloud
        upload_result = cloudinary.uploader.upload(
            pptx_memory_file,
            folder="eventrio_media",
            resource_type="raw",
            format="pptx",
            public_id=f"eventrio_presentation_{eventID}"
        )
        final_cloudinary_url = upload_result.get('secure_url')
        if not final_cloudinary_url:
            return {"link": None, "error": "Cloudinary upload failed to return a URL."}

        #saving the url    
        currentProject = Projects.objects(id=eventID).first()
        currentProject.slideShowLink = final_cloudinary_url
        try:
            currentProject.save()
        except Exception as db_e:
            print(f"Error saving Slide Show Link to Project: {db_e}")

        return {"link": final_cloudinary_url, "error": None}

    except Exception as e:
        print(f"Slide creation failed: {e}")
        return {"link": None, "error": f"Slide generation or upload failed: {str(e)}"}

    finally:
        #Clean up the disk
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

#save tasks to DB
def save_tasks_to_db(owner_id: str, event_id: str,org_id:str, tasks_data_json: str) -> str:
    import re
    # Validate ObjectId format
    if not re.match(r'^[a-f0-9]{24}$', str(event_id)):
        return f"Error: Invalid event_id '{event_id}'. It must be a 24-character hex string from create_event."
    project = Projects.objects(id=event_id).first()
    if not project: return "Error: Event not found."
    
    # Securely use the orgID from the verified project instead of trusting the LLM
    org_id = project.orgID
    try:
        if isinstance(tasks_data_json, str):
            # Strip out any conversational fluff before or after the JSON array
            tasks_data_json = tasks_data_json.strip()
            start_idx = tasks_data_json.find('[')
            end_idx = tasks_data_json.rfind(']')
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                tasks_data_json = tasks_data_json[start_idx:end_idx+1]
            
            tasks_data = json.loads(tasks_data_json)
        else:
            tasks_data = tasks_data_json
            
        # Handle if model wraps the list in a "tasks" or "task_list" key
        if isinstance(tasks_data, dict):
            for key in ["tasks", "task_list", "items"]:
                if key in tasks_data and isinstance(tasks_data[key], list):
                    tasks_data = tasks_data[key]
                    break
    except Exception as e:
        return f"Error: Invalid JSON format for tasks_data_json. {e}"

    if not isinstance(tasks_data, list):
        return "Error: tasks_data_json must be a JSON array or an object containing a list under 'tasks'."
    new_tasks = []
    for item in tasks_data:
        # Convert empty strings to None for DateTimeField validation
        start_date = item.get('start_date')
        due_date = item.get('due_date')
        
        newTask = tasks(
            orgID=org_id,
            event_id=event_id,
            created_by="SYSTEM",
            assigned_to="NONE",
            title=item.get('title', 'Untitled Task'),
            description=item.get('description',''),
            startDate=start_date if start_date else None,
            deadline=due_date if due_date else None,
            media_links=[]
        )
        try:
            newTask.save()
        except Exception as e:
            print(f"Error saving task '{item.get('title')}': {e}")
            continue
    return f"Successfully processed tasks to MongoDB."
