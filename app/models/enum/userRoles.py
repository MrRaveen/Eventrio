from enum import Enum

class userRoles(str, Enum):
    MANAGER = 'manager'
    STUDENT = 'student'
    BUSINESS_OWNER = 'business owner'
    EVENT_PLANNER = 'event planner'
    TEACHER = 'teacher'
    SPORT_COACH = 'sport coach'


    