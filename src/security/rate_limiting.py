"""
🛡️ DEFENSIVE LAYER 1: RATE LIMITING
Blocks: DDoS, Brute Force
For the Commons Good!
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"]  # Global default
)

# Endpoint-specific rate limits
RATE_LIMITS = {
    'verify_license': '100/minute',
    'login': '10/minute',
    'register': '5/minute',
    'health': '1000/minute',
    'public': '500/minute',
}

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else 60
        }
    )

def get_rate_limit(endpoint: str) -> str:
    """Get rate limit for specific endpoint"""
    return RATE_LIMITS.get(endpoint, "100/minute")
