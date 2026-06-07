from typing import TypedDict, Optional, Dict, Any

class EventState(TypedDict):
    event_details: Dict[str, Any]
    project_id: str
    user_id: str
    prompt: str
    context: str
    announcing_script_result: Optional[Any]
    media_result: Optional[Any]
    readme_result: Optional[str]


