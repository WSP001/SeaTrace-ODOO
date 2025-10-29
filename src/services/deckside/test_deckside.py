"""Pytest tests for DeckSide service"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.deckside.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "deckside"
    assert "correlation_id" in data


def test_process_valid_packet():
    """Test processing a valid packet"""
    request_data = {
        "packet_id": "test-001",
        "correlation_id": "corr-001",
        "vessel_data": {
            "vessel_id": "WSP-001",
            "catch_weight": 500.0,
            "species": "Tuna",
            "location": {
                "latitude": 10.5,
                "longitude": 20.3
            }
        },
        "verified": True
    }
    
    response = client.post("/api/v1/process", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["packet_id"] == "test-001"
    assert data["validation_results"]["valid"] is True


def test_process_invalid_species():
    """Test rejection of invalid species"""
    request_data = {
        "packet_id": "test-002",
        "correlation_id": "corr-002",
        "vessel_data": {
            "vessel_id": "WSP-002",
            "catch_weight": 100.0,
            "species": "Dragon",  # Invalid species
        },
        "verified": True
    }
    
    response = client.post("/api/v1/process", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["validation_results"]["valid"] is False
    assert len(data["validation_results"]["errors"]) > 0


def test_validate_endpoint():
    """Test standalone validation"""
    vessel_data = {
        "vessel_id": "WSP-003",
        "catch_weight": 250.0,
        "species": "Salmon"
    }
    
    response = client.post("/api/v1/validate", json=vessel_data)
    assert response.status_code == 200
    data = response.json()
    assert "validation_results" in data


def test_correlation_id_propagation():
    """Test that correlation IDs are propagated"""
    response = client.get(
        "/health",
        headers={"X-Correlation-ID": "test-correlation-123"}
    )
    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == "test-correlation-123"


def test_metrics_endpoint():
    """Test metrics endpoint exists"""
    response = client.get("/metrics")
    assert response.status_code == 200
