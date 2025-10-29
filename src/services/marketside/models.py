"""Pydantic data models for MarketSide service"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class MarketPacket(BaseModel):
    """Market transaction packet"""
    packet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_type: str = Field(..., pattern="^(purchase|sale|transfer|verification)$")
    vessel_id: Optional[str] = None
    product_data: Dict[str, Any]
    buyer_info: Optional[Dict[str, str]] = None
    seller_info: Optional[Dict[str, str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PublishRequest(BaseModel):
    """Request to publish data to market"""
    packet_id: str
    correlation_id: str
    publish_type: str = Field(..., pattern="^(listing|transaction|certificate)$")
    data: Dict[str, Any]
    signature_required: bool = True

class PublishResponse(BaseModel):
    """Response after publishing to market"""
    status: str = Field(..., pattern="^(published|pending|rejected)$")
    packet_id: str
    correlation_id: str
    published_at: datetime = Field(default_factory=datetime.utcnow)
    signature: Optional[str] = None  # PRIVATE KEY OUTGOING
    market_url: Optional[str] = None

class PMTokenRequest(BaseModel):
    """PM Token verification request"""
    token: str = Field(..., min_length=10)
    requested_access: str = Field(default="dashboard")

class PMTokenResponse(BaseModel):
    """PM Token verification response"""
    valid: bool
    token: str
    access_level: Optional[str] = None
    pillar_access: List[str] = []
    dashboard_url: Optional[str] = None
    expires_at: Optional[datetime] = None

class MarketStats(BaseModel):
    """Market statistics"""
    total_transactions: int
    total_listings: int
    total_certificates: int
    active_vessels: int
    total_volume_kg: float
    top_species: Dict[str, int]

class CertificateRequest(BaseModel):
    """Request for traceability certificate"""
    packet_id: str
    correlation_id: str
    vessel_id: str
    include_full_chain: bool = True

class CertificateResponse(BaseModel):
    """Traceability certificate response"""
    status: str
    certificate_id: str
    packet_id: str
    correlation_id: str
    vessel_id: str
    traceability_chain: List[Dict[str, Any]]
    signature: str  # PRIVATE KEY OUTGOING - signed certificate
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
