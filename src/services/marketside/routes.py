"""API routes for MarketSide service"""
import structlog
from fastapi import APIRouter, HTTPException, Request, Depends
from httpx import AsyncClient, ConnectError

from .models import (
    MarketPacket, PublishRequest, PublishResponse,
    PMTokenRequest, PMTokenResponse, MarketStats,
    CertificateRequest, CertificateResponse
)
from .publisher import publisher
from .pm_tokens import pm_token_manager
from .config import settings

logger = structlog.get_logger()
router = APIRouter()


async def get_correlation_id(request: Request) -> str:
    """Dependency to get correlation ID from request"""
    return getattr(request.state, "correlation_id", "unknown")


@router.get("/health")
async def health_check(correlation_id: str = Depends(get_correlation_id)):
    """Health check endpoint with dependency status"""
    
    logger.info("health_check_requested", correlation_id=correlation_id)
    
    # Check if DockSide is reachable
    dockside_status = "reachable"
    try:
        async with AsyncClient(timeout=settings.upstream_timeout) as client:
            response = await client.get(f"{settings.dockside_url}/health")
            if response.status_code != 200:
                dockside_status = "unreachable"
    except (ConnectError, Exception) as e:
        logger.warning("dockside_dependency_check_failed", error=str(e))
        dockside_status = "unreachable"
    
    return {
        "status": "healthy",
        "service": "marketside",
        "version": settings.service_version,
        "correlation_id": correlation_id,
        "dependencies": {
            "dockside": dockside_status
        },
        "features": {
            "pm_tokens_enabled": settings.enable_pm_tokens,
            "market_exchange_enabled": settings.enable_market_exchange
        }
    }


@router.post("/api/v1/publish")
async def publish_to_market(
    request: PublishRequest,
    correlation_id: str = Depends(get_correlation_id)
) -> PublishResponse:
    """
    Publish data to market (PRIVATE KEY OUTGOING - signs outgoing data).
    """
    
    try:
        logger.info(
            "publish_request_received",
            packet_id=request.packet_id,
            publish_type=request.publish_type,
            correlation_id=correlation_id
        )
        
        # Publish based on type
        if request.publish_type == "listing":
            result = await publisher.publish_listing(request.packet_id, request.data)
        elif request.publish_type == "transaction":
            result = await publisher.publish_transaction(request.packet_id, request.data)
        elif request.publish_type == "certificate":
            result = await publisher.issue_certificate(
                request.packet_id,
                request.data.get("vessel_id", "unknown"),
                request.data.get("traceability_chain", [])
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid publish type")
        
        if result.get("success"):
            # Generate signature if required (PRIVATE KEY OUTGOING)
            signature = None
            if request.signature_required:
                signature = result.get("signature", "mock-signature-placeholder")
            
            logger.info(
                "publish_successful",
                packet_id=request.packet_id,
                publish_type=request.publish_type,
                correlation_id=correlation_id
            )
            
            return PublishResponse(
                status="published",
                packet_id=request.packet_id,
                correlation_id=correlation_id,
                signature=signature,
                market_url=result.get("market_url")
            )
        else:
            logger.error(
                "publish_failed",
                packet_id=request.packet_id,
                error=result.get("error"),
                correlation_id=correlation_id
            )
            return PublishResponse(
                status="rejected",
                packet_id=request.packet_id,
                correlation_id=correlation_id,
                signature=None,
                market_url=None
            )
            
    except Exception as e:
        logger.error(
            "publish_error",
            packet_id=request.packet_id,
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=500, detail=f"Publish error: {str(e)}")


@router.post("/api/v1/pm/verify")
async def verify_pm_token(
    request: PMTokenRequest,
    correlation_id: str = Depends(get_correlation_id)
) -> PMTokenResponse:
    """
    Verify PM Token for investor/endorser access.
    """
    
    try:
        logger.info(
            "pm_token_verification_requested",
            token_prefix=request.token[:10],
            correlation_id=correlation_id
        )
        
        result = await pm_token_manager.verify_token(request.token)
        
        if result["valid"]:
            logger.info(
                "pm_token_verified",
                token_prefix=request.token[:10],
                access_level=result["access_level"],
                correlation_id=correlation_id
            )
            return PMTokenResponse(**result)
        else:
            logger.warning(
                "pm_token_invalid",
                token_prefix=request.token[:10],
                correlation_id=correlation_id
            )
            raise HTTPException(status_code=401, detail="Invalid PM token")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "pm_token_verification_error",
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@router.get("/api/v1/pm/tokens")
async def list_pm_tokens(correlation_id: str = Depends(get_correlation_id)):
    """
    List available PM tokens (for demo purposes).
    """
    tokens = await pm_token_manager.list_tokens()
    return {
        "correlation_id": correlation_id,
        "tokens": tokens,
        "note": "Demo tokens for investor access"
    }


@router.post("/api/v1/certificate")
async def issue_certificate(
    request: CertificateRequest,
    correlation_id: str = Depends(get_correlation_id)
) -> CertificateResponse:
    """
    Issue traceability certificate (PRIVATE KEY OUTGOING - signed).
    """
    
    try:
        logger.info(
            "certificate_request_received",
            packet_id=request.packet_id,
            vessel_id=request.vessel_id,
            correlation_id=correlation_id
        )
        
        # Build traceability chain (mock for now)
        traceability_chain = [
            {"pillar": "seaside", "action": "ingested", "timestamp": "2025-10-16T00:00:00Z"},
            {"pillar": "deckside", "action": "validated", "timestamp": "2025-10-16T00:01:00Z"},
            {"pillar": "dockside", "action": "stored", "timestamp": "2025-10-16T00:02:00Z"},
            {"pillar": "marketside", "action": "certified", "timestamp": "2025-10-16T00:03:00Z"}
        ]
        
        result = await publisher.issue_certificate(
            request.packet_id,
            request.vessel_id,
            traceability_chain
        )
        
        if result.get("success"):
            return CertificateResponse(
                status="issued",
                certificate_id=result["certificate_id"],
                packet_id=request.packet_id,
                correlation_id=correlation_id,
                vessel_id=request.vessel_id,
                traceability_chain=traceability_chain,
                signature=result["signature"],
                valid_until=result.get("valid_until")
            )
        else:
            raise HTTPException(status_code=500, detail="Certificate issuance failed")
            
    except Exception as e:
        logger.error(
            "certificate_issuance_error",
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=500, detail=f"Certificate error: {str(e)}")


@router.get("/api/v1/stats")
async def get_market_stats(correlation_id: str = Depends(get_correlation_id)) -> MarketStats:
    """
    Get market statistics.
    """
    try:
        publisher_stats = await publisher.get_stats()
        pm_stats = await pm_token_manager.get_stats()
        
        return MarketStats(
            total_transactions=publisher_stats.get("total_transactions", 0),
            total_listings=publisher_stats.get("total_listings", 0),
            total_certificates=publisher_stats.get("total_certificates", 0),
            active_vessels=0,  # Placeholder
            total_volume_kg=0.0,  # Placeholder
            top_species={}  # Placeholder
        )
    except Exception as e:
        logger.error("stats_error", error=str(e), correlation_id=correlation_id)
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@router.get("/metrics")
async def metrics(correlation_id: str = Depends(get_correlation_id)):
    """
    Prometheus metrics endpoint.
    """
    stats = await publisher.get_stats()
    
    return {
        "correlation_id": correlation_id,
        "total_published": stats["total_published"],
        "total_listings": stats["total_listings"],
        "total_transactions": stats["total_transactions"],
        "total_certificates": stats["total_certificates"]
    }
