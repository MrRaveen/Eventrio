import grpc
import traceback
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from app.proto import agent_pb2_grpc
from app.proto import agent_pb2
from app.agents.core.mainAgent import MainAgent, AGENT_INSTRUCTIONS


class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
    """gRPC Servicer: handles RunAgent unary RPC calls."""

    async def RunAgent(self, request, context):
        """Execute the agent with pre-fetched RAG context."""
        try:
            agent_manager = MainAgent()

            #Retrieve RAG context directly (no LLM tool-calling) ──
            rag_context = agent_manager.retrieve_context(
                event_id=request.eventID,
                query=request.query,
            )

            #Build augmented system prompt ──
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
            history.add_user_message(request.query)

            #Call LLM — no tools registered, plain completion ──
            kernel = agent_manager.get_kernel()
            settings = OpenAIChatPromptExecutionSettings()
            #The code queries the Kernel for the registered OpenAI service.
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
            return agent_pb2.AgentResponse(
                response=response_text,
                is_complete=True,
            )

        except Exception as e:
            full_trace = traceback.format_exc()
            print(f"[RunAgent ERROR]\n{full_trace}", flush=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return agent_pb2.AgentResponse(
                response="",
                is_complete=False,
                error=str(e),
            )


async def serve():
    """Start the async gRPC server and block until termination."""
    server = grpc.aio.server()
    agent_pb2_grpc.add_AgentServiceServicer_to_server(AgentServicer(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("GRPC Server 1 started", flush=True)
    await server.wait_for_termination()
