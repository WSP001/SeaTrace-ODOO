"""License status and introspection endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["public"])


@router.get("/api/license/status")
async def license_status(request: Request):
    """Get current license status and entitlements.
    
    Returns license information including type, tier, features, and limits.
    Useful for client-side feature gating and upgrade prompts.
    """
    claims = getattr(request.state, "license_claims", None) or {}
    
    if not claims:
        return JSONResponse(
            status_code=200,
            content={
                "status": "none",
                "message": "No license token provided. Public routes only.",
                "upgrade_url": "https://seatrace.worldseafoodproducers.com/pricing"
            },
            headers={"Cache-Control": "no-store"}
        )
    
    typ = claims.get("typ")
    status = "valid"
    
    # Check expiry
    import time
    exp = claims.get("exp", 0)
    if time.time() > exp:
        status = "expired"
    
    response_data = {
        "status": status,
        "typ": typ,
        "license_id": claims.get("license_id"),
        "org": claims.get("org"),
        "tier": claims.get("tier"),
        "exp": exp,
        "features": claims.get("features", []),
        "limits": claims.get("limits", {}),
        "pillars": claims.get("pillars", []),
    }
    
    # Add upgrade prompt if PUL
    if typ == "PUL":
        response_data["upgrade_available"] = {
            "message": "Upgrade to Private-Limited for MarketSide premium features",
            "url": "https://seatrace.worldseafoodproducers.com/pricing",
            "features": ["Dynamic trading", "Pricing algorithms", "Premium QR analytics"]
        }
    
    # Add renewal prompt if expired
    if status == "expired":
        response_data["renewal_url"] = "https://seatrace.worldseafoodproducers.com/billing"
    
    return JSONResponse(
        status_code=200,
        content=response_data,
        headers={"Cache-Control": "no-store"}
    )


def list_public_routes(app) -> list[str]:
    """Extract public routes from FastAPI app.
    
    Only includes routes tagged with 'public' to avoid exposing
    MarketSide premium endpoints in the PUL scope.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Sorted list of route signatures (METHOD:/path)
    """
    sigs = []
    for route in app.routes:
        try:
            path = getattr(route, "path", None)
            if not path:
                continue
            
            # Check if route is tagged as public
            tags = getattr(route, "tags", None) or []
            if "public" not in tags:
                continue
            
            # Get HTTP methods
            methods = getattr(route, "methods", None) or []
            for method in methods:
                sigs.append(f"{method}:{path}")
        except Exception:
            pass
    
    return sorted(sigs)
