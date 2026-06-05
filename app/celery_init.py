from flask import Flask
from celery import Celery, Task
import os

def init_celery(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app = Celery(
        app.import_name,
        broker=os.getenv('CELERY_BROKER_URL'),
        backend=os.getenv('CELERY_RESULT_BACKEND'),
        task_cls=FlaskTask
    )
    celery_app.conf.update(app.config)
    
    return celery_app