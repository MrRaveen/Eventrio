import json

def execute_workflow_redis(payload: dict, redisClient: any):
    try:
        inner_payload = payload.get('payload', {})
        user_id = inner_payload.get('user_id')
        workflow_id = inner_payload.get('workflowID')
        
        redis_key = f"saga_cache:{user_id}:{workflow_id}"
        
        first_cache = {
            "userID": user_id,
            "workflowID": workflow_id,
            "projectID": inner_payload.get('project_id'),
            "plan_des": inner_payload.get('plan_des'),
            "event_name": inner_payload.get('event_name'),
            "start_time": inner_payload.get('start_time'),
            "end_time": inner_payload.get('end_time'),
            "event_description": inner_payload.get('event_description')
        }
        
        json_payload = json.dumps(first_cache, default=str)
        redisClient.set(redis_key, json_payload)
        return True
    except Exception as e:
        print(f"Error in execute_workflow_redis: {e}")
        return False
