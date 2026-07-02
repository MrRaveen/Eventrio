import os
from flask import Flask, request, jsonify
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAITextEmbedding
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.volatile_memory_store import VolatileMemoryStore
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin

app = Flask(__name__)

# Initialize Kernel and AI Services
kernel = Kernel()
api_key = os.environ.get("OPENAI_API_KEY")

kernel.add_service(
    OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o", api_key=api_key)
)
kernel.add_service(
    OpenAITextEmbedding(service_id="embedding", ai_model_id="text-embedding-3-small", api_key=api_key)
)

# Initialize Vector Memory (Replace VolatileMemoryStore with a persistent DB in production)
memory_store = VolatileMemoryStore()
memory = SemanticTextMemory(storage=memory_store, embeddings_generator=kernel.get_service("embedding"))
kernel.import_plugin_from_object(TextMemoryPlugin(memory), "TextMemoryPlugin")

# Define RAG Prompt Strategy
RAG_PROMPT = """
Answer the question using strictly the context provided below.
If the context does not contain the answer, state that you lack sufficient information.

Context:
{{$context}}

Question:
{{$request}}
"""
rag_function = kernel.add_function(
    plugin_name="KnowledgeBase",
    function_name="Ask",
    prompt=RAG_PROMPT,
)

@app.route('/ingest', methods=['POST'])
async def ingest_document():
    data = request.json
    await memory.save_information_async(
        collection="app_data",
        id=data['id'],
        text=data['text']
    )
    return jsonify({"status": "success", "id": data['id']})

@app.route('/query', methods=['POST'])
async def query_knowledge_base():
    user_query = request.json['query']
    
    # 1. Retrieve Context
    search_results = await memory.search_async("app_data", user_query, limit=3, min_relevance_score=0.75)
    context_data = "\n".join([result.text for result in search_results])
    
    # 2. Augment and Generate
    result = await kernel.invoke(
        rag_function, 
        request=user_query, 
        context=context_data
    )
    
    return jsonify({"answer": str(result)})

if __name__ == '__main__':
    # Use ASGI servers like Hypercorn or Gunicorn with Uvicorn workers in production
    app.run(port=5000)


# import asyncio
# from app.agents.agent_manager import agent_manager

# async def test():
#     print("Testing hello...")
#     res = agent_manager.run_agent(agent_manager.main_agent, "hello")
#     print(f"Hello response: {res}")
    
#     print("Testing full workflow...")
#     res = agent_manager.run_full_event_workflow(user_id="user123", event_name="Test Event")
#     print(f"Workflow response: {res}")

# if __name__ == "__main__":
#     asyncio.run(test())
