from mcp import StdioServerParameters
import traceback
from app.agents.manual_services import save_tasks_to_db
from app.agents.manual_services import schedule_real_google_calendar
from app.agents.manual_services import create_google_doc_for_event
from app.agents.manual_services import generate_media_for_event
from app.agents.manual_services import create_event
from app.agents.manual_services import create_slides
from app.agents.manual_services import automate_google_meet
from app.agents.manual_services import post_image_to_facebook_page
from app.models.posts import Posts
import os
from app.models.projects import Projects
from app.models.userAcc import userAcc

try:
    from google.adk.agents import Agent  
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    from google import genai  
    from google.adk.models import LiteLlm  
    from google.genai import types
except ImportError as e:
    print(f"CRITICAL: Global ADK Import Failed: {e}")
    Agent = types = Runner = InMemorySessionService = LiteLlm = None

import uuid
import requests
import json
import asyncio


class EventAgentsManager:
    def __init__(self):
        try:
            from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
            print("MCP tools loaded successfully")
        except ImportError:
            print("Notice: MCP tools not found. Running agents without MCP.")
            McpToolset = StdioConnectionParams = None

        if Agent is None:
            print("Google ADK missing. Agent functionality disabled.")
            self.planning_agent = None
            self.media_agent = None
            self.social_media_agent = None
            self.slides_agent = None
            self.meet_agent = None
            self.stream_handler_agent = None
            self.main_agent = None
            return

        try:
            mcp_toolset = None
            # The reason it takes 10 minutes is because LiteLLM has a default timeout of 600 seconds.
            # 'https://ollama.com' is a webpage, not an API server. LiteLLM hangs trying to reach it.
            # To test using a cloud method, you must use a valid cloud API endpoint.
            # Example using Google Gemini (fast, reliable cloud method):
            local_llm = LiteLlm(
                model="ollama/glm-4.7:cloud",
                api_key=os.getenv("MODEL_KEY"),
                api_base="https://ollama.com",
                timeout=1800
            )
            
            if McpToolset and StdioConnectionParams:
                mcp_script_path = os.path.join(os.path.dirname(__file__), 'mcp_server.py')
                connection_params = StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="python",
                        args=[mcp_script_path]
                    )
                )
                mcp_toolset = McpToolset(connection_params=connection_params)

            # Define tool groups for each agent
            planning_tools = [create_event, create_google_doc_for_event, 
                            schedule_real_google_calendar, save_tasks_to_db, 
                            generate_media_for_event]
            
            media_tools = [generate_media_for_event]
            
            social_tools = [post_image_to_facebook_page]
            
            slides_tools = [create_slides]
            
            meet_tools = [automate_google_meet]
            
            # Add MCP tools if available
            if mcp_toolset:
                planning_tools.append(mcp_toolset)
                media_tools.append(mcp_toolset)
                social_tools.append(mcp_toolset)

            # Planning Agent - Core event creation and scheduling
            self.planning_agent = Agent(
                model=local_llm,
                name='planning_agent',
                description='Creates events, generates plans, schedules calendars, and manages tasks.',
                instruction="""You are an autonomous event planner. When asked to create an event:
                1. DO NOT ask the user for tasks or a plan - generate everything automatically
                2. Use create_event to save to DB (extract org_id from [Context] block if present)
                3. For schedule_real_google_calendar, format times as RFC3339 (e.g., 2026-04-09T00:30:00Z)
                4. For save_tasks_to_db, pass tasks_data_json as a valid JSON array of task objects:
                   [{"title": "Task name", "description": "...", "start_date": "...", "due_date": "..."}]
                5. Use create_google_doc_for_event with a detailed plan text
                6. Use generate_media_for_event with a short fun welcome script as script_context""",
                tools=planning_tools
            )

            # Media Agent - Image generation and media management
            self.media_agent = Agent(
                model=local_llm,
                name='media_agent',
                description='Generates event images, scripts, and media content.',
                instruction="""You handle all media generation for events:
                1. Use generate_media_for_event with the event_id and a creative script_context
                2. The script_context should be a fun, engaging 1-2 sentence announcer script
                3. Always confirm media links are generated successfully""",
                tools=media_tools
            )

            # Slides Agent - Presentation creation
            # Slides Agent - Presentation creation with proper markdown formatting
            self.slides_agent = Agent(
                model=local_llm,
                name='slides_agent',
                description='Creates slide decks and presentations for events using markdown format.',
                instruction="""You create professional slide presentations using markdown. Follow these rules strictly:

            FORMAT RULES:
            1. Slide titles are level-1 headings: # Title Here
            2. Slide separators are three dashes: ---
            3. Subtitles and sections use level-2 headings: ## Section Here
            4. Bullet points use hyphens: - Point here
            5. Each slide MUST have a title followed by content
            6. Separate every slide with --- on its own line

            EXAMPLE FORMAT:
            # Welcome to [Event Name]
            [Tagline or subtitle]

            ---

            # Event Schedule
            [Duration or time details]
            - Day 1: [Activity]
            - Day 2: [Activity]
            - Day 3: [Activity]

            ---

            # Key Highlights
            What to expect
            - Highlight 1
            - Highlight 2
            - Highlight 3

            ---

            # [Another Section]
            [Section description]
            - Point A
            - Point B
            - Point C

            Generate 4-6 slides covering:
            1. Title/Welcome slide with event name and tagline
            2. Event schedule or timeline
            3. Key features, highlights, or what attendees will learn
            4. Speakers, judges, or special guests (if applicable)
            5. Practical information (venue, date, rules, requirements)
            6. Call to action or closing slide

            IMPORTANT: 
            - Always generate REAL content based on the event context, never placeholders
            - Use the exact markdown format shown above
            - Each slide MUST be separated by ---
            - Pass the complete markdown string directly to create_slides function""",
                tools=slides_tools
            )

            # Meet Agent - Google Meet creation
            self.meet_agent = Agent(
                model=local_llm,
                name='meet_agent',
                description='Creates Google Meet meetings for events.',
                instruction="""You handle video conferencing setup:
                1. Use automate_google_meet with proper event details
                2. Ensure start_time and end_time are in correct RFC3339 format
                3. Pass user_access_token and event_details dictionary""",
                tools=meet_tools
            )

            # Social Media Agent - Facebook posting
            self.social_media_agent = Agent(
                model=local_llm,
                name='social_media_agent',
                description='Creates and publishes social media posts for events.',
                instruction="""You manage social media promotion:
                1. Use post_image_to_facebook_page with proper parameters
                2. Craft engaging messages for posts
                3. Always pass user_token, page_id, message, and image_url
                4. Confirm post success with post_id""",
                tools=social_tools
            )

            # Stream Handler Agent
            self.stream_handler_agent = Agent(
                model=local_llm,
                name='stream_handler_agent',
                description='Handles event streaming and live session initiation.',
                instruction="""You manage event streaming setup:
                1. Coordinate with other agents for complete event setup
                2. Ensure all streaming prerequisites are met
                3. Handle live session initialization""",
                tools=[mcp_toolset] if mcp_toolset else []
            )

            # Main Orchestrator Agent
            self.main_agent = Agent(
                model=local_llm,
                name='main_agent',
                description='Primary orchestrator that delegates to specialized sub-agents.',
                instruction="""You are the central coordinator for Eventrio. Your job is to:
                1. Parse the user's request and any [Context] blocks
                2. Determine which sub-agents are needed based on the request:
                   - planning_agent: For event creation, scheduling, tasks, documents
                   - media_agent: For image and script generation
                   - slides_agent: For presentation creation
                   - meet_agent: For Google Meet setup
                   - social_media_agent: For Facebook posting
                3. Transfer control to the appropriate sub-agent(s)
                4. Ensure all context, IDs, and user tokens are passed through
                5. Handle multi-step workflows that require multiple agents""",
                sub_agents=[
                    self.planning_agent, 
                    self.media_agent, 
                    self.slides_agent,
                    self.meet_agent,
                    self.social_media_agent, 
                    self.stream_handler_agent
                ]
            )

            # Initialize session service and runner
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="Eventrio",
                agent=self.main_agent,
                session_service=self.session_service,
                auto_create_session=True
            )

            print("ADK Agents Initialized successfully with all services.")
            
        except Exception as e:
            print(f"Failed to initialize ADK agents: {str(e)}")
            traceback.print_exc()
            self.planning_agent = None
            self.media_agent = None
            self.social_media_agent = None
            self.slides_agent = None
            self.meet_agent = None
            self.stream_handler_agent = None
            self.main_agent = None

    def run_agent(self, agent_to_use, prompt: str, fbPageID: str = None, user_id: str = "user_default") -> str:
        """Run an agent with retry logic and proper error handling."""
        if not self.main_agent or not self.runner:
            return "Error: Agents not initialized."

        # Use the main runner for main agent, or create a temporary runner for sub-agents
        if agent_to_use == self.main_agent:
            target_runner = self.runner
        else:
            target_runner = Runner(
                app_name="EventrioSub",
                agent=agent_to_use,
                session_service=InMemorySessionService(),
                auto_create_session=True
            )

        content = types.Content(role="user", parts=[types.Part(text=prompt)])

        async def _run_with_retry():
            current_delay = 2
            for attempt in range(3):
                response_text = ""
                try:
                    async for event in target_runner.run_async(
                        user_id=user_id,
                        session_id=f"stateless_{uuid.uuid4().hex[:8]}",
                        new_message=content
                    ):
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    response_text += part.text
                    
                    if response_text:
                        return response_text
                    
                except Exception as e:
                    error_str = str(e)
                    if "503" in error_str and attempt < 2:
                        print(f"Service unavailable. Retrying in {current_delay}s... (Attempt {attempt+1}/3)")
                        await asyncio.sleep(current_delay)
                        current_delay *= 2
                        continue
                    return f"Agent Execution Error: {error_str}"
            
            return "Error: Maximum retries reached with no response."

        return asyncio.run(_run_with_retry())

    def run_full_event_workflow(self, user_id: str, fb_page_id: str = None, 
                                 event_name: str = None, description: str = None,
                                 start_time: str = None, end_time: str = None,
                                 org_id: str = None) -> str:
        """Run the complete event creation workflow with all services."""
        
        # Build comprehensive prompt for the main agent
        prompt = f"""Create a complete event with the following details:
Event Name: {event_name or 'Untitled Event'}
Description: {description or 'No description provided'}
Start Time: {start_time or '2026-05-01T09:00:00Z'}
End Time: {end_time or '2026-05-01T17:00:00Z'}

[Context]
Organization ID: {org_id}
Owner ID: {user_id}

Please complete ALL of these tasks automatically without asking for additional input:
1. Create the event in the database
2. Generate media (image and announcer script)
3. Create a Google Document with the event plan
4. Schedule on Google Calendar
5. Create a task list for event preparation
6. Generate a slide presentation
7. Set up a Google Meet meeting
8. Create a Facebook post to promote the event (if page access is available)
"""
        
        return self.run_agent(self.main_agent, prompt, fbPageID=fb_page_id, user_id=user_id)


# Initialize the agent manager
agent_manager = EventAgentsManager()