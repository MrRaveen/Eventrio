import json
import os
import traceback

import redis
from app.agents.core.mainAgent import AGENT_INSTRUCTIONS, MainAgent
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory


def _get_redis_client():
    """Create a standalone Redis client for the gRPC server (separate from Flask app's singleton)."""
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )


async def user_questions_task(job_id: str, eventID: str, query: str, tempUserID: str):
    """
    Standalone async background task to:
    1. Retrieve RAG context from the database.
    2. Build and invoke the LLM with the context.
    3. Publish the result to Redis pub/sub so the subscribed Flask SSE client receives it.
    """
    try:
        redis_client = _get_redis_client()
        agent_manager = MainAgent()

        # Retrieve RAG context directly (no LLM tool-calling) ──
        rag_context = agent_manager.retrieve_context(
            event_id=eventID,
            query=query,
        )

        # Build augmented system prompt ──
        if rag_context:
            system_msg = (
                f"{AGENT_INSTRUCTIONS}\n\n"
                f"--- Retrieved Event Context ---\n{rag_context}\n"
                f"--- End of Context ---"
            )
        else:
            system_msg = (
                f"{AGENT_INSTRUCTIONS}\n\n"
                "(No context was retrieved from the database for this query.)"
            )

        history = ChatHistory()
        history.add_system_message(system_msg)
        history.add_user_message(query)

        # Call LLM — no tools registered, plain completion ──
        kernel = agent_manager.get_kernel()
        settings = OpenAIChatPromptExecutionSettings()
        # The code queries the Kernel for the registered OpenAI service.
        chat_service: OpenAIChatCompletion = kernel.get_service(
            type=OpenAIChatCompletion
        )

        # This is the execution trigger. The OpenAIChatCompletion service takes the standardized,
        # framework-agnostic objects (history and settings),
        # translates them into the specific JSON payload required by OpenAI's
        # REST API, makes the asynchronous network call, and parses the response back into a Semantic Kernel object.
        result = await chat_service.get_chat_message_contents(
            chat_history=history,
            settings=settings,
        )

        response_text = result[-1].content if result else ""
        channel_name = os.getenv('PARTICIPANT_CHANNEL')

        payload = {
            "type":"message",
            "eventID": eventID,
            "userID": tempUserID,
            "job_id": job_id,
            "query": query,
            "res_text": response_text,
        }

        json_payload = json.dumps(payload)
        subscribers_count = redis_client.publish(channel_name, json_payload)
        breakpoint()
        print(f"[user_questions_task] Published response for job={job_id} to {subscribers_count} subscriber(s).", flush=True)

    except Exception as e:
        full_trace = traceback.format_exc()
        print(f"[user_questions_task ERROR]\n{full_trace}", flush=True)

        # Attempt to publish an error payload so the SSE client can display it
        try:
            redis_client = _get_redis_client()
            channel_name = os.getenv('PARTICIPANT_CHANNEL', 'participant_events')
            error_payload = json.dumps({
                "eventID": eventID,
                "userID": tempUserID,
                "job_id": job_id,
                "query": query,
                "res_text": f"[Agent Error] {str(e)}",
                "error": True,
            })
            redis_client.publish(channel_name, error_payload)
        except Exception:
            pass
