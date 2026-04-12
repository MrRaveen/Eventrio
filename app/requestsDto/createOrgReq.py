from app.models.enum.RoleEnum import RoleEnum
from pydantic import BaseModel, Field
from typing import Optional

# Importing your existing enums
from app.models.enum.IndustryEnum import IndustryEnum


class createOrgReq(BaseModel):
    # Using the exact defaults from your snippet
    orgName: str = Field(default='Unnamed Org')
    address: str = Field(default='')
    industry: IndustryEnum
    userRole: RoleEnum