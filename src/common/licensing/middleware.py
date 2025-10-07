"""License enforcement middleware for SeaTrace-ODOO.

This middleware validates license tokens (PUL and PL) using Ed25519 signatures
and enforces scope restrictions to prevent unauthorized access to premium features.
"""

import asyncio
import base64
import json
import time
import uuid
from typing import Dict, Optional, Set

import structlog
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

try:
    import nacl.signing
    import nacl.exceptions
except ImportError:
    raise ImportError("PyNaCl required: pip install pynacl")

logger = structlog.get_logger()


class LicenseValidationError(Exception):
    """Raised when license validation fails."""
    pass


def _b64url_decode(s: str) -> bytes:
    """Decode base64url string with proper padding.
    
    Args:
        s: Base64url encoded string
        
    Returns:
        Decoded bytes
    """
    pad = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


class LicenseMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce license restrictions on API routes.
    
    Validates license tokens and enforces scope restrictions:
    - PUL (Public Unlimited): Free access to SeaSide/DeckSide/DockSide
    - PL (Private Limited): Paid access to MarketSide premium features
    """
    
    def __init__(
        self,
        app,
        public_scope_digest: str,
        public_routes: list[str],
        verify_key: Optional[str] = None,
        crl_url: Optional[str] = None,
        verify_keys_by_kid: Optional[Dict[str, str]] = None,
    ):
        """Initialize license middleware.
        
        Args:
            app: FastAPI application
            public_scope_digest: SHA-256 digest of allowed public routes
            public_routes: List of route signatures allowed under PUL
            verify_key: Base64-encoded Ed25519 public key (default)
            crl_url: Certificate Revocation List URL (optional)
            verify_keys_by_kid: Dict of kid -> verify_key for rotation
        """
        super().__init__(app)
        self.public_digest = public_scope_digest
        self.public_routes: Set[str] = set(public_routes)
        self.verify_key = verify_key
        self.verify_keys_by_kid = verify_keys_by_kid or {}
        self.crl_url = crl_url
        self._crl_cache: Optional[dict] = None
        self._crl_cache_time: float = 0
        
    async def dispatch(self, request: Request, call_next):
        """Process request with license validation.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
            
        Returns:
            HTTP response
            
        Raises:
            HTTPException: If license validation fails
        """
        # Generate or extract correlation ID for distributed tracing
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        log = structlog.get_logger().bind(correlation_id=correlation_id)
        
        # Derive route signature "METHOD:/path"
        route_sig = f"{request.method}:{request.url.path}"
        
        # Get license token from header or Authorization Bearer
        lic_token = request.headers.get("x-st-license", "")
        if not lic_token and "authorization" in request.headers:
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                lic_token = auth.split("Bearer ")[-1]
        
        # No token: allow only public routes
        if not lic_token:
            if route_sig not in self.public_routes:
                logger.warning("license_required", route=route_sig)
                raise HTTPException(
                    status_code=403,
                    detail="License required for this endpoint"
                )
            return await call_next(request)
        
        # Verify token signature with kid support
        try:
            header, payload = await self._verify_jws(lic_token)
        except LicenseValidationError as e:
            raise HTTPException(status_code=401, detail=str(e))
        
        # Check revocation
        if await self._is_revoked(payload.get("license_id")):
            logger.error("license_revoked", 
                        license_id=payload.get("license_id"))
            raise HTTPException(
                status_code=403,
                detail="License has been revoked"
            )
        
        # Validate based on license type
        typ = payload.get("typ")
        
        if typ == "PUL":
            # Public Unlimited License
            await self._validate_pul(payload, route_sig)
            
        elif typ == "PL":
            # Private Limited License
            await self._validate_pl(request, payload, route_sig)
            
        else:
            logger.error("license_type_unsupported", type=typ)
            raise HTTPException(
                status_code=403,
                detail=f"Unsupported license type: {typ}"
            )
        
        # Attach license claims to request state
        request.state.license_claims = payload
        
        # Add license headers to response
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-License-Type"] = payload.get("typ", "unknown")
        response.headers["X-License-Id"] = payload.get("license_id", "")
        response.headers["X-License-Org"] = payload.get("org", "")
        if payload.get("tier"):
            response.headers["X-License-Tier"] = payload.get("tier")
        
        # Add quota warning if present
        if hasattr(request.state, "quota_warning"):
            response.headers["X-Quota-Warning"] = request.state.quota_warning
        
        return response
    
    async def _verify_jws(self, token: str) -> tuple[dict, dict]:
        """Verify JWS token with kid support.
        
        Args:
            token: JWS compact serialization
            
        Returns:
            Tuple of (header, payload)
            
        Raises:
            LicenseValidationError: If verification fails
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise LicenseValidationError("Invalid token format")
        
        h64, p64, s64 = parts
        
        # Decode and validate header
        header = json.loads(_b64url_decode(h64))
        if header.get("alg") not in ("EdDSA", "Ed25519"):
            raise LicenseValidationError(
                f"Unsupported alg; require EdDSA/Ed25519, got {header.get('alg')}"
            )
        
        # Get verify key by kid
        kid = header.get("kid")
        verify_key_b64 = self.verify_keys_by_kid.get(kid) or self.verify_key
        if not verify_key_b64:
            raise LicenseValidationError(f"Unknown key id (kid): {kid}")
        
        # Verify signature (constant-time to prevent timing attacks)
        message = f"{h64}.{p64}".encode()
        signature = _b64url_decode(s64)
        
        try:
            verify_key = nacl.signing.VerifyKey(base64.b64decode(verify_key_b64))
            verify_key.verify(message, signature)
            valid = True
        except nacl.exceptions.BadSignatureError:
            valid = False
        
        # Constant-time delay to prevent timing attacks
        # Ed25519 verification is already constant-time, but exception
        # handling adds timing variance. Add small delay to normalize.
        await asyncio.sleep(0.001)  # 1ms constant delay (async-safe)
        
        if not valid:
            raise LicenseValidationError("Invalid license signature")
        
        # Decode payload
        payload = json.loads(_b64url_decode(p64))
        
        # Check expiry
        exp = payload.get("exp", 0)
        if exp and time.time() > exp:
            raise LicenseValidationError("License expired")
        
        logger.info("license_verified",
                   license_type=payload.get("typ"),
                   license_id=payload.get("license_id"),
                   kid=kid)
        
        return header, payload
    
    async def _validate_pul(self, payload: dict, route_sig: str):
        """Validate Public Unlimited License.
        
        Args:
            payload: Decoded license token payload
            route_sig: Route signature (METHOD:/path)
            
        Raises:
            HTTPException: If validation fails
        """
        # Check scope digest
        if payload.get("scope_digest") != self.public_digest:
            logger.error("pul_scope_mismatch",
                        expected=self.public_digest,
                        actual=payload.get("scope_digest"))
            raise HTTPException(
                status_code=403,
                detail="License scope digest mismatch"
            )
        
        # Check route is in public scope
        if route_sig not in self.public_routes:
            logger.warning("pul_route_denied", route=route_sig)
            raise HTTPException(
                status_code=403,
                detail="Route not in public scope"
            )
        
        # Check expiry
        exp = payload.get("exp", 0)
        if time.time() > exp:
            logger.error("pul_expired", license_id=payload.get("license_id"))
            raise HTTPException(
                status_code=403,
                detail="License expired"
            )
    
    async def _validate_pl(self, request: Request, payload: dict, route_sig: str):
        """Validate Private Limited License.
        
        Args:
            request: FastAPI request object
            payload: Decoded license token payload
            route_sig: Route signature (METHOD:/path)
            
        Raises:
            HTTPException: If validation fails
        """
        # Check expiry with grace period
        exp = payload.get("exp", 0)
        grace_period = 14 * 24 * 3600  # 14 days
        
        if exp and time.time() > exp + grace_period:
            logger.error("pl_expired_beyond_grace",
                        license_id=payload.get("license_id"))
            raise HTTPException(
                status_code=403,
                detail="License expired (beyond grace period)"
            )
        elif exp and time.time() > exp:
            # In grace period - allow but warn
            days_remaining = int((exp + grace_period - time.time()) / 86400)
            logger.warning("pl_grace_period",
                          license_id=payload.get("license_id"),
                          days_remaining=days_remaining)
        
        # Check domain binding (if specified)
        domain_bind = payload.get("domain_bind", [])
        if domain_bind:
            host = request.headers.get("host", "").split(":")[0].lower()
            if host not in [d.lower() for d in domain_bind]:
                logger.error("pl_domain_mismatch",
                            expected=domain_bind,
                            actual=host)
                raise HTTPException(
                    status_code=403,
                    detail="Domain not authorized for this license"
                )
        
        # Detailed entitlement checks handled by endpoint decorators
        # (features, limits, etc.)
    
    async def _is_revoked(self, license_id: Optional[str]) -> bool:
        """Check if license is revoked using CRL.
        
        Args:
            license_id: License identifier
            
        Returns:
            True if revoked, False otherwise
        """
        if not license_id or not self.crl_url:
            return False
        
        # Cache CRL for 24 hours
        cache_ttl = 24 * 3600
        now = time.time()
        
        if not self._crl_cache or now - self._crl_cache_time > cache_ttl:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(self.crl_url, timeout=5.0)
                    resp.raise_for_status()
                    self._crl_cache = resp.json()
                    self._crl_cache_time = now
                    logger.info("crl_refreshed", url=self.crl_url)
            except Exception as e:
                logger.error("crl_fetch_failed", error=str(e))
                # Fail open on CRL fetch errors
                return False
        
        # Check if license is in revoked list
        revoked_list = self._crl_cache.get("revoked", [])
        for entry in revoked_list:
            if entry.get("license_id") == license_id:
                logger.warning("license_revoked_crl",
                              license_id=license_id,
                              reason=entry.get("reason"))
                return True
        
        return False


def require_feature(feature: str):
    """Decorator to require specific feature entitlement.
    
    Usage:
        @app.post("/api/v1/marketside/trade")
        @require_feature("trade")
        async def create_trade(request: Request):
            ...
    
    Args:
        feature: Required feature name
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")
            
            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Request object not found"
                )
            
            # Check license claims
            claims = getattr(request.state, "license_claims", None)
            if not claims or claims.get("typ") != "PL":
                logger.error("feature_requires_pl", feature=feature)
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{feature}' requires Private-Limited license"
                )
            
            # Check feature entitlement
            features = claims.get("features", [])
            if feature not in features:
                logger.warning("feature_not_entitled",
                              feature=feature,
                              license_id=claims.get("license_id"))
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{feature}' not enabled in your license"
                )
            
            # Check expiry
            if time.time() > claims.get("exp", 0):
                raise HTTPException(
                    status_code=403,
                    detail="License expired"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
