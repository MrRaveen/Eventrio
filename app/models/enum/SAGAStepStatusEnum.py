from enum import Enum

class SAGAStepStatusEnum(str, Enum):
    COMPLETED = 'completed'
    PENDING = 'pending'
    ERROR = 'error'
    PROGRESS = 'progress'
