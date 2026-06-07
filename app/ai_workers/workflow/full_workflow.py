import os
from celery import shared_task, Celery
from flask import Flask, request, jsonify
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

from app.ai_workers.state import EventState
from app.ai_workers.nodes.extract_basic_node import extract_basic_node
from app.ai_workers.nodes.generate_announcing_script_node import generate_announcing_script_node
from app.ai_workers.nodes.generate_media_node import generate_media_node
from app.ai_workers.nodes.generate_readme_node import generate_readme_node
from app.ai_workers.nodes.save_details_node import save_details_node
from app.agents.manual_services import create_slides
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

    # Define the execution edges sequentially
    workflow.add_edge(START, "extract_basic_data")
    workflow.add_edge("extract_basic_data", "save_details")
    workflow.add_edge("save_details", "create_announcing_script")
    workflow.add_edge("create_announcing_script", "create_media")
    workflow.add_edge("create_media", "create_readme")
    workflow.add_edge("create_readme", END)

    event_pipeline = workflow.compile()
    return event_pipeline

@shared_task(name='execute_workflow')
def execute_workflow(user_id: str, prompt: str):
    try:
        # Initial input validation
        if not user_id or not isinstance(user_id, str):
            raise APIError("400", "Valid user_id is required")
            
        if not prompt or not isinstance(prompt, str):
            raise APIError("400", "Valid prompt is required")

        initial_state: EventState = {
            "user_id": user_id,
            "prompt": prompt
        }
        
        event_pipeline = get_compiled_pipeline()
        final_state = event_pipeline.invoke(initial_state)
        
        readme_result = final_state.get("readme_result")
        project_id = final_state.get("project_id")
        
        # Testing only - generating slides
        if readme_result and project_id:
            create_slides(readme_result, project_id)
            
        return {
            "status": "success",
            "project_id": project_id,
            "extracted_data": final_state.get("event_details"),
            "announcing_script": final_state.get("announcing_script_result"),
            "media_result": final_state.get("media_result"),
            "readme_result": readme_result
        }, 200
        
    except APIError as api_err:
        return {"status": "error", "error_code": api_err.error_code, "message": api_err.error_message}, int(api_err.error_code)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}, 500

# --- TESTING SECTION ---
app = Flask(__name__)

# Initialize a basic Celery instance for testing within this file
app.config.update(
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

test_celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
test_celery.conf.update(app.config)

@app.route('/test-workflow', methods=['POST'])
def test_workflow():
    data = request.json or {}
    user_id = data.get('user_id', 'test_user_123')
    prompt = data.get('prompt', 'Plan a small tech meetup.')
    
    # Execute the Celery task asynchronously
    task = execute_workflow.delay(user_id, prompt)
    
    return jsonify({
        "status": "Task Queued",
        "task_id": str(task.id)
    }), 202

if __name__ == '__main__':
    print("Starting test Flask server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
