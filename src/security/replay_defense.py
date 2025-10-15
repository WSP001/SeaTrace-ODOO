"""
🛡️ DEFENSIVE LAYER 4: REPLAY ATTACK DEFENSE
Blocks: Replay Attacks, Token Reuse
For the Commons Good!
"""

import time
from typing import Optional, Set
from fastapi import HTTPException
import asyncio

# In-memory nonce cache (use Redis in production)
_nonce_cache: Set[str] = set()
_cache_lock = asyncio.Lock()

class NonceValidator:
    """Validates nonces to prevent replay attacks"""
    
    def __init__(self, max_age_seconds: int = 300):
        """
        Initialize nonce validator
        
        Args:
            max_age_seconds: Maximum age of valid requests (default: 5 minutes)
        """
        self.max_age_seconds = max_age_seconds
        self.nonce_cache: Set[str] = set()
    
    async def verify_nonce(self, nonce: str, timestamp: int) -> bool:
        """
        Verify nonce is unique and timestamp is recent
        
        Args:
            nonce: Unique nonce value
            timestamp: Unix timestamp of request
            
        Returns:
            True if valid, raises HTTPException if invalid
        """
        current_time = int(time.time())
        
        # Check if timestamp is too old
        age = current_time - timestamp
        if age > self.max_age_seconds:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "request_expired",
                    "message": f"Request timestamp is too old ({age}s > {self.max_age_seconds}s)",
                    "timestamp": timestamp,
                    "current_time": current_time
                }
            )
        
        # Check if timestamp is in the future (clock skew)
        if age < -60:  # Allow 60 seconds clock skew
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_timestamp",
                    "message": "Request timestamp is in the future",
                    "timestamp": timestamp,
                    "current_time": current_time
                }
            )
        
        # Check if nonce was already used
        async with _cache_lock:
            if nonce in self.nonce_cache:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "replay_attack_detected",
                        "message": "Nonce has already been used",
                        "nonce": nonce[:16] + "..."  # Don't leak full nonce
                    }
                )
            
            # Store nonce
            self.nonce_cache.add(nonce)
        
        # Schedule cleanup of old nonces
        asyncio.create_task(self._cleanup_old_nonces(nonce, self.max_age_seconds))
        
        return True
    
    async def _cleanup_old_nonces(self, nonce: str, ttl: int):
        """Remove nonce from cache after TTL expires"""
        await asyncio.sleep(ttl)
        async with _cache_lock:
            self.nonce_cache.discard(nonce)

# Global nonce validator instance
nonce_validator = NonceValidator(max_age_seconds=300)

async def verify_request_freshness(nonce: str, timestamp: int) -> bool:
    """
    Convenience function to verify request freshness
    
    Args:
        nonce: Unique nonce value
        timestamp: Unix timestamp of request
        
    Returns:
        True if valid, raises HTTPException if invalid
    """
    return await nonce_validator.verify_nonce(nonce, timestamp)
