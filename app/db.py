import os
import certifi
from mongoengine import connect

def init_db():
    MONGO_URI = os.environ.get('MONGO_URI')
    connect(
        db='EventrioOfficial',
        host=MONGO_URI,
        tlsCAFile=certifi.where(),
        alias='default'
    )

    