"""Entitlement gates and quota enforcement for MarketSide premium features.

This module provides decorators and utilities to enforce feature entitlements
and usage quotas for Private-Limited (PL) license holders.
"""

import time
from functools import wraps
from typing import Callable, Optional

import structlog
from fastapi import HTTPException, Request
from prometheus_client import Counter, Gauge

logger = structlog.get_logger()

# Prometheus metrics
FEATURE_DENIED = Counter(
    "st_feature_denied_total",
    "Total feature access denials",
    ["feature", "reason"]
)
QUOTA_EXCEEDED = Counter(
    "st_quota_exceeded_total",
    "Total quota exceeded events",
    ["resource", "org"]
)
OVERAGE_INCURRED = Counter(
    "st_overage_incurred_total",
    "Total overage events",
    ["resource", "org"]
)
OVERAGE_COST_USD = Gauge(
    "st_overage_cost_usd",
    "Overage costs in USD",
    ["org"]
)


def require_feature(feature: str):
    """Decorator to require specific feature entitlement.
    
    Validates that the request has a valid PL license with the required feature.
    
    Usage:
        @app.post("/api/v1/marketside/trade")
        @require_feature("trade")
        async def create_trade(request: Request, data: TradeData):
            ...
    
    Args:
        feature: Required feature name (e.g., "trade", "pricing", "settlement")
        
    Returns:
        Decorator function
        
    Raises:
        HTTPException: 403 if feature not entitled or license invalid
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = _extract_request(args, kwargs)
            
            # Get license claims from request state
            claims = getattr(request.state, "license_claims", None)
            
            if not claims:
                FEATURE_DENIED.labels(feature=feature, reason="no_license").inc()
                logger.error("feature_requires_license", feature=feature)
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{feature}' requires a valid license"
                )
            
            # Check license type
            if claims.get("typ") != "PL":
                FEATURE_DENIED.labels(feature=feature, reason="wrong_license_type").inc()
                logger.error("feature_requires_pl",
                           feature=feature,
                           license_type=claims.get("typ"))
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{feature}' requires Private-Limited license"
                )
            
            # Check feature entitlement
            features = claims.get("features", [])
            if feature not in features:
                FEATURE_DENIED.labels(feature=feature, reason="not_entitled").inc()
                logger.warning("feature_not_entitled",
                             feature=feature,
                             license_id=claims.get("license_id"),
                             org=claims.get("org"))
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{feature}' not enabled in your license. "
                           f"Upgrade at https://seatrace.com/pricing"
                )
            
            # Check expiry
            exp = claims.get("exp", 0)
            if time.time() > exp:
                FEATURE_DENIED.labels(feature=feature, reason="expired").inc()
                logger.error("license_expired",
                           license_id=claims.get("license_id"))
                raise HTTPException(
                    status_code=403,
                    detail="License expired. Please renew at "
                           "https://seatrace.com/billing"
                )
            
            # Feature check passed
            logger.info("feature_granted",
                       feature=feature,
                       org=claims.get("org"),
                       license_id=claims.get("license_id"))
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def _period_key(prefix: str, license_id: str, metric: str) -> str:
    """Generate monthly period key for quota tracking.
    
    Args:
        prefix: Key prefix (e.g., 'quota')
        license_id: License identifier
        metric: Metric name (e.g., 'qr_scans')
        
    Returns:
        Period key with YYYYMM suffix
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return f"{prefix}:{license_id}:{metric}:{now:%Y%m}"


