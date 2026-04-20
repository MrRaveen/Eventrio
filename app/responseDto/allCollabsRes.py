
from datetime import datetime
from pydantic import BaseModel

class allCollabsRes(BaseModel):
    docID: str
    projectName: str
    projectDes: str
    startDate: datetime
    endDate: datetime
    ownerName: str
    orgname: str
    accept_stat: bool
    eventID: str
    orgID: str
    role: str



