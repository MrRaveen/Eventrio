import os
import grpc
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI
from app.proto import agent_pb2_grpc
from app.proto import agent_pb2


class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
    """gRPC Servicer: handles RunAgent unary RPC calls."""

    async def RunAgent(self, request, context):
        """Execute the agent with the provided query and return a response."""
        try:
            kernel = Kernel()

            client = AsyncOpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            service = OpenAIChatCompletion(
                service_id="groq",
                ai_model_id="llama-3.1-8b-instant",
                async_client=client
            )
            kernel.add_service(service)

            # invoke_prompt is a coroutine — await it, don't wrap in asyncio.run()
            result = await kernel.invoke_prompt(request.query)

            return agent_pb2.AgentResponse(
                response=str(result),
                is_complete=True
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return agent_pb2.AgentResponse(
                response="",
                is_complete=False,
                error=str(e)
            )


async def serve():
    """Start the async gRPC server and block until termination."""
    server = grpc.aio.server()
    agent_pb2_grpc.add_AgentServiceServicer_to_server(
        AgentServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("GRPC Server 1 started")
    await server.wait_for_termination()
