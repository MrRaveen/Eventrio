from datetime import datetime, date, timezone
import instructor
from litellm import completion
from typing import Dict, Any
from app.ai_workers.state import EventState
from app.ai_workers.outputSchema.EventDetailsSchema import EventDetailsSchema
from errors import APIError

class extract_basic_node:
    def __init__(self, model: str):
        self.client = instructor.from_litellm(completion)
        self.model = model

    def __call__(self, state: EventState) -> Dict[str, Any]:
        try:
            if not state:
                raise APIError("400", "State is empty or None")
            
            prompt = state.get("prompt")
            if not prompt or not isinstance(prompt, str) or not prompt.strip():
                raise APIError("400", "State missing required variable: prompt")

            current_date = date.today().strftime("%Y-%m-%d")
            
            extracted_data = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert event planner. "
                            f"Today's date is {current_date}. All generated dates must be in the future. "
                            "IMPORTANT: You must write out your logical deductions, date calculations, "
                            "and brainstorming steps inside the 'chain_of_thought' field FIRST. "
                            "Only after completing your thought process should you populate the remaining fields."
                        )
                    },
                    {
                        "role": "user",
                        "content": state.get('prompt')
                    }
                ],
                response_model=EventDetailsSchema,
                max_retries=3, 
            )
            start_str = extracted_data.start_time.replace('Z', '+00:00')
            end_str = extracted_data.end_time.replace('Z', '+00:00')
            try:
                start_dt = datetime.fromisoformat(start_str)
                end_dt = datetime.fromisoformat(end_str)
                
                current_time = datetime.now(timezone.utc) if start_dt.tzinfo else datetime.now()
                if start_dt < current_time:
                    raise APIError("400", f"Validation failed: Event start time ({extracted_data.start_time}) must be in the future.")

                if end_dt <= start_dt:
                    raise APIError("400", f"Validation failed: Event end time ({extracted_data.end_time}) must be after start time ({extracted_data.start_time}).")
            except ValueError as val_err:
                raise APIError("400", f"Validation failed: Invalid RFC3339 datetime format for event start/end times: {str(val_err)}")
            for task in extracted_data.tasks:
                try:
                    task_start = datetime.strptime(task.start_date, "%Y-%m-%d").date()
                    task_due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    
                    if task_start < date.today():
                        raise APIError("400", f"Validation failed for task '{task.title}': task start date must be today or in the future.")

                    if task_due < task_start:
                        raise APIError("400", f"Validation failed for task '{task.title}': task due date must be after or equal to task start date.")
                except ValueError as task_date_err:
                    raise APIError("400", f"Validation failed for task '{task.title}': invalid task date format. Must be YYYY-MM-DD. Error: {str(task_date_err)}")

            return {"event_details": extracted_data.model_dump()}

        except APIError:
            raise
        except Exception as e:
            raise APIError("500", f"Error occurred in event extraction: {str(e)}")
