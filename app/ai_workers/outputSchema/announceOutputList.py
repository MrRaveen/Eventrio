from pydantic import BaseModel, RootModel, Field
from typing import List

class annouceOutput(BaseModel):
    agendaTitle: str = Field(description="The specific time-boxed agenda item title (e.g., '09:00 AM - 09:30 AM: Introduction') directly from the provided agenda.")
    agendaAnnounceContent: str = Field(description="An engaging, enthusiastic, and contextual script for this specific agenda item, designed to be spoken out loud by an MC or event announcer.")

class announceOutputList(RootModel):
    chain_of_thought: str = Field(
        ..., 
        description="Think step-by-step to plan the event. Explicitly calculate the start and end dates relative to the current date, brainstorm the theme, and list required steps before generating the final fields."
    )
    root: List[annouceOutput] = Field(description="A list of announcing scripts corresponding sequentially to each item in the provided event agenda.")