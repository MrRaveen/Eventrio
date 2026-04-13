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

    async def run_async(self, user_id=None, session_id=None, new_message=None, **kwargs):
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
                tasks_data_json=os.getenv('TEST_TASKS_DATA')
            )

            results_stream = [
                f"**System Log:** Event created natively. ID: {clean_event_id}\n\n",
                f"**Media:** {createMediaRes}\n\n",
                f"**Documentation:** {docResult}\n\n",
                f"**Scheduling:** {calendarResult}\n\n",
                f"**Tasks:** {tasksSaveRes}"
            ]

            for chunk in results_stream:
                await asyncio.sleep(0.1) 
                yield MockEvent(chunk)

        except Exception as e:
            error_message = f"Critical Mock Execution Error: {str(e)}"
            print(error_message)
            yield MockEvent(error_message)