async def enforce_quota(
    request: Request,
    meter: dict,
    key: str,
    cost: int = 1,
    redis_client: Optional[object] = None,
    idempotency_key: Optional[str] = None
) -> None:
    """Enforce usage quota for a specific resource.
    
    Checks current usage against license limits and enforces overage policy.
    
    Args:
        request: FastAPI request object with license claims
        meter: Usage meter dictionary (in-memory or Redis-backed)
        key: Resource key (e.g., "qr_scans", "tx_per_month")
        cost: Usage cost to increment (default: 1)
        redis_client: Optional Redis client for distributed metering
        
    Raises:
        HTTPException: 429 if quota exceeded with throttle policy
        HTTPException: 402 if quota exceeded with block policy
    """
    claims = getattr(request.state, "license_claims", None)
    if not claims or claims.get("typ") != "PL":
        return  # No quota enforcement for non-PL licenses
    
    org = claims.get("org", "unknown")
    license_id = claims.get("license_id", "unknown")
    limits = claims.get("limits", {})
    billing = claims.get("billing", {})
    
    # Get limit for this resource
    limit = limits.get(key)
    if limit is None:
        # Unlimited for this dimension
        return
    
    # Get current usage with monthly period
    if redis_client:
        # Distributed metering via Redis with monthly buckets
        bucket = _period_key("quota", license_id, key)
        
        # Check idempotency to avoid double-counting
        if idempotency_key:
            idem_key = f"idem:{bucket}"
            seen = await redis_client.sadd(idem_key, idempotency_key)
            if not seen:
                # Duplicate request - don't meter twice
                logger.info("idempotent_request_skipped",
                          license_id=license_id,
                          key=key,
                          idempotency_key=idempotency_key)
                return
            await redis_client.expire(idem_key, 86400 * 40)  # 40 days
        
        used = int(await redis_client.get(bucket) or 0)
        new_usage = used + cost
        
        # Use pipeline for atomic update
        pipe = redis_client.pipeline()
        pipe.set(bucket, new_usage)
        pipe.expire(bucket, 86400 * 40)  # 40 days (>= 1 month)
        await pipe.execute()
    else:
        # In-memory metering (not recommended for production)
        used = meter.get(key, 0)
        new_usage = used + cost
        meter[key] = new_usage
    
    # Check if within limit
    if new_usage <= limit:
        return
    
    # Quota exceeded - apply overage policy
    overage_mode = billing.get("overage", "bill")
    overage_amount = new_usage - limit
    
    logger.warning("quota_exceeded",
                  org=org,
                  license_id=license_id,
                  resource=key,
                  limit=limit,
                  usage=new_usage,
                  overage=overage_amount,
                  policy=overage_mode)
    
    QUOTA_EXCEEDED.labels(resource=key, org=org).inc()
    
    if overage_mode == "bill":
        # Allow overage, bill later
        OVERAGE_INCURRED.labels(resource=key, org=org).inc()
        
        # Calculate overage cost
        overage_rates = {
            "qr_scans": 0.01,      # $0.01 per scan
            "tx_per_month": 0.05,  # $0.05 per transaction
            "api_calls": 0.001,    # $0.001 per API call
        }
        rate = overage_rates.get(key, 0)
        cost_usd = overage_amount * rate
        
        OVERAGE_COST_USD.labels(org=org).set(cost_usd)
        
        # Emit billing event
        await _emit_billing_event(
            license_id=license_id,
            org=org,
            event_type="overage_incurred",
            metadata={
                "resource": key,
                "limit": limit,
                "usage": new_usage,
                "overage": overage_amount,
                "cost_usd": cost_usd
            }
        )
        
        # Add warning header
        request.state.quota_warning = (
            f"Quota exceeded for {key}. "
            f"Overage: {overage_amount} units at ${rate}/unit = ${cost_usd:.2f}"
        )
        
        return  # Allow request
    
    elif overage_mode == "throttle":
        # Soft throttle - return 429
        raise HTTPException(
            status_code=429,
            detail=f"Quota exceeded for {key}. "
                   f"Limit: {limit}, Usage: {new_usage}. "
                   f"Upgrade at https://seatrace.com/pricing",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + 86400),
                "Retry-After": "86400"
            }
        )
    
    elif overage_mode == "block":
        # Hard block - return 402
        raise HTTPException(
            status_code=402,
            detail=f"Payment required. Quota exceeded for {key}. "
                   f"Please upgrade your plan at https://seatrace.com/billing"
        )


async def _emit_billing_event(
    license_id: str,
    org: str,
    event_type: str,
    metadata: dict
) -> None:
    """Emit billing event to queue or database.
    
    Args:
        license_id: License identifier
        org: Organization name
        event_type: Event type (e.g., "overage_incurred")
        metadata: Event metadata
    """
    import uuid
    from datetime import datetime
    
    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:16]}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "license_id": license_id,
        "org": org,
        "metadata": metadata
    }
    
    # TODO: Emit to Kafka/RabbitMQ/MongoDB
    logger.info("billing_event_emitted", **event)


def _extract_request(args: tuple, kwargs: dict) -> Request:
    """Extract Request object from function args/kwargs.
    
    Args:
        args: Function positional arguments
        kwargs: Function keyword arguments
        
    Returns:
        Request object
        
    Raises:
        HTTPException: 500 if Request not found
    """
    # Check args
    for arg in args:
        if isinstance(arg, Request):
            return arg
    
    # Check kwargs
    if "request" in kwargs:
        return kwargs["request"]
    
    raise HTTPException(
        status_code=500,
        detail="Request object not found in function signature"
    )


def require_tier(min_tier: str):
    """Decorator to require minimum license tier.
    
    Usage:
        @app.post("/api/v1/marketside/white-label")
        @require_tier("enterprise")
        async def create_white_label(request: Request):
            ...
    
    Args:
        min_tier: Minimum required tier ("starter", "pro", "enterprise")
        
    Returns:
        Decorator function
    """
    tier_hierarchy = {"starter": 1, "pro": 2, "enterprise": 3}
    min_level = tier_hierarchy.get(min_tier, 0)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _extract_request(args, kwargs)
            claims = getattr(request.state, "license_claims", None)
            
            if not claims or claims.get("typ") != "PL":
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires {min_tier} tier or higher"
                )
            
            current_tier = claims.get("tier", "starter")
            current_level = tier_hierarchy.get(current_tier, 0)
            
            if current_level < min_level:
                logger.warning("tier_insufficient",
                             required=min_tier,
                             current=current_tier,
                             org=claims.get("org"))
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires {min_tier} tier. "
                           f"Current tier: {current_tier}. "
                           f"Upgrade at https://seatrace.com/pricing"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
