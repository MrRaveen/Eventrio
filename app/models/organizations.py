from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum
from mongoengine import Document, StringField, ListField

class Organizations(Document):
    meta = {'collection': 'organizations'}
    
    orgName = StringField(required=True)
    address = StringField()
    createdBy = StringField(required=True)
    industry = ListField(StringField(choices=[e.value for e in IndustryEnum]))
    userRole = ListField(StringField(choices=[e.value for e in RoleEnum]))
