from fastapi import APIRouter, Depends, Request
from api.dependencies import get_ai_service, get_qdrant_client, get_redis_client
from ai import AIService

router = APIRouter()

# return service status
@router.get("/healthz")
async def healthz(qdrant_client = Depends(get_qdrant_client), redis_client = Depends(get_redis_client)) -> dict[str, str]:
    try:
        await qdrant_client.info() # version call to health check
        qdrant_health = True  
    except Exception as e:
        print(f"Qdrant failed: {e}")
        qdrant_health = False

    try:
        redis_health = await redis_client.ping()
    except Exception as e:
        print(f"Redis failed: {e}")
        redis_health = False

    status = qdrant_health and redis_health
    return {
        "status": "ok" if status else "error",
        "qdrant": "ok" if qdrant_health else "error",
        "redis": "ok" if redis_health else "error",
    }


@router.post("/search")
async def search(q: str, k: int = 10, ai: AIService = Depends(get_ai_service), redis_client = Depends(get_redis_client)) -> dict:
    if ai.texts.empty:
        return {"results": []}

    similar = await ai.find_k_similar(q, k)

    # save q to redis with score and timestamp
    import time
    timestamp = time.time()
    await redis_client.lpush("queries", f"{timestamp}:{q}") 

    return {"results": similar.to_dict(orient="records")}

@router.post("/ingest")
async def ingest (request: Request, ai: AIService = Depends(get_ai_service)) -> dict:
    # reinstantiate the AIService to load a dataset, create embeddings and save to Qdrant
    new_ai = await AIService.create("all-MiniLM-L6-v2", "main", ai.qdrant_client)
    request.app.state.ai = new_ai

    return {"status" : "ingest finished"}
