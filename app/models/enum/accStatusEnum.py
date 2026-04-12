from enum import Enum

class accStatusEnum(str, Enum):
    ACTIVE = 'Active'
    D_ACTIVATED = 'D-activated'
    PENDING_PAYMENT = 'Pending-Payment'


