import os

from app.models.projects import Projects
from app.models.userAcc import userAcc

try:
    from google.adk.agents.llm_agent import Agent
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
except ImportError:
    Agent = None
    types = None
    Runner = None
    InMemorySessionService = None

def create_event(name: str, description: str, org_id: str, owner_id: str, start_time: str = None, end_time: str = None) -> str:
    """Creates a new event (project) in the database and updates user limits."""
    # Lookup the user to verify limits
    user = userAcc.objects(sub=owner_id).first()
    if not user:
        return f"Error: User not found with ID {owner_id}"
    # For MVP, check projectsCount limit
    if user.limits.projectsCount >= 5 and user.payments.tier == 'free':
        return "Error: Free tier limit of 5 projects reached. Please upgrade to create more."

    project = Projects(
        name=name,
        description=description,
        orgID=org_id,
        ownerID=owner_id
    )
    if start_time:
        project.startDate = start_time
    if end_time:
        project.endDate = end_time
    project.save()

    # Increment usage
    user.limits.projectsCount += 1
    user.save()

    return f"Successfully created event '{name}' with ID: {str(project.id)}."

from urllib.parse import quote


def generate_media_for_event(event_id: str, script_context: str) -> str:
    """Creates real media assets and links them to an event."""
    project = Projects.objects(id=event_id).first()
    if not project:
        return f"Error: Event {event_id} not found."

    # Generate a real image URL via Pollinations
    safe_prompt = quote(f"{project.name} {script_context[:100]} professional event cover art")
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&nologo=true"

    # Generate a real functional viewable text file using Data URIs for the script
    safe_script = quote(script_context)
    script_url = f"data:text/plain;charset=utf-8,{safe_script}"

    project.scriptLink = script_url
    project.mediaLinks = [image_url]
    project.save()
    return f"Media generated and linked to event {event_id} (Image & Script ready)."

import uuid

import requests


def create_google_doc_for_event(owner_id: str, event_id: str, plan_text: str) -> str:
    """Creates a Google Doc directly on the user's account with the event plan."""
    user = userAcc.objects(sub=owner_id).first()
    if not user or not user.oauthToken: return "Error: No Google Auth token found."

    token = user.oauthToken.get('access_token')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 1. Create empty document
    res = requests.post("https://docs.googleapis.com/v1/documents", headers=headers, json={"title": f"Event Plan: {event_id}"})
    if res.status_code != 200: return f"Error creating doc: {res.text}"
    doc_id = res.json().get('documentId')

    # 2. Insert text
    insert_req = {
        "requests": [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": plan_text
                }
            }
        ]
    }
    res2 = requests.post(f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate", headers=headers, json=insert_req)

    doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
    return f"Successfully created your Google Doc: {doc_link}"

def schedule_real_google_calendar(owner_id: str, event_name: str, start_time: str, end_time: str) -> str:
    """Schedule the event directly into the user's Google Calendar natively."""
    user = userAcc.objects(sub=owner_id).first()
    if not user or not user.oauthToken: return "Error: No Google Auth token found."

    token = user.oauthToken.get('access_token')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "summary": event_name,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time}
    }

    res = requests.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", headers=headers, json=payload)
    if res.status_code != 200: return f"Error scheduling calendar: {res.text}"

    event_link = res.json().get('htmlLink')
    return f"Successfully scheduled Event in your calendar! Link: {event_link}"

import json


def save_tasks_to_db(owner_id: str, event_id: str, tasks_data_json: str) -> str:
    """Saves structured tasks to MongoDB. `tasks_data_json` MUST be a valid JSON array string containing dicts with 'title', 'start_date', 'due_date'."""
    project = Projects.objects(id=event_id).first()
    if not project: return "Error: Event not found."

    try:
        tasks_data = json.loads(tasks_data_json)
    except Exception as e:
        return f"Error: Invalid JSON format for tasks_data_json. {e}"

    if not isinstance(tasks_data, list):
        return "Error: tasks_data_json must be a JSON array."

    new_tasks = []
    for item in tasks_data:
        if isinstance(item, str):
            new_tasks.append({
                "id": str(uuid.uuid4()),
                "title": item,
                "isCompleted": False
            })
        elif isinstance(item, dict):
            new_tasks.append({
                "id": str(uuid.uuid4()),
                "title": item.get('title', 'Untitled Task'),
                "startDate": item.get('start_date', ''),
                "dueDate": item.get('due_date', ''),
                "isCompleted": False
            })

    project.tasks.extend(new_tasks)
    project.save()
    return f"Successfully saved {len(new_tasks)} tasks to MongoDB."

class EventAgentsManager:
    def __init__(self):
        try:
            from google.adk.tools.mcp import McpToolset, StdioConnectionParams
        except ImportError:
            try:
                from google.adk.mcp import McpToolset, StdioConnectionParams
            except ImportError:
                McpToolset = None
                StdioConnectionParams = None

        if Agent is None:
            print("Google ADK missing. Agent functionality disabled.")
            self.planning_agent = None
            self.media_agent = None
            self.social_media_agent = None
            self.stream_handler_agent = None
            self.main_agent = None
            return

        try:
            mcp_toolset = None
            if McpToolset and StdioConnectionParams:
                mcp_script_path = os.path.join(os.path.dirname(__file__), 'mcp_server.py')
                connection_params = StdioConnectionParams(
                    command="python",
                    args=[mcp_script_path]
                )
                mcp_toolset = McpToolset(connection_params)

            planning_tools = [create_event, create_google_doc_for_event, schedule_real_google_calendar, save_tasks_to_db, generate_media_for_event, mcp_toolset] if mcp_toolset else [create_event, create_google_doc_for_event, schedule_real_google_calendar, save_tasks_to_db, generate_media_for_event]
            media_tools = [generate_media_for_event, mcp_toolset] if mcp_toolset else [generate_media_for_event]
            other_tools = [mcp_toolset] if mcp_toolset else []

            self.planning_agent = Agent(
                model='gemini-3.1-flash-lite-preview',
                name='planning_agent',
                description='Plans events and schedules them natively and externally.',
                instruction='You are an autonomous event planner. When asked to create an event, DO NOT ask the user for tasks or a plan. Automatically generate a detailed list of tasks including their start and due dates based on the event context. Use create_event to save to DB (IMPORTANT: Extract the org_id from the [Context] block if present, and use the provided owner_id). IMPORTANT: For schedule_real_google_calendar, you MUST convert and format start_time and end_time as valid RFC3339 datetime strings (e.g. 2026-04-09T00:30:00Z) before calling it. For save_tasks_to_db, pass `tasks_data_json` as a valid JSON string (an array of dictionaries). Draft the document using create_google_doc_for_event. Finally, you MUST use generate_media_for_event to generate an image and announcer script for the event. For the script_context, provide a short, fun 1-sentence welcome script for the announcer.',
                tools=planning_tools
            )

            self.media_agent = Agent(
                model='gemini-3.1-flash-lite-preview',
                name='media_agent',
                description='Generates media items (scripts, images) for a specific event.',
                instruction='Use generate_media_for_event for DB links and generate_pollinations_image to create real image URLs.',
                tools=media_tools
            )

            self.social_media_agent = Agent(
                model='gemini-3.1-flash-lite-preview',
                name='social_media_agent',
                description='Creates and evaluates social media posts.',
                instruction='Craft engaging social media posts. Ask the user, then use send_buffer_social_post to stage them.',
                tools=other_tools
            )

            self.stream_handler_agent = Agent(
                model='gemini-3.1-flash-lite-preview',
                name='stream_handler_agent',
                description='Handles stream initiation logic.',
                instruction='You act as the automatic handler for starting event streams.',
                tools=other_tools
            )

            self.main_agent = Agent(
                model='gemini-3.1-flash-lite-preview',
                name='main_agent',
                description='The primary orchestrator agent that delegates to sub-agents.',
                instruction='You are the central coordinator. Parse context (including any Organization ID in the [Context] block) and transfer control to the necessary sub-agent based on user request (planning_agent, media_agent, social_media_agent). Ensure all context, especially IDs, is passed through.',
                sub_agents=[self.planning_agent, self.media_agent, self.social_media_agent, self.stream_handler_agent]
            )

            # Performance: Initialize runner once
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="Eventrio",
                agent=self.main_agent,
                session_service=self.session_service,
                auto_create_session=True
            )

            print("ADK Agents Initialized successfully with Native + MCP tools.")
        except Exception as e:
            print(f"Failed to initialize ADK agents: {str(e)}")
            self.planning_agent = None
            self.media_agent = None
            self.social_media_agent = None
            self.stream_handler_agent = None
            self.main_agent = None

    def run_agent(self, agent_to_use, prompt: str, user_id: str = "user_default") -> str:
        """Utility to run an agent via the official ADK Runner sync interface."""
        if not self.main_agent or not self.runner:
            return "Error: Agents not initialized."

        # If we want to run a specific agent directly, we create a temporary runner
        # or just invoke the main runner if it's the main agent.
        target_runner = self.runner
        if agent_to_use != self.main_agent:
            target_runner = Runner(
                app_name="EventrioSub",
                agent=agent_to_use,
                session_service=InMemorySessionService(),
                auto_create_session=True
            )

        content = types.Content(role="user", parts=[types.Part(text=prompt)])

        import asyncio
        import time
        max_retries = 3
        delay = 2

        async def _run_with_retry():
            current_delay = delay
            for attempt in range(max_retries):
                response_text = ""
                try:
                    # Async execution allows us to properly catch API exceptions
                    async for event in target_runner.run_async(
                        user_id=user_id,
                        session_id=f"stateless_{attempt}",
                        new_message=content
                    ):
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    response_text += part.text
                    return response_text
                except Exception as e:
                    if "503" in str(e) and attempt < max_retries - 1:
                        print(f"Gemini 503 detected. Retrying {attempt+1}/{max_retries}...")
                        await asyncio.sleep(current_delay)
                        current_delay *= 2
                        continue
                    return f"Agent Execution Error: {str(e)}"
            return "Error: Maximum retries reached."

        return asyncio.run(_run_with_retry())

agent_manager = EventAgentsManager()
