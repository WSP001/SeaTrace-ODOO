"""API routes for DockSide service"""
import structlog
from fastapi import APIRouter, HTTPException, Request, Depends
from httpx import AsyncClient, ConnectError
from typing import Optional

from .models import (
    StoreRequest, StoreResponse, RetrieveResponse,
    QueryRequest, QueryResponse, StoredPacket, StorageStats
)
from .storage import storage
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
    
    # Check if DeckSide is reachable
    deckside_status = "reachable"
    try:
        async with AsyncClient(timeout=settings.upstream_timeout) as client:
            response = await client.get(f"{settings.deckside_url}/health")
            if response.status_code != 200:
                deckside_status = "unreachable"
    except (ConnectError, Exception) as e:
        logger.warning("deckside_dependency_check_failed", error=str(e))
        deckside_status = "unreachable"
    
    # Get storage stats
    packet_count = await storage.count()
    
    return {
        "status": "healthy",
        "service": "dockside",
        "version": settings.service_version,
        "correlation_id": correlation_id,
        "dependencies": {
            "deckside": deckside_status
        },
        "storage": {
            "mode": settings.storage_mode,
            "packet_count": packet_count
        }
    }


@router.post("/api/v1/store")
async def store_packet(
    request: StoreRequest,
    correlation_id: str = Depends(get_correlation_id)
) -> StoreResponse:
    """
    Store a validated packet from DeckSide.
    """
    
    try:
        logger.info(
            "storage_request_received",
            packet_id=request.packet_id,
            validation_passed=request.validation_passed,
            correlation_id=correlation_id
        )
        
        # Only store validated packets
        if not request.validation_passed:
            logger.warning(
                "packet_rejected_validation_failed",
                packet_id=request.packet_id,
                correlation_id=correlation_id
            )
            return StoreResponse(
                status="rejected",
                packet_id=request.packet_id,
                correlation_id=correlation_id,
                storage_location=None
            )
        
        # Create stored packet
        stored_packet = StoredPacket(
            packet_id=request.packet_id,
            correlation_id=request.correlation_id,
            vessel_id=request.vessel_data.get("vessel_id", "unknown"),
            catch_weight=request.vessel_data.get("catch_weight", 0.0),
            species=request.vessel_data.get("species", "unknown"),
            location=request.vessel_data.get("location"),
            verified=request.vessel_data.get("verified", False),
            validated=request.validation_passed,
            enriched_data=request.enriched_data,
            source_service="deckside"
        )
        
        # Store packet
        success = await storage.store(stored_packet)
        
        if success:
            logger.info(
                "packet_stored_successfully",
                packet_id=request.packet_id,
                correlation_id=correlation_id
            )
            return StoreResponse(
                status="stored",
                packet_id=request.packet_id,
                correlation_id=correlation_id,
                storage_location=f"memory://{request.packet_id}"
            )
        else:
            logger.error(
                "storage_failed",
                packet_id=request.packet_id,
                correlation_id=correlation_id
            )
            return StoreResponse(
                status="error",
                packet_id=request.packet_id,
                correlation_id=correlation_id,
                storage_location=None
            )
            
    except Exception as e:
        logger.error(
            "store_packet_error",
            packet_id=request.packet_id,
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")


@router.get("/api/v1/retrieve/{packet_id}")
async def retrieve_packet(
    packet_id: str,
    correlation_id: str = Depends(get_correlation_id)
) -> RetrieveResponse:
    """
    Retrieve a stored packet by ID.
    """
    
    try:
        logger.info(
            "retrieve_request",
            packet_id=packet_id,
            correlation_id=correlation_id
        )
        
        packet = await storage.retrieve(packet_id)
        
        if packet:
            return RetrieveResponse(
                status="found",
                packet_id=packet_id,
                correlation_id=correlation_id,
                data=packet,
                found=True
            )
        else:
            return RetrieveResponse(
                status="not_found",
                packet_id=packet_id,
                correlation_id=correlation_id,
                data=None,
                found=False
            )
            
    except Exception as e:
        logger.error(
            "retrieve_error",
            packet_id=packet_id,
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")


@router.post("/api/v1/query")
async def query_packets(
    query: QueryRequest,
    correlation_id: str = Depends(get_correlation_id)
) -> QueryResponse:
    """
    Query stored packets with filters.
    """
    
    try:
        logger.info(
            "query_request",
            filters=query.dict(exclude_none=True),
            correlation_id=correlation_id
        )
        
        packets = await storage.query(query)
        
        return QueryResponse(
            status="success",
            correlation_id=correlation_id,
            total_count=len(packets),
            returned_count=len(packets),
            packets=packets
        )
        
    except Exception as e:
        logger.error(
            "query_error",
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


@router.get("/api/v1/stats")
async def get_statistics(correlation_id: str = Depends(get_correlation_id)) -> StorageStats:
    """
    Get storage statistics.
    """
    
    try:
        stats_dict = await storage.get_stats()
        return StorageStats(**stats_dict)
        
    except Exception as e:
        logger.error(
            "stats_error",
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@router.get("/metrics")
async def metrics(correlation_id: str = Depends(get_correlation_id)):
    """
    Prometheus metrics endpoint.
    """
    
    stats = await storage.get_stats()
    
    return {
        "correlation_id": correlation_id,
        "storage_mode": settings.storage_mode,
        "total_packets": stats["total_packets"],
        "verified_packets": stats["verified_packets"],
        "storage_utilization_percent": stats["storage_utilization"]
    }
