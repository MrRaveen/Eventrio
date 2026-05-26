import os
import sys
import datetime
import instructor
from litellm import completion
# Allow running this file directly from anywhere by adding the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv()

# Load the import hook (mocking infrastructure) if APP_STATUS is set to Development
app_status = os.getenv('APP_STATUS')

import traceback
import asyncio
import json
import uuid
import re
import requests
from app.agents.outputSchemas import EventDetailsSchema
from google.adk.agents import SequentialAgent
from flask import Flask, request, render_template
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

app = Flask(__name__)

class SequentialAgents:
    def __init__(self):
        # Check the agent's availability
        if Agent is None:
            print("Google ADK missing. Agent functionality disabled.")
            return

        try:
            # Model declaration
            if modelDeployment == 'cloud':
                # local_llm = LiteLlm(
                #     model="ollama/glm-4.7:cloud",
                #     api_key=os.getenv("MODEL_KEY"),
                #     api_base="https://ollama.com",
                #     timeout=1800
                # )
                local_llm = LiteLlm(
                    model="groq/openai/gpt-oss-120b", 
                    api_key=os.getenv("GROQ_API_KEY"), 
                    timeout=1800
                )
            else:
                local_llm = LiteLlm(
                    model="ollama_chat/qwen2.5:3b"
                )
            # schema_instructions = EventDetailsSchema.model_json_schema()
            # Agent 1: Basic Info Extractor
            # self.basic_info_agent = Agent(
            #     model=local_llm,
            #     name='create_basic_info',
            #     description='Extracts event details from user prompt into a structured JSON payload.',
            #     instruction=f"""You are an event information extractor. Extract event details from the user's prompt.
            #     If the user didn't provide dates, use reasonable defaults.
            #     Format the start_time and end_time as RFC3339.
                
            #     You MUST respond with a raw JSON object that strictly adheres to the following JSON schema:
            #     {json.dumps(schema_instructions)}
                
            #     IMPORTANT: Return ONLY the raw JSON. Do NOT wrap the output in ```json markdown blocks.""",
                
            #     # REMOVED: output_schema=EventDetailsSchema
            #     output_key='event_details'
            # )

            
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
                
            self.event_pipeline = SequentialAgent(
                name="CompleteEventPipeline",
                sub_agents=[
                    self.create_media_agent,
                    self.create_readme_agent
                ]
            )
            print("Sequential agents initialized successfully.")

        except Exception as e:
            print(f"Failed to initialize agents: {str(e)}")
            traceback.print_exc()
    def testRun(self, prompt: str, user_id: str = "user_default"):
        try:
            # 1. Define the current date dynamically when the function runs
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            client = instructor.from_litellm(completion)
            extracted_data = client.chat.completions.create(
                # 2. Use a valid Groq model! (gpt-oss-120b threw a 404 previously)
                model="groq/llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert, creative event planner and strategist. Your job is to take the "
                            "user's core idea and flesh it out into a complete, comprehensive event plan. "
                            "Do not just extract data; brainstorm and generate missing details. "
                            "If the user provides a brief concept, you must invent a catchy event name, "
                            "write an engaging description, and establish realistic start and end times. "
                            "Break down the preparation into 5-7 actionable tasks with logical timelines. "
                            f"Assume today's date is {current_date}. All generated dates must be in the future."
                        )
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_model=EventDetailsSchema,
                max_retries=3, 
            )
            
            # Since extracted_data is a Pydantic object, you need to dump it to a dict 
            # if you are going to return it directly in a Flask JSON response.
            return extracted_data.model_dump()
            
        except Exception as e:
            print(f"Error in extraction: {str(e)}")
            traceback.print_exc()
            return None


# Initialize the agent instance at the module level
agents = SequentialAgents()


@app.route('/test', methods=['GET'])
def test():
    try:
        # Fetch the prompt from GET query parameter, or use a default prompt
        prompt = request.args.get(
            'prompt', 
            'Plan a coding hackathon called Eventrio Hackathon from 2026-06-15 to 2026-06-17'
        )
        print(f"[/test] Received prompt: {prompt}")
        
        user_id = request.args.get('user_id', 'user_default')
        extracted_data = agents.testRun(prompt, user_id=user_id)
        
        if extracted_data:
            return {
                "status": "success",
                "extracted_data": extracted_data
            }, 200
        else:
            return {
                "status": "error",
                "message": "Failed to extract event details."
            }, 500
    except Exception as e:
        print(f"[/test] Route exception: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }, 500


if __name__ == '__main__':
    app.run(debug=True)

