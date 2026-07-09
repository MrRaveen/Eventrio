from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enum.SAGAStepStatusEnum import SAGAStepStatusEnum

class notification_payload(BaseModel):
    isQuestions: bool
    allQuestions: Optional[List[str]] = None
    userID: Optional[str] = None
    projectID: Optional[str] = None
    workflowID: Optional[str] = None

class EventPayload(BaseModel):
    project_id: str
    workflowID: str
    user_id: str | None = None  
    plan_des: str
    event_name: str
    start_time: datetime
    end_time: datetime
    event_description: str

class SagaStepResponse(BaseModel):
    status: SAGAStepStatusEnum
    function_name: str
    payload: EventPayload

class channel_output(BaseModel):
    return_data: Dict[str, Any]
