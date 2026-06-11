import json
from app.config import getRedisClient
from app.orchestrator.services.document_service import document_service
from app.orchestrator.services.meet_service import meet_service
from app.orchestrator.services.social_service import social_service

def create_google_doc_for_event_task_payload(user_id: str, workflow_id: str):
    redis_key = f"saga_cache:{user_id}:{workflow_id}"
    redis_client = getRedisClient()
    
    cached_data = redis_client.get(redis_key)
    if not cached_data:
        raise ValueError(f"No cache data found in Redis for key: {redis_key}")
        
    parsed_data = json.loads(cached_data)
    
    # Map the cached data to the Pydantic model
    payload_model = document_service.req_data(
        owner_id=parsed_data.get("userID"),
        event_id=parsed_data.get("projectID"),
        plan_text=parsed_data.get("plan_des", ""),
        workflow_id=workflow_id
    )
    
    return payload_model

def automate_google_meet_task_payload(user_id: str, workflow_id: str):
    redis_key = f"saga_cache:{user_id}:{workflow_id}"
    redis_client = getRedisClient()
    cached_data = redis_client.get(redis_key)
    if not cached_data:
        raise ValueError(f"No cache data found in Redis for key: {redis_key}")
    parsed_data = json.loads(cached_data)
    
    payload_model = meet_service.req_data(
        owner_id=parsed_data.get("userID"),
        event_id=parsed_data.get("projectID"),
        title=parsed_data.get("event_name"),
        start_time=parsed_data.get("start_time"),
        end_time=parsed_data.get("end_time"),
        workflow_id=workflow_id
    )
    
    return payload_model    

def post_image_to_facebook_page_task_payload(user_id: str, workflow_id: str):
    redis_key = f"saga_cache:{user_id}:{workflow_id}"
    redis_client = getRedisClient()
    cached_data = redis_client.get(redis_key)
    if not cached_data:
        raise ValueError(f"No cache data found in Redis for key: {redis_key}")
    parsed_data = json.loads(cached_data)
    
    payload_model = social_service.req_data(
        owner_id=parsed_data.get("userID"),
        event_id=parsed_data.get("projectID"),
        page_id=parsed_data.get("page_id",None),
        workflow_id=workflow_id
    )
    return payload_model
def schedule_real_google_calendar_task_payload(user_id: str, workflow_id: str):
    redis_key = f"saga_cache:{user_id}:{workflow_id}"
    redis_client = getRedisClient()
    cached_data = redis_client.get(redis_key)
    if not cached_data:
        raise ValueError(f"No cache data found in Redis for key: {redis_key}")
    parsed_data = json.loads(cached_data)
    
    from app.orchestrator.services.calendar_service import calendar_service
    payload_model = calendar_service.req_data(
        owner_id=parsed_data.get("userID"),
        event_name=parsed_data.get("event_name"),
        start_time=parsed_data.get("start_time"),
        end_time=parsed_data.get("end_time"),
        workflow_id=workflow_id
    )
    
    return payload_model   
 

