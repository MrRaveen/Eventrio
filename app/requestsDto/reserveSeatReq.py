from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class ParticipantSchema(BaseModel):
    name: str
    email: str
    eventID: str
    orgID: str
    verificationCode: str


