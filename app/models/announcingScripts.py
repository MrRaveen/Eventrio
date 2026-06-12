from app.models.enum.rolesEnum import rolesEnum
from mongoengine import BooleanField, Document, EmailField, StringField
class announcingScripts(Document):
    eventID: StringField()
    script: StringField()
