import uuid
import asyncio
import grpc
import traceback
from app.proto import agent_pb2_grpc
from app.proto import agent_pb2
from app.tasks.user_questions_task import user_questions_task


class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
    """gRPC Servicer: handles RunAgent unary RPC calls."""

    async def RunAgent(self, request, context):
        """
        Accept the request immediately, fire the heavy RAG+LLM work as a
        background asyncio task, and return a job_id to the caller so it
        can track the result via SSE / Redis pub-sub.
        """
        try:
            job_id = str(uuid.uuid4())

            # Fire background task — does NOT block the gRPC response
            asyncio.create_task(
                user_questions_task(
                    job_id=job_id,
                    eventID=request.eventID,
                    query=request.query,
                    tempUserID=request.tempUserID,
                )
            )

            # Return immediately with the job_id so the Flask caller can
            # tell the frontend which job to watch on the SSE stream.
            return agent_pb2.AgentResponse(
                eventID=request.eventID,
                job_id=job_id,
                is_complete=False,  # Work is still in progress in the background
            )

        except Exception as e:
            full_trace = traceback.format_exc()
            print(f"[RunAgent ERROR]\n{full_trace}", flush=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return agent_pb2.AgentResponse(
                eventID=request.eventID,
                job_id="",
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
