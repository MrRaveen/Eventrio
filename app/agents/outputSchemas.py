from pydantic import BaseModel, Field
from typing import List

class Task(BaseModel):
    title: str = Field(description="Task name")
    description: str = Field(description="Task details")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    due_date: str = Field(description="Due date in YYYY-MM-DD format")

class EventDetailsSchema(BaseModel):
    event_name: str = Field(description="Short, catchy event name")
    event_description: str = Field(description="2-3 sentence description of the event")
    event_plan: str = Field(description="5-8 sentences describing the event plan, schedule, and activities")
    announcing_script: str = Field(description="Short, fun 1-2 sentence script for an event announcer")
    start_time: str = Field(description="Start date/time in RFC3339 format")
    end_time: str = Field(description="End date/time in RFC3339 format")
    image_prompt: str = Field(description="Short prompt (max 100 chars) for generating a cover image")
    tasks: List[Task] = Field(description="List of 5-7 tasks for the event")