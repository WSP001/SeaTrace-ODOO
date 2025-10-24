"""
Public Vessel Packet Model

This represents the PUBLIC CHAIN output from Claim 1 (Vessel Admission).
When SeaSide receives vessel PING, the packet switching handler FORKS:
  - PUBLIC CHAIN: This model (general location, certifications)
  - PRIVATE CHAIN: Investor prospectus model (precise GPS, registration)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PublicVesselPacket(BaseModel):
    """
    Public vessel identity packet - Commons Good license.
    
    This is the "public PING packet" created by the SeaSide packet 
    switching handler (Claim 1: Vessel Admission & PING Routing).
    """
    
    # Packet Metadata
    packet_id: str = Field(
        ...,
        description="Unique PING packet identifier",
        example="PING-2025-BW-001"
    )
    
    packet_type: str = Field(
        "VESSEL_PING",
        description="Packet type for routing",
        example="VESSEL_PING"
    )
    
    # Public Vessel Identity
    vessel_public_id: str = Field(
        ...,
        description="Public vessel identifier (NOT registration number)",
        example="bl-001"
    )
    
    vessel_name: str = Field(
        ...,
        description="Vessel name (public knowledge)",
        example="Bluewave Endeavor"
    )
    
    # Location (General, NOT Precise GPS)
    general_location: str = Field(
        ...,
        description="General fishing area (NOT precise coordinates)",
        example="Eastern Pacific, FAO 77"
    )
    
    last_ping_ts: datetime = Field(
        ...,
        description="Timestamp of last GPS ping (public)"
    )
    
    # Certifications (Public)
    certifications: list[str] = Field(
        default_factory=list,
        description="Public certifications (MSC, FairTrade, etc.)",
        example=["MSC", "FairTrade"]
    )
    
    # Operational Status (Public)
    active_status: str = Field(
        "ACTIVE",
        description="Vessel operational status",
        example="ACTIVE"
    )
    
    # Compliance Flags (Public)
    vms_compliant: bool = Field(
        True,
        description="Vessel Monitoring System compliance"
    )
    
    observer_program: Optional[str] = Field(
        None,
        description="Observer program participation",
        example="NMFS West Coast Groundfish"
    )
    
    # PING Routing Metadata
    next_packet_type: str = Field(
        "CATCH",
        description="Expected next packet type in chain",
        example="CATCH"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "packet_id": "PING-2025-BW-001",
                "packet_type": "VESSEL_PING",
                "vessel_public_id": "bl-001",
                "vessel_name": "Bluewave Endeavor",
                "general_location": "Eastern Pacific, FAO 77",
                "last_ping_ts": "2025-10-23T10:15:00Z",
                "certifications": ["MSC", "FairTrade"],
                "active_status": "ACTIVE",
                "vms_compliant": True,
                "observer_program": "NMFS West Coast Groundfish",
                "next_packet_type": "CATCH"
            }
        }
