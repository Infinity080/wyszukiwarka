import redis.asyncio as redis
from qdrant_client.async_qdrant_client import AsyncQdrantClient as QdrantClient
import os

redis_client: redis.Redis = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0
)

qdrant_client: QdrantClient = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)