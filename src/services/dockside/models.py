"""Pydantic data models for DockSide service"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class StoredPacket(BaseModel):
    """Packet data stored in DockSide"""
    packet_id: str
    correlation_id: str
    vessel_id: str
    catch_weight: float
    species: str
    location: Optional[Dict[str, float]] = None
    verified: bool = False
    validated: bool = False
    enriched_data: Optional[Dict[str, Any]] = None
    stored_at: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "deckside"

class StoreRequest(BaseModel):
    """Request to store a validated packet"""
    packet_id: str
    correlation_id: str
    vessel_data: Dict[str, Any]
    validation_passed: bool
    enriched_data: Optional[Dict[str, Any]] = None

class StoreResponse(BaseModel):
    """Response after storing a packet"""
    status: str = Field(..., pattern="^(stored|rejected|error)$")
    packet_id: str
    correlation_id: str
    stored_at: datetime = Field(default_factory=datetime.utcnow)
    storage_location: Optional[str] = None

class RetrieveResponse(BaseModel):
    """Response when retrieving a packet"""
    status: str
    packet_id: str
    correlation_id: str
    data: Optional[StoredPacket] = None
    found: bool

class QueryRequest(BaseModel):
    """Request to query stored packets"""
    vessel_id: Optional[str] = None
    species: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    verified_only: bool = False
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

class QueryResponse(BaseModel):
    """Response from packet query"""
    status: str
    correlation_id: str
    total_count: int
    returned_count: int
    packets: List[StoredPacket]

class StorageStats(BaseModel):
    """Storage statistics"""
    total_packets: int
    verified_packets: int
    unverified_packets: int
    total_catch_weight: float
    species_breakdown: Dict[str, int]
    storage_utilization: float  # Percentage
    oldest_packet_date: Optional[datetime] = None
    newest_packet_date: Optional[datetime] = None
