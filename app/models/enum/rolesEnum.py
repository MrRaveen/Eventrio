from enum import Enum

class rolesEnum(str, Enum):
    ADMIN = 'Admin'
    MANAGER = 'Manager'
    WORKER = 'Worker'

    