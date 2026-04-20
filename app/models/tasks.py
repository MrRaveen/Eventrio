import enum

from mongoengine import DateTimeField, Document, EnumField, ListField, StringField


class TaskPriority(enum.Enum):
    LOWEST = 'lowest'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class TaskStatus(enum.Enum):
    IN_PROGRESS = 'in progress'
    DONE = 'done'
    UNDER_REVIEW = 'under review'
    CANCELLED = 'cancelled'

class tasks(Document):
    meta = {'collection': 'tasks'}

    orgID = StringField()
    event_id = StringField()
    created_by = StringField()
    assigned_to = StringField()
    title = StringField(required=True)
    description = StringField()
    priority = EnumField(TaskPriority, default=TaskPriority.MEDIUM)
    status = EnumField(TaskStatus, default=TaskStatus.IN_PROGRESS)
    deadline = DateTimeField()
    media_links = ListField(StringField())
