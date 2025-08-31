from fastapi import Request
from qdrant_client.async_qdrant_client import AsyncQdrantClient
import redis.asyncio as redis
from api.clients import qdrant_client, redis_client
from ai import AIService

def get_ai_service(request: Request) -> AIService:
    return request.app.state.ai

def get_qdrant_client(request: Request) -> AsyncQdrantClient:
    return request.app.state.qdrant_client

def get_redis_client(request: Request) -> redis.Redis:
    return request.app.state.redis_client