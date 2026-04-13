import redis
import os

clientRedis = None 

def getRedisClient():
    global clientRedis
    if clientRedis is None:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST'), 
            port=int(os.getenv('REDIS_PORT')), 
            db=0, 
            decode_responses=True 
        )
        clientRedis = redis_client
    return clientRedis
