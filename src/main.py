from fastapi import FastAPI
from api.endpoints import router
from api.clients import qdrant_client, redis_client, setup_qdrant_collection
from ai import AIService

# setup
app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def main():
    # setup
    await setup_qdrant_collection("main", 384, "COSINE")
    # dependency injection
    app.state.ai = AIService("all-MiniLM-L6-v2", "main", qdrant_client) # not calling create yet, only on /ingest
    app.state.qdrant_client = qdrant_client
    app.state.redis_client = redis_client
