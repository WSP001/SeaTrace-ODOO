"""API routes for DeckSide service"""
import time
import structlog
from fastapi import APIRouter, HTTPException, Request, Depends
from httpx import AsyncClient, ConnectError
from typing import Optional

from .models import ProcessRequest, ProcessResponse, ValidationResult, ValidationError
from .processor import DeckSideProcessor
from .config import settings
from .prospectus import ProspectusCalculator

logger = structlog.get_logger()
router = APIRouter()

# Metrics
REQUEST_COUNT = {}
REQUEST_DURATION = {}

async def get_correlation_id(request: Request) -> str:
    """Dependency to get correlation ID from request"""
    return getattr(request.state, "correlation_id", "unknown")


@router.get("/health")
async def health_check(correlation_id: str = Depends(get_correlation_id)):
    """Health check endpoint with dependency status"""
    
    logger.info("health_check_requested", correlation_id=correlation_id)
    
    # Check if SeaSide is reachable
    seaside_status = "reachable"
    try:
        async with AsyncClient(timeout=settings.upstream_timeout) as client:
            response = await client.get(f"{settings.seaside_url}/health")
            if response.status_code != 200:
                seaside_status = "unreachable"
    except (ConnectError, Exception) as e:
        logger.warning("seaside_dependency_check_failed", error=str(e))
        seaside_status = "unreachable"
    
    return {
        "status": "healthy",
        "service": "deckside",
        "version": settings.service_version,
        "correlation_id": correlation_id,
        "dependencies": {
            "seaside": seaside_status
        }
    }


@router.post("/api/v1/process")
async def process_packet(
    request: ProcessRequest,
    correlation_id: str = Depends(get_correlation_id)
) -> ProcessResponse:
    """
    Process a vessel packet (from SeaSide).
    Validates and enriches the data.
    """
    
    start_time = time.time()
    
    try:
        logger.info(
            "packet_processing_started",
            packet_id=request.packet_id,
            vessel_id=request.vessel_data.vessel_id,
            correlation_id=correlation_id
        )
        
        # Validate the vessel data
        validation_result, enriched_data = DeckSideProcessor.validate_vessel_data(
            request.vessel_data
        )
        
        # Determine processing status
        if validation_result.valid:
            status = "processed"
            next_step = "route_to_dockside"
        else:
            status = "rejected"
            next_step = None
        
        # Calculate processing time
        duration_ms = (time.time() - start_time) * 1000
        
        response = ProcessResponse(
            status=status,
            packet_id=request.packet_id,
            correlation_id=correlation_id,
            vessel_data_enriched=enriched_data if validation_result.valid else None,
            validation_results=validation_result,
            next_step=next_step,
            processing_duration_ms=round(duration_ms, 2)
        )
        
        logger.info(
            "packet_processing_completed",
            packet_id=request.packet_id,
            status=status,
            duration_ms=round(duration_ms, 2),
            correlation_id=correlation_id
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "packet_processing_error",
            packet_id=request.packet_id,
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )


