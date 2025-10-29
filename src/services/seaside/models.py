# 🌊 SeaSide Pydantic Models
# For the Commons Good!

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class VesselData(BaseModel):
    """Vessel operation data"""
    vessel_id: str = Field(..., description="Unique vessel identifier")
    catch_weight: float = Field(..., gt=0, description="Catch weight in kg")
    species: str = Field(..., description="Species caught")
    location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")


class IncomingPacket(BaseModel):
    """Incoming packet from vessel"""
    correlation_id: str = Field(..., description="Unique correlation ID")
    source: str = Field(..., description="Packet source (e.g., 'vessel')")
    payload: Dict[str, Any] = Field(..., description="Packet payload data")
    signature: Optional[str] = Field(None, description="Base64-encoded signature")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "correlation_id": "uuid-123-456",
                "source": "vessel",
                "payload": {
                    "vessel_id": "WSP-001",
                    "catch_weight": 500.0,
                    "species": "Tuna",
                    "location": {"lat": 10.5, "lon": -60.3}
                },
                "signature": "base64-encoded-signature",
                "timestamp": "2025-01-20T10:00:00Z"
            }
        }


class IngestResponse(BaseModel):
    """Response from packet ingestion"""
    status: str = Field(..., description="Ingestion status")
    packet_id: str = Field(..., description="Assigned packet ID")
    correlation_id: str = Field(..., description="Original correlation ID")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    verified: bool = Field(False, description="Signature verification status")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
