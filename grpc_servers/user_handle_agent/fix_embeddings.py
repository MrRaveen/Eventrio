"""
Re-embed all documents in eventContext with correct 384-dim vectors
from all-MiniLM-L6-v2, then create the Atlas Vector Search index.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=project_root / ".env")

from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB_NAME", "").strip("'\"")
collection_name = os.getenv("EVENT_CONTEXT_COLLECTION", "eventContext").strip("'\"")

print("Loading SentenceTransformer model...", flush=True)
model = SentenceTransformer('all-MiniLM-L6-v2')

client = MongoClient(mongo_uri)
coll = client[db_name][collection_name]

# Step 1: Re-embed all documents
print("\n=== Re-embedding documents ===", flush=True)
docs = list(coll.find())
for i, doc in enumerate(docs):
    content = doc.get("content", "")
    if not content:
        print(f"  Doc {i+1}: SKIP (no content)", flush=True)
        continue
    
    embedding = model.encode(content).tolist()
    coll.update_one(
        {"_id": doc["_id"]},
        {"$set": {"embedding": embedding}}
    )
    print(f"  Doc {i+1}: re-embedded ({len(embedding)} dims) | {content[:80]}...", flush=True)

# Verify
print("\n=== Verification ===", flush=True)
sample = coll.find_one()
emb = sample.get("embedding", [])
print(f"  Sample embedding dims: {len(emb)}")

# Step 2: Create Atlas Vector Search index
print("\n=== Creating Atlas Vector Search Index ===", flush=True)
index_definition = {
    "fields": [
        {
            "type": "vector",
            "path": "embedding",
            "numDimensions": 384,
            "similarity": "cosine"
        },
        {
            "type": "filter",
            "path": "eventID"
        }
    ]
}

try:
    # Check existing indexes first
    existing = list(coll.list_search_indexes())
    existing_names = [idx.get("name") for idx in existing]
    print(f"  Existing search indexes: {existing_names}", flush=True)
    
    if "vector_index" in existing_names:
        print("  'vector_index' already exists — dropping and recreating...", flush=True)
        coll.drop_search_index("vector_index")
        import time
        time.sleep(5)  # Wait for drop to propagate
    
    coll.create_search_index(
        model={
            "name": "vector_index",
            "type": "vectorSearch",
            "definition": index_definition
        }
    )
    print("  ✅ Atlas Vector Search index 'vector_index' created!", flush=True)
    print("  ⏳ Note: Index may take 1-2 minutes to become active on Atlas.", flush=True)
except Exception as e:
    print(f"  ❌ Could not create search index: {e}", flush=True)
    print("  You may need to create it manually in the Atlas UI.", flush=True)

client.close()
print("\n[DONE]")
