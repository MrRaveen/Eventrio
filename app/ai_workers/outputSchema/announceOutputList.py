from pydantic import BaseModel, RootModel, Field
from typing import List

class annouceOutput(BaseModel):
    agendaTitle: str = Field(description="The specific time-boxed agenda item title (e.g., '09:00 AM - 09:30 AM: Introduction') directly from the provided agenda.")
    agendaAnnounceContent: str = Field(description="An engaging, enthusiastic, and contextual script for this specific agenda item, designed to be spoken out loud by an MC or event announcer.")

class announceOutputList(BaseModel):
    chain_of_thought: str = Field(
        ..., 
        description="Think step-by-step to plan the announcing scripts based on the agenda items."
    )
    root: List[annouceOutput] = Field(description="A list of announcing scripts corresponding sequentially to each item in the provided event agenda.")