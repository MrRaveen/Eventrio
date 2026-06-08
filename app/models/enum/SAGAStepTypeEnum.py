from enum import Enum

class SAGAStepTypeEnum(str, Enum):
    AI_TASKS = 'execute_workflow'
    UPDATE_PROJECT = 'update_project'
    CREATE_GOOGLE_DOC = 'create_google_doc_for_event'
    CREATE_GOOGLE_MEET = 'automate_google_meet'
    CREATE_FB_PAGE = 'post_image_to_facebook_page'
    CREATE_GOOGLE_CALENDAR = 'schedule_real_google_calendar'
