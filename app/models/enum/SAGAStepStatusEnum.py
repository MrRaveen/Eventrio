from enum import Enum

class SAGAStepStatusEnum(str, Enum):
    COMPLETED = 'completed'
    PENDING = 'pending'
    FAILED = 'failed'
    ERROR = 'error'
    PROGRESS = 'progress'
