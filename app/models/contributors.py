from app.models.enum.rolesEnum import rolesEnum
from mongoengine import BooleanField, Document, EmailField, StringField


class contributors(Document):
    meta = {'collection': 'contributors'}

    eventID = StringField()
    orgID = StringField()
    targetEmail = EmailField(required=True)
    accept_stat = BooleanField(default=False)
    userAccountID = StringField()
    role = StringField(choices=[e.value for e in rolesEnum])
