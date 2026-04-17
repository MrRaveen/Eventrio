from app.models.enum.toolStackEnum import toolStackEnum
from app.models.enum.accStatusEnum import accStatusEnum
from app.models.enum.planOptionsEnum import planOptionsEnum
from app.models.enum.ObjectiveEnum import ObjectiveEnum
from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum
from datetime import datetime, timezone

from mongoengine import (
    BooleanField,
    DateTimeField,
    DictField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
    ListField,
    StringField,
)


class PaymentInfo(EmbeddedDocument):
    tier = StringField(choices=[e.value for e in planOptionsEnum], default=planOptionsEnum.FREE)
    joinedDate = DateTimeField(default=lambda: datetime.now(timezone.utc))
    lastRenewedDate = DateTimeField()
    nextReniewDate = DateTimeField()

class Limits(EmbeddedDocument):
    orgCount = IntField(default=0)
    projectsCount = IntField(default=0)
    chatReqCount = IntField(default=0)

class UserSpecificData(EmbeddedDocument):
    industry = ListField(StringField(choices=[e.value for e in IndustryEnum]))
    role = ListField(StringField(choices=[e.value for e in RoleEnum]))
    averageAttendeeCount = IntField(default=0)
    averageEventCountExcepected = IntField(default=0)
    toolStack = ListField(StringField(choices=[e.value for e in toolStackEnum]))
    mainObjectiveOfUser = ListField(StringField(choices=[e.value for e in ObjectiveEnum]))
class socialMediaTokens(EmbeddedDocument):
    facebook = StringField(default="")
    linkedIn = StringField(default="")
    pinterest = StringField(default="")
    youtube = StringField(default="")
class userAcc(Document):
    meta = {'collection': 'users'}
    sub = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    emailVerified = BooleanField(default=False)
    displayName = StringField()
    givenName = StringField()
    familyName = StringField()
    profilePicUrl = StringField()
    isOnline = BooleanField(default=False)
    accStatus = ListField(StringField(choices=[e.value for e in accStatusEnum]))
    payments = EmbeddedDocumentField(PaymentInfo, default=PaymentInfo)
    limits = EmbeddedDocumentField(Limits, default=Limits)
    userSpecificData = EmbeddedDocumentField(UserSpecificData, default=UserSpecificData)
    socialMediaTokens = EmbeddedDocumentField(socialMediaTokens, default=lambda: socialMediaTokens())
    oauthToken = DictField()


