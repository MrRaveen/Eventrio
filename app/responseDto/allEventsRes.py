from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum

class ProjectSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    industry: List[IndustryEnum] = []
    attendeeCountExpected: int = 0
    startDate: datetime = Field(default_factory=lambda: datetime.utcnow())
    endDate: Optional[datetime] = None
    isEventStarted: bool = False
    orgName: str
    orgID: str
    orgLocation:str
    mediaLinks: List[str] = []
    targetingPointsToDiscuss: List[dict] = []


    