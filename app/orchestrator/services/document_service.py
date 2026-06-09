import requests
from celery import shared_task
from pydantic import BaseModel

from app.models.userAcc import userAcc


class document_service:
    class req_data(BaseModel):
        owner_id: str
        event_id: str
        plan_text: str
        
    @shared_task(bind=True)
    def create_google_doc_for_event_task(self, reqData: "document_service.req_data") -> str:
        if isinstance(reqData, dict):
            reqData = document_service.req_data(**reqData)

        user = userAcc.objects(sub=reqData.owner_id).first()
        if not user:
            return "Error: User not found. Please log in again."
        if not user.oauthToken:
            return "Error: Google account not connected. Please connect your Google account in Settings."
        if not user.oauthToken.get('access_token'):
            return "Error: Google access token expired. Please reconnect your Google account."
        headers = {"Authorization": f"Bearer {user.oauthToken.get('access_token')}", "Content-Type": "application/json"}
        #Create empty document
        res = requests.post("https://docs.googleapis.com/v1/documents", headers=headers, json={"title": f"Event Plan: {reqData.event_id}"})
        if res.status_code != 200: return f"Error creating doc: {res.text}"
        doc_id = res.json().get('documentId')
        #Insert text
        insert_req = {
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": reqData.plan_text
                    }
                }
            ]
        }
        res2 = requests.post(f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate", headers=headers, json=insert_req)
        doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
        return f"Successfully created your Google Doc: {doc_link}"
