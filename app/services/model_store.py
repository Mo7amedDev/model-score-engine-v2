from pydantic import BaseModel
from typing import List
import httpx
import redis 
import os 
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

r = redis.Redis(host=os.getenv('REDIS_HOST'),port=6379,db=0,decode_responses=True) 

def is_valid_url(url: str):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.netloc


def add_webhook(url: str):
    if not is_valid_url(url):
        raise ValueError("Invalid URL")
    r.sadd("webhooks", url)

def get_webhooks():
    return list(r.smembers('webhooks'))

def remove_webhook(url:str):
    removed = r.srem("webhooks", url)
    return bool(removed)

 
class WebhookEvent(BaseModel):
    event: str   # "models.updated"
    version: str
    changed_models: List[str] = []
    
 
# model_store.py

async def notify_webhooks(event: WebhookEvent):
    async with httpx.AsyncClient() as client:
        urls = get_webhooks()
        print(urls, '++++++++++++++=============+++++++++++++=======+++++====')

        for url in urls:
            fail_count_key = f"fail:{url}"

            try:
                res = await client.post(
                    url,
                    json=event.model_dump(),
                    timeout=5
                )

                # ✅ Treat non-2xx as failure
                if res.status_code >= 400:
                    r.incr(fail_count_key)
                    print(f"{url} -> FAILED ({res.status_code})")

                else:
                    # ✅ Success → reset counter
                    r.delete(fail_count_key)
                    print(f"{url} -> SUCCESS ({res.status_code})")

            except Exception as e:
                r.incr(fail_count_key)
                print(f"Failed {url}: {e}")

            # ✅ Remove after threshold
            if int(r.get(fail_count_key) or 0) > 5:
                remove_webhook(url)
                r.delete(fail_count_key)  # cleanup
                print(f"{url} removed after repeated failures")