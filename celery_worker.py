import os
from dotenv import load_dotenv
from app.ai_workers.workflow.full_workflow import execute_workflow
load_dotenv()

from app import create_app

flask_app = create_app()
celery = flask_app.extensions["celery"]

if __name__ == '__main__':
    celery.start()