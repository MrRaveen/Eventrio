import os
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import httpx

def llmService() -> OpenAIChatCompletion:
    api_key = os.getenv("GROQ_API_KEY")
    base_url = os.getenv("GROQ_BASE")
    service_id = os.getenv("SERVICE_ID", "groq")
    model = os.getenv("MODEL", "llama-3.1-8b-instant")
    
    if api_key:
        api_key = api_key.strip("'\"")
    if base_url:
        base_url = base_url.strip("'\"")
    if service_id:
        service_id = service_id.strip("'\"")
    if model:
        model = model.strip("'\"")

    print(f"[LLM] Connecting to: {base_url} | model: {model}", flush=True)

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=httpx.Timeout(60.0, connect=10.0),
    )
    service = OpenAIChatCompletion(
        service_id=service_id,
        ai_model_id=model,
        async_client=client
    )
    return service

