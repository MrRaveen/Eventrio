import asyncio
import datetime
import json
import os
import threading
import uuid

import grpc
import jwt
import redis
from flask import Blueprint, Response, jsonify, request, session, stream_with_context
from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from app.config import getRedisClient
from app.decorators.get_temp_participantID import SECRET_KEY, require_token
from app.models.projects import Projects
from app.orchestrator.saga.engine import engine
from grpc_servers.user_handle_agent.app.proto import agent_pb2, agent_pb2_grpc

ai_routes_bp = Blueprint('ai_routes', __name__)
redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
        )
def background_task(tempUserID: str, stop_event: threading.Event):
    channel_name = os.getenv('PARTICIPANT_CHANNEL')

    # 2. Loop only while the event is NOT set
    while not stop_event.is_set():
        # Use stop_event.wait() instead of time.sleep().
        # It acts like sleep, but can be interrupted instantly if the event is triggered.
        is_stopped = stop_event.wait(20.0)

        if is_stopped:
            break # Exit the loop immediately if the user disconnects

        payload = {
            "type": "ping",
            "user": tempUserID
        }
        json_payload = json.dumps(payload)
        redis_client.publish(channel_name, json_payload)

    print(f"[Thread] Background ping task for {tempUserID} safely terminated.")

@ai_routes_bp.route('/get-temp-ID', methods=['GET'])
def get_temp_id():
    try:
        temp_id = str(uuid.uuid4())
        payload = {
            'user_id': temp_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        breakpoint()
        return jsonify({'token': token})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_routes_bp.route('/listen-participant', methods=['GET'])
@require_token
def listen_notifications_participant():
    meeting_url = request.args.get('meetingURL') or request.args.get('meeting_url')
    if not meeting_url:
        return jsonify({"error": "meetingURL parameter is required"}), 400

    project = Projects.objects(meetingUrl=meeting_url).first()
    if not project:
        project = Projects.objects(meetingUrl__contains=meeting_url).first()

    if not project:
        return jsonify({"error": "No matching event found for the provided meeting info."}), 404

    eventID = str(project.id)
    user_id = getattr(request, 'temp_user_id', None)
    channel = os.getenv('PARTICIPANT_CHANNEL', 'default_participant_channel')

    def event_stream():
        redis_client = getRedisClient()
        pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(channel)
        print(f"[SSE] User (participant) '{user_id}' connected to stream on channel '{channel}'")

        try:
            while True:
                # Poll Redis with a 15-second timeout
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=15.0)

                if message is None:
                    # No new messages in 15s — yield heartbeat to prevent Cloudflare/Proxy timeout
                    yield ": keepalive\n\n"
                    continue

                try:
                    raw = message['data']
                    if isinstance(raw, bytes):
                        raw = raw.decode('utf-8')

                    payload = json.loads(raw)

                    # Ignore external ping messages if any exist
                    if payload.get("type") == "ping":
                        yield ": keepalive\n\n"
                        continue

                    # Filter by eventID
                    if payload.get('eventID') != eventID:
                        continue

                    # Filter by target user
                    target_user = payload.get('userID')
                    if target_user and target_user != user_id:
                        continue

                    event_data = json.dumps(payload)
                    yield f"data: {event_data}\n\n"

                except (json.JSONDecodeError, Exception) as parse_err:
                    print(f"[SSE] Error parsing message: {parse_err}")
                    continue

        except GeneratorExit:
            print(f"[SSE] User '{user_id}' disconnected from notification stream")
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()

    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'  # Prevents CORS errors on reconnects
        }
    )



@ai_routes_bp.route('/test-agent', methods=['POST'])
@require_token
def test_agent():
    try:
        address = os.getenv('USER_AGENT_GRPC', 'localhost:50051')
        data = request.json or {}

        query = data.get('query') or data.get('prompt') or ''
        user_id = getattr(request, 'temp_user_id', None)
        if not query or not user_id:
            return jsonify({"error": "prompt and userID is required"}), 400

        # Try to resolve eventID (from eventID direct, meetingCode, or meetingURL)
        eventID = data.get('eventID') or data.get('event_id')

        if not eventID:
            meeting_code = data.get('meetingCode') or data.get('meeting_code')
            meeting_url = data.get('meetingURL') or data.get('meeting_url')

            project = None
            if meeting_code:
                # Retrieve project by meeting code substring (e.g. 'abc-defg-hij')
                project = Projects.objects(meetingUrl__contains=meeting_code).first()
            if not project and meeting_url:
                project = Projects.objects(meetingUrl=meeting_url).first()

            if not project:
                return jsonify({"error": "No matching event found for the provided meeting info."}), 404

            eventID = str(project.id)
        else:
            eventID = str(eventID)

        with grpc.insecure_channel(address) as channel:
            stub = agent_pb2_grpc.AgentServiceStub(channel)
            grpc_request = agent_pb2.AgentRequest(
                eventID=eventID,
                tempUserID=user_id,
                query=query
            )
            response = stub.RunAgent(grpc_request)

            if response.error:
                return jsonify({"error": response.error, "is_complete": False}), 500

            # The gRPC server accepted the job. The actual AI response will be
            # published to Redis pub/sub and delivered via the /listen-participant SSE stream.
            return jsonify({
                "job_id": response.job_id,
                "eventID": response.eventID,
                "is_complete": False,
                "status": "accepted"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# kernel = Kernel()

# @ai_routes_bp.route('/test-agent', methods=['POST'])
# def test_agent():
#     try:
#         client = AsyncOpenAI(
#             api_key=os.getenv("GROQ_API_KEY"),
#             base_url="https://api.groq.com/openai/v1"
#         )
#         service = OpenAIChatCompletion(
#             service_id="groq",
#             ai_model_id="llama-3.1-8b-instant",
#             async_client=client
#         )

#         kernel.add_service(service)
#         result = asyncio.run(kernel.invoke_prompt("Summarise the latest news in 3 bullet points"))
#         return str(result)
#     except Exception as e:
#         return str(e)


@ai_routes_bp.route('/generate-event', methods=['POST'])
def generate_event():
    """
    Starts the SAGA orchestrator engine to generate an AI event.
    Expects JSON body: { prompt: str, orgID: str, page_id?: str }
    Returns immediately — the frontend listens for completion via SSE /notifications/listen.
    """
    user_id = session.get('user_id', 'unknown_user')

    data = request.json or {}
    prompt = data.get('prompt')
    org_id = data.get('orgID')
    page_id = data.get('page_id', None)

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    if not org_id:
        return jsonify({"error": "Organization ID is required"}), 400

    try:
        engine.start_engine(
            userID=user_id,
            prompt=prompt,
            org_id=org_id,
            page_id=page_id
        )
        return jsonify({
            "status": "success",
            "message": "AI event generation started. You will be notified when it completes."
        }), 202
    except Exception as e:
        return jsonify({"error": f"Failed to start engine: {str(e)}"}), 500
