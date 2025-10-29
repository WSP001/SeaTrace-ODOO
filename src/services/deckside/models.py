"""Pydantic data models for DeckSide service"""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class LocationData(BaseModel):
    """GPS location information"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: Optional[datetime] = None

class VesselData(BaseModel):
    """Vessel catch data"""
    vessel_id: str = Field(..., min_length=1, max_length=50)
    catch_weight: float = Field(..., gt=0)
    species: str = Field(..., min_length=1, max_length=100)
    location: Optional[LocationData] = None
    timestamp: Optional[datetime] = None
    
    @validator("catch_weight")
    def validate_weight(cls, v):
        if v > 1000000:  # Max 1M kg catch
            raise ValueError("Catch weight exceeds maximum (1,000,000 kg)")
        return v

class ProcessRequest(BaseModel):
    """Request to process a vessel packet"""
    packet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vessel_data: VesselData
    verified: bool = False
    source_service: str = "seaside"

class ValidationError(BaseModel):
    """Individual validation error"""
    field: str
    message: str
    code: str

class ValidationResult(BaseModel):
    """Result of data validation"""
    valid: bool
    errors: List[ValidationError] = []
    warnings: List[str] = []

class ProcessResponse(BaseModel):
    """Response after processing a packet"""
    status: str = Field(..., pattern="^(processed|rejected|pending)$")
    packet_id: str
    correlation_id: str
    vessel_data_enriched: Optional[Dict] = None
    validation_results: ValidationResult
    next_step: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_duration_ms: float = 0.0
