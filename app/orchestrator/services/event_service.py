from celery import shared_task
from app.models.projects import Projects
from app.models.userAcc import userAcc

@shared_task(bind=True)
def create_event_task(self, name: str, description: str, org_id: str, owner_id: str, start_time: str = None, end_time: str = None) -> str:
    # Lookup the user to verify limits
    user = userAcc.objects(sub=owner_id).first()
    if not user:
        return f"Error: User not found with ID {owner_id}"
    # if user.limits.projectsCount >= 5 and user.payments.tier == 'free':
    #     return "Error: Free tier limit of 5 projects reached. Please upgrade to create more."
    project = Projects(
        name=name,
        description=description,
        orgID=org_id,
        ownerID=owner_id,
        attendeeCountExpected=100,
        industry=["IT"],
        userRole=["manager"]
    )
    if start_time:
        project.startDate = start_time
    if end_time:
        project.endDate = end_time
    try:
        project.save()
        # Increment usage
        user.limits.projectsCount += 1
        user.save()
    except Exception as e:
        return f"Error saving event to database: {str(e)}"
    
    event_id_str = str(project.id)
    return f"SUCCESS: Event created. The event_id is: {event_id_str}. You MUST use this exact event_id ({event_id_str}) in all subsequent function calls (generate_media_for_event, create_google_doc_for_event, save_tasks_to_db)."
