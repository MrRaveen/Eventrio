from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum
from mongoengine import Document, StringField, ListField, IntField, DateTimeField, BooleanField, DictField
from datetime import datetime, timezone

class Agenda(Document):
    meta = {'collection': 'agenda'}
    
    eventID = StringField()
    agendaList = ListField(StringField())