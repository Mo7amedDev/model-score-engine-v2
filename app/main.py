from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ranking import router as ranking_router
from app.api.tracking import router as traking_router
from pydantic import BaseModel

app = FastAPI(
    title="ScoreEngine API",
    description="""
AI Model Scoring Engine.

### How to use:
1. Generate weights from a task
2. Rank models using those weights
3. Subscribe to webhook updates

### Features:
- Dynamic model ranking
- Webhook notifications
- Custom filtering
    """
    
    )

# =========================
# CORS (Cross-Origin)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # ⚠️ for dev only (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Routers
# =========================
app.include_router(ranking_router, prefix="/rank", tags=["ranking"])
app.include_router(traking_router,prefix="/track",tags=['track'])

# =========================
# Health check (important for Docker + monitoring)
# =========================
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "scoreengine"
    }

class MODEL_UPDATE(BaseModel):
    event:str
    version:str 


@app.post("/update_models")
def update_models(req:MODEL_UPDATE):
    print('updated models thanks!')
    return True

 
    
''' 
docker start redis || docker run -d -p 6379:6379 redis
celery -A app.services.celery_app.celery beat --loglevel=info
celery -A app.services.tasks worker --loglevel=info
uvicorn app.main:app --reload
'''