from fastapi import APIRouter
from api.clients import qdrant_client, redis_client

router = APIRouter()

# return service status
@router.get("/healthz")
async def healthz() -> dict[str, str]:
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