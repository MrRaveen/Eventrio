from datetime import datetime
from pydantic import BaseModel

class getEventsForAdminRes(BaseModel):
    eventDocID: str
    eventName: str
    isEventStarted: bool
    organizationID: str
    organizationName: str
    startDate: datetime
    endDate: datetime
    eventStatus: str

