import requests
from celery import shared_task
from app.models.projects import Projects
from app.models.userAcc import userAcc

@shared_task(bind=True)
def post_image_to_facebook_page_task(self, owner_id, page_id, message, event_id=None, image_url=None):
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
