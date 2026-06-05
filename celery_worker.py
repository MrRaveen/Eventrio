import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from app import create_app

flask_app = create_app()
celery = flask_app.extensions["celery"]

# Uncomment and adjust below when you create your tasks file
# import app.tasks

if __name__ == '__main__':
    celery.start()