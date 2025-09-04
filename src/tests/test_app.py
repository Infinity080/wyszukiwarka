from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
import pytest
from unittest.mock import AsyncMock
import pandas as pd

class QdrantCollection:
    def __init__(self):
        self.points_count = 0

class MockAIState:
    def __init__(self, qdrant_client, redis_client):
        self.qdrant_client = qdrant_client
        self.redis_client = redis_client
        self.texts = pd.DataFrame()
        self.model = None

class MockAIService:
    def __init__(self):
        self.qdrant_client = AsyncMock()
        self.redis_client = AsyncMock()

        self.qdrant_client.get_collection = AsyncMock(return_value=QdrantCollection())

        self.ai = MockAIState(self.qdrant_client, self.redis_client) # reuse clients

class MockRedis:
    def __init__(self):
        self.data = {}
    async def ping(self):
        return True
    async def lpush(self, name, value):
        value = value.encode() # ensure value is bytes (just like redis)
        self.data.setdefault(name, []).insert(0, value)
    async def lrange(self, name, start, end):
        return self.data.get(name, [])[start:end+1]

@pytest.fixture(scope="session")
def mock_redis():
    return MockRedis()

@pytest.fixture(scope="session")
async def mock_client(mock_redis):
    mock_service = MockAIService()
    app.state.ai = mock_service.ai
    app.state.qdrant_client = mock_service.qdrant_client
    app.state.redis_client = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session") # shared ingested client to limit /ingest calls
async def ingested_client(mock_client):
    await mock_client.post("/ingest")
    yield mock_client

# test endpoints
@pytest.mark.asyncio
async def test_healthz(mock_client):
    response = await mock_client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["qdrant"] == "ok"
    assert data["redis"] == "ok"

@pytest.mark.asyncio
@pytest.mark.parametrize("k", [1, 5, 15])
async def test_search_k(mock_client, k):
    response = await mock_client.get("/search", params={"q": "random q", "k": k})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= k

@pytest.mark.asyncio
@pytest.mark.parametrize("k", [0, -1, -10, 1.5, 100])
async def test_search_bad_k(mock_client, k):
    response = await mock_client.get("/search", params={"q": "random q", "k": k})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_search_no_params(mock_client):
    response = await mock_client.get("/search")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_stats_before_ingest(mock_client):
    response = await mock_client.get("/stats")
    assert response.status_code == 200
    data = response.json() 
    assert data["stats"] == {}

@pytest.mark.asyncio
async def test_ingest(mock_client): # keep test_ingest isolated to truly test the endpoint
    old_ai = app.state.ai
    response = await mock_client.post("/ingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ingest finished"
    assert app.state.ai != old_ai

@pytest.mark.asyncio
async def test_stats_after_ingest(ingested_client):
    if app.state.ai: # after ingest = ai is initialized
        response = await ingested_client.get("/stats")
        assert response.status_code == 200
        data = response.json() 
        assert data["stats"]["document_count"] > 0
        assert data["stats"]["avg_document_length"] > 0
        assert data["stats"]["unique_authors"] > 0

@pytest.mark.asyncio
async def test_doc(ingested_client):
    response = await ingested_client.get("/doc/0")
    assert response.status_code == 200
    data = response.json()
    assert len(data.keys()) > 0

@pytest.mark.asyncio
async def test_recent_queries(ingested_client):
    _ = await ingested_client.get("/search", params={"q": "test q", "k": 1})
    response = await ingested_client.get("/queries/recent", params={"limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert len(data) <= 5 

@pytest.mark.asyncio
async def test_recent_queries_order(ingested_client):
    await ingested_client.get("/search", params={"q": "query 1", "k": 1})
    await ingested_client.get("/search", params={"q": "query 2", "k": 1})
    await ingested_client.get("/search", params={"q": "query 3", "k": 1})

    response = await ingested_client.get("/queries/recent", params={"limit": 3})
    assert response.status_code == 200
    data = response.json()

    queries = [q.split(":")[1] for q in data["queries"]] # strip from the timestamp
    assert queries == ["query 3", "query 2", "query 1"]