import os
import traceback
import asyncio
import json
import uuid
import re
import requests

from google.adk.agents import SequentialAgent

from app.agents.manual_services import (
    automate_google_meet,
    create_event,
    create_google_doc_for_event,
    create_slides,
    generate_media_for_event,
    post_image_to_facebook_page,
    save_tasks_to_db,
    schedule_real_google_calendar,
)
from app.models.posts import Posts
from app.models.projects import Projects
from app.models.userAcc import userAcc

try:
    from google import genai
    from google.adk import Runner
    from google.adk.agents import Agent
    from google.adk.models import LiteLlm
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
except ImportError as e:
    print(f"Global ADK Import Failed. Message: {str(e)}")
    raise e

modelDeployment = os.getenv('MODEL_DEPLOYMENT', 'local')


class SequentialAgents:
    def __init__(self):
        # Check the agent's availability
        if Agent is None:
            print("Google ADK missing. Agent functionality disabled.")
            return

        try:
            # Model declaration
            if modelDeployment == 'cloud':
                local_llm = LiteLlm(
                    model="ollama/glm-4.7:cloud",
                    api_key=os.getenv("MODEL_KEY"),
                    api_base="https://ollama.com",
                    timeout=1800
                )
            else:
                local_llm = LiteLlm(
                    model="ollama_chat/qwen2.5:3b"
                )

            # ================================================================
            # Agent 1: Basic Info Extractor (no changes needed)
            # ================================================================
            self.basic_info_agent = Agent(
                model=local_llm,
                name='create_basic_info',
                description='Extracts event details from user prompt and generates event plan, script, and tasks.',
                instruction="""You are an event information extractor. From the user's prompt, you must extract and generate the following:

1. **event_name**: Extract the event name from the prompt. If not explicitly stated, create a short, catchy name.
2. **event_description**: Create a 2-3 sentence description of the event.
3. **event_plan**: Write a detailed paragraph (5-8 sentences) describing the event plan, schedule, and activities.
4. **announcing_script**: Write a short, fun 1-2 sentence script for an event announcer.
5. **start_time**: Extract the start date/time in RFC3339 format (e.g., "2026-06-15T09:00:00Z")
6. **end_time**: Extract the end date/time in RFC3339 format (e.g., "2026-06-17T18:00:00Z")
7. **image_prompt**: Create a short prompt (max 100 chars) for generating an event cover image.
8. **tasks_json**: Generate a JSON array of 5-7 tasks. Each task must have:
   - "title": Task name (string)
   - "description": Task details (string)
   - "start_date": Start date in "YYYY-MM-DD" format
   - "due_date": Due date in "YYYY-MM-DD" format

IMPORTANT RULES:
- DO NOT call any tools - just generate the information
- If the user didn't provide dates, use reasonable defaults
- Format the start_time and end_time as RFC3339: "YYYY-MM-DDTHH:MM:SSZ"
- The tasks_json must be a valid JSON array
- Output ALL fields listed above

Example tasks_json:
[{"title":"Set up venue","description":"Prepare the event space","start_date":"2026-06-14","due_date":"2026-06-15"},{"title":"Send invitations","description":"Email all guests","start_date":"2026-06-10","due_date":"2026-06-12"}]

Output format:
event_name: [name]
event_description: [description]
event_plan: [plan paragraph]
announcing_script: [script]
start_time: [RFC3339 datetime]
end_time: [RFC3339 datetime]
image_prompt: [image generation prompt]
tasks_json: [JSON array]""",
                output_key='event_details'
            )

            # ================================================================
            # Agent 2: Event Creator (FIXED - reads org_id/user_id from message)
            # ================================================================
            self.event_creator_agent = Agent(
                model=local_llm,
                name='create_event',
                description='Creates an event using extracted details from the basic_info agent and returns the event ID.',
                instruction="""You are an event creator. Create an event using the details below.

--- EVENT DETAILS FROM PREVIOUS STEP ---
{event_details}
---

YOUR TASK: Find the org_id and owner_id in the user's original message (they were provided at the start). Then call create_event ONCE with ALL parameters:

- **name**: Find "event_name:" line in event_details above
- **description**: Find "event_description:" line in event_details above
- **org_id**: Find "org_id:" in the user's original message
- **owner_id**: Find "user_id:" in the user's original message
- **start_time**: Find "start_time:" line in event_details above
- **end_time**: Find "end_time:" line in event_details above

EXAMPLE:
If the user's message contained:
  org_id: 69f18d8b21e3d1dbf2fb5a37
  user_id: 113617420998142644821

And event_details contains:
  event_name: AI Innovation Hackathon 2026
  event_description: A 48-hour virtual coding competition
  start_time: 2026-06-15T09:00:00Z
  end_time: 2026-06-17T18:00:00Z

Then call:
  create_event(
    name="AI Innovation Hackathon 2026",
    description="A 48-hour virtual coding competition",
    org_id="69f18d8b21e3d1dbf2fb5a37",
    owner_id="113617420998142644821",
    start_time="2026-06-15T09:00:00Z",
    end_time="2026-06-17T18:00:00Z"
  )

The function returns: "SUCCESS: Event created. The event_id is: 69f1915795b71fcde548f369"

CRITICAL RULES:
- Call create_event ONCE only
- Output ONLY the 24-character hex event_id
- DO NOT call any other tools
- DO NOT add extra text""",
                tools=[create_event],
                output_key='event_id'
            )
            # ================================================================
            # Agent 3: Media Agent
            # ================================================================
            self.create_media_agent = Agent(
                model=local_llm,
                name='create_media',
                description='Generates media (image and script) for the created event using the event_id and announcing_script from the first agent.',
                instruction="""You are a media generator. Create media for the event using the details from previous steps.

            --- EVENT DETAILS FROM PREVIOUS STEP ---
            {event_details}
            ---

            --- EVENT ID FROM PREVIOUS STEP ---
            {event_id}
            ---

            YOUR TASK: Call generate_media_for_event ONCE with these EXACT parameters:

            - **event_id**: "{event_id}" (use the event_id shown above)
            - **script_context**: Find the "announcing_script:" line in event_details and use that value

            EXAMPLE:
            If event_details contains:
            announcing_script: Welcome hackers! Get ready to build the future!

            Then call:
            generate_media_for_event(
                event_id="{event_id}",
                script_context="Welcome hackers! Get ready to build the future!"
            )

            CRITICAL RULES:
            - Call generate_media_for_event ONCE only
            - Use the EXACT announcing_script from event_details
            - Use the EXACT event_id provided above
            - Output the result from the function
            - DO NOT call any other tools
            - DO NOT transfer to other agents""",
                tools=[generate_media_for_event],
                output_key='media_result'
            )
            # ================================================================
            # Agent 4: Slides/Readme Creator
            # ================================================================
            self.create_readme_agent = Agent(
                model=local_llm,
                name='create_readme_slide',
                description='Creates a markdown presentation for the event based on the event details.',
                instruction="""You are a presentation creator. Generate a markdown slide deck for the event.

            --- EVENT DETAILS FROM PREVIOUS STEP ---
            {event_details}
            ---

            YOUR TASK:
            1. Read the event_details above to understand the event
            2. Generate a markdown presentation with 4-6 slides using this EXACT format:

            # [Slide Title]
            [Slide content - can use bullet points with - or paragraphs]

            ---

            # [Next Slide Title]
            [More content]

            ---

            FORMAT RULES:
            - Slide titles are level-1 headings: # Title Here
            - Slide separators are three dashes: ---
            - Bullet points use hyphens: - Point here
            - Each slide MUST have a title followed by content
            - Separate every slide with --- on its own line

            SLIDES TO CREATE:
            1. **Welcome/Title Slide**: Event name and catchy tagline
            2. **Event Schedule/Timeline**: Key dates and activities
            3. **Key Highlights**: What attendees will experience
            4. **Practical Information**: Venue, requirements, what to bring
            5. **Speakers/Guests** (if applicable): Who will be there
            6. **Call to Action**: How to join, next steps

            EXAMPLE OUTPUT:
            # Welcome to AI Hackathon 2026
            Join us for an unforgettable innovation experience!

            ---

            # Event Schedule
            48 Hours of Code
            - Day 1: Ideation & Team Formation
            - Day 2: Development & Mentorship
            - Day 3: Final Pitches & Awards

            ---

            # Key Highlights
            What to expect
            - Expert-led workshops
            - Networking opportunities
            - $10,000 in prizes

            ---

            # What to Bring
            - Laptop and charger
            - Creative ideas
            - Team spirit!

            ---

            # Join Us!
            Register at hackathon.example.com
            See you there!

            CRITICAL RULES:
            - Generate REAL content based on the event_details, never placeholders
            - Use the EXACT markdown format shown above
            - Each slide MUST be separated by ---
            - Output ONLY the markdown text - no explanations
            - DO NOT call any tools - just generate the markdown""",
                # NO tools - this agent just generates markdown text
                output_key='readmeCode'
            )
            # ================================================================
            # Agent 5: Slide Creator (Updated with eventID parameter)
            # ================================================================
            self.create_slides_agent = Agent(
                model=local_llm,
                name='create_slides',
                description='Creates the actual slide file using the generated markdown code and event ID, then uploads to cloud storage.',
                instruction="""You are a slide file creator. Create the actual presentation file using the markdown from the previous step.

            --- MARKDOWN CODE FROM PREVIOUS STEP ---
            {readmeCode}
            ---

            --- EVENT ID FROM PREVIOUS STEP ---
            {event_id}
            ---

            YOUR TASK: Call create_slides ONCE with these EXACT parameters:

            - **markdown_text**: Use the ENTIRE markdown code from the readmeCode above
            - **eventID**: Use the event_id shown above ("{event_id}")

            EXAMPLE:
            If readmeCode contains:
            # Welcome to AI Hackathon 2026
            Join us for an amazing event!
            
            ---
            
            # Event Schedule
            48 Hours of Code
            - Day 1: Ideation
            - Day 2: Development

            And event_id is: 69f1915795b71fcde548f369

            Then call:
            create_slides(
                markdown_text="# Welcome to AI Hackathon 2026\nJoin us for an amazing event!\n\n---\n\n# Event Schedule\n48 Hours of Code\n- Day 1: Ideation\n- Day 2: Development",
                eventID="69f1915795b71fcde548f369"
            )

            The function will return a JSON response like:
            {"link": "https://res.cloudinary.com/.../eventrio_presentation.pptx", "error": null}

            On success, it outputs the Cloudinary URL and saves it to the project.

            CRITICAL RULES:
            - Call create_slides ONCE only
            - Use the EXACT markdown text from readmeCode - do NOT modify it
            - Use the EXACT event_id provided above - do NOT make up an ID
            - Pass the COMPLETE markdown as a single string
            - Output the result (the link or error)
            - DO NOT call any other tools
            - DO NOT transfer to other agents""",
                tools=[create_slides],
                output_key='fileUploadLink'
            )
            # ================================================================
            # Agent 6: Create Google Meet
            # ================================================================
            self.create_google_meet_agent = Agent(
                model=local_llm,
                name='create_google_meet',
                description='Creates a Google Meet link using the event details from the first agent.',
                instruction="""You are a Google Meet creator. Create a meeting for the event.

            --- EVENT DETAILS FROM PREVIOUS STEP ---
            {event_details}
            ---

            --- USER CONTEXT ---
            Owner ID: Find "user_id:" in the user's original message

            YOUR TASK: Call automate_google_meet ONCE with these EXACT parameters:

            - **owner_id**: Find "user_id:" in the user's original message
            - **event_details**: A dictionary with these keys extracted from event_details:
                - "title": Find "event_name:" line in event_details
                - "start_time": Find "start_time:" line in event_details
                - "end_time": Find "end_time:" line in event_details

            EXAMPLE:
            If the user's message contained:
            user_id: 113617420998142644821

            And event_details contains:
            event_name: AI Innovation Hackathon 2026
            start_time: 2026-06-15T09:00:00Z
            end_time: 2026-06-17T18:00:00Z

            Then call:
            automate_google_meet(
                owner_id="113617420998142644821",
                event_details={
                "title": "AI Innovation Hackathon 2026",
                "start_time": "2026-06-15T09:00:00Z",
                "end_time": "2026-06-17T18:00:00Z"
                }
            )

            The function returns either:
            {"link": "https://meet.google.com/abc-defg-hij"} (success)
            {"error": "..."} (if Google auth is missing)

            CRITICAL RULES:
            - Call automate_google_meet ONCE only
            - Use the EXACT values from event_details
            - Output the result (link or error)
            - If Google auth fails, output the error message
            - DO NOT call any other tools""",
                tools=[automate_google_meet],
                output_key='meeting_link'
            )
            # ================================================================
            # Agent 7: Create Facebook Post
            # ================================================================
            self.create_fb_post_agent = Agent(
                model=local_llm,
                name='create_fb_post',
                description='Creates a Facebook post for the event using the generated media and event details.',
                instruction="""You are a social media poster. Create a Facebook post for the event.

            --- EVENT DETAILS FROM PREVIOUS STEP ---
            {event_details}
            ---

            --- USER CONTEXT ---
            Owner ID: Find "user_id:" in the user's original message
            FB Page ID: Find "fb_page_id:" in the user's original message

            YOUR TASK: Call post_image_to_facebook_page ONCE with these EXACT parameters:

            - **owner_id**: Find "user_id:" in the user's original message
            - **page_id**: Find "fb_page_id:" in the user's original message
            - **message**: Create an engaging post using the event_description from event_details
            - **image_url**: NOT NEEDED - the function handles this internally

            EXAMPLE:
            If the user's message contained:
            user_id: 113617420998142644821
            fb_page_id: 123456789012345

            And event_details contains:
            event_name: AI Innovation Hackathon 2026
            event_description: A 48-hour virtual coding competition

            Then call:
            post_image_to_facebook_page(
                owner_id="113617420998142644821",
                page_id="123456789012345",
                message="Join us for AI Innovation Hackathon 2026! A 48-hour virtual coding competition. Register now! #Hackathon #AI #Innovation"
            )

            The function returns either:
            {"id": "post_id_123", ...} (success)
            {"error": "..."} (if Facebook auth is missing)

            CRITICAL RULES:
            - Call post_image_to_facebook_page ONCE only
            - Use the EXACT owner_id and page_id from the user's message
            - Create an engaging, promotional message from the event_description
            - Output the result (post ID or error)
            - If Facebook auth fails, output the error message
            - DO NOT call any other tools""",
                tools=[post_image_to_facebook_page],
                output_key='post_response'
            )
            # ================================================================
            # Agent 8: Create Google Doc
            # ================================================================
            self.create_google_doc_agent = Agent(
                model=local_llm,
                name='create_doc',
                description='Creates a Google Doc using the event ID, user ID, and event plan from the first agent.',
                instruction="""You are a document creator. Create a Google Doc for the event.

            --- EVENT DETAILS FROM PREVIOUS STEP ---
            {event_details}
            ---

            --- EVENT ID FROM PREVIOUS STEP ---
            {event_id}
            ---

            --- USER CONTEXT ---
            Owner ID: Find "user_id:" in the user's original message

            YOUR TASK: Call create_google_doc_for_event ONCE with these EXACT parameters:

            - **owner_id**: Find "user_id:" in the user's original message
            - **event_id**: Use the event_id shown above ("{event_id}")
            - **plan_text**: Find the "event_plan:" line in event_details and use that value

            EXAMPLE:
            If the user's message contained:
            user_id: 113617420998142644821

            And event_id is: 69f1915795b71fcde548f369

            And event_details contains:
            event_plan: The hackathon will begin with team formation on Day 1, followed by development sessions on Day 2, and final presentations on Day 3. Mentors will be available throughout.

            Then call:
            create_google_doc_for_event(
                owner_id="113617420998142644821",
                event_id="69f1915795b71fcde548f369",
                plan_text="The hackathon will begin with team formation on Day 1, followed by development sessions on Day 2, and final presentations on Day 3. Mentors will be available throughout."
            )

            The function returns:
            "Successfully created your Google Doc: https://docs.google.com/document/d/.../edit"

            CRITICAL RULES:
            - Call create_google_doc_for_event ONCE only
            - Use the EXACT event_plan text from event_details
            - Use the EXACT event_id provided above
            - Use the EXACT owner_id from the user's message
            - Output the result (doc link or error)
            - If Google auth fails, output the error message
            - DO NOT call any other tools""",
                tools=[create_google_doc_for_event],
                output_key='google_doc_link'
            )
            # ================================================================
            # Agent 9: Save Tasks
            # ================================================================
            self.save_tasks_agent = Agent(
                model=local_llm,
                name='save_tasks',
                description='Saves the generated tasks to the database using the event ID, user ID, organization ID, and tasks JSON from the first agent.',
                instruction="""You are a task saver. Save the generated tasks for the event.

            --- EVENT DETAILS FROM PREVIOUS STEP ---
            {event_details}
            ---

            --- EVENT ID FROM PREVIOUS STEP ---
            {event_id}
            ---

            --- USER CONTEXT ---
            Owner ID: Find "user_id:" in the user's original message
            Organization ID: Find "org_id:" in the user's original message

            YOUR TASK: Call save_tasks_to_db ONCE with these EXACT parameters:

            - **owner_id**: Find "user_id:" in the user's original message
            - **event_id**: Use the event_id shown above ("{event_id}")
            - **org_id**: Find "org_id:" in the user's original message
            - **tasks_data_json**: Find the "tasks_json:" line in event_details and use the ENTIRE JSON array

            EXAMPLE:
            If the user's message contained:
            user_id: 113617420998142644821
            org_id: 69f18d8b21e3d1dbf2fb5a37

            And event_id is: 69f1915795b71fcde548f369

            And event_details contains:
            tasks_json: [{"title":"Set up venue","description":"Prepare the event space","start_date":"2026-06-14","due_date":"2026-06-15"},{"title":"Send invitations","description":"Email all guests","start_date":"2026-06-10","due_date":"2026-06-12"}]

            Then call:
            save_tasks_to_db(
                owner_id="113617420998142644821",
                event_id="69f1915795b71fcde548f369",
                org_id="69f18d8b21e3d1dbf2fb5a37",
                tasks_data_json='[{"title":"Set up venue","description":"Prepare the event space","start_date":"2026-06-14","due_date":"2026-06-15"},{"title":"Send invitations","description":"Email all guests","start_date":"2026-06-10","due_date":"2026-06-12"}]'
            )

            The function returns:
            "Successfully saved 2 tasks to MongoDB."

            CRITICAL RULES:
            - Call save_tasks_to_db ONCE only
            - Use the EXACT tasks_json from event_details - do NOT modify it
            - Use the EXACT event_id provided above - do NOT make up an ID
            - Use the EXACT owner_id and org_id from the user's message
            - Pass the COMPLETE JSON array as a string
            - Output the result (number of saved tasks or error)
            - DO NOT call any other tools""",
                tools=[save_tasks_to_db],
                output_key='savedTaskLength'
            )       
            # ================================================================
            # Build Pipeline
            # ================================================================
            self.event_pipeline = SequentialAgent(
                name="CompleteEventPipeline",
                sub_agents=[
                    self.basic_info_agent,
                    self.event_creator_agent,
                    self.create_media_agent,
                    self.create_readme_agent,
                    self.create_slides_agent,
                    self.create_google_meet_agent,
                    self.create_fb_post_agent,
                    self.create_google_doc_agent,
                    self.save_tasks_agent
                ]
            )

            print("Sequential agents initialized successfully.")

        except Exception as e:
            print(f"Failed to initialize agents: {str(e)}")
            traceback.print_exc()

    # ================================================================
    # Run Full Pipeline (FIXED - passes org_id/user_id in message text)
    # ================================================================
    def run_full_pipeline(self, prompt: str, user_id: str, org_id: str, fbPageID: str = None) -> str:
        """Run the sequential agent pipeline to create an event from a user prompt."""
        if not hasattr(self, 'event_pipeline'):
            return "Error: Agents not initialized."

        runner = Runner(
            app_name="Eventrio",
            agent=self.event_pipeline,
            session_service=InMemorySessionService(),
            auto_create_session=True
        )
        # Build the initial prompt with ALL context values
        initial_prompt = f"""
    IMPORTANT CONTEXT (use these exact values when calling functions):
    org_id: {org_id}
    user_id: {user_id}
    fb_page_id: {fbPageID or ''}

    USER REQUEST: {prompt}
    """

        content = types.Content(role="user", parts=[types.Part(text=initial_prompt)])

        async def _run_pipeline():
            response_text = ""

            try:
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=f"pipeline_{uuid.uuid4().hex[:8]}",
                    new_message=content
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                response_text += part.text
                                print(f"[Pipeline] {part.text[:200]}...")

            except Exception as e:
                print(f"Pipeline execution error: {e}")
                return f"Error: {str(e)}"

            return f"Pipeline completed.\nOutput:\n{response_text}"

        return asyncio.run(_run_pipeline())


# Initialize at module level
sequential_agents = SequentialAgents()