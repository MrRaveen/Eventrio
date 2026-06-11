import instructor
from litellm import completion
from typing import Dict, Any
from datetime import datetime
from app.ai_workers.state import EventState
from app.ai_workers.outputSchema.fbPostOutput import fbPostOutput
from errors import APIError
class generate_fb_node:
    def __init__(self,model:str):
        self.client = instructor.from_litellm(completion)
        self.model = model
    def __call__(self, state: EventState) -> Dict[str, Any]:
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            event_details = state.get("event_details", {})
            agenda = event_details.get("agenda", [])
            
            if not event_details:
                raise APIError("500", "No event details found to generate Facebook post.")

            prompt = (
                f"Here are the event details:\n{event_details}\n\n"
                "Please generate an engaging Facebook post to promote this event."
            )

            extracted_data = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert social media manager. "
                            f"Today's date is {current_date}. "
                            "Your task is to take the provided event details and write an engaging, "
                            "exciting Facebook post to promote the event to the target audience. "
                            "Use appropriate emojis, formatting, and hashtags. Follow the provided schema precisely."
                        )
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_model=fbPostOutput,
                max_retries=3, 
            )
            
            return {"facebook_post_result": extracted_data.model_dump()}
            
        except APIError:
            raise
        except Exception as e:
            raise APIError("500", f"Error generating Facebook post: {str(e)}")