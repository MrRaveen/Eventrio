import os
import time
import json
from typing import List, Any
from pydantic import BaseModel
from celery import shared_task
from app.config import getRedisClient
from app.models.eventContext import EventContext, ChunkType
from sentence_transformers import SentenceTransformer
from app.orchestrator.channel_output import channel_output

model = None

class context_service:
    class req_data(BaseModel):
        owner_id: str
        event_id: str
        allQuestionsAnswers: List[Any]
        allParagraphs: List[Any]
        workflow_id: str

    @staticmethod
    @shared_task(name='create_context', bind=False)
    def create_context(reqData: dict):
        try:
            global model
            if model is None:
                model = SentenceTransformer('all-MiniLM-L6-v2')

            if isinstance(reqData, dict):
                reqData = context_service.req_data(**reqData)

            start_time_exec = time.time()
            redis_client = getRedisClient()
            channel_name = os.getenv('CHANNEL_NAME_ORCHESTRATOR')

            event_id = reqData.event_id
            
            # Process Questions and Answers
            qa_texts = []
            for qa in reqData.allQuestionsAnswers:
                if isinstance(qa, dict):
                    q = qa.get('question', '') or qa.get('Q', '')
                    a = qa.get('answer', '') or qa.get('A', '')
                    if q and a:
                        qa_texts.append(f"Q: {q} A: {a}")
                    elif q:
                        qa_texts.append(f"Q: {q}")
                    elif a:
                        qa_texts.append(f"A: {a}")
                elif isinstance(qa, str) and qa.strip():
                    qa_texts.append(qa.strip())

            if qa_texts:
                qa_embeddings = model.encode(qa_texts)
                qa_docs = []
                for idx, text in enumerate(qa_texts):
                    qa_docs.append(EventContext(
                        eventID=event_id,
                        chunkType=ChunkType.Q_AND_A,
                        content=text,
                        embedding=qa_embeddings[idx].tolist()
                    ))
                if qa_docs:
                    EventContext.objects.insert(qa_docs)

            # Process Paragraphs
            para_texts = []
            for para in reqData.allParagraphs:
                if isinstance(para, str) and para.strip():
                    para_texts.append(para.strip())

            if para_texts:
                para_embeddings = model.encode(para_texts)
                para_docs = []
                for idx, text in enumerate(para_texts):
                    para_docs.append(EventContext(
                        eventID=event_id,
                        chunkType=ChunkType.PARAGRAPH,
                        content=text,
                        embedding=para_embeddings[idx].tolist()
                    ))
                if para_docs:
                    EventContext.objects.insert(para_docs)

            end_time = time.time()
            time_ms = int((end_time - start_time_exec) * 1000)

            pushing_data = channel_output(
                return_data={
                    "status": "SUCCESS",
                    "message": "Context created successfully"
                }
            )
            
            payload = {
                "status": "SUCCESS",
                "function_name": "create_context",
                "ms": time_ms,
                "payload": {
                    "workflowID": reqData.workflow_id,
                    "user_id": reqData.owner_id,
                    "project_id": event_id
                },
                "channel_output": pushing_data.model_dump()
            }
            redis_client.publish(channel_name, json.dumps(payload, default=str))

        except Exception as e:
            print(f"Error in create_context: {e}")
            try:
                redis_client = getRedisClient()
                channel_name = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
                workflow_id = reqData.get('workflow_id') if isinstance(reqData, dict) else reqData.workflow_id
                user_id = reqData.get('owner_id') if isinstance(reqData, dict) else reqData.owner_id
                payload = {
                    "status": "FAILED",
                    "function_name": "create_context",
                    "ms": 0,
                    "payload": {
                        "workflowID": workflow_id,
                        "user_id": user_id,
                    },
                    "error": str(e)
                }
                redis_client.publish(channel_name, json.dumps(payload, default=str))
            except Exception as publish_err:
                print(f"Error publishing failure: {publish_err}")
