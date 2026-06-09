from mongoengine import DictField, Document, EnumField, IntField, StringField

from app.models.enum.SAGAStepStatusEnum import SAGAStepStatusEnum
from app.models.enum.SAGAStepTypeEnum import SAGAStepTypeEnum


class SAGA_steps(Document):
    meta = {'collection': 'saga_steps'}

    workflow_ID = StringField(required=True)
    step_type = EnumField(SAGAStepTypeEnum, required=True)
    total_time_ms = IntField(default=0)
    response_json = DictField(default={})
    step_status = EnumField(SAGAStepStatusEnum, default=SAGAStepStatusEnum.PENDING)
