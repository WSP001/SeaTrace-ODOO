"""CRL (Certificate Revocation List) Management API for SeaTrace-ODOO administrators.

This module provides secure endpoints for immediate license revocation, restoration,
and CRL inspection. All operations require admin authentication.

Security:
- Admin tokens use Ed25519 signatures with "admin" scope
- All operations logged with structlog for audit trail
- Bloom filter automatically marked stale after modifications

Commons Good:
- Transparent revocation process (public CRL list endpoint)
- Immediate enforcement (no grace periods for abuse)
- Restoration process for false positives
"""

import structlog
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/admin/crl", tags=["admin", "crl"])


# ============================================================================
# Request Models
# ============================================================================

class RevokeLicenseRequest(BaseModel):
    """Request to revoke a license."""
    reason: str
    revoked_by: str
    notes: Optional[str] = None


class RevocationResponse(BaseModel):
    """Response for revocation operations."""
    status: str
    license_id: str
    timestamp: str
    message: str


class CRLEntry(BaseModel):
    """Single CRL entry with metadata."""
    license_id: str
    revoked_at: str
    reason: str
    revoked_by: str
    notes: Optional[str]


class CRLListResponse(BaseModel):
    """Full CRL list response."""
    revoked_licenses: list[str]
    total_count: int
    with_metadata: Optional[list[CRLEntry]]


# ============================================================================
# Admin Authentication (TODO: Replace with real implementation)
# ============================================================================

