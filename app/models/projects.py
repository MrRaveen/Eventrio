from mongoengine import Document, StringField, ListField, IntField, DateTimeField, BooleanField, DictField
from datetime import datetime, timezone

class Projects(Document):
    meta = {'collection': 'projects'}
    
    name = StringField(required=True)
    description = StringField()
    industry = ListField(StringField(choices=(
        'IT', 'Health care', 'Sports', 'Business events', 
        'Casual', 'Education (school)', 'Competitions'
    )))
    userRole = ListField(StringField(choices=(
        'manager', 'student', 'business owner', 
        'event planner', 'teacher', 'sport coach'
    )))
    attendeeCountExpected = IntField(default=0)
    startDate = DateTimeField(default=lambda: datetime.now(timezone.utc))
    endDate = DateTimeField()
    isEventStarted = BooleanField(default=False)
    orgID = StringField()
    ownerID = StringField()
    mediaLinks = ListField(StringField())
    slideShowLink = StringField()
    scriptLink = StringField()
    tasks = ListField(DictField())
