from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, EnumField
from app.models.enum.SAGAWorkflowStatusEnum import SAGAWorkflowStatusEnum

class SAGA_workflow(Document):
    meta = {'collection': 'saga_workflow'}

    userID = StringField(required=True)
    status = EnumField(SAGAWorkflowStatusEnum, default=SAGAWorkflowStatusEnum.PROCESSING)
    created_timestamp = DateTimeField(default=datetime.utcnow)
    ending_timestamp = DateTimeField()
