"""
🏈 SeaTrace Rate Limiting (Defensive Line)
For the Commons Good! 🌊

Sliding window rate limiter for in-memory protection.
Production: Use Redis with slowapi for distributed rate limiting.
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque

# Default limits
WINDOW = 60  # seconds
LIMIT = 60   # requests per window

# In-memory buckets (use Redis in production)
buckets: Dict[str, Deque[float]] = defaultdict(lambda: deque())
_lock = asyncio.Lock()

async def allow(key: str, limit: int = LIMIT, window: int = WINDOW) -> bool:
    """
    Check if request is allowed under rate limit.
    
    Args:
        key: Unique identifier (e.g., "login:192.168.1.1")
        limit: Max requests per window
        window: Time window in seconds
    
    Returns:
        True if allowed, False if rate limited
    """
    async with _lock:
        now = time.time()
        q = buckets[key]
        
        # Remove expired timestamps
        while q and now - q[0] > window:
            q.popleft()
        
        # Check limit
        if len(q) >= limit:
            return False
        
        # Add current request
        q.append(now)
        return True

async def reset(key: str) -> None:
    """Reset rate limit for a key"""
    async with _lock:
        if key in buckets:
            del buckets[key]

def get_remaining(key: str, limit: int = LIMIT, window: int = WINDOW) -> int:
    """Get remaining requests in current window"""
    now = time.time()
    q = buckets.get(key, deque())
    
    # Count valid requests
    valid = sum(1 for ts in q if now - ts <= window)
    return max(0, limit - valid)
