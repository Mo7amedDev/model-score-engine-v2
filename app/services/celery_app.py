# app/services/celery_app.py

from celery import Celery
from celery.schedules import crontab
import os 
from dotenv import load_dotenv
load_dotenv()
ENV = os.getenv("ENV","DEV")

schedule = (
    crontab(minute="*")
    if ENV == "DEV"
    else crontab(hour="*/12", minute=0) # every 12 hours
)

#schedule = crontab(minute="*")

celery = Celery(
    "worker",
    broker=f"redis://{os.getenv('REDIS_HOST')}:6379/0",# in docker : redis
    backend=f"redis://{os.getenv('REDIS_HOST')}:6379/0",# in docker: redis
)

# 🔥 FORCE import of tasks
celery.autodiscover_tasks(["app.services"])

# ✅ scheduler
celery.conf.beat_schedule = {
    "update-models-schedule": {
        "task": "app.services.tasks.notify_apps",
        "schedule": schedule,
    },
}