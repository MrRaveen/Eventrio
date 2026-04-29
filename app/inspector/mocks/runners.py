from app.agents.manual_services import create_slides
from app.agents.manual_services import automate_google_meet
from app.models.posts import Posts
from app.agents.manual_services import post_image_to_facebook_page
from app.models.userAcc import userAcc
from app.models.projects import Projects
from app.agents.manual_services import save_tasks_to_db
from app.agents.manual_services import schedule_real_google_calendar
from app.agents.manual_services import create_google_doc_for_event
from app.agents.manual_services import generate_media_for_event
from app.agents.manual_services import create_event
import asyncio
#classes which builds event->content->parts->text chain section with a delay
class MockPart:
    def __init__(self, text):
        self.text = text

class MockContent:
    def __init__(self, text):
        self.parts = [MockPart(text)]

class MockEvent:
    def __init__(self, text):
        self.content = MockContent(text)   

class Runner:
    def __init__(self,app_name:str,agent,session_service,auto_create_session):
        self.app_name = app_name
        self.agent = agent
        self.session_service = session_service
        self.auto_create_session = auto_create_session

    async def run_async(self, user_id=None,fbPageID=None,session_id=None, new_message=None, **kwargs):
        import os
        import asyncio

        required_env_vars = [
            'TEST_ORG_ID', 'TEST_EVENT_NAME', 'TEST_DES', 'TEST_START_TIME', 
            'TEST_END_TIME', 'TEST_SCRIPT_CONTEXT_IMG_GEN', 'TEST_PLAN_TEXT', 'TEST_TASKS_DATA'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            yield MockEvent(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
            return

        try:
            createEventResult = create_event(
                name=os.getenv('TEST_EVENT_NAME'),
                description=os.getenv('TEST_DES'),
                start_time=os.getenv('TEST_START_TIME'),
                end_time=os.getenv('TEST_END_TIME'),
                org_id=os.getenv('TEST_ORG_ID'),
                owner_id=user_id
            )

            if "Error" in createEventResult:
                yield MockEvent(f"Agent Action Failed: {createEventResult}")
                return
            clean_event_id = createEventResult.split("ID: ")[-1].strip(".")
     
            
            createMediaRes = generate_media_for_event(
                event_id=clean_event_id,
                script_context=os.getenv('TEST_SCRIPT_CONTEXT_IMG_GEN')
            )
            updatedUser = userAcc.objects(sub=user_id).first()
            tokenFb = updatedUser.socialMediaTokens.facebook if (updatedUser and updatedUser.socialMediaTokens) else None
            currentProject = Projects.objects(id=clean_event_id).first()
            media = currentProject.mediaLinks[0] if currentProject and currentProject.mediaLinks else None

            #create slides
            slide_result = create_slides(
                markdown_text=os.getenv('TEST_MOCK_SLIDESHOW_MD'),
                eventID=currentProject.id
            )
            if isinstance(slide_result, dict) and slide_result.get('link'):
                currentProject.slideShowLink = slide_result['link']
                try:
                    currentProject.save()
                except Exception as db_e:
                    print(f"Error saving Slide Show Link to Project: {db_e}")
            elif isinstance(slide_result, dict) and slide_result.get('error'):
                print(f"Slide Creation Error: {slide_result['error']}")

            #create the google meet event safely
            accessToken = None
            if updatedUser and hasattr(updatedUser, 'oauthToken') and updatedUser.oauthToken:
                if isinstance(updatedUser.oauthToken, dict):
                    accessToken = updatedUser.oauthToken.get('access_token')
                else: 
                    accessToken = getattr(updatedUser.oauthToken, 'access_token', None)
            if accessToken and currentProject:
                eventDetails = {
                    "title": os.getenv('TEST_EVENT_NAME'),
                    "start_time": os.getenv('TEST_START_TIME'),
                    "end_time": os.getenv('TEST_END_TIME')
                }
                meet_result = automate_google_meet(user_access_token=accessToken, event_details=eventDetails)
                if isinstance(meet_result, dict) and 'link' in meet_result:
                    currentProject.meetingUrl = meet_result['link']
                    try:
                        currentProject.save()
                    except Exception as db_e:
                        print(f"Error saving Meeting URL to Project: {db_e}")
                elif isinstance(meet_result, dict) and 'error' in meet_result:
                    print(f"Meet Creation Error: {meet_result['error']}")
            else:
                print("Skipped Google Meet creation. Missing Google Access Token or Project.")


            # Facebook Posting Logic with Validation and Error Handling
            fb_status = None
            if tokenFb and fbPageID and media:
                fb_status = post_image_to_facebook_page(
                    image_url=media,
                    message=os.getenv('TEST_DES'),
                    user_token=tokenFb,
                    page_id=fbPageID
                )
                
                # Check for successful post (FB returns an 'id' on success)
                if isinstance(fb_status, dict) and 'post_id' in fb_status:
                    try:
                        postID = fb_status.get('post_id')
                        newPostDoc = Posts(
                            postID=postID,
                            postTitle=f"Post for {os.getenv('TEST_EVENT_NAME')}",
                            description=os.getenv('TEST_DES'),
                            imageUrl=media,
                            projectID=clean_event_id,
                            orgID=os.getenv('TEST_ORG_ID')
                        )
                        newPostDoc.save()
                    except Exception as db_e:
                        print(f"Error saving Post document for {clean_event_id}: {db_e}")
                elif isinstance(fb_status, dict) and 'error' in fb_status:
                    print(f"Facebook API Error: {fb_status.get('error')}")
            else:
                missing = []
                if not tokenFb: missing.append("FB Token")
                if not fbPageID: missing.append("FB Page ID")
                if not media: missing.append("Media URL")
                print(f"Skipped Facebook posting. Missing: {', '.join(missing)}")


            docResult = create_google_doc_for_event(
                event_id=clean_event_id,
                owner_id=user_id,
                plan_text=os.getenv('TEST_PLAN_TEXT')
            )
            
            calendarResult = schedule_real_google_calendar(
                owner_id=user_id,
                event_name=os.getenv('TEST_EVENT_NAME'),
                start_time=os.getenv('TEST_START_TIME'),
                end_time=os.getenv('TEST_END_TIME')
            )
            
            tasksSaveRes = save_tasks_to_db(
                owner_id=user_id,
                event_id=clean_event_id,
                org_id=os.getenv('TEST_ORG_ID'),
                tasks_data_json=os.getenv('TEST_TASKS_DATA')
            )

            results_stream = [
                f"**System Log:** Event created natively. ID: {clean_event_id}\n\n",
                f"**Media:** {createMediaRes}\n\n",
                f"**Documentation:** {docResult}\n\n",
                f"**Scheduling:** {calendarResult}\n\n",
                f"**Tasks:** {tasksSaveRes}\n\n",
                f"**FB status:** {fb_status}",
            ]

            for chunk in results_stream:
                await asyncio.sleep(0.1) 
                yield MockEvent(chunk)

        except Exception as e:
            error_message = f"Critical Mock Execution Error: {str(e)}"
            event_to_remove = Projects.objects(id=clean_event_id).first()
            if event_to_remove:
                event_to_remove.delete()
            print(error_message)
            yield MockEvent(error_message)


