from fastapi import FastAPI
from api.endpoints import router
from api.clients import qdrant_client, redis_client, setup_qdrant_collection
from ai import AIService

# setup
app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def main():
    # health checks
    from api.endpoints import healthz
    await healthz()

    # setup
    await setup_qdrant_collection("main", 384, "COSINE")
    ai = await AIService.create("all-MiniLM-L6-v2", "main")
