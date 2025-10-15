"""
🛡️ DEFENSIVE LAYER 7: CRL VALIDATION
Blocks: Revoked License Usage, Stolen Credentials
For the Commons Good!
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional, Set
import logging
import asyncio

logger = logging.getLogger(__name__)

class CRLValidator:
    """Validates licenses against Certificate Revocation List"""
    
    def __init__(
        self,
        crl_url: str,
        cache_ttl_hours: int = 1,
        fail_open: bool = True
    ):
        """
        Initialize CRL validator
        
        Args:
            crl_url: URL to fetch CRL from
            cache_ttl_hours: Hours to cache CRL (default: 1 hour)
            fail_open: Allow requests if CRL fetch fails (default: True)
        """
        self.crl_url = crl_url
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.fail_open = fail_open
        
        self.crl_cache: Set[str] = set()
        self.cache_expiry: Optional[datetime] = None
        self._refresh_lock = asyncio.Lock()
    
    async def is_revoked(self, license_key: str) -> bool:
        """
        Check if license key is revoked
        
        Args:
            license_key: License key to check
            
        Returns:
            True if revoked, False if valid
        """
        # Refresh cache if expired
        if self._should_refresh_cache():
            await self._refresh_crl()
        
        # Check if license is in revocation list
        return license_key in self.crl_cache
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refresh"""
        if not self.crl_cache or self.cache_expiry is None:
            return True
        return datetime.now() > self.cache_expiry
    
    async def _refresh_crl(self):
        """Fetch latest CRL from server"""
        async with self._refresh_lock:
            # Double-check after acquiring lock
            if not self._should_refresh_cache():
                return
            
            try:
                logger.info(f"Fetching CRL from {self.crl_url}")
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(self.crl_url)
                    response.raise_for_status()
                    
                    # Parse CRL (expected format: {"revoked_licenses": ["key1", "key2", ...]})
                    data = response.json()
                    revoked_licenses = data.get('revoked_licenses', [])
                    
                    # Update cache
                    self.crl_cache = set(revoked_licenses)
                    self.cache_expiry = datetime.now() + self.cache_ttl
                    
                    logger.info(f"CRL updated: {len(self.crl_cache)} revoked licenses")
            
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch CRL: {e}")
                
                if self.fail_open:
                    # Fail-open: Allow requests if CRL fetch fails
                    logger.warning("CRL fetch failed, failing open (allowing requests)")
                    self.crl_cache = set()
                    self.cache_expiry = datetime.now() + timedelta(minutes=5)
                else:
                    # Fail-closed: Block all requests if CRL fetch fails
                    logger.error("CRL fetch failed, failing closed (blocking all requests)")
                    raise
            
            except Exception as e:
                logger.error(f"Unexpected error fetching CRL: {e}")
                
                if self.fail_open:
                    self.crl_cache = set()
                    self.cache_expiry = datetime.now() + timedelta(minutes=5)
                else:
                    raise
    
    async def force_refresh(self):
        """Force immediate CRL refresh"""
        self.cache_expiry = None
        await self._refresh_crl()

# Global CRL validator instance
crl_validator: Optional[CRLValidator] = None

def init_crl_validator(crl_url: str, **kwargs) -> CRLValidator:
    """
    Initialize global CRL validator
    
    Args:
        crl_url: URL to fetch CRL from
        **kwargs: Additional arguments for CRLValidator
        
    Returns:
        Initialized CRL validator
    """
    global crl_validator
    crl_validator = CRLValidator(crl_url, **kwargs)
    return crl_validator

async def is_license_revoked(license_key: str) -> bool:
    """
    Convenience function to check if license is revoked
    
    Args:
        license_key: License key to check
        
    Returns:
        True if revoked, False if valid
    """
    if crl_validator is None:
        logger.warning("CRL validator not initialized, assuming license is valid")
        return False
    
    return await crl_validator.is_revoked(license_key)
