import json
from app.config import getRedisClient
from app.orchestrator.services.document_service import document_service

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
        plan_text=parsed_data.get("plan_des", "")
    )
    
    return payload_model
