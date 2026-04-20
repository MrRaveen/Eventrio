from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.IndustryEnum import IndustryEnum

class allColabPersonsDropdownRes(BaseModel):
    docID: str
    userAccID: str
    personName: str
    status: str
    email: str


