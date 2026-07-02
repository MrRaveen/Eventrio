import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from app.agents.core.llmService import llmService
from app.agents.plugins.RAG_pluggin import MongoRAGPlugin

AGENT_INSTRUCTIONS = (
    "You are the official event assistant. Answer participant questions about "
    "event logistics, schedules, and details using ONLY the provided context. "
    "If the context does not contain the answer, say the detail is currently unavailable. "
    "Do not make up information."
)


class MainAgent:
    def __init__(self):
        self.llm_service = llmService()
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME")
        self.target_collection = os.getenv("EVENT_CONTEXT_COLLECTION", "event_chunks")

    def get_kernel(self) -> Kernel:
        """Build a plain Kernel with the LLM service — no tools registered."""
        kernel = Kernel()
        kernel.add_service(self.llm_service)
        return kernel

    def retrieve_context(self, event_id: str, query: str) -> str:
        """
        Directly call the RAG plugin and return retrieved context as a string.
        Pre-fetching avoids relying on Groq's llama model to correctly emit
        OpenAI-style tool calls (it often generates a broken format that
        causes a 400 from Groq's API).
        """
        plugin = MongoRAGPlugin(
            connection_string=self.mongo_uri,
            db_name=self.db_name,
            collection_name=self.target_collection,
            event_id=event_id,
        )
        try:
            context = plugin.retrieve_context(query=query)
            return context or ""
        except Exception as e:
            print(f"[RAG retrieve_context error]: {e}", flush=True)
            return ""