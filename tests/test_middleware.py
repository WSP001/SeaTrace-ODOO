"""Tests for license middleware.

This test suite covers:
- JWK-based license validation with kid support
- Async safety for _verify_jws method
- Timing attack mitigation
- Token signature verification
- License expiry checks
- CRL (Certificate Revocation List) checks
"""

import asyncio
import base64
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

try:
    import nacl.signing
    import nacl.encoding
except ImportError:
    pytest.skip("PyNaCl not installed", allow_module_level=True)

from src.common.licensing.middleware import (
    LicenseMiddleware,
    LicenseValidationError,
    _b64url_decode,
)


# Test fixtures
@pytest.fixture
def signing_key():
    """Generate Ed25519 signing key for tests."""
    return nacl.signing.SigningKey.generate()


@pytest.fixture
def verify_key(signing_key):
    """Get base64-encoded public key."""
    return base64.b64encode(signing_key.verify_key.encode()).decode()


@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    
    @app.get("/public/test")
    async def public_route():
        return {"status": "ok", "type": "public"}
    
    @app.get("/private/test")
    async def private_route(request: Request):
        claims = getattr(request.state, "license_claims", {})
        return {"status": "ok", "type": "private", "claims": claims}
    
    return app


@pytest.fixture
def public_routes():
    """List of public route signatures."""
    return ["GET:/public/test"]


@pytest.fixture
def public_digest():
    """SHA-256 digest of public routes."""
    import hashlib
    routes = "GET:/public/test"
    return hashlib.sha256(routes.encode()).hexdigest()


def create_jws_token(
    payload: dict,
    signing_key,
    kid: str = "key-001",
    alg: str = "EdDSA"
) -> str:
    """Create JWS token for testing.
    
    Args:
        payload: Token payload
        signing_key: Ed25519 signing key
        kid: Key ID
        alg: Algorithm (EdDSA or Ed25519)
        
    Returns:
        JWS compact serialization string
    """
    # Create header
    header = {"alg": alg, "kid": kid}
    h64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip("=")
    
    # Create payload
    p64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip("=")
    
    # Sign
    message = f"{h64}.{p64}".encode()
    signature = signing_key.sign(message).signature
    s64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{h64}.{p64}.{s64}"


# Tests
class TestB64UrlDecode:
    """Test base64url decoding utility."""
    
    def test_decode_with_padding(self):
        """Test decoding with proper padding."""
        encoded = base64.urlsafe_b64encode(b"test").decode().rstrip("=")
        decoded = _b64url_decode(encoded)
        assert decoded == b"test"
    
    def test_decode_no_padding(self):
        """Test decoding handles missing padding."""
        # "test" in base64url without padding
        result = _b64url_decode("dGVzdA")
        assert result == b"test"


