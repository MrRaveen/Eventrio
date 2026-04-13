from mongoengine import DateTimeField
from mongoengine import Document, StringField, BooleanField
from datetime import datetime, timezone
class Participants(Document):
    meta = {'collection': 'participants'}
    
    name = StringField(required=True)
    isVerifiedStat = BooleanField(default=False)
    email = StringField(required=True)
    eventID = StringField(required=True)
    orgID = StringField(required=True)
    createdDate = DateTimeField(default=lambda: datetime.now(timezone.utc))
