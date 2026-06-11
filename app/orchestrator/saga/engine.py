import json
import os
from app import scheduler
from typing import Optional
from app.models.saga_workflow import SAGA_workflow
from app.models.enum.SAGAWorkflowStatusEnum import SAGAWorkflowStatusEnum
from app.models.saga_steps import SAGA_steps
from app.models.enum.SAGAStepTypeEnum import SAGAStepTypeEnum
from app.models.enum.SAGAStepStatusEnum import SAGAStepStatusEnum

from app.ai_workers.workflow.full_workflow import execute_workflow
from app.orchestrator.services.document_service import document_service
from app.orchestrator.redis_orchestrator_queue import listen_to_response_channel
from datetime import datetime
from app.config import getRedisClient
from app.orchestrator.saga.redis_save import (
    execute_workflow_redis,
    create_google_doc_for_event_task_redis,
    automate_google_meet_task_redis,
    post_image_to_facebook_page_task_redis,
    schedule_real_google_calendar_task_redis
)

from app.orchestrator.services.meet_service import meet_service
from app.orchestrator.services.social_service import social_service
from app.orchestrator.services.calendar_service import calendar_service
from app.orchestrator.saga.payload_creator import (
    create_google_doc_for_event_task_payload,
    automate_google_meet_task_payload,
    post_image_to_facebook_page_task_payload,
    schedule_real_google_calendar_task_payload
)
from errors import APIError

TASK_MAPPING = {
    "execute_workflow": execute_workflow,
    "create_google_doc_for_event": document_service.create_google_doc_for_event_task,
    "automate_google_meet": meet_service.automate_google_meet_task,
    "post_image_to_facebook_page": social_service.post_image_to_facebook_page_task,
    "schedule_real_google_calendar": calendar_service.schedule_real_google_calendar_task
}
REDIS_MAPPING = {
    "execute_workflow": execute_workflow_redis,
    "create_google_doc_for_event": create_google_doc_for_event_task_redis,
    "automate_google_meet": automate_google_meet_task_redis,
    "post_image_to_facebook_page": post_image_to_facebook_page_task_redis,
    "schedule_real_google_calendar": schedule_real_google_calendar_task_redis
}
PAYLOADS = {
    "create_google_doc_for_event": create_google_doc_for_event_task_payload,
    "automate_google_meet": automate_google_meet_task_payload,
    "post_image_to_facebook_page": post_image_to_facebook_page_task_payload,
    "schedule_real_google_calendar": schedule_real_google_calendar_task_payload
}
class engine:
    def __init__(self):
        self.redis_client = getRedisClient()

    @staticmethod
    def start_engine(userID:str, prompt:str,org_id:str,page_id:Optional[str]):
        try:
            newWorkflow = SAGA_workflow(
                userID=userID,
                status=SAGAWorkflowStatusEnum.PROCESSING
            )
            newWorkflow.save()
            #save the page id if there
            if page_id:
                redis_client = getRedisClient()
                redis_key = f"saga_cache:{userID}:{str(newWorkflow.id)}"
                first_cache_save = {
                    "page_id":page_id
                }
                json_payload = json.dumps(first_cache_save, default=str)
                redis_client.set(redis_key, json_payload)
            execute_workflow.delay(userID,prompt,org_id,str(newWorkflow.id))
        except Exception as e:
            print(f"Error in start_engine: {e}") 

# @scheduler.task('interval', id='orch_background', seconds=30, misfire_grace_time=900)
def background_orches_worker():
    try:
        print("background orches ")
        redis_client = getRedisClient()
        pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
        channel = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            print("listeneing.....")
            try:
                if message['type'] != 'message':
                    continue
                payload = json.loads(message['data'].decode('utf-8'))
                current_function_name = payload.get('function_name')
                if not current_function_name:
                    continue

                # update redis
                function_redis = REDIS_MAPPING.get(current_function_name)
                if function_redis:
                    function_redis(payload, redis_client)

                # save mongo
                inner_payload = payload.get('payload', {})
                newStep = SAGA_steps(
                    workflow_ID = inner_payload.get('workflowID'),
                    step_type = SAGAStepTypeEnum(current_function_name),
                    step_status = SAGAStepStatusEnum(payload.get('status')),
                    total_time_ms = payload.get('ms'),
                    response_json = payload
                )
                newStep.save()

                # find the next step
                rules_path = os.path.join(os.path.dirname(__file__), '..', 'step_rules', 'rules_v1.json')
                with open(rules_path, 'r') as f:
                    rules = json.load(f)
                    
                next_function_name = None
                steps = rules.get('main_steps', [])
                for i, step in enumerate(steps):
                    if step.get('function_name') == current_function_name:
                        if i + 1 < len(steps):
                            next_function_name = steps[i+1].get('function_name')
                        break

                if next_function_name:
                    selectedStep = TASK_MAPPING.get(next_function_name)
                    if selectedStep is not None:
                        selected_payload_fun = PAYLOADS.get(next_function_name)
                        generated_payload = selected_payload_fun(inner_payload.get('user_id'), inner_payload.get('workflowID'))
                        
                        if hasattr(generated_payload, 'model_dump'):
                            data_for_task = generated_payload.model_dump()
                        elif hasattr(generated_payload, 'dict'):
                            data_for_task = generated_payload.dict()
                        else:
                            data_for_task = generated_payload
                            
                        print(f"Calling Celery task: {next_function_name}")
                        selectedStep.delay(data_for_task)
                    else:
                        raise APIError("500", f"Task selected is empty for {next_function_name}")
                else:
                    print(f"Reached the end of the workflow for workflowID: {inner_payload.get('workflowID')}")
            except Exception as inner_e:
                print(f"Error processing message: {inner_e}")
    except Exception as e:
        print(f"Error in background_orches_worker: {e}")
    
