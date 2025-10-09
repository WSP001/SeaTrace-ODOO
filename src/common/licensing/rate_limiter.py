"""Per-license rate limiting to prevent abuse while maintaining Commons Good access.

This module implements Redis-based rate limiting that complements the existing
fair-use priority system (priority.py semaphores). 

Key Differences:
- Semaphores (priority.py): Limit CONCURRENT requests (2-8 per pillar)
- Rate Limiter (this file): Limit TOTAL requests per minute (100-10k per license)

Commons Good Alignment:
- Free users (PUL): 100 req/min ensures fair access for everyone
- Sponsors (PL-B/P/E): Higher limits reward support without blocking free users
- All users eventually process (no paywalls, just priority + rate limits)
"""

import structlog
from typing import Optional
from fastapi import HTTPException, Request

logger = structlog.get_logger(__name__)


class LicenseRateLimiter:
    """Redis-based per-license rate limiting with tier-based quotas."""
    
    # Rate limits by license tier (requests per minute)
    LIMITS = {
        "PUL": 100,        # Public Unlimited: 100 req/min (fair-use)
        "PL-B": 1000,      # Private Limited Basic: 1k req/min
        "PL-P": 10000,     # Private Limited Pro: 10k req/min
        "PL-E": None       # Private Limited Enterprise: Unlimited
    }
    
    def __init__(self, redis_client):
        """Initialize rate limiter.
        
        Args:
            redis_client: Async Redis client for rate limit tracking
        """
        self.redis = redis_client
        logger.info("rate_limiter_initialized", limits=self.LIMITS)
    
    async def check_rate_limit(
        self,
        license_id: str,
        license_type: str,
        tier: Optional[str],
        pillar: str,
        request: Request
    ):
        """Check and enforce rate limit for a license.
        
        Args:
            license_id: Unique license identifier
            license_type: "PUL" or "PL"
            tier: License tier (e.g., "PL-B", "PL-P", "PL-E")
            pillar: Service pillar (seaside, deckside, dockside, marketside)
            request: FastAPI request object
        
        Raises:
            HTTPException: 429 Too Many Requests if limit exceeded
        
        Performance:
            - Redis INCR: ~1ms
            - Redis EXPIRE: ~0.5ms
            - Total overhead: ~1.5ms per request
        """
        # Determine effective tier
        effective_tier = tier if tier else license_type
        
        # Enterprise tier = unlimited
        if effective_tier == "PL-E":
            return
        
        # Get limit for this tier
        limit = self.LIMITS.get(effective_tier, self.LIMITS["PUL"])
        
        # Redis key: ratelimit:{license_id}:{pillar}
        # Separate limits per pillar (prevent cross-pillar DOS)
        key = f"ratelimit:{license_id}:{pillar}"
        
        try:
            # Increment request count
            current = await self.redis.incr(key)
            
            # Set 60-second expiry on first request
            if current == 1:
                await self.redis.expire(key, 60)
            
            # Get TTL for X-RateLimit-Reset header
            ttl = await self.redis.ttl(key)
            
            # Check if limit exceeded
            if current > limit:
                logger.warning(
                    "rate_limit_exceeded",
                    license_id=license_id[:16] + "...",
                    license_type=effective_tier,
                    pillar=pillar,
                    current=current,
                    limit=limit,
                    path=request.url.path
                )
                
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": f"Rate limit exceeded: {current}/{limit} requests per minute",
                        "license_type": effective_tier,
                        "pillar": pillar,
                        "limit": limit,
                        "current": current,
                        "reset_in_seconds": ttl,
                        "upgrade_info": {
                            "message": "Upgrade to Private Limited for higher limits",
                            "tiers": {
                                "PL-B": "1,000 req/min",
                                "PL-P": "10,000 req/min",
                                "PL-E": "Unlimited"
                            },
                            "contact": "https://worldseafoodproducers.com/licensing"
                        } if effective_tier == "PUL" else None
                    },
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(ttl),
                        "Retry-After": str(ttl)
                    }
                )
            
            # Log rate limit info (debug level)
            logger.debug(
                "rate_limit_check",
                license_id=license_id[:16] + "...",
                license_type=effective_tier,
                pillar=pillar,
                current=current,
                limit=limit,
                remaining=limit - current
            )
        
        except HTTPException:
            raise  # Re-raise 429 errors
        except Exception as e:
            # Fail open on Redis errors (don't block access)
            logger.error(
                "rate_limit_check_failed",
                error=str(e),
                license_id=license_id[:16] + "..."
            )
    
    async def get_current_usage(self, license_id: str, pillar: str) -> dict:
        """Get current rate limit usage for a license.
        
        Args:
            license_id: License identifier
            pillar: Service pillar
        
        Returns:
            dict with current usage, limit, remaining, reset time
        """
        key = f"ratelimit:{license_id}:{pillar}"
        
        try:
            current = await self.redis.get(key)
            ttl = await self.redis.ttl(key)
            
            # Determine tier from license (would need license lookup in production)
            # For now, default to PUL
            limit = self.LIMITS["PUL"]
            
            return {
                "current": int(current) if current else 0,
                "limit": limit,
                "remaining": max(0, limit - (int(current) if current else 0)),
                "reset_in_seconds": ttl if ttl > 0 else 0
            }
        except Exception as e:
            logger.error("get_rate_limit_usage_failed", error=str(e))
            return {"current": 0, "limit": 0, "remaining": 0, "reset_in_seconds": 0}
    
    async def reset_license_rate_limit(self, license_id: str, pillar: Optional[str] = None):
        """Reset rate limit for a license (admin operation).
        
        Args:
            license_id: License identifier
            pillar: Specific pillar to reset, or None for all pillars
        """
        if pillar:
            key = f"ratelimit:{license_id}:{pillar}"
            await self.redis.delete(key)
            logger.info("rate_limit_reset", license_id=license_id[:16] + "...", pillar=pillar)
        else:
            # Reset all pillars
            pillars = ["seaside", "deckside", "dockside", "marketside"]
            for p in pillars:
                key = f"ratelimit:{license_id}:{p}"
                await self.redis.delete(key)
            logger.info("rate_limit_reset_all", license_id=license_id[:16] + "...")
