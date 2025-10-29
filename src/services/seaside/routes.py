# 🌊 SeaSide API Routes
# For the Commons Good!

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import uuid
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.seaside.models import (
    IncomingPacket,
    IngestResponse,
    HealthResponse
)

# Try to import crypto handler (optional for basic testing)
try:
    from security.packet_crypto import PacketCryptoHandler, CryptoPacket
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  Crypto handler not available - running without signature verification")

router = APIRouter()

# Global crypto handler (will be initialized if available)
crypto_handler = None

if CRYPTO_AVAILABLE:
    try:
        # Initialize with test keys for now (in production, load from secure storage)
        crypto_handler = PacketCryptoHandler.generate_keypair()
        print("✅ Crypto handler initialized")
    except Exception as e:
        print(f"⚠️  Could not initialize crypto handler: {e}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and version information.
    """
    return HealthResponse(
        status="healthy",
        service="seaside",
        version="1.0.0"
    )


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_packet(packet: IncomingPacket):
    """
    Ingest incoming packet from vessel
    
    PUBLIC KEY INCOMING - Verifies signature if provided
    
    Args:
        packet: Incoming packet data with optional signature
    
    Returns:
        IngestResponse with packet_id and verification status
    """
    try:
        # Generate packet ID
        packet_id = str(uuid.uuid4())
        
        # Verify signature if crypto is available and signature provided
        verified = False
        if CRYPTO_AVAILABLE and crypto_handler and packet.signature:
            try:
                # Create CryptoPacket from incoming packet
                crypto_packet = CryptoPacket(
                    correlation_id=packet.correlation_id,
                    source=packet.source,
                    payload=packet.payload
                )
                crypto_packet.signature = packet.signature.encode() if isinstance(packet.signature, str) else packet.signature
                
                # Verify signature
                verified = crypto_handler.verify_signature(crypto_packet)
                
                if not verified:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid packet signature"
                    )
            except Exception as e:
                print(f"⚠️  Signature verification failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Signature verification error: {str(e)}"
                )
        
        # Process packet (in production, this would route to DeckSide)
        # For now, just acknowledge receipt
        print(f"📦 Packet ingested: {packet_id}")
        print(f"   Correlation ID: {packet.correlation_id}")
        print(f"   Source: {packet.source}")
        print(f"   Verified: {verified}")
        
        return IngestResponse(
            status="ingested",
            packet_id=packet_id,
            correlation_id=packet.correlation_id,
            verified=verified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error ingesting packet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest packet: {str(e)}"
        )


@router.get("/packets/{packet_id}")
async def get_packet(packet_id: str):
    """
    Retrieve packet by ID
    
    NOTE: This is a placeholder - in production, this would query storage
    """
    # Placeholder response
    return {
        "packet_id": packet_id,
        "status": "stored",
        "message": "Packet retrieval not yet implemented - connect to DeckSide"
    }


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus-compatible metrics endpoint
    
    Returns basic service metrics
    """
    # Placeholder metrics
    return {
        "service": "seaside",
        "packets_ingested_total": 0,
        "packets_verified_total": 0,
        "packets_rejected_total": 0,
        "crypto_available": CRYPTO_AVAILABLE
    }
