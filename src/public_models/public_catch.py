"""
Public Catch Packet Model

This represents the PUBLIC CHAIN output from Claim 2 (Enrichment & Forking).
When DeckSide receives captain's e-Log, the packet switching handler FORKS:
  - PUBLIC CHAIN: This model (SIMP-required data for regulators)
  - PRIVATE CHAIN: Investor prospectus model (not in public repo)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PublicCatchPacket(BaseModel):
    """
    Public catch data packet - Commons Good license.
    
    This is the "public estimated #CATCH KEY PACKET_ID" created by
    the DeckSide packet switching handler (Claim 2: Enrichment & Forking).
    """
    
    # Packet Metadata
    packet_id: str = Field(
        ...,
        description="Unique packet identifier (public-facing)",
        example="CATCH-2025-BW-001"
    )
    
    parent_packet_id: Optional[str] = Field(
        None,
        description="Link to parent SeaSide PING packet (for chain traversal)",
        example="PING-2025-BW-001"
    )
    
    # Public Vessel Info
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
    
    # Catch Data (SIMP-Required)
    species_common_name: str = Field(
        ...,
        description="Common species name (NOT scientific name for now)",
        example="Yellowfin Tuna"
    )
    
    weight_kg: float = Field(
        ...,
        description="Total landed weight in kilograms",
        example=450.5,
        gt=0
    )
    
    catch_area_general: str = Field(
        ...,
        description="General fishing area (NOT precise coordinates)",
        example="Eastern Pacific, FAO 77"
    )
    
    landed_ts: datetime = Field(
        ...,
        description="Timestamp when catch was landed at port"
    )
    
    # Compliance Flags (Public)
    compliance_status: str = Field(
        "PENDING",
        description="Regulatory compliance status",
        example="VERIFIED"
    )
    
    er_report_submitted: bool = Field(
        False,
        description="Electronic Report submission flag"
    )
    
    # Chain-of-Custody (Public)
    fish_ticket_id: Optional[str] = Field(
        None,
        description="Government-issued fish ticket number",
        example="CA-2025-12345"
    )
    
    port_of_landing: str = Field(
        ...,
        description="Port where catch was landed",
        example="San Diego, CA"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "packet_id": "CATCH-2025-BW-001",
                "parent_packet_id": "PING-2025-BW-001",
                "vessel_public_id": "bl-001",
                "vessel_name": "Bluewave Endeavor",
                "species_common_name": "Yellowfin Tuna",
                "weight_kg": 450.5,
                "catch_area_general": "Eastern Pacific, FAO 77",
                "landed_ts": "2025-10-21T14:30:00Z",
                "compliance_status": "VERIFIED",
                "er_report_submitted": True,
                "fish_ticket_id": "CA-2025-12345",
                "port_of_landing": "San Diego, CA"
            }
        }
