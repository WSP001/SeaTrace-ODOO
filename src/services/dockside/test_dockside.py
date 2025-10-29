"""Pytest tests for DockSide service"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.dockside.main import app
from services.dockside.storage import storage

client = TestClient(app)


@pytest.fixture(autouse=True)
async def clear_storage():
    """Clear storage before each test"""
    await storage.clear_all()
    yield
    await storage.clear_all()


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "dockside"
    assert "storage" in data
    assert data["storage"]["mode"] == "memory"


def test_store_packet():
    """Test storing a validated packet"""
    request_data = {
        "packet_id": "test-001",
        "correlation_id": "corr-001",
        "vessel_data": {
            "vessel_id": "WSP-001",
            "catch_weight": 500.0,
            "species": "Tuna",
            "verified": True
        },
        "validation_passed": True,
        "enriched_data": {"enriched": True}
    }
    
    response = client.post("/api/v1/store", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "stored"
    assert data["packet_id"] == "test-001"
    assert "storage_location" in data


def test_store_invalid_packet():
    """Test rejection of unvalidated packet"""
    request_data = {
        "packet_id": "test-002",
        "correlation_id": "corr-002",
        "vessel_data": {
            "vessel_id": "WSP-002",
            "catch_weight": 100.0,
            "species": "Salmon"
        },
        "validation_passed": False  # Not validated
    }
    
    response = client.post("/api/v1/store", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


def test_retrieve_packet():
    """Test retrieving a stored packet"""
    # First store a packet
    store_data = {
        "packet_id": "test-003",
        "correlation_id": "corr-003",
        "vessel_data": {
            "vessel_id": "WSP-003",
            "catch_weight": 250.0,
            "species": "Cod",
            "verified": True
        },
        "validation_passed": True
    }
    client.post("/api/v1/store", json=store_data)
    
    # Retrieve it
    response = client.get("/api/v1/retrieve/test-003")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "found"
    assert data["found"] is True
    assert data["data"]["vessel_id"] == "WSP-003"


def test_retrieve_nonexistent_packet():
    """Test retrieving a packet that doesn't exist"""
    response = client.get("/api/v1/retrieve/nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_found"
    assert data["found"] is False
    assert data["data"] is None


def test_query_packets():
    """Test querying stored packets"""
    # Store multiple packets
    for i in range(3):
        client.post("/api/v1/store", json={
            "packet_id": f"test-query-{i}",
            "correlation_id": f"corr-{i}",
            "vessel_data": {
                "vessel_id": "WSP-001",
                "catch_weight": 100.0 * (i + 1),
                "species": "Tuna",
                "verified": True
            },
            "validation_passed": True
        })
    
    # Query by vessel
    response = client.post("/api/v1/query", json={
        "vessel_id": "WSP-001",
        "limit": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["returned_count"] == 3


def test_storage_stats():
    """Test storage statistics"""
    # Store some packets
    client.post("/api/v1/store", json={
        "packet_id": "stats-001",
        "correlation_id": "corr-001",
        "vessel_data": {
            "vessel_id": "WSP-001",
            "catch_weight": 500.0,
            "species": "Tuna",
            "verified": True
        },
        "validation_passed": True
    })
    
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_packets"] == 1
    assert data["verified_packets"] == 1
    assert "species_breakdown" in data


def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "storage_mode" in data
    assert "total_packets" in data


def test_correlation_id_propagation():
    """Test correlation ID propagation"""
    response = client.get(
        "/health",
        headers={"X-Correlation-ID": "test-correlation-123"}
    )
    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == "test-correlation-123"