async def verify_admin_token(request: Request) -> dict:
    """Verify admin token and return claims.
    
    TODO: Implement Ed25519 signature verification with "admin" scope check.
    For now, this is a placeholder that checks for Authorization header.
    
    In production:
    1. Extract JWT from Authorization: Bearer <token>
    2. Verify Ed25519 signature using admin public key
    3. Check claims["scope"] includes "admin"
    4. Check claims["exp"] > now
    5. Return claims dict
    
    Raises:
        HTTPException: 401 if token invalid, 403 if not admin
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    # TODO: Real Ed25519 verification
    token = auth_header[7:]  # Remove "Bearer "
    
    # Placeholder: Accept any token for development
    # In production, this would verify signature and check scope
    return {
        "sub": "admin",
        "scope": "admin",
        "exp": 9999999999
    }


# ============================================================================
# CRL Management Endpoints
# ============================================================================

@router.post("/revoke/{license_id}", response_model=RevocationResponse)
async def revoke_license(
    license_id: str,
    request: RevokeLicenseRequest,
    admin_claims: dict = Depends(verify_admin_token)
):
    """Revoke a license immediately (added to CRL).
    
    Args:
        license_id: License to revoke
        request: Revocation details (reason, admin name, notes)
        admin_claims: Admin JWT claims (from dependency)
    
    Returns:
        RevocationResponse with status and timestamp
    
    Example:
        POST /admin/crl/revoke/pul-abc123
        {
            "reason": "Terms of Service violation - spam",
            "revoked_by": "admin@worldseafoodproducers.com",
            "notes": "User sent 10k requests in 1 minute"
        }
    """
    from fastapi import FastAPI
    
    # Get Redis and Bloom CRL from app state
    app: FastAPI = request.app
    redis = app.state.redis
    bloom_crl = app.state.bloom_crl
    
    try:
        # Add to Redis CRL set
        await redis.sadd("license_crl", license_id)
        
        # Store revocation metadata
        metadata_key = f"license_crl_metadata:{license_id}"
        metadata = {
            "revoked_at": datetime.utcnow().isoformat(),
            "reason": request.reason,
            "revoked_by": request.revoked_by,
            "notes": request.notes or ""
        }
        await redis.hset(metadata_key, mapping=metadata)
        
        # Mark Bloom filter stale (will rebuild on next check)
        await bloom_crl.mark_stale()
        
        logger.info(
            "license_revoked",
            license_id=license_id[:16] + "...",
            reason=request.reason,
            revoked_by=request.revoked_by,
            admin_sub=admin_claims.get("sub")
        )
        
        return RevocationResponse(
            status="revoked",
            license_id=license_id,
            timestamp=metadata["revoked_at"],
            message=f"License {license_id} revoked successfully"
        )
    
    except Exception as e:
        logger.error("license_revocation_failed", error=str(e), license_id=license_id[:16] + "...")
        raise HTTPException(status_code=500, detail=f"Revocation failed: {str(e)}")


@router.delete("/revoke/{license_id}", response_model=RevocationResponse)
async def unrevoke_license(
    license_id: str,
    request: Request,
    admin_claims: dict = Depends(verify_admin_token)
):
    """Restore a revoked license (remove from CRL).
    
    Args:
        license_id: License to restore
        admin_claims: Admin JWT claims
    
    Returns:
        RevocationResponse with restoration status
    
    Example:
        DELETE /admin/crl/revoke/pul-abc123
    """
    from fastapi import FastAPI
    
    app: FastAPI = request.app
    redis = app.state.redis
    bloom_crl = app.state.bloom_crl
    
    try:
        # Remove from Redis CRL set
        removed = await redis.srem("license_crl", license_id)
        
        if removed == 0:
            raise HTTPException(status_code=404, detail=f"License {license_id} not found in CRL")
        
        # Remove metadata
        metadata_key = f"license_crl_metadata:{license_id}"
        await redis.delete(metadata_key)
        
        # Mark Bloom filter stale
        await bloom_crl.mark_stale()
        
        logger.info(
            "license_restored",
            license_id=license_id[:16] + "...",
            admin_sub=admin_claims.get("sub")
        )
        
        return RevocationResponse(
            status="restored",
            license_id=license_id,
            timestamp=datetime.utcnow().isoformat(),
            message=f"License {license_id} restored successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("license_restoration_failed", error=str(e), license_id=license_id[:16] + "...")
        raise HTTPException(status_code=500, detail=f"Restoration failed: {str(e)}")


@router.get("/list", response_model=CRLListResponse)
async def list_revoked_licenses(
    request: Request,
    include_metadata: bool = False,
    admin_claims: dict = Depends(verify_admin_token)
):
    """List all revoked licenses (CRL inspection).
    
    Args:
        include_metadata: If True, fetch revocation metadata for each license
        admin_claims: Admin JWT claims
    
    Returns:
        CRLListResponse with all revoked licenses
    
    Example:
        GET /admin/crl/list?include_metadata=true
    """
    from fastapi import FastAPI
    
    app: FastAPI = request.app
    redis = app.state.redis
    
    try:
        # Fetch all revoked licenses
        crl_set = await redis.smembers("license_crl")
        revoked_licenses = sorted([
            lic.decode() if isinstance(lic, bytes) else lic 
            for lic in crl_set
        ])
        
        metadata_list = None
        
        if include_metadata:
            metadata_list = []
            for license_id in revoked_licenses:
                metadata_key = f"license_crl_metadata:{license_id}"
                metadata = await redis.hgetall(metadata_key)
                
                if metadata:
                    # Convert bytes to strings
                    metadata = {
                        k.decode() if isinstance(k, bytes) else k: 
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in metadata.items()
                    }
                    
                    metadata_list.append(CRLEntry(
                        license_id=license_id,
                        revoked_at=metadata.get("revoked_at", "unknown"),
                        reason=metadata.get("reason", "unknown"),
                        revoked_by=metadata.get("revoked_by", "unknown"),
                        notes=metadata.get("notes")
                    ))
        
        logger.info(
            "crl_list_requested",
            total_count=len(revoked_licenses),
            include_metadata=include_metadata,
            admin_sub=admin_claims.get("sub")
        )
        
        return CRLListResponse(
            revoked_licenses=revoked_licenses,
            total_count=len(revoked_licenses),
            with_metadata=metadata_list
        )
    
    except Exception as e:
        logger.error("crl_list_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"CRL list failed: {str(e)}")


@router.get("/check/{license_id}")
async def check_license_status(
    license_id: str,
    request: Request,
    admin_claims: dict = Depends(verify_admin_token)
):
    """Check if a specific license is revoked.
    
    Args:
        license_id: License to check
        admin_claims: Admin JWT claims
    
    Returns:
        dict with revocation status and metadata (if revoked)
    
    Example:
        GET /admin/crl/check/pul-abc123
    """
    from fastapi import FastAPI
    
    app: FastAPI = request.app
    redis = app.state.redis
    
    try:
        is_revoked = await redis.sismember("license_crl", license_id)
        
        result = {
            "license_id": license_id,
            "is_revoked": bool(is_revoked),
            "checked_at": datetime.utcnow().isoformat()
        }
        
        if is_revoked:
            metadata_key = f"license_crl_metadata:{license_id}"
            metadata = await redis.hgetall(metadata_key)
            
            if metadata:
                result["revocation_metadata"] = {
                    k.decode() if isinstance(k, bytes) else k:
                    v.decode() if isinstance(v, bytes) else v
                    for k, v in metadata.items()
                }
        
        return result
    
    except Exception as e:
        logger.error("crl_check_failed", error=str(e), license_id=license_id[:16] + "...")
        raise HTTPException(status_code=500, detail=f"CRL check failed: {str(e)}")


@router.get("/stats")
async def get_crl_stats(
    request: Request,
    admin_claims: dict = Depends(verify_admin_token)
):
    """Get CRL performance statistics.
    
    Args:
        admin_claims: Admin JWT claims
    
    Returns:
        dict with Bloom filter performance stats
    
    Example:
        GET /admin/crl/stats
    """
    from fastapi import FastAPI
    
    app: FastAPI = request.app
    bloom_crl = app.state.bloom_crl
    
    try:
        stats = bloom_crl.get_stats()
        return {
            "bloom_filter": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error("crl_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")
