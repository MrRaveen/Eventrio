from pydantic import BaseModel, Field

class fbPostOutput(BaseModel):
    chain_of_thought: str = Field(
        ..., 
        description="Think step-by-step to plan the Facebook post based on the event details."
    )
    post_content: str = Field(
        ...,
        description="The main text content for the Facebook post. Should be engaging, informative, and include appropriate emojis and hashtags."
    )