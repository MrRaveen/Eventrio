"""Show all 5 documents and their embedding dimensions."""
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=project_root / ".env")

from pymongo import MongoClient

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB_NAME", "").strip("'\"")
collection_name = os.getenv("EVENT_CONTEXT_COLLECTION", "eventContext").strip("'\"")

client = MongoClient(mongo_uri)
coll = client[db_name][collection_name]

for i, doc in enumerate(coll.find()):
    emb = doc.get("embedding", [])
    content = doc.get("content", "")[:120]
    print(f"\n--- Doc {i+1} ---")
    print(f"  eventID: {doc.get('eventID')}")
    print(f"  chunkType: {doc.get('chunkType')}")
    print(f"  content: {content}")
    print(f"  embedding dims: {len(emb)}")
    if emb:
        print(f"  first 5 values: {emb[:5]}")

client.close()
