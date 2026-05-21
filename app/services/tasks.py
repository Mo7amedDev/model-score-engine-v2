# app/services/tasks.py
from app.services.celery_app import celery
import asyncio
from app.services.model_store import notify_webhooks, WebhookEvent
from app.core.updater import updateModels
import anyio

@celery.task(name="app.services.tasks.notify_apps", bind=True, max_retries=3)
def notify_apps(self):
    try:
        # 1. Update models
        updateModels()
        # 2. Create event
        event = WebhookEvent(
            event="models.updated",
            version="1.0",
        )

        # 3. Run async webhook sender properly
        anyio.run(notify_webhooks,event)

        print("Webhooks sent")

    except Exception as e:
        print(e)
        raise self.retry(countdown=5 * (2 ** self.request.retries))