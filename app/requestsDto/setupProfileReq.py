from app.models.enum.toolStackEnum import toolStackEnum
from app.models.enum.ObjectiveEnum import ObjectiveEnum
from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum
from pydantic import BaseModel, Field
from typing import List
from enum import Enum
class setupProfileReq(BaseModel):
    industry: List[IndustryEnum] = Field(default_factory=list)
    role: List[RoleEnum] = Field(default_factory=list)    
    averageAttendeeCount: int = Field(default=0, ge=0)
    averageEventCountExcepected: int = Field(default=0, ge=0)
    toolStack: List[toolStackEnum] = Field(default_factory=list)
    mainObjectiveOfUser: List[ObjectiveEnum] = Field(default_factory=list)


