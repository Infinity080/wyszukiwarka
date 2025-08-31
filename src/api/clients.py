import redis.asyncio as redis
from qdrant_client.async_qdrant_client import AsyncQdrantClient
import os
from qdrant_client.models import Distance, VectorParams

redis_client: redis.Redis = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0
)

qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333)),
    timeout=60.0
)

async def setup_qdrant_collection(collection_name: str, vec_size: int, metric: str = "COSINE") -> None:
    await qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vec_size, distance=Distance[metric])
    )