class TestLicenseMiddleware:
    """Test LicenseMiddleware functionality."""
    
    @pytest.mark.asyncio
    async def test_public_route_no_token(
        self, app, public_routes, public_digest
    ):
        """Test public routes accessible without token."""
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/public/test"
        request.headers = {}
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        call_next.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_private_route_no_token_denied(
        self, app, public_routes, public_digest
    ):
        """Test private routes require token."""
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"
        request.headers = {}
        
        call_next = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        
        assert "License required" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_verify_jws_valid_token(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test _verify_jws with valid token."""
        payload = {
            "typ": "PUL",
            "license_id": "test-123",
            "exp": int(time.time()) + 3600,
            "scope_digest": public_digest,
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        header, decoded_payload = await middleware._verify_jws(token)
        
        assert header["alg"] == "EdDSA"
        assert header["kid"] == "key-001"
        assert decoded_payload["typ"] == "PUL"
        assert decoded_payload["license_id"] == "test-123"
    
    @pytest.mark.asyncio
    async def test_verify_jws_with_kid_rotation(
        self, app, public_routes, public_digest
    ):
        """Test JWK key rotation support with kid."""
        # Generate two different keys
        key1 = nacl.signing.SigningKey.generate()
        key2 = nacl.signing.SigningKey.generate()
        
        verify_key1 = base64.b64encode(key1.verify_key.encode()).decode()
        verify_key2 = base64.b64encode(key2.verify_key.encode()).decode()
        
        # Create tokens with different kids
        payload1 = {
            "typ": "PUL",
            "license_id": "test-key1",
            "exp": int(time.time()) + 3600,
        }
        payload2 = {
            "typ": "PUL",
            "license_id": "test-key2",
            "exp": int(time.time()) + 3600,
        }
        
        token1 = create_jws_token(payload1, key1, kid="key-001")
        token2 = create_jws_token(payload2, key2, kid="key-002")
        
        # Setup middleware with kid mapping
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_keys_by_kid={
                "key-001": verify_key1,
                "key-002": verify_key2,
            }
        )
        
        # Verify both tokens work
        header1, payload1_decoded = await middleware._verify_jws(token1)
        assert payload1_decoded["license_id"] == "test-key1"
        
        header2, payload2_decoded = await middleware._verify_jws(token2)
        assert payload2_decoded["license_id"] == "test-key2"
    
    @pytest.mark.asyncio
    async def test_verify_jws_invalid_format(
        self, app, verify_key, public_routes, public_digest
    ):
        """Test _verify_jws rejects invalid token format."""
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        with pytest.raises(LicenseValidationError, match="Invalid token format"):
            await middleware._verify_jws("not.enough")
    
    @pytest.mark.asyncio
    async def test_verify_jws_expired_token(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test _verify_jws rejects expired tokens."""
        payload = {
            "typ": "PUL",
            "license_id": "test-expired",
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        with pytest.raises(LicenseValidationError, match="License expired"):
            await middleware._verify_jws(token)
    
    @pytest.mark.asyncio
    async def test_verify_jws_invalid_signature(
        self, app, signing_key, public_routes, public_digest
    ):
        """Test _verify_jws rejects invalid signatures."""
        # Create token with one key
        payload = {"typ": "PUL", "license_id": "test", "exp": int(time.time()) + 3600}
        token = create_jws_token(payload, signing_key)
        
        # Try to verify with different key
        wrong_key = nacl.signing.SigningKey.generate()
        wrong_verify_key = base64.b64encode(wrong_key.verify_key.encode()).decode()
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=wrong_verify_key,
        )
        
        with pytest.raises(LicenseValidationError, match="Invalid license signature"):
            await middleware._verify_jws(token)
    
    @pytest.mark.asyncio
    async def test_verify_jws_unsupported_algorithm(
        self, app, verify_key, public_routes, public_digest
    ):
        """Test _verify_jws rejects unsupported algorithms."""
        # Create token with unsupported algorithm
        header = {"alg": "HS256", "kid": "key-001"}
        payload = {"typ": "PUL"}
        
        h64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        p64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        
        # Token with fake signature
        token = f"{h64}.{p64}.fakesignature"
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        with pytest.raises(LicenseValidationError, match="Unsupported alg"):
            await middleware._verify_jws(token)
    
    @pytest.mark.asyncio
    async def test_crl_check_revoked_license(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test CRL revocation checking."""
        payload = {
            "typ": "PL",
            "license_id": "revoked-license",
            "exp": int(time.time()) + 3600,
            "features": ["trade"],
        }
        
        token = create_jws_token(payload, signing_key)
        
        # Mock CRL response
        crl_data = {
            "version": 1,
            "updated": "2025-01-15T00:00:00Z",
            "revoked": [
                {
                    "license_id": "revoked-license",
                    "reason": "payment_failure",
                    "revoked_at": "2025-01-10T12:00:00Z"
                }
            ]
        }
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
            crl_url="https://example.com/crl.json",
        )
        
        # Pre-populate CRL cache
        middleware._crl_cache = crl_data
        middleware._crl_cache_time = time.time()
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"
        request.headers = {"x-st-license": token}
        request.state = MagicMock()
        
        call_next = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        
        assert "revoked" in str(exc_info.value.detail).lower()


class TestPulValidation:
    """Test PUL (Public Unlimited License) validation."""
    
    @pytest.mark.asyncio
    async def test_pul_valid_token(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test valid PUL token grants access."""
        payload = {
            "typ": "PUL",
            "license_id": "pul-test-123",
            "exp": int(time.time()) + 3600,
            "scope_digest": public_digest,
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/public/test"
        request.headers = {"x-st-license": token}
        request.state = MagicMock()
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        assert response.headers["X-License-Type"] == "PUL"
    
    @pytest.mark.asyncio
    async def test_pul_scope_mismatch(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test PUL token with wrong scope digest is rejected."""
        payload = {
            "typ": "PUL",
            "license_id": "pul-test-mismatch",
            "exp": int(time.time()) + 3600,
            "scope_digest": "wrong-digest-12345",
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/public/test"
        request.headers = {"x-st-license": token}
        request.state = MagicMock()
        
        call_next = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        
        assert "scope digest mismatch" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_pul_route_denied(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test PUL token denied for private routes."""
        payload = {
            "typ": "PUL",
            "license_id": "pul-test-private",
            "exp": int(time.time()) + 3600,
            "scope_digest": public_digest,
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"  # Not in public routes
        request.headers = {"x-st-license": token}
        request.state = MagicMock()
        
        call_next = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        
        assert "not in public scope" in str(exc_info.value.detail).lower()


class TestPlValidation:
    """Test PL (Private Limited License) validation."""
    
    @pytest.mark.asyncio
    async def test_pl_valid_token(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test valid PL token grants access."""
        payload = {
            "typ": "PL",
            "license_id": "pl-test-123",
            "exp": int(time.time()) + 3600,
            "features": ["trade", "pricing"],
            "tier": "pro",
            "org": "acme-corp",
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"
        request.headers = {"x-st-license": token, "host": "api.example.com"}
        request.state = MagicMock()
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        assert response.headers["X-License-Type"] == "PL"
        assert response.headers["X-License-Tier"] == "pro"
    
    @pytest.mark.asyncio
    async def test_pl_grace_period(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test PL token in grace period still works."""
        # Expired 1 day ago, but within 14-day grace period
        payload = {
            "typ": "PL",
            "license_id": "pl-grace-test",
            "exp": int(time.time()) - 86400,  # 1 day ago
            "features": ["trade"],
            "tier": "starter",
            "org": "grace-corp",
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"
        request.headers = {"x-st-license": token, "host": "api.example.com"}
        request.state = MagicMock()
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_pl_expired_beyond_grace(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test PL token beyond grace period is rejected."""
        # Expired 15 days ago (beyond 14-day grace period)
        payload = {
            "typ": "PL",
            "license_id": "pl-expired-test",
            "exp": int(time.time()) - (15 * 86400),
            "features": ["trade"],
            "tier": "starter",
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"
        request.headers = {"x-st-license": token, "host": "api.example.com"}
        request.state = MagicMock()
        
        call_next = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        
        assert "grace period" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_pl_domain_binding(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test PL token with domain binding enforced."""
        payload = {
            "typ": "PL",
            "license_id": "pl-domain-test",
            "exp": int(time.time()) + 3600,
            "features": ["trade"],
            "domain_bind": ["api.acme.com", "market.acme.com"],
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        # Test with wrong domain
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"
        request.headers = {"x-st-license": token, "host": "evil.example.com"}
        request.state = MagicMock()
        
        call_next = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        
        assert "domain not authorized" in str(exc_info.value.detail).lower()
        
        # Test with correct domain
        request2 = MagicMock(spec=Request)
        request2.method = "GET"
        request2.url.path = "/private/test"
        request2.headers = {"x-st-license": token, "host": "api.acme.com"}
        request2.state = MagicMock()
        
        call_next2 = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request2, call_next2)
        assert response.status_code == 200


class TestCorrelationIds:
    """Test correlation ID support for distributed tracing."""
    
    @pytest.mark.asyncio
    async def test_correlation_id_generated(
        self, app, public_routes, public_digest
    ):
        """Test that correlation ID is generated if not provided."""
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/public/test"
        request.headers = {}
        request.state = MagicMock()
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request, call_next)
        
        # Should have correlation ID header
        assert "X-Correlation-Id" in response.headers
        # Should be a valid UUID
        import uuid
        assert uuid.UUID(response.headers["X-Correlation-Id"])
    
    @pytest.mark.asyncio
    async def test_correlation_id_preserved(
        self, app, public_routes, public_digest
    ):
        """Test that existing correlation ID is preserved."""
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
        )
        
        existing_correlation_id = "test-correlation-123"
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/public/test"
        request.headers = {"x-correlation-id": existing_correlation_id}
        request.state = MagicMock()
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request, call_next)
        
        # Should preserve the existing correlation ID
        assert response.headers["X-Correlation-Id"] == existing_correlation_id


class TestTimingAttackMitigation:
    """Test timing attack mitigation through async sleep."""
    
    @pytest.mark.asyncio
    async def test_verify_timing_variance(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test that verification has consistent timing with async sleep mitigation."""
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        # Create valid token
        payload = {
            "typ": "PUL",
            "license_id": "timing-test",
            "exp": int(time.time()) + 3600,
        }
        token = create_jws_token(payload, signing_key)
        
        # Measure timing for multiple verifications
        times = []
        for _ in range(5):
            start = time.perf_counter()
            await middleware._verify_jws(token)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        # Check that timing includes the async sleep (at least 1ms)
        avg_time = sum(times) / len(times)
        
        # Each verification should take at least 1ms due to async sleep
        assert avg_time >= 0.001  # At least 1ms
        
        # But timing variance should still be reasonable
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        assert variance < 0.01  # Less than 10ms variance


class TestCrlErrorHandling:
    """Test CRL error handling."""
    
    @pytest.mark.asyncio
    async def test_crl_fetch_failure(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test that CRL fetch failures fail open (allow access)."""
        payload = {
            "typ": "PL",
            "license_id": "crl-test",
            "exp": int(time.time()) + 3600,
            "features": ["trade"],
        }
        
        token = create_jws_token(payload, signing_key)
        
        # Setup middleware with unreachable CRL URL
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
            crl_url="https://unreachable.invalid/crl.json",
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/private/test"
        request.headers = {"x-st-license": token, "host": "api.example.com"}
        request.state = MagicMock()
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        # Should allow access despite CRL fetch failure (fail open)
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200


class TestAuthorizationHeader:
    """Test Authorization Bearer token support."""
    
    @pytest.mark.asyncio
    async def test_bearer_token(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test that Bearer token in Authorization header works."""
        payload = {
            "typ": "PUL",
            "license_id": "bearer-test",
            "exp": int(time.time()) + 3600,
            "scope_digest": public_digest,
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/public/test"
        request.headers = {"authorization": f"Bearer {token}"}
        request.state = MagicMock()
        
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        assert response.headers["X-License-Type"] == "PUL"
    
    @pytest.mark.asyncio
    async def test_unsupported_license_type(
        self, app, signing_key, verify_key, public_routes, public_digest
    ):
        """Test that unsupported license types are rejected."""
        payload = {
            "typ": "UNKNOWN",  # Unsupported type
            "license_id": "unknown-test",
            "exp": int(time.time()) + 3600,
        }
        
        token = create_jws_token(payload, signing_key)
        
        middleware = LicenseMiddleware(
            app=app,
            public_scope_digest=public_digest,
            public_routes=public_routes,
            verify_key=verify_key,
        )
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/public/test"
        request.headers = {"x-st-license": token}
        request.state = MagicMock()
        
        call_next = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        
        assert "Unsupported license type" in str(exc_info.value.detail)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
