import redis.asyncio as redis
from qdrant_client.async_qdrant_client import AsyncQdrantClient as QdrantClient

redis_client = redis.Redis(host="redis", port=6379, db=0)
qdrant_client = QdrantClient(host="qdrant", port=6333)