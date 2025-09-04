from fastapi import APIRouter, Depends, Request, Query
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


@router.get("/search")
async def search( # use Query for easier testing
    q: str = Query(min_length=3, max_length=50),
    k: int = Query(10, ge=1, le=20),
    ai: AIService = Depends(get_ai_service),
    redis_client = Depends(get_redis_client)
) -> dict:
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

@router.get("/doc/{id}")
def get_doc(id: int, ai: AIService = Depends(get_ai_service)) -> dict | None:
    if "id" not in ai.texts.columns:
        return None

    doc = ai.texts[ai.texts["id"] == id]

    if doc.empty: 
        return None
    return doc.iloc[0].to_dict()
    
@router.get("/queries/recent")
async def recent_queries(limit: int = 5, redis_client = Depends(get_redis_client)) -> dict:
    recent = await redis_client.lrange("queries", 0, limit - 1)
    if not recent:
        return {"queries": []}
    return {"queries" : [i.decode() for i in recent]} 

@router.get("/stats")
def stats(ai: AIService = Depends(get_ai_service)) -> dict:
    if ai.texts.empty:
        return {"stats": {}}
    document_count = len(ai.texts)
    avg_document_length = ai.texts["text"].apply(len).mean()
    unique_authors = ai.texts["metadata"].apply(lambda x: x.get("author")).nunique()

    return {"stats": {
        "document_count": document_count, "avg_document_length": avg_document_length, "unique_authors": unique_authors
    }}
