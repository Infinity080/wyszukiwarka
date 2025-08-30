from fastapi import FastAPI
from api.endpoints import router
from api.clients import qdrant_client, redis_client

# setup
app = FastAPI()
app.include_router(router)