import instructor
from litellm import completion
from typing import Dict, Any
from datetime import datetime
from app.ai_workers.state import EventState
from app.ai_workers.outputSchema.announceOutputList import announceOutputList
from errors import APIError
class generate_announcing_script_node:
    def __init__(self,model:str):
        self.client = instructor.from_litellm(completion)
        self.model = model
    def __call__(self, state: EventState) -> Dict[str, Any]:
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            event_details = state.get("event_details", {})
            agenda = event_details.get("agenda", [])
            
            if not agenda:
                raise APIError("500", "No agenda found in event_details to generate announcing script.")

            prompt = (
                f"Here is the event agenda:\n{agenda}\n\n"
                "Please generate an enthusiastic and engaging announcing script for EACH item in this agenda."
            )

            extracted_data = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert, highly energetic MC (Master of Ceremonies) and event announcer. "
                            f"Today's date is {current_date}. "
                            "Your task is to take a provided event agenda and write out the exact script "
                            "you would speak to the audience to introduce and transition between each agenda item. "
                            "Follow the provided schema precisely."
                        )
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_model=announceOutputList,
                max_retries=3, 
            )
            
            return {"announcing_script_result": extracted_data.model_dump()}
            
        except APIError:
            raise
        except Exception as e:
            raise APIError("500", f"Error generating announcing script: {str(e)}")