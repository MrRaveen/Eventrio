import os
import asyncio
from flask import Blueprint, jsonify, request, session
from app.orchestrator.saga.engine import engine
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI
import grpc
from grpc_servers.user_handle_agent.app.proto import agent_pb2
from grpc_servers.user_handle_agent.app.proto import agent_pb2_grpc

ai_routes_bp = Blueprint('ai_routes', __name__)

@ai_routes_bp.route('/test-agent', methods=['POST'])
def test_agent():
    try:
        address = os.getenv('USER_AGENT_GRPC', 'localhost:50051')
        data = request.json or {}
        
        user_id = data.get('userID') or data.get('user_id') or 'unknown_user'
        query = data.get('query') or data.get('prompt') or ''

        if not query:
            return jsonify({"error": "query or prompt is required"}), 400

        with grpc.insecure_channel(address) as channel:
            stub = agent_pb2_grpc.AgentServiceStub(channel)
            grpc_request = agent_pb2.AgentRequest(
                user_id=user_id,
                query=query
            )
            response = stub.RunAgent(grpc_request)
            
            if response.error:
                return jsonify({"error": response.error, "is_complete": False}), 500

            return jsonify({
                "response": response.response,
                "is_complete": response.is_complete
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
