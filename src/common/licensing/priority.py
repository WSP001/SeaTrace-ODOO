"""Priority-based concurrency controls for SeaTrace Commons.

Implements fair-use scheduling without paywalls:
- All requests eventually process (no blocking)
- Sponsor credits enable higher priority (optional)
- Concurrency limits prevent resource exhaustion
"""

import asyncio
from typing import Optional

import structlog
from fastapi import Request
from prometheus_client import Gauge, Histogram

logger = structlog.get_logger()

# Prometheus metrics
CONCURRENCY_ACTIVE = Gauge(
    "st_concurrency_active",
    "Active concurrent requests",
    ["pillar", "priority"]
)
QUEUE_WAIT_TIME = Histogram(
    "st_queue_wait_seconds",
    "Time spent waiting in queue",
    ["pillar", "priority"]
)


class PriorityManager:
    """Manages priority-based concurrency for heavy endpoints."""
    
    def __init__(self):
        """Initialize priority semaphores."""
        # SeaSide concurrency
        self.seaside_low = asyncio.Semaphore(2)
        self.seaside_sponsor = asyncio.Semaphore(8)
        
        # DeckSide concurrency
        self.deckside_low = asyncio.Semaphore(2)
        self.deckside_sponsor = asyncio.Semaphore(8)
        
        # DockSide concurrency
        self.dockside_low = asyncio.Semaphore(2)
        self.dockside_sponsor = asyncio.Semaphore(8)
    
    def get_semaphore(
        self,
        pillar: str,
        request: Request
    ) -> asyncio.Semaphore:
        """Get appropriate semaphore based on priority.
        
        Args:
            pillar: Pillar name (seaside, deckside, dockside)
            request: FastAPI request with license claims
            
        Returns:
            Semaphore for concurrency control
        """
        claims = getattr(request.state, "license_claims", None) or {}
        
        # Determine priority
        is_sponsor = self._is_sponsor(claims)
        
        # Select semaphore
        if pillar == "seaside":
            sem = self.seaside_sponsor if is_sponsor else self.seaside_low
        elif pillar == "deckside":
            sem = self.deckside_sponsor if is_sponsor else self.deckside_low
        elif pillar == "dockside":
            sem = self.dockside_sponsor if is_sponsor else self.dockside_low
        else:
            # Default to low priority
            sem = self.deckside_low
        
        return sem
    
    def _is_sponsor(self, claims: dict) -> bool:
        """Check if request has sponsor priority.
        
        Args:
            claims: License token claims
            
        Returns:
            True if sponsor priority, False otherwise
        """
        # PL licenses always get sponsor priority
        if claims.get("typ") == "PL":
            return True
        
        # PUL with sponsor credits
        if claims.get("typ") == "PUL":
            priority = claims.get("priority")
            credits = claims.get("credits")
            if priority == "sponsor" or credits:
                return True
        
        return False


async def with_priority(
    pillar: str,
    request: Request,
    priority_manager: PriorityManager
):
    """Context manager for priority-based concurrency.
    
    Usage:
        async with with_priority("deckside", request, app.state.priority_mgr):
            # Heavy operation
            pass
    
    Args:
        pillar: Pillar name
        request: FastAPI request
        priority_manager: PriorityManager instance
    """
    claims = getattr(request.state, "license_claims", None) or {}
    is_sponsor = priority_manager._is_sponsor(claims)
    priority = "sponsor" if is_sponsor else "low"
    
    sem = priority_manager.get_semaphore(pillar, request)
    
    # Track queue wait time
    import time
    start_wait = time.time()
    
    async with sem:
        wait_time = time.time() - start_wait
        
        # Record metrics
        CONCURRENCY_ACTIVE.labels(pillar=pillar, priority=priority).inc()
        QUEUE_WAIT_TIME.labels(pillar=pillar, priority=priority).observe(wait_time)
        
        # Add queue info to response headers
        if wait_time > 1.0:
            request.state.queue_wait_time = wait_time
        
        logger.info("priority_acquired",
                   pillar=pillar,
                   priority=priority,
                   wait_time=wait_time)
        
        try:
            yield
        finally:
            CONCURRENCY_ACTIVE.labels(pillar=pillar, priority=priority).dec()


def check_sponsor_credits(
    request: Request,
    resource: str,
    cost: int = 1
) -> bool:
    """Check and decrement sponsor credits.
    
    Args:
        request: FastAPI request with license claims
        resource: Resource key (e.g., "deckside_batch_mb")
        cost: Cost to deduct
        
    Returns:
        True if credits available, False otherwise
    """
    claims = getattr(request.state, "license_claims", None) or {}
    
    # PL licenses have unlimited credits
    if claims.get("typ") == "PL":
        return True
    
    # Check PUL sponsor credits
    if claims.get("typ") == "PUL":
        credits = claims.get("credits", {})
        available = credits.get(resource, 0)
        
        if available >= cost:
            # TODO: Persist credit deduction to Redis/DB
            logger.info("sponsor_credits_used",
                       resource=resource,
                       cost=cost,
                       remaining=available - cost)
            return True
    
    return False
