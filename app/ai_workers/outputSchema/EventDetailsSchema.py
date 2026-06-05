from pydantic import BaseModel, Field
from typing import List

class Task(BaseModel):
    title: str = Field(description="Task name")
    description: str = Field(description="Task details")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    due_date: str = Field(description="Due date in YYYY-MM-DD format")

class EventDetailsSchema(BaseModel):
    chain_of_thought: str = Field(
        ..., 
        description="Think step-by-step to plan the event. Explicitly calculate the start and end dates relative to the current date, brainstorm the theme, and list required steps before generating the final fields."
    )
    event_name: str = Field(description="Short, catchy event name")
    event_description: str = Field(description="2-3 sentence description of the event")
    event_plan: str = Field(description="5-8 sentences describing the event plan, schedule, and activities")
    start_time: str = Field(description="Start date/time in RFC3339 format")
    end_time: str = Field(description="End date/time in RFC3339 format")
    image_prompt: str = Field(description="Short prompt (max 100 chars) for generating a cover image")
    tasks: List[Task] = Field(description="List of 5-7 tasks for the event")
    targetingPointsToDiscuss: List[str] = Field(description="10 main points to discuss within the event and this helps to create the presentation.")
    agenda: List[str] = Field(description="A detailed, chronological, and time-boxed agenda (e.g., '09:00 AM - 09:30 AM: Introduction') that strategically covers all 'targetingPointsToDiscuss' in a logical flow, ensuring maximum attendee engagement and efficient time management for the event.")