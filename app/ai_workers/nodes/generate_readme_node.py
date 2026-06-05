import json
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from app.ai_workers.state import EventState
from errors import APIError

class generate_readme_node:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.prompt = PromptTemplate.from_template("""
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
            
    def __call__(self, state: EventState) -> Dict[str, Any]:
        try:
            if not state:
                raise APIError("400", "State is empty or None")
            if "event_details" not in state or not isinstance(state["event_details"], dict):
                raise APIError("400", "State missing required variable: event_details")
            
            event_details = state["event_details"]
            chain = self.prompt | self.llm
            response = chain.invoke({"event_details": json.dumps(event_details, indent=2)})
            return {"readme_result": response.content}
        except APIError:
            raise
        except Exception as e:
            raise APIError("500", f"Error occurred in readme generation: {str(e)}")
