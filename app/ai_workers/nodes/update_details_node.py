from datetime import datetime
from typing import Dict, Any
from app.ai_workers.outputSchema.EventDetailsSchema import EventDetailsSchema
from app.ai_workers.state import EventState
from app.models.projects import Projects
from app.models.agenda import Agenda
from app.models.tasks import tasks
from errors import APIError

class update_details_node:
    def __call__(self, state: EventState) -> Dict[str, Any]:
        try:
            project_id = state.get('project_id')
            if not project_id:
                raise APIError("MISSING_PROJECT_ID", "Project ID is missing from state")

            event = Projects.objects(id=project_id).first()
            if not event:
                raise APIError("EVENT_NOT_FOUND", f"Event not found with id {project_id}")

            event_details = state.get('event_details', {})
            validated_created_details = EventDetailsSchema(**event_details)
            
            event.startDate = datetime.fromisoformat(validated_created_details.start_time.replace('Z', '+00:00'))
            event.endDate = datetime.fromisoformat(validated_created_details.end_time.replace('Z', '+00:00'))
            event.isEventStarted = False
            event.orgID = state.get('org_id')
            event.mediaLinks = state.get('media_result')
            event.targetingPointsToDiscuss = validated_created_details.targetingPointsToDiscuss
            event.eventPlan = validated_created_details.event_plan
            event.save()
            
            newAgenda = Agenda(
                eventID=project_id,
                agendaList=validated_created_details.agenda
            )
            newAgenda.save()
            
            for task in validated_created_details.tasks:
                newTask = tasks(
                    orgID=state.get('org_id'),
                    event_id=project_id,
                    created_by="SYSTEM",
                    title=task.title,
                    description=task.description,
                    startDate=task.start_date,
                    deadline=task.due_date
                )
                newTask.save()
                
            return {}
        except APIError:
            raise
        except Exception as e:
            raise APIError("UPDATE_DETAILS_ERROR", str(e))