@router.post("/api/v1/validate")
async def validate_vessel(
    vessel_data: dict,
    correlation_id: str = Depends(get_correlation_id)
):
    """
    Standalone validation endpoint.
    Useful for pre-checking data before processing.
    """
    
    try:
        from .models import VesselData
        
        vessel = VesselData(**vessel_data)
        validation_result, _ = DeckSideProcessor.validate_vessel_data(vessel)
        
        logger.info(
            "standalone_validation_performed",
            valid=validation_result.valid,
            error_count=len(validation_result.errors),
            correlation_id=correlation_id
        )
        
        return {
            "correlation_id": correlation_id,
            "validation_results": validation_result.dict()
        }
        
    except Exception as e:
        logger.error(
            "validation_error",
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/metrics")
async def metrics(correlation_id: str = Depends(get_correlation_id)):
    """
    Prometheus metrics endpoint.
    (Live metrics will be implemented with prometheus-client)
    """
    
    # Placeholder - will be replaced with real Prometheus metrics
    # This demonstrates the endpoint exists
    return {
        "correlation_id": correlation_id,
        "status": "metrics_endpoint_ready",
        "note": "Use prometheus-client for production metrics"
    }


@router.post("/api/v1/prospectus")
async def calculate_prospectus(
    estimated_catch_kg: float,
    projected_ground_price_usd_per_kg: float,
    species: str,
    vessel_id: str,
    packet_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    correlation_id: str = Depends(get_correlation_id)
):
    """
    CRITICAL INVESTOR IP: Calculate $CHECK KEY
    
    This is the "predictive hand" - the first immutable financial projection
    that links the public #CATCH KEY to the private $CHECK KEY monetization.
    
    Formula: estimated_catch × projected_ground_price = $CHECK KEY
    
    **Track:** PRIVATE_KEY (Track 2 - Investor Monetization)
    **License Required:** LIMITED (MarketSide subscription)
    **Next Step:** DockSide reconciliation with actual landed value
    
    Args:
        estimated_catch_kg: Estimated catch weight in kilograms (at-sea)
        projected_ground_price_usd_per_kg: Projected ground price USD per kg
        species: Fish species (e.g., "Tuna", "Salmon")
        vessel_id: Vessel identifier
        packet_id: Optional SEASIDE packet ID for traceability
        metadata: Optional metadata (fishing_area, gear_type, quality_grade, etc.)
        correlation_id: Request correlation ID (auto-injected)
    
    Returns:
        $CHECK KEY calculation with immutability hash, timestamps, and next-step routing
    
    Example:
        POST /api/v1/prospectus
        {
            "estimated_catch_kg": 500.0,
            "projected_ground_price_usd_per_kg": 15.00,
            "species": "Tuna",
            "vessel_id": "WSP-001",
            "metadata": {
                "fishing_area": "FAO-67",
                "quality_grade": "A",
                "gear_type": "longline"
            }
        }
        
        Response:
        {
            "check_key_usd": 7500.00,
            "estimated_catch_kg": 500.0,
            "projected_price_per_kg_usd": 15.00,
            "species": "Tuna",
            "vessel_id": "WSP-001",
            "correlation_id": "abc-123",
            "packet_id": "DECKSIDE-xyz-789",
            "track": "PRIVATE_KEY",
            "license_required": "LIMITED",
            "next_step": "dockside_reconciliation",
            ...
        }
    """
    
    start_time = time.time()
    
    try:
        logger.info(
            "prospectus_calculation_started",
            vessel_id=vessel_id,
            species=species,
            estimated_catch_kg=estimated_catch_kg,
            projected_price=projected_ground_price_usd_per_kg,
            correlation_id=correlation_id
        )
        
        # Calculate $CHECK KEY
        check_key_result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=estimated_catch_kg,
            projected_ground_price_usd_per_kg=projected_ground_price_usd_per_kg,
            species=species,
            vessel_id=vessel_id,
            correlation_id=correlation_id,
            packet_id=packet_id,
            metadata=metadata
        )
        
        # Calculate processing duration
        duration_ms = (time.time() - start_time) * 1000
        check_key_result["calculation"]["duration_ms"] = round(duration_ms, 2)
        
        logger.info(
            "prospectus_calculation_completed",
            vessel_id=vessel_id,
            check_key_usd=check_key_result["check_key_usd"],
            duration_ms=round(duration_ms, 2),
            correlation_id=correlation_id
        )
        
        return check_key_result
        
    except ValueError as e:
        # Validation errors (invalid inputs)
        logger.warning(
            "prospectus_validation_error",
            vessel_id=vessel_id,
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Unexpected errors
        logger.error(
            "prospectus_calculation_error",
            vessel_id=vessel_id,
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Prospectus calculation error: {str(e)}"
        )


@router.post("/api/v1/prospectus/enrich")
async def enrich_prospectus_with_market_data(
    check_key: dict,
    market_data: dict,
    correlation_id: str = Depends(get_correlation_id)
):
    """
    Enrich a $CHECK KEY with real-time market data (PREMIUM FEATURE)
    
    **Track:** PRIVATE_KEY (Track 2 - Investor Monetization)
    **License Required:** LIMITED (MarketSide subscription)
    
    This endpoint enhances the prospectus calculation with:
    - Current spot pricing
    - 30-day average pricing
    - Market variance/volatility
    - Confidence scoring
    - Recalculated spot $CHECK KEY
    
    Args:
        check_key: Original $CHECK KEY calculation from /api/v1/prospectus
        market_data: Real-time market data (spot_price, avg_price_30d, variance, confidence)
        correlation_id: Request correlation ID (auto-injected)
    
    Returns:
        Enriched $CHECK KEY with market analysis
    
    Example:
        POST /api/v1/prospectus/enrich
        {
            "check_key": { ... original check_key ... },
            "market_data": {
                "spot_price": 15.25,
                "avg_price_30d": 14.80,
                "variance": 3.0,
                "confidence": 0.92,
                "conditions": "favorable"
            }
        }
    """
    
    try:
        logger.info(
            "prospectus_enrichment_started",
            original_check_key_usd=check_key.get("check_key_usd"),
            spot_price=market_data.get("spot_price"),
            correlation_id=correlation_id
        )
        
        enriched = ProspectusCalculator.enrich_with_market_data(check_key, market_data)
        
        logger.info(
            "prospectus_enrichment_completed",
            original_check_key_usd=check_key.get("check_key_usd"),
            spot_check_key_usd=enriched["market_enrichment"]["spot_check_key_usd"],
            correlation_id=correlation_id
        )
        
        return enriched
        
    except Exception as e:
        logger.error(
            "prospectus_enrichment_error",
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Market enrichment error: {str(e)}"
        )


@router.post("/api/v1/prospectus/variance")
async def calculate_variance(
    check_key: dict,
    actual_landed_value_usd: float,
    correlation_id: str = Depends(get_correlation_id)
):
    """
    Calculate variance between projected $CHECK KEY and actual landed value
    
    **Track:** PRIVATE_KEY (Track 2 - Investor Monetization)
    **License Required:** LIMITED (MarketSide subscription)
    **Purpose:** ML model training data for improving predictive accuracy
    
    This endpoint calculates the variance between:
    - DeckSide projected $CHECK KEY (at-sea estimate)
    - DockSide actual landed value (ground truth)
    
    Variance data feeds ML models to improve future projections.
    
    Args:
        check_key: Original $CHECK KEY calculation from /api/v1/prospectus
        actual_landed_value_usd: Actual landed value from DockSide
        correlation_id: Request correlation ID (auto-injected)
    
    Returns:
        Variance analysis with accuracy classification
    
    Example:
        POST /api/v1/prospectus/variance
        {
            "check_key": { ... original check_key ... },
            "actual_landed_value_usd": 7800.00
        }
        
        Response:
        {
            "projected_value_usd": 7500.00,
            "actual_landed_value_usd": 7800.00,
            "variance_usd": 300.00,
            "variance_percent": 4.00,
            "accuracy_classification": "excellent",
            "within_5_percent": true,
            "within_10_percent": true,
            ...
        }
    """
    
    try:
        logger.info(
            "variance_calculation_started",
            projected_value_usd=check_key.get("check_key_usd"),
            actual_landed_value_usd=actual_landed_value_usd,
            correlation_id=correlation_id
        )
        
        variance = ProspectusCalculator.calculate_variance(check_key, actual_landed_value_usd)
        
        logger.info(
            "variance_calculation_completed",
            variance_usd=variance["variance_usd"],
            variance_percent=variance["variance_percent"],
            accuracy_classification=variance["accuracy_classification"],
            correlation_id=correlation_id
        )
        
        return variance
        
    except Exception as e:
        logger.error(
            "variance_calculation_error",
            error=str(e),
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Variance calculation error: {str(e)}"
        )

