import os

import redis
from mailjet_rest import Client

clientRedis = None
mailjetClient = None

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
def getMailjetClient():
    api_key = os.environ["MJ_APIKEY_PUBLIC"]
    api_secret = os.environ["MJ_APIKEY_PRIVATE"]
    global mailjetClient
    if mailjetClient is None:
        mailjetClient = Client(auth=(api_key, api_secret))
    return mailjetClient
