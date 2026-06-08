import json
import redis

def listen_to_response_channel(task_terminate:str,channel_name="saga_responses"):
    client = redis.Redis(host='localhost', port=6379, db=0)

    pubsub = client.pubsub()
    
    pubsub.subscribe(channel_name)
    print(f"[*] Orchestrator listening exclusively on channel: {channel_name}")
    
    for message in pubsub.listen():
        if message['type'] == 'subscribe':
            continue
            
        try:
            payload = json.loads(message['data'].decode('utf-8'))
            
            saga_id = payload.get("saga_id")
            current_step = payload.get("step")
            status = payload.get("status")
            data = payload.get("data")

            if current_step == task_terminate:
                break
            
            print(f"[+] Received event for Saga {saga_id}: Step {current_step} is {status}")
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"[-] Malformed message received on channel: {e}")
    return payload        