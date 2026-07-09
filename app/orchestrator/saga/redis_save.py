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
        existing_data = redisClient.get(redis_key)
        if existing_data:
            cache_dict = json.loads(existing_data)
            cache_dict.update(first_cache)
        else:
            cache_dict = first_cache    
        json_payload = json.dumps(cache_dict, default=str)
        redisClient.set(redis_key, json_payload)
        return True
    except Exception as e:
        print(f"Error in execute_workflow_redis: {e}")
        return False
def create_context_redis(payload: dict, redisClient: any):
    try:
        inner_payload = payload.get('payload', {})
        user_id = inner_payload.get('user_id')
        workflow_id = inner_payload.get('workflowID')
        allAnswers = inner_payload.get('allAnswers')
        allParagraphs = inner_payload.get('allParagraphs')
        redis_key = f"saga_cache:{user_id}:{workflow_id}"
        update_cache = {
            "allQuestionsAnswers":allAnswers,
            "allParagraphs":allParagraphs
        }
        existing_data = redisClient.get(redis_key)
        if existing_data:
            cache_dict = json.loads(existing_data)
            cache_dict.update(update_cache)
        else:
            cache_dict = update_cache    
        json_payload = json.dumps(cache_dict, default=str)
        redisClient.set(redis_key, json_payload)
        return True
    except Exception as e:
        print(f"Error in create_context_redis: {e}")
        return False    
def create_google_doc_for_event_task_redis(payload: dict, redisClient: any):
    pass
def automate_google_meet_task_redis(payload: dict, redisClient: any):
    pass
def post_image_to_facebook_page_task_redis(payload: dict, redisClient: any):
    pass
def schedule_real_google_calendar_task_redis(payload: dict, redisClient: any):
    pass


