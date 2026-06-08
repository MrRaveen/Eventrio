import json
import os
from app.models.saga_workflow import SAGA_workflow
from app.models.enum.SAGAWorkflowStatusEnum import SAGAWorkflowStatusEnum
from app.models.saga_steps import SAGA_steps
from app.models.enum.SAGAStepTypeEnum import SAGAStepTypeEnum
from app.models.enum.SAGAStepStatusEnum import SAGAStepStatusEnum

# Import celery tasks
from app.ai_workers.workflow.full_workflow import execute_workflow
from app.orchestrator.services import (
    create_google_doc_for_event_task,
    automate_google_meet_task,
    post_image_to_facebook_page_task,
    schedule_real_google_calendar_task
)
from app.orchestrator.redis_orchestrator_queue import listen_to_response_channel

TASK_MAPPING = {
    "execute_workflow": execute_workflow,
    "create_google_doc_for_event": create_google_doc_for_event_task,
    "automate_google_meet": automate_google_meet_task,
    "post_image_to_facebook_page": post_image_to_facebook_page_task,
    "schedule_real_google_calendar": schedule_real_google_calendar_task
}

class engine:
    @staticmethod
    def execute_saga(userID:str, prompt:str, isRecovery: bool = False):
        try:
            if isRecovery:
                pass
            else:
                newWorkflow = SAGA_workflow(
                    userID=userID,
                    status=SAGAWorkflowStatusEnum.PROCESSING
                )
                newWorkflow.save()
                
                # Load JSON file
                rules_path = os.path.join(os.path.dirname(__file__), '..', 'step_rules', 'rules_v1.json')
                with open(rules_path, 'r') as f:
                    rules = json.load(f)
                
                for step in rules.get('main_steps', []):
                    function_name = step.get('function_name')
                    task_function = TASK_MAPPING.get(function_name)
                    
                    if task_function:
                        print(f"Calling Celery task: {function_name}")
                        newStep = SAGA_steps(
                            workflow_ID = str(newWorkflow.id),
                            step_type = SAGAStepTypeEnum(function_name),
                            step_status = SAGAStepStatusEnum.PROGRESS
                        )
                        newStep.save()
                        
                        import time
                        start_time = time.time()
                        #todo: pass the data taken from the response json
                        if function_name == "execute_workflow":
                            task_function.delay(userID, prompt)
                        else:
                            task_function.delay()
                        result = listen_to_response_channel(task_terminate = function_name)   
                        end_time = time.time()
                        time_diff_ms = int((end_time - start_time) * 1000)
                        
                        oldStep =  SAGA_steps.objects(id=newStep.id).first()
                        if oldStep and result:
                            status_str = result.get("status")
                            if status_str:
                                try:
                                    oldStep.step_status = SAGAStepStatusEnum(status_str)
                                except ValueError:
                                    oldStep.step_status = SAGAStepStatusEnum.ERROR
                            
                            oldStep.response_json = result.get("data", {})
                            oldStep.total_time_ms = time_diff_ms
                            oldStep.save()

                    else:
                        print(f"Task mapping not found for function: {function_name}")
                    
        except Exception as e:
            print(f"Error in execute_saga: {e}")


