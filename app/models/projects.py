from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum
from mongoengine import Document, StringField, ListField, IntField, DateTimeField, BooleanField, DictField
from datetime import datetime, timezone

class Projects(Document):
    meta = {'collection': 'projects'}
    
    name = StringField(required=True)
    description = StringField()
    industry = ListField(StringField(choices=[e.value for e in IndustryEnum]))
    userRole = ListField(StringField(choices=[e.value for e in RoleEnum]))
    attendeeCountExpected = IntField(default=0)
    startDate = DateTimeField(default=lambda: datetime.now(timezone.utc))
    endDate = DateTimeField()
    isEventStarted = BooleanField(default=False)
    orgID = StringField()
    ownerID = StringField()
    mediaLinks = ListField(StringField())
    meetingUrl = StringField(default="")
    slideShowLink = StringField()
    scriptLink = StringField()
