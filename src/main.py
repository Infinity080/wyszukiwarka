from fastapi import FastAPI
import redis.asyncio as redis
from qdrant_client.async_qdrant_client import AsyncQdrantClient as QdrantClient
import requests

# setup
app = FastAPI()
redis_client = redis.Redis(host="redis", port=6379, db=0)
qdrant_client = QdrantClient(host="qdrant", port=6333)

# return service status
@app.get("/healthz")
async def healthz():
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



"""
GET /healthz – stan usługi.
POST /ingest – przyjmuje dane, tworzy embeddingi, zapisuje do bazy wektorowej.
GET /search?q=...&k=10&filter_lang=... – zwraca top-K wyników (id, text, score, metadata).
Wymagane: każdorazowo zapisz zapytanie (q) w Redisie w kolejności
wysłania (np. z timestampe).
GET /doc/{id} – zwraca pojedynczy dokument z metadanymi.
GET /queries/recent?limit=50 – zwraca ostatnie zarejestrowane zapytania w odwrotnej
kolejności (od najnowszych).
GET /stats – podstawowe statystyki (np. liczba dokumentów, średnia długość
dokumentów)
"""