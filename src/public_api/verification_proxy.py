"""
PublicVerificationProxy - API Gateway for Consumer QR Verification

This service acts as the gatekeeper for public data requests (QR code scans).
It proxies requests to the PRIVATE MarketSide service, but only returns
publicly-allowed fields to the consumer.

Classification: PUBLIC-UNLIMITED (Commons Good)
Author: SeaTrace Development Team
Date: October 2025

Architecture:
    Consumer QR Scan → PublicVerificationProxy → (authenticated) Private MarketSide
                                                      ↓
                                                  Full Chain Lookup
                                                      ↓
                                            Sanitize Private Fields
                                                      ↓
    Consumer ← PublicVerificationPacket ← Return Only Public Data

This completely hides internal chain structure and private data while
providing verifiable public information.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import httpx
import os
from typing import Optional
import logging

# Import PUBLIC model (defines what consumers can see)
from src.public_models.public_verification import PublicVerificationPacket

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="SeaTrace Public Verification Proxy",
    description="Public API Gateway for consumer QR code verification",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Environment config
PRIVATE_MARKETSIDE_URL = os.getenv("PRIVATE_MARKETSIDE_URL", "http://localhost:8004")
PRIVATE_API_KEY = os.getenv("PRIVATE_API_KEY", "")  # Internal service auth


class QRVerificationRequest(BaseModel):
    """Public request from consumer scanning QR code"""
    packet_id: str
    qr_code: Optional[str] = None
    consumer_id: Optional[str] = None


class PrivateVerificationResponse(BaseModel):
    """PRIVATE response from MarketSide (contains all fields)"""
    packet_id: str
    species: str
    catch_area_general: str
    landed_kg: float
    vessel_public_id: str
    vessel_name: str
    compliance_status: str
    trust_score: float
    chain_verified: bool
    landing_date: str
    
    # PRIVATE fields (not exposed to public)
    precise_gps_lat: Optional[float] = None
    precise_gps_lon: Optional[float] = None
    financial_value_usd: Optional[float] = None
    ml_quality_score: Optional[float] = None
    projected_check_value: Optional[float] = None
    investor_dashboard_url: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "SeaTrace Public Verification Proxy",
        "status": "operational",
        "classification": "PUBLIC-UNLIMITED",
        "endpoints": {
            "verify": "/api/v1/verify/{packet_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check for load balancers"""
    # Check if we can reach private MarketSide
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{PRIVATE_MARKETSIDE_URL}/health",
                headers={"X-API-Key": PRIVATE_API_KEY}
            )
            if response.status_code == 200:
                return {"status": "healthy", "private_service": "reachable"}
            else:
                return {"status": "degraded", "private_service": "unreachable"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "degraded", "error": str(e)}


@app.get("/api/v1/verify/{packet_id}", response_model=PublicVerificationPacket)
async def verify_packet(packet_id: str):
    """
    Public endpoint for consumer QR code verification.
    
    This is the GATEKEEPER that sanitizes private data.
    
    Args:
        packet_id: Packet ID from QR code (e.g., CATCH-2025-FV-001-012)
    
    Returns:
        PublicVerificationPacket: Only PUBLIC fields exposed
    
    Raises:
        HTTPException: If packet not found or verification fails
    """
    logger.info(f"Public verification request for packet: {packet_id}")
    
    # Call PRIVATE MarketSide service (authenticated internal call)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{PRIVATE_MARKETSIDE_URL}/api/v1/internal/verify/{packet_id}",
                headers={
                    "X-API-Key": PRIVATE_API_KEY,
                    "X-Service": "PublicProxy"
                }
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Packet {packet_id} not found")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Internal verification service error"
                )
            
            # Parse PRIVATE response (contains all fields)
            private_data = PrivateVerificationResponse(**response.json())
            
    except httpx.RequestError as e:
        logger.error(f"Failed to reach private MarketSide: {e}")
        raise HTTPException(
            status_code=503,
            detail="Verification service temporarily unavailable"
        )
    
    # SANITIZE: Create PUBLIC response (exclude private fields)
    public_response = PublicVerificationPacket(
        packet_id=private_data.packet_id,
        species=private_data.species,
        catch_area_general=private_data.catch_area_general,  # Generalized FAO area
        landed_kg=private_data.landed_kg,
        vessel_public_id=private_data.vessel_public_id,
        vessel_name=private_data.vessel_name,
        compliance_status=private_data.compliance_status,
        trust_score=private_data.trust_score,
        chain_verified=private_data.chain_verified,
        landing_date=private_data.landing_date,
        # EXCLUDED from public response:
        # - precise_gps_lat, precise_gps_lon (competitive data)
        # - financial_value_usd (proprietary pricing)
        # - ml_quality_score (investor algorithm output)
        # - projected_check_value (prospectus calculation)
        # - investor_dashboard_url (private access)
    )
    
    logger.info(f"Verification successful - returned PUBLIC data only for {packet_id}")
    return public_response


@app.post("/api/v1/verify", response_model=PublicVerificationPacket)
async def verify_qr_code(request: QRVerificationRequest):
    """
    Alternative endpoint that accepts QR code data.
    
    Some QR codes may contain additional metadata beyond packet_id.
    This endpoint normalizes the request and routes to the same verification logic.
    """
    return await verify_packet(request.packet_id)


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8001"))
    logger.info(f"Starting PublicVerificationProxy on port {port}")
    logger.info(f"Proxying to private MarketSide: {PRIVATE_MARKETSIDE_URL}")
    
    uvicorn.run(
        "verification_proxy:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
