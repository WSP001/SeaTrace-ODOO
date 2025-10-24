"""
Public Chain Pydantic Models
=============================

This package contains PUBLIC-UNLIMITED models for the SeaTrace Four Pillars
packet switching architecture. These models represent the PUBLIC CHAIN outputs
from each claim (Vessel Admission, Enrichment & Forking, Building Lot
Aggregation, Consumer Trust & Payment).

Classification: PUBLIC-UNLIMITED (Commons Good License)
Repository: https://github.com/WSP001/SeaTrace-ODOO

Four Pillars Public Models:
- PublicVesselPacket: SeaSide PING output (Claim 1: Vessel Admission)
- PublicCatchPacket: DeckSide catch validation output (Claim 2: Enrichment)
- PublicLotPacket: DockSide lot reconciliation output (Claim 3: Aggregation)
- PublicVerificationPacket: MarketSide QR verification (Claim 4: Trust)

Usage Example:
    from public_models import (
        PublicVesselPacket,
        PublicCatchPacket,
        PublicLotPacket,
        PublicVerificationPacket
    )

    # Validate incoming data
    vessel = PublicVesselPacket(**vessel_data)
    catch = PublicCatchPacket(**catch_data)
    lot = PublicLotPacket(**lot_data)
    verification = PublicVerificationPacket(**verification_data)
"""

from .public_vessel import PublicVesselPacket
from .public_catch import PublicCatchPacket
from .public_lot import PublicLotPacket
from .public_verification import PublicVerificationPacket

__all__ = [
    "PublicVesselPacket",
    "PublicCatchPacket",
    "PublicLotPacket",
    "PublicVerificationPacket",
]

__version__ = "1.0.0"
__classification__ = "PUBLIC-UNLIMITED"
