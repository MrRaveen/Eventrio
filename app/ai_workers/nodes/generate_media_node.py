from typing import Dict, Any
import cloudinary.uploader
from app.ai_workers.state import EventState
from app.ai_workers.imageModelCall import imageModelCall
from app.models.projects import Projects
from errors import APIError

class generate_media_node:
    def __init__(self, width: int, height: int, model: str, count: int):
        self.imgCreateObj = imageModelCall(width=width, height=height, model=model, count=count)
        
    def __call__(self, state: EventState) -> Dict[str, Any]:    
        try:
            # Validate state variables
            if not state:
                raise APIError("400", "State is empty or None")
            if "project_id" not in state or not state["project_id"]:
                raise APIError("400", "State missing required variable: project_id")
            if "event_details" not in state or not isinstance(state["event_details"], dict):
                raise APIError("400", "State missing required variable: event_details")
            
            event_details = state["event_details"]
            image_prompt = event_details.get("image_prompt")
            if not image_prompt or not isinstance(image_prompt, str) or not image_prompt.strip():
                raise APIError("400", "event_details missing required field: image_prompt")

            project = Projects.objects(id=state["project_id"]).first()
            if not project:
                raise APIError("404", "Project is not found when generating the image")
                
            imgStream = self.imgCreateObj(image_prompt)
            
            upload_result = cloudinary.uploader.upload(
                imgStream,
                folder="eventrio_media"
            )
            final_cloudinary_url = upload_result.get('secure_url')
            
            project.mediaLinks = [final_cloudinary_url]
            project.save()
            
            return {"media_result": final_cloudinary_url}
        except APIError:
            raise
        except Exception as e:
            raise APIError("500", f"Error occurred: {str(e)}")