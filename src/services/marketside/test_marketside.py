"""Pytest tests for MarketSide service"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.marketside.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "marketside"
    assert "features" in data


def test_publish_listing():
    """Test publishing a market listing"""
    request_data = {
        "packet_id": "test-001",
        "correlation_id": "corr-001",
        "publish_type": "listing",
        "data": {
            "vessel_id": "WSP-001",
            "product": "Tuna",
            "weight_kg": 500,
            "price_per_kg": 15.00
        },
        "signature_required": True
    }
    
    response = client.post("/api/v1/publish", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["packet_id"] == "test-001"
    assert data["signature"] is not None


def test_publish_transaction():
    """Test publishing a market transaction"""
    request_data = {
        "packet_id": "test-002",
        "correlation_id": "corr-002",
        "publish_type": "transaction",
        "data": {
            "buyer": "Restaurant A",
            "seller": "WSP-001",
            "amount": 7500.00
        },
        "signature_required": True
    }
    
    response = client.post("/api/v1/publish", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"


def test_publish_certificate():
    """Test publishing a certificate"""
    request_data = {
        "packet_id": "test-003",
        "correlation_id": "corr-003",
        "publish_type": "certificate",
        "data": {
            "vessel_id": "WSP-001",
            "traceability_chain": []
        },
        "signature_required": True
    }
    
    response = client.post("/api/v1/publish", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["signature"] is not None


def test_verify_valid_pm_token():
    """Test verifying a valid PM token"""
    request_data = {
        "token": "PM-MARK-2024-004",
        "requested_access": "dashboard"
    }
    
    response = client.post("/api/v1/pm/verify", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["access_level"] == "Investors (Full Access)"
    assert "marketside" in data["pillar_access"]


def test_verify_invalid_pm_token():
    """Test verifying an invalid PM token"""
    request_data = {
        "token": "INVALID-TOKEN",
        "requested_access": "dashboard"
    }
    
    response = client.post("/api/v1/pm/verify", json=request_data)
    assert response.status_code == 401


def test_list_pm_tokens():
    """Test listing PM tokens"""
    response = client.get("/api/v1/pm/tokens")
    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert len(data["tokens"]) == 4


def test_issue_certificate():
    """Test issuing a traceability certificate"""
    request_data = {
        "packet_id": "cert-001",
        "correlation_id": "corr-cert-001",
        "vessel_id": "WSP-001",
        "include_full_chain": True
    }
    
    response = client.post("/api/v1/certificate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "issued"
    assert data["vessel_id"] == "WSP-001"
    assert data["signature"] is not None
    assert len(data["traceability_chain"]) > 0


def test_get_stats():
    """Test getting market statistics"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data
    assert "total_listings" in data
    assert "total_certificates" in data


def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_published" in data


def test_correlation_id_propagation():
    """Test correlation ID propagation"""
    response = client.get(
        "/health",
        headers={"X-Correlation-ID": "test-correlation-123"}
    )
    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == "test-correlation-123"
