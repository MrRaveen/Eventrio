import enum
from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum
from mongoengine import Document, StringField, ListField, FloatField, EnumField
class ChunkType(enum.Enum):
    PARAGRAPH = 'paragraph'
    Q_AND_A = 'q_and_a'

class EventContext(Document):
    meta = {'collection': 'eventContext'}
    
    eventID = StringField(required=True)
    chunkType = EnumField(ChunkType, required = True)
    content = StringField()
    embedding = ListField(FloatField())
    
