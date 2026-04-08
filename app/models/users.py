from mongoengine import (
    Document, 
    EmbeddedDocument, 
    StringField, 
    BooleanField, 
    DateTimeField, 
    IntField, 
    ListField,
    EmbeddedDocumentField,
    DictField
)
from datetime import datetime, timezone

class PaymentInfo(EmbeddedDocument):
    tier = StringField(choices=('free', 'pro', 'ultimate'), default='free')
    joinedDate = DateTimeField(default=lambda: datetime.now(timezone.utc))
    lastRenewedDate = DateTimeField()
    nextReniewDate = DateTimeField()

class Limits(EmbeddedDocument):
    orgCount = IntField(default=0)
    projectsCount = IntField(default=0)
    chatReqCount = IntField(default=0)

class UserSpecificData(EmbeddedDocument):
    industry = ListField(StringField(choices=(
        'IT', 'Health care', 'Sports', 'Business events', 
        'Casual', 'Education (school)', 'Competitions'
    )))
    role = ListField(StringField(choices=(
        'manager', 'student', 'business owner', 
        'event planner', 'teacher', 'sport coach' # Note: corrected 'couch' to 'coach'
    )))
    averageAttendeeCount = IntField(default=0)
    averageEventCountExcepected = IntField(default=0)
    toolStack = ListField(StringField())
    mainObjectiveOfUser = ListField(StringField(choices=(
        'Lead generation', 'internal training', 'networking'
    )))

class users(Document):
    meta = {'collection': 'users'}

    id = StringField(primary_key=True) 
    sub = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    emailVerified = BooleanField(default=False)
    displayName = StringField()
    givenName = StringField()
    familyName = StringField()
    profilePicUrl = StringField()
    isOnline = BooleanField(default=False)
    
    payments = EmbeddedDocumentField(PaymentInfo, default=PaymentInfo)
    limits = EmbeddedDocumentField(Limits, default=Limits)
    userSpecificData = EmbeddedDocumentField(UserSpecificData, default=UserSpecificData)
    oauthToken = DictField()