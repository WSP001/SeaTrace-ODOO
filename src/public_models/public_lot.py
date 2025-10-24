"""
Public Lot Packet Model

This represents the PUBLIC CHAIN output from Claim 3 (Building Lot Aggregation).
When DockSide reconciles catch into storage lots, the packet switching handler FORKS:
  - PUBLIC CHAIN: This model (BBSS lot number, HACCP status)
  - PRIVATE CHAIN: Investor prospectus model (detailed inventory, margins)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PublicLotPacket(BaseModel):
    """
    Public lot reconciliation packet - Commons Good license.
    
    This is the "public lot aggregation packet" created by the DockSide 
    packet switching handler (Claim 3: Building Lot Aggregation).
    """
    
    # Packet Metadata
    packet_id: str = Field(
        ...,
        description="Unique lot packet identifier",
        example="LOT-2025-BBSS-001"
    )
    
    packet_type: str = Field(
        "LOT_RECONCILIATION",
        description="Packet type for routing",
        example="LOT_RECONCILIATION"
    )
    
    parent_packet_id: str = Field(
        ...,
        description="Parent catch packet (traceability link)",
        example="CATCH-2025-BW-001"
    )
    
    # Lot Identity (BBSS Format)
    lot_number: str = Field(
        ...,
        description="BlueBlue Storage System lot number",
        example="BBSS-2025-1019-001",
        pattern=r"^BBSS-\d{4}-\d{4}-\d{3}$"
    )
    
    # Aggregated Catch Data
    total_weight_kg: float = Field(
        ...,
        description="Total lot weight in kilograms",
        example=450.5,
        gt=0
    )
    
    species_common_name: str = Field(
        ...,
        description="Species common name",
        example="Yellowfin Tuna"
    )
    
    # Storage Facility (Public)
    storage_facility: str = Field(
        ...,
        description="Cold storage facility name",
        example="BlueBlue Cold Storage - San Diego"
    )
    
    storage_ts: datetime = Field(
        ...,
        description="Timestamp when lot entered storage"
    )
    
    # Temperature Monitoring (Public Flag Only)
    temp_logs_available: bool = Field(
        False,
        description="Temperature logs available for verification"
    )
    
    avg_storage_temp_celsius: Optional[float] = Field(
        None,
        description="Average storage temperature (°C)",
        example=-18.2,
        le=0
    )
    
    # HACCP Compliance (Public)
    haccp_status: str = Field(
        "PENDING",
        description="HACCP compliance status",
        example="APPROVED"
    )
    
    haccp_approval_date: Optional[str] = Field(
        None,
        description="HACCP approval date (if approved)",
        example="2025-10-23"
    )
    
    # Traceability (QR Codes Generated)
    qr_codes: list[str] = Field(
        default_factory=list,
        description="Generated QR codes for consumer scanning",
        example=["QR-2025-001", "QR-2025-002"]
    )
    
    # Processing Metadata
    processing_type: str = Field(
        "WHOLE_FROZEN",
        description="Processing type applied",
        example="WHOLE_FROZEN"
    )
    
    # BONE File Reference (Public Ledger)
    bone_file_available: bool = Field(
        False,
        description="BONE (Blockchain Ocean Network Exchange) file available"
    )
    
    # Chain-of-Custody
    next_packet_type: str = Field(
        "VERIFICATION",
        description="Expected next packet type (MarketSide QR scan)",
        example="VERIFICATION"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "packet_id": "LOT-2025-BBSS-001",
                "packet_type": "LOT_RECONCILIATION",
                "parent_packet_id": "CATCH-2025-BW-001",
                "lot_number": "BBSS-2025-1019-001",
                "total_weight_kg": 450.5,
                "species_common_name": "Yellowfin Tuna",
                "storage_facility": "BlueBlue Cold Storage - San Diego",
                "storage_ts": "2025-10-23T15:30:00Z",
                "temp_logs_available": True,
                "avg_storage_temp_celsius": -18.2,
                "haccp_status": "APPROVED",
                "haccp_approval_date": "2025-10-23",
                "qr_codes": ["QR-2025-001", "QR-2025-002"],
                "processing_type": "WHOLE_FROZEN",
                "bone_file_available": True,
                "next_packet_type": "VERIFICATION"
            }
        }
