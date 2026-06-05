import os
import json
import sys
import datetime
import traceback
import instructor
from litellm import completion
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from flask import Flask, request

from app.agents.manual_services import generate_media_for_event, create_slides
from app.agents.outputSchemas import EventDetailsSchema
from app.models.projects import Projects

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv()

from app.db import init_db
init_db()

modelDeployment = os.getenv('MODEL_DEPLOYMENT', 'local')

app = Flask(__name__)

class EventState(TypedDict):
    event_details: Dict[str, Any]
    project_id: str
    media_result: Optional[Any]
    readme_result: Optional[str]

class optimized_flow:
    @staticmethod
    def generate_media_node(state: EventState) -> Dict[str, Any]:    
        try:
            event_details = state["event_details"]
            img_prompt = event_details.get("image_prompt", "")
            media_result = generate_media_for_event(state["project_id"], img_prompt)
            return {"media_result": media_result}
        except Exception as e:
            return {"media_result": str(e)}

    @staticmethod
    def generate_readme_node(state: EventState) -> Dict[str, Any]:
        try:
            event_details = state["event_details"]
            llm = ChatGroq(
                model="llama-3.3-70b-versatile", 
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.2
            )
            prompt = PromptTemplate.from_template("""
            You are a presentation creator. Generate a markdown slide deck for the event.

            --- EVENT DETAILS ---
            {event_details}
            ---

            FORMAT RULES:
            - Slide titles are level-1 headings: # Title Here
            - Slide separators are three dashes: ---
            - Bullet points use hyphens: - Point here
            - Separate every slide with --- on its own line

            Generate a 4-6 slide markdown presentation based on the event details. 
            Output ONLY the markdown text.
            """)
            chain = prompt | llm
            response = chain.invoke({"event_details": json.dumps(event_details, indent=2)})
            return {"readme_result": response.content}
        except Exception as e:
            return {"readme_result": str(e)}   

    @staticmethod
    def extract_basic_details(prompt: str, user_id: str):
        try:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            client = instructor.from_litellm(completion)
            extracted_data = client.chat.completions.create(
                model="groq/llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert event planner. "
                            f"Today's date is {current_date}. All generated dates must be in the future. "
                            "IMPORTANT: You must write out your logical deductions, date calculations, "
                            "and brainstorming steps inside the 'chain_of_thought' field FIRST. "
                            "Only after completing your thought process should you populate the remaining fields."
                        )
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_model=EventDetailsSchema,
                max_retries=3, 
            )
            return extracted_data.model_dump() 
        except Exception as e:
            print(f"Error in extraction: {str(e)}")
            traceback.print_exc()
            return None      

    @staticmethod
    def get_compiled_pipeline():
        workflow = StateGraph(EventState)
       
        workflow.add_node("create_media", optimized_flow.generate_media_node)
        workflow.add_node("create_readme", optimized_flow.generate_readme_node)

        workflow.add_edge(START, "create_media")
        workflow.add_edge("create_media", "create_readme")
        workflow.add_edge("create_readme", END)

        event_pipeline = workflow.compile()
        return event_pipeline

@app.route('/test-flow', methods=['GET'])
def test():
    try:
        prompt = request.args.get('prompt', 'Plan a coding hackathon...')
        user_id = request.args.get('user_id', 'user_default')
        
        extracted_data = optimized_flow.extract_basic_details(prompt,user_id)
    
        if extracted_data:
            project = Projects(
                name=extracted_data.get('event_name') or "Untitled Event",
                description=extracted_data.get('event_description'),
                ownerID=user_id
            )
            project.save()
            
            initial_state = {
                "event_details": extracted_data,
                "project_id": str(project.id)
            }
            event_pipeline = optimized_flow.get_compiled_pipeline()
            final_state = event_pipeline.invoke(initial_state)
            create_slides(final_state.get("readme_result"),project.id)
            return {
                "status": "success",
                "extracted_data": extracted_data,
                "media_result": final_state.get("media_result"),
                "readme_result": final_state.get("readme_result")
            }, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)

