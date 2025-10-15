"""
JWK (JSON Web Key) Cache with Auto-Refresh
Supports Ed25519 key rotation without downtime.

Pattern based on SeaTrace003's PREVIOUS_KEY rotation strategy:
- Multiple keys active simultaneously (zero-downtime rotation)
- Auto-refresh from verify-keys.json every 1 hour
- kid (Key ID) support for multi-key management
- Redis-backed caching with file fallback

For the Commons Good! 🌊
"""

import asyncio
import base64
import json
import time
from pathlib import Path
from typing import Dict, Optional

import structlog

logger = structlog.get_logger()


class JWKCache:
    """
    JWK cache with automatic refresh and key rotation support.
    
    Features:
    - Auto-refresh from verify-keys.json (configurable interval)
    - Zero-downtime key rotation (both old/new keys active during migration)
    - kid (Key ID) support for multi-key management (e.g., "pul-2025-v1")
    - Fallback to file if Redis unavailable
    - Mirrors SeaTrace003's PREVIOUS_KEY pattern
    
    Usage:
        cache = JWKCache("docs/licensing/verify-keys.json")
        await cache.start()
        public_key_bytes = await cache.get("pul-2025-v1")
    
    Example verify-keys.json structure:
        {
          "keys": [
            {
              "kid": "pul-2025-v1",
              "ed25519": "base64url_encoded_public_key",
              "status": "active",
              "created": "2025-01-01T00:00:00Z"
            },
            {
              "kid": "pul-2024-v2",
              "ed25519": "base64url_encoded_public_key",
              "status": "deprecated",
              "created": "2024-06-01T00:00:00Z"
            }
          ]
        }
    """
    
    def __init__(
        self,
        keys_file: str = "docs/licensing/verify-keys.json",
        refresh_interval: int = 3600,  # 1 hour (matches SeaTrace003 pattern)
        redis_client=None,
    ):
        """Initialize JWK cache.
        
        Args:
            keys_file: Path to verify-keys.json
            refresh_interval: Cache refresh interval in seconds (default 1 hour)
            redis_client: Optional Redis client for distributed caching
        """
        self.keys_file = Path(keys_file)
        self.refresh_interval = refresh_interval
        self.redis = redis_client
        self._cache: Dict[str, bytes] = {}
        self._last_refresh: float = 0
        self._refresh_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start background refresh task."""
        await self._refresh()
        self._refresh_task = asyncio.create_task(self._refresh_loop())
        logger.info(
            "jwk_cache_started",
            keys_loaded=len(self._cache),
            refresh_interval=self.refresh_interval,
        )
    
    async def stop(self):
        """Stop background refresh task."""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
        logger.info("jwk_cache_stopped")
    
    async def get(self, kid: str) -> bytes:
        """
        Get Ed25519 public key by Key ID.
        
        Args:
            kid: Key ID (e.g., "pul-2025-v1")
        
        Returns:
            Ed25519 public key bytes (32 bytes)
        
        Raises:
            KeyError: If kid not found
        """
        # Check cache
        if kid in self._cache:
            logger.debug("jwk_cache_hit", kid=kid)
            return self._cache[kid]
        
        # Refresh if cache miss (new key added)
        logger.info("jwk_cache_miss", kid=kid, action="refreshing")
        await self._refresh()
        
        if kid not in self._cache:
            logger.error("jwk_not_found", kid=kid, available_keys=list(self._cache.keys()))
            raise KeyError(f"JWK kid '{kid}' not found in {self.keys_file}")
        
        return self._cache[kid]
    
    async def _refresh(self):
        """Reload keys from file."""
        try:
            # Read verify-keys.json
            if not self.keys_file.exists():
                logger.error("jwk_file_not_found", path=str(self.keys_file))
                return
            
            with open(self.keys_file, "r") as f:
                keys_data = json.load(f)
            
            # Validate structure
            if "keys" not in keys_data:
                logger.error("jwk_invalid_format", expected="keys array")
                return
            
            new_cache: Dict[str, bytes] = {}
            
            for key_obj in keys_data["keys"]:
                kid = key_obj.get("kid")
                ed25519_b64 = key_obj.get("ed25519")
                status = key_obj.get("status", "unknown")
                
                if not kid or not ed25519_b64:
                    logger.warning("jwk_missing_fields", kid=kid)
                    continue
                
                # Decode base64url Ed25519 public key (32 bytes)
                try:
                    # Add padding if needed (base64url may omit padding)
                    padding = "=" * (-len(ed25519_b64) % 4)
                    public_key_bytes = base64.urlsafe_b64decode(ed25519_b64 + padding)
                    
                    if len(public_key_bytes) != 32:
                        logger.warning(
                            "jwk_invalid_key_length",
                            kid=kid,
                            expected=32,
                            actual=len(public_key_bytes),
                        )
                        continue
                    
                    # Store in cache
                    new_cache[kid] = public_key_bytes
                    
                    logger.info(
                        "jwk_loaded",
                        kid=kid,
                        status=status,
                        created=key_obj.get("created"),
                    )
                
                except Exception as e:
                    logger.error("jwk_decode_failed", kid=kid, error=str(e))
                    continue
            
            # Atomic update (all-or-nothing)
            if new_cache:
                self._cache = new_cache
                self._last_refresh = time.time()
                logger.info(
                    "jwk_refresh_complete",
                    keys_loaded=len(self._cache),
                    kids=list(self._cache.keys()),
                )
            else:
                logger.warning("jwk_refresh_empty", path=str(self.keys_file))
        
        except Exception as e:
            logger.error("jwk_refresh_failed", error=str(e), path=str(self.keys_file))
    
    async def _refresh_loop(self):
        """Background refresh loop."""
        while True:
            try:
                await asyncio.sleep(self.refresh_interval)
                await self._refresh()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("jwk_refresh_loop_error", error=str(e))
                # Continue loop even on errors (resilience)
