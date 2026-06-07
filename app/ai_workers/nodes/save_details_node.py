from typing import Dict, Any
from app.ai_workers.state import EventState
from app.models.projects import Projects
from errors import APIError

class save_details_node:
    def __call__(self, state: EventState) -> Dict[str, Any]:
        try:
            if not state:
                raise APIError("400", "State is empty or None in save_details_node")

            event_details = state.get("event_details")
            if not event_details:
                raise APIError("400", "Event details is missing in save_details_node")

            user_id = state.get("user_id")
            if not user_id:
                raise APIError("400", "User ID is missing in save_details_node")

            event_name = event_details.get('event_name')
            if not event_name:
                raise APIError("400", "Event name is missing in event_details")

            event_description = event_details.get('event_description', '')

            project = Projects(
                name=event_name,
                description=event_description,
                ownerID=user_id
            )
            project.save()

            return {"project_id": str(project.id)}

        except APIError:
            raise
        except Exception as e:
            raise APIError("500", f"Error occurred in save_details_node: {str(e)}")