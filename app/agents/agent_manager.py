from app.agents.manual_services import save_tasks_to_db
from app.agents.manual_services import schedule_real_google_calendar
from app.agents.manual_services import create_google_doc_for_event
from app.agents.manual_services import generate_media_for_event
from app.agents.manual_services import create_event
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
import uuid
import requests
import json

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
                model='gemini-2.5-flash-lite',
                name='planning_agent',
                description='Plans events and schedules them natively and externally.',
                instruction='You are an autonomous event planner. When asked to create an event, DO NOT ask the user for tasks or a plan. Automatically generate a detailed list of tasks including their start and due dates based on the event context. Use create_event to save to DB (IMPORTANT: Extract the org_id from the [Context] block if present, and use the provided owner_id). IMPORTANT: For schedule_real_google_calendar, you MUST convert and format start_time and end_time as valid RFC3339 datetime strings (e.g. 2026-04-09T00:30:00Z) before calling it. For save_tasks_to_db, pass `tasks_data_json` as a valid JSON string (an array of dictionaries). Draft the document using create_google_doc_for_event. Finally, you MUST use generate_media_for_event to generate an image and announcer script for the event. For the script_context, provide a short, fun 1-sentence welcome script for the announcer.',
                tools=planning_tools
            )

            self.media_agent = Agent(
                model='gemini-2.5-flash-lite',
                name='media_agent',
                description='Generates media items (scripts, images) for a specific event.',
                instruction='Use generate_media_for_event for DB links and generate_pollinations_image to create real image URLs.',
                tools=media_tools
            )

            self.social_media_agent = Agent(
                model='gemini-2.5-flash-lite',
                name='social_media_agent',
                description='Creates and evaluates social media posts.',
                instruction='Craft engaging social media posts. Ask the user, then use send_buffer_social_post to stage them.',
                tools=other_tools
            )

            self.stream_handler_agent = Agent(
                model='gemini-2.5-flash-lite',
                name='stream_handler_agent',
                description='Handles stream initiation logic.',
                instruction='You act as the automatic handler for starting event streams.',
                tools=other_tools
            )

            self.main_agent = Agent(
                model='gemini-2.5-flash-lite',
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
