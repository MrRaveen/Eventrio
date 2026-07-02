import asyncio
import os
import sys
from pathlib import Path

print("Initializing GRPC Server... Loading heavy AI dependencies (PyTorch). This can take a few minutes on external drives. Please wait...", flush=True)

from app.routes.mainAgentAccess import serve
from dotenv import load_dotenv

#only the GRPC server (not a flask server)
if __name__ == "__main__":
    # The .env lives in the project root (mvp/), two levels up from this file
    project_root = Path(__file__).resolve().parent.parent.parent
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Debug: confirm critical vars loaded
    print(f"[ENV] GROQ_BASE = {os.getenv('GROQ_BASE', 'NOT SET')}", flush=True)
    print(f"[ENV] MONGO_URI = {'SET' if os.getenv('MONGO_URI') else 'NOT SET'}", flush=True)
    print(f"[ENV] MONGO_DB_NAME = {os.getenv('MONGO_DB_NAME', 'NOT SET')}", flush=True)
    print(f"[ENV] EVENT_CONTEXT_COLLECTION = {os.getenv('EVENT_CONTEXT_COLLECTION', 'NOT SET')}", flush=True)
    
    asyncio.run(serve())
