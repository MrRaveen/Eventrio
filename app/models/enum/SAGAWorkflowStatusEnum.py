from enum import Enum

class SAGAWorkflowStatusEnum(str, Enum):
    ENDED = 'ended'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
