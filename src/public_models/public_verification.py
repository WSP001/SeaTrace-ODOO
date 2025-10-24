"""
Public Verification Packet Model

This represents the PUBLIC CHAIN output from Claim 4 (Consumer Trust & Payment).
When MarketSide receives QR scan request, the packet switching handler returns:
  - PUBLIC CHAIN: This model (full traceability for consumers)
  - PRIVATE CHAIN: Investor prospectus model (payment details, margins)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PublicVerificationPacket(BaseModel):
    """
    Public QR verification response - Commons Good license.
    
    This is the "public verification packet" returned by the MarketSide
    packet switching handler (Claim 4: Consumer Trust & Payment).
    
    This model provides COMPLETE TRACEABILITY for consumers scanning
    QR codes, showing the full chain from ocean to table.
    """
    
    # Verification Metadata
    verification_id: str = Field(
        ...,
        description="Unique verification transaction ID",
        example="VERIFY-2025-001"
    )
    
    packet_type: str = Field(
        "CONSUMER_VERIFICATION",
        description="Packet type for routing",
        example="CONSUMER_VERIFICATION"
    )
    
    qr_code: str = Field(
        ...,
        description="Scanned QR code identifier",
        example="QR-2025-001"
    )
    
    verified_ts: datetime = Field(
        ...,
        description="Timestamp of QR scan verification"
    )
    
    # === FULL TRACEABILITY CHAIN ===
    
    # Origin: SeaSide (HOLD)
    vessel_name: str = Field(
        ...,
        description="Origin vessel name",
        example="Bluewave Endeavor"
    )
    
    vessel_certifications: list[str] = Field(
        default_factory=list,
        description="Vessel certifications",
        example=["MSC", "FairTrade"]
    )
    
    # Catch: DeckSide (RECORD)
    species_common_name: str = Field(
        ...,
        description="Species common name",
        example="Yellowfin Tuna"
    )
    
    catch_area_general: str = Field(
        ...,
        description="General catch area (NOT precise GPS)",
        example="Eastern Pacific, FAO 77"
    )
    
    landed_date: str = Field(
        ...,
        description="Date catch was landed at port",
        example="2025-10-21"
    )
    
    catch_weight_kg: float = Field(
        ...,
        description="Original catch weight (kg)",
        example=450.5,
        gt=0
    )
    
    # Storage: DockSide (STORE)
    lot_number: str = Field(
        ...,
        description="BlueBlue Storage System lot number",
        example="BBSS-2025-1019-001"
    )
    
    storage_facility: str = Field(
        ...,
        description="Cold storage facility",
        example="BlueBlue Cold Storage - San Diego"
    )
    
    processing_type: str = Field(
        ...,
        description="Processing type applied",
        example="WHOLE_FROZEN"
    )
    
    avg_storage_temp_celsius: Optional[float] = Field(
        None,
        description="Average storage temperature (°C)",
        example=-18.2
    )
    
    # === COMPLIANCE & CERTIFICATION ===
    
    compliance_status: str = Field(
        "VERIFIED",
        description="Overall compliance status",
        example="VERIFIED"
    )
    
    er_report_submitted: bool = Field(
        False,
        description="Electronic Report submitted to regulators"
    )
    
    haccp_status: str = Field(
        "APPROVED",
        description="HACCP compliance status",
        example="APPROVED"
    )
    
    # === CONSUMER TRUST METRICS ===
    
    trust_score: float = Field(
        ...,
        description="Consumer trust score (0-100, higher is better)",
        example=98.5,
        ge=0,
        le=100
    )
    
    verification_count: int = Field(
        1,
        description="Number of times this QR has been scanned",
        example=1,
        ge=1
    )
    
    # === BLOCKCHAIN PROOF (Optional) ===
    
    blockchain_anchored: bool = Field(
        False,
        description="Whether traceability is anchored to blockchain"
    )
    
    blockchain_hash: Optional[str] = Field(
        None,
        description="Blockchain anchor hash (if available)",
        example="0x1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890"
    )
    
    blockchain_network: Optional[str] = Field(
        None,
        description="Blockchain network (if anchored)",
        example="Ethereum"
    )
    
    # === COMMONS FUND CONTRIBUTION ===
    
    commons_fund_eligible: bool = Field(
        True,
        description="Whether this transaction contributes to Commons Fund"
    )
    
    commons_fund_percentage: Optional[float] = Field(
        None,
        description="Percentage of transaction supporting Commons Fund",
        example=12.5,
        ge=0,
        le=100
    )
    
    # === PACKET ROUTING ===
    
    parent_packets: dict[str, str] = Field(
        default_factory=dict,
        description="Parent packet IDs for full chain traversal",
        example={
            "ping": "PING-2025-BW-001",
            "catch": "CATCH-2025-BW-001",
            "lot": "LOT-2025-BBSS-001"
        }
    )
    
    verification_url: str = Field(
        ...,
        description="Public URL for verification details",
        example="https://seatrace.worldseafoodproducers.com/verify/QR-2025-001"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "verification_id": "VERIFY-2025-001",
                "packet_type": "CONSUMER_VERIFICATION",
                "qr_code": "QR-2025-001",
                "verified_ts": "2025-10-23T18:45:00Z",
                "vessel_name": "Bluewave Endeavor",
                "vessel_certifications": ["MSC", "FairTrade"],
                "species_common_name": "Yellowfin Tuna",
                "catch_area_general": "Eastern Pacific, FAO 77",
                "landed_date": "2025-10-21",
                "catch_weight_kg": 450.5,
                "lot_number": "BBSS-2025-1019-001",
                "storage_facility": "BlueBlue Cold Storage - San Diego",
                "processing_type": "WHOLE_FROZEN",
                "avg_storage_temp_celsius": -18.2,
                "compliance_status": "VERIFIED",
                "er_report_submitted": True,
                "haccp_status": "APPROVED",
                "trust_score": 98.5,
                "verification_count": 1,
                "blockchain_anchored": True,
                "blockchain_hash": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890",
                "blockchain_network": "Ethereum",
                "commons_fund_eligible": True,
                "commons_fund_percentage": 12.5,
                "parent_packets": {
                    "ping": "PING-2025-BW-001",
                    "catch": "CATCH-2025-BW-001",
                    "lot": "LOT-2025-BBSS-001"
                },
                "verification_url": "https://seatrace.worldseafoodproducers.com/verify/QR-2025-001"
            }
        }
