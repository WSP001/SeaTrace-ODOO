"""Commons Fund transparency endpoint for SeaTrace.

Provides monthly reporting on how MarketSide revenue subsidizes
free SeaSide/DeckSide/DockSide infrastructure.
"""

from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["public"])


async def get_commons_fund_data(period: Optional[str] = None) -> Dict:
    """Get Commons Fund data for a specific period.
    
    Args:
        period: YYYY-MM format (defaults to current month)
        
    Returns:
        Commons Fund financial data
    """
    # TODO: Replace with actual database queries
    # This is a template showing the expected schema
    
    if not period:
        now = datetime.now(timezone.utc)
        period = f"{now:%Y-%m}"
    
    # Example data structure (replace with real data)
    return {
        "period": period,
        "currency": "USD",
        "marketside_gross_revenue": 125000.00,
        "commons_allocation_percent": 12.5,
        "commons_fund_total": 15625.00,
        "expenses": {
            "seaside_infrastructure": 3200.00,
            "deckside_infrastructure": 5800.00,
            "dockside_infrastructure": 4100.00,
            "shared_services": 2000.00,
            "total": 15100.00
        },
        "coverage_percent": 103.5,
        "fund_balance": 525.00,
        "ytd_summary": {
            "total_allocated": 140625.00,
            "total_spent": 135900.00,
            "surplus": 4725.00
        },
        "breakdown": {
            "seaside": {
                "compute_hours": 1200.50,
                "storage_gb": 8500,
                "bandwidth_gb": 1200,
                "database_ops": 450000,
                "cost": 3200.00
            },
            "deckside": {
                "compute_hours": 2100.75,
                "storage_gb": 15000,
                "bandwidth_gb": 2800,
                "database_ops": 890000,
                "cost": 5800.00
            },
            "dockside": {
                "compute_hours": 1650.25,
                "storage_gb": 12000,
                "bandwidth_gb": 1900,
                "database_ops": 620000,
                "cost": 4100.00
            }
        }
    }


@router.get("/api/commons/fund")
async def commons_fund_report(
    request: Request,
    period: Optional[str] = None
):
    """Get Commons Fund transparency report.
    
    Shows how MarketSide revenue subsidizes free infrastructure.
    
    Query Parameters:
        period: YYYY-MM format (optional, defaults to current month)
        
    Returns:
        JSON with revenue allocation, expenses, and coverage metrics
    """
    data = await get_commons_fund_data(period)
    
    return JSONResponse(
        status_code=200,
        content=data,
        headers={
            "Cache-Control": "public, max-age=3600",  # 1 hour cache
            "X-Commons-Charter": "https://seatrace.com/docs/COMMONS_CHARTER.md"
        }
    )


@router.get("/api/commons/fund/history")
async def commons_fund_history(
    request: Request,
    months: int = 12
):
    """Get historical Commons Fund data.
    
    Query Parameters:
        months: Number of months to retrieve (default: 12, max: 36)
        
    Returns:
        Array of monthly Commons Fund reports
    """
    if months > 36:
        months = 36
    
    # TODO: Fetch actual historical data
    history = []
    now = datetime.now(timezone.utc)
    
    for i in range(months):
        # Calculate period (going backwards)
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
        
        period = f"{year:04d}-{month:02d}"
        data = await get_commons_fund_data(period)
        history.append(data)
    
    return JSONResponse(
        status_code=200,
        content={"periods": history},
        headers={"Cache-Control": "public, max-age=3600"}
    )


@router.get("/api/commons/metrics")
async def commons_metrics(request: Request):
    """Get real-time Commons infrastructure metrics.
    
    Returns:
        Current usage and health metrics for free pillars
    """
    # TODO: Fetch from Prometheus/monitoring system
    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "pillars": {
            "seaside": {
                "requests_per_second": 45.2,
                "avg_response_time_ms": 120,
                "error_rate_percent": 0.02,
                "active_vessels": 1250,
                "uptime_percent": 99.95
            },
            "deckside": {
                "requests_per_second": 32.8,
                "avg_response_time_ms": 180,
                "error_rate_percent": 0.05,
                "active_batches": 450,
                "uptime_percent": 99.92
            },
            "dockside": {
                "requests_per_second": 28.5,
                "avg_response_time_ms": 150,
                "error_rate_percent": 0.03,
                "active_storage_units": 890,
                "uptime_percent": 99.94
            }
        },
        "infrastructure": {
            "total_compute_utilization_percent": 45,
            "storage_used_gb": 35500,
            "storage_capacity_gb": 100000,
            "bandwidth_used_gb_today": 1250,
            "queue_depth": 12
        }
    }
    
    return JSONResponse(
        status_code=200,
        content=metrics,
        headers={"Cache-Control": "no-cache"}
    )
