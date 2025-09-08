from fastapi import FastAPI, Request
from api.endpoints import router
from api.clients import qdrant_client, redis_client, setup_qdrant_collection
from ai import AIService
from logger import logger
import time
from datetime import datetime, timedelta, timezone

# setup
app = FastAPI()
app.include_router(router)

@app.middleware("http")
async def log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    logger.info(
        "Request handled",
        extra={
            "timestamp": datetime.now(timezone(timedelta(hours=2))).isoformat(),
            "request_path": request.url.path,
            "status_code": response.status_code,
            "method": request.method,
            "duration": end_time - start_time
        }
    )
    return response

@app.on_event("startup")
async def main():
    # setup
    await setup_qdrant_collection("main", 384, "COSINE")
    # dependency injection
    app.state.ai = AIService("all-MiniLM-L6-v2", "main", qdrant_client) # not calling create yet, only on /ingest
    app.state.qdrant_client = qdrant_client
    app.state.redis_client = redis_client
