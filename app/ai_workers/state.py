from typing import Any, Dict, Optional, TypedDict


class EventState(TypedDict):
    event_details: Optional[Dict[str, Any]]
    project_id: Optional[str]
    user_id: Optional[str]
    org_id: Optional[str]
    prompt: Optional[str]
    context: Optional[str]
    announcing_script_result: Optional[Any]
    media_result: Optional[Any]
    readme_result: Optional[str]
