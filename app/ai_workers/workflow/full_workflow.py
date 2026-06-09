import os
import json

from celery import Celery, shared_task
from flask import Flask, jsonify, request
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

from app.agents.manual_services import create_slides
from app.ai_workers.nodes.extract_basic_node import extract_basic_node
from app.ai_workers.nodes.generate_announcing_script_node import (
    generate_announcing_script_node,
)
from app.ai_workers.nodes.generate_media_node import generate_media_node
from app.ai_workers.nodes.generate_readme_node import generate_readme_node
from app.ai_workers.nodes.save_details_node import save_details_node
from app.ai_workers.nodes.update_details_node import update_details_node
from app.ai_workers.state import EventState
from app.models.enum.stepStatusEnum import stepStatusEnum
from app.orchestrator.channel_output import channel_output
from app.config import getRedisClient
from errors import APIError


def get_compiled_pipeline():
    workflow = StateGraph(EventState)

    # Initialize shared clients
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2
    )

    # Register nodes (classes must be instantiated)
    workflow.add_node("extract_basic_data", extract_basic_node(model="groq/llama-3.3-70b-versatile"))
    workflow.add_node("save_details", save_details_node())
    workflow.add_node("create_announcing_script", generate_announcing_script_node(model="groq/llama-3.3-70b-versatile"))
    workflow.add_node("create_media", generate_media_node(width=1024, height=1024, model="flux", count=1))
    workflow.add_node("create_readme", generate_readme_node(llm_client=llm))
    workflow.add_node("update_details_node", update_details_node())

    # Define the execution edges sequentially
    workflow.add_edge(START, "extract_basic_data")
    workflow.add_edge("extract_basic_data", "save_details")
    workflow.add_edge("save_details", "create_announcing_script")
    workflow.add_edge("create_announcing_script", "create_media")
    workflow.add_edge("create_media", "create_readme")
    workflow.add_edge("create_readme", "update_details_node")
    workflow.add_edge("update_details_node", END)

    event_pipeline = workflow.compile()
    return event_pipeline

@shared_task(name='execute_workflow')
def execute_workflow(user_id: str, prompt: str,orgID:str,workflowID:str):
    try:
        start_time = time.time()
        redis_client = getRedisClient()
        channel_name = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
        # Initial input validation
        if not user_id or not isinstance(user_id, str):
            raise APIError("400", "Valid user_id is required")

        if not prompt or not isinstance(prompt, str):
            raise APIError("400", "Valid prompt is required")

        initial_state: EventState = {
            "user_id": user_id,
            "prompt": prompt,
            "org_id":orgID
        }

        event_pipeline = get_compiled_pipeline()
        final_state = event_pipeline.invoke(initial_state)

        readme_result = final_state.get("readme_result")
        project_id = final_state.get("project_id")

        # Testing only - generating slides
        if readme_result and project_id:
            create_slides(readme_result, project_id)
        #update the workflow for project id or save it
        currentWorkflow = SAGA_workflow.objects(id=workflowID).first()
        if currentWorkflow:
            currentWorkflow.eventID = project_id
            currentWorkflow.save()
        else:
            newWorkflow = SAGA_workflow(
                userID=user_id,
                status=SAGAWorkflowStatusEnum.PROCESSING,
                eventID=project_id
            )
            newWorkflow.save()    
        final_event_details = final_state.get('event_details',{})
        validated_event_details = EventDetailsSchema(**final_event_details)
        end_time = time.time()
        time_diff_ms = int((end_time - start_time) * 1000)
        pushing_data = channel_output(
            return_data={
                "status":SAGAStepStatusEnum.COMPLETED.value,
                "function_name":"execute_workflow",
                "ms":time_diff_ms,
                "payload":{
                "project_id":project_id,
                "workflowID":workflowID,
                "user_id":final_state.get('user_id'),
                "plan_des": validated_event_details.event_plan,
                "event_name":validated_event_details.event_name,
                "start_time":validated_event_details.start_time,
                "end_time":validated_event_details.end_time,
                "event_description":validated_event_details.event_description
                }
            }
        )
        converted_data = json.dumps(pushing_data.return_data,default=str)
        sub_count = redis_client.publish(channel_name,converted_data)
    except APIError as api_err:
        return {"status": "error", "error_code": api_err.error_code, "message": api_err.error_message}, int(api_err.error_code)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}, 500

# # --- TESTING SECTION ---
# app = Flask(__name__)

# # Initialize a basic Celery instance for testing within this file
# app.config.update(
#     CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
#     CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
# )

# test_celery = Celery(
#     app.import_name,
#     broker=app.config['CELERY_BROKER_URL'],
#     backend=app.config['CELERY_RESULT_BACKEND']
# )
# test_celery.conf.update(app.config)

# @app.route('/test-workflow', methods=['POST'])
# def test_workflow():
#     data = request.json or {}
#     user_id = data.get('user_id', 'test_user_123')
#     prompt = data.get('prompt', 'Plan a small tech meetup.')

#     # Execute the Celery task asynchronously
#     task = execute_workflow.delay(user_id, prompt)

#     return jsonify({
#         "status": "Task Queued",
#         "task_id": str(task.id)
#     }), 202

# if __name__ == '__main__':
#     print("Starting test Flask server on port 5001...")
#     app.run(host='0.0.0.0', port=5001, debug=True)
