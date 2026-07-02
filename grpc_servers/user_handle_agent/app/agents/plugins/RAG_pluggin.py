from typing import Annotated
from pymongo import MongoClient
from semantic_kernel.functions import kernel_function
from app.utils.vector_converter import vector_converter


class MongoRAGPlugin:
    def __init__(self, connection_string: str, db_name: str, collection_name: str, event_id: str = None):
        self.client = MongoClient(connection_string)
        self.collection = self.client[db_name][collection_name]
        self.converter = vector_converter()
        self.event_id = event_id

    @kernel_function(
        name="RetrieveEnterpriseContext",
        description="Searches the MongoDB vector database to retrieve context for user queries."
    )
    def retrieve_context(self, query: str) -> str:
        query_vector = self.converter.convertToVector(text = query)
        
        vector_search_stage = {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_vector,
            "numCandidates": 100,
            "limit": 3
        }
        if self.event_id:
            vector_search_stage["filter"] = {"eventID": self.event_id}
            
        pipeline = [
            {
                "$vectorSearch": vector_search_stage
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return "\n".join([doc.get("content", doc.get("text_content", "")) for doc in results])