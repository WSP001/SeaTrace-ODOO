"""
🏈 SeaTrace Health & Metrics Tests
For the Commons Good! 🌊
"""

import httpx
import pytest

PILLARS = [
    (8001, "seaside"),
    (8002, "deckside"),
    (8003, "dockside"),
    (8004, "marketside")
]

@pytest.mark.parametrize("port,pillar", PILLARS)
@pytest.mark.asyncio
async def test_health(port, pillar):
    """Test health endpoint for each pillar"""
    async with httpx.AsyncClient(base_url=f"http://localhost:{port}") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert data.get("pillar") == pillar

@pytest.mark.parametrize("port,pillar", PILLARS)
@pytest.mark.asyncio
async def test_metrics(port, pillar):
    """Test metrics endpoint for each pillar"""
    async with httpx.AsyncClient(base_url=f"http://localhost:{port}") as client:
        response = await client.get("/metrics")
        assert response.status_code == 200
        assert f"seatrace_{pillar}_requests_total" in response.text

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns service info"""
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "pillar" in data
        assert "role" in data
        assert "endpoints" in data

@pytest.mark.asyncio
async def test_kpi_endpoint():
    """Test KPI endpoint returns metrics"""
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.get("/kpi")
        assert response.status_code == 200
        data = response.json()
        assert "transparency" in data
        assert "compliance" in data
        assert "equity" in data
        assert "climate" in data
