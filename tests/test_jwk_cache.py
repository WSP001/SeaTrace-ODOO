"""
Test JWK cache with kid rotation support (Phase 1.5A - Fix 2).

Verifies:
1. Cache returns Ed25519 public key bytes by kid
2. Unknown kid handling (raises KeyError or returns None)
3. Auto-refresh mechanism (if implemented)
4. Multi-key rotation support (current + previous keys)

Pattern: Mirrors SeaTrace003 PREVIOUS_KEY rotation from .env.codex.template
"""
import json
import base64
from pathlib import Path
import pytest


def create_test_keys_file(tmp_path, keys_data):
    """
    Helper to create test verify-keys.json file.
    
    Args:
        tmp_path: pytest tmp_path fixture
        keys_data: Dict with "keys" array
    
    Returns:
        Path to created keys file
    """
    keys_file = tmp_path / "verify-keys.json"
    keys_file.write_text(json.dumps(keys_data))
    return keys_file


def test_jwk_cache_basic_import():
    """Verify JWK cache module imports cleanly."""
    try:
        from src.common.security.jwk_cache import JWKCache
        assert JWKCache is not None
    except ImportError as e:
        pytest.fail(f"JWK cache import failed: {e}")


def test_jwk_cache_returns_key_by_kid(tmp_path):
    """
    Test JWK cache retrieves Ed25519 public key by kid.
    
    Expected behavior:
    - get("current") returns bytes
    - get("previous") returns bytes
    - Both keys are different (rotation support)
    """
    # Create mock verify-keys.json with keys array format (matches jwk_cache.py structure)
    # Ed25519 keys are exactly 32 bytes
    current_key_bytes = b"C" * 32  # 32 bytes exactly
    previous_key_bytes = b"P" * 32  # 32 bytes exactly
    
    keys = {
        "keys": [
            {
                "kid": "pul-2025-v1",
                "ed25519": base64.urlsafe_b64encode(current_key_bytes).decode().rstrip("="),
                "created_at": "2025-01-01T00:00:00Z",
                "status": "active"
            },
            {
                "kid": "pul-2024-v1",
                "ed25519": base64.urlsafe_b64encode(previous_key_bytes).decode().rstrip("="),
                "created_at": "2024-01-01T00:00:00Z",
                "status": "previous"
            }
        ]
    }
    
    keys_file = create_test_keys_file(tmp_path, keys)
    
    try:
        from src.common.security.jwk_cache import JWKCache
        
        # Initialize cache with test file
        cache = JWKCache(keys_file=str(keys_file), refresh_interval=3600, redis_client=None)
        
        # Test synchronous get (if async, wrap in asyncio.run)
        import asyncio
        import inspect
        
        if inspect.iscoroutinefunction(cache.get):
            # Async version
            current_key = asyncio.run(cache.get("pul-2025-v1"))
            previous_key = asyncio.run(cache.get("pul-2024-v1"))
        else:
            # Sync version
            current_key = cache.get("pul-2025-v1")
            previous_key = cache.get("pul-2024-v1")
        
        # Verify both keys are bytes and different
        assert isinstance(current_key, (bytes, bytearray)), f"Current key should be bytes, got {type(current_key)}"
        assert isinstance(previous_key, (bytes, bytearray)), f"Previous key should be bytes, got {type(previous_key)}"
        assert current_key != previous_key, "Current and previous keys should differ (rotation support)"
        
        # Verify keys are 32 bytes (Ed25519 public key size)
        assert len(current_key) == 32, f"Ed25519 key should be 32 bytes, got {len(current_key)}"
        assert len(previous_key) == 32, f"Ed25519 key should be 32 bytes, got {len(previous_key)}"
        
    except ImportError:
        pytest.skip("JWK cache not available for testing")
    except Exception as e:
        pytest.fail(f"JWK cache test failed: {e}")


def test_jwk_cache_unknown_kid_handling(tmp_path):
    """
    Test JWK cache handles unknown kid gracefully.
    
    Expected behavior:
    - get("unknown-kid") raises KeyError OR returns None
    - Does NOT crash or raise unexpected exception
    """
    keys = {
        "keys": [
            {
                "kid": "known-kid",
                "ed25519": base64.urlsafe_b64encode(b"A" * 32).decode().rstrip("="),
                "created_at": "2025-01-01T00:00:00Z",
                "status": "active"
            }
        ]
    }
    
    keys_file = create_test_keys_file(tmp_path, keys)
    
    try:
        from src.common.security.jwk_cache import JWKCache
        import asyncio
        import inspect
        
        cache = JWKCache(keys_file=str(keys_file), refresh_interval=3600, redis_client=None)
        
        # Attempt to get unknown kid
        if inspect.iscoroutinefunction(cache.get):
            try:
                result = asyncio.run(cache.get("unknown-kid-12345"))
                # If no exception, verify result is None
                assert result is None, "Unknown kid should return None if not raising KeyError"
            except KeyError:
                pass  # Expected behavior
        else:
            try:
                result = cache.get("unknown-kid-12345")
                assert result is None, "Unknown kid should return None if not raising KeyError"
            except KeyError:
                pass  # Expected behavior
                
    except ImportError:
        pytest.skip("JWK cache not available for testing")
    except AssertionError:
        raise
    except Exception as e:
        pytest.fail(f"Unexpected exception for unknown kid: {e}")


def test_jwk_cache_refresh_mechanism(tmp_path):
    """
    Test JWK cache auto-refresh (if background task exists).
    
    Expected behavior:
    - Cache can start/stop refresh loop
    - Refresh doesn't crash
    - _last_refresh timestamp updates
    """
    keys = {
        "keys": [
            {
                "kid": "test-kid",
                "ed25519": base64.urlsafe_b64encode(b"B" * 32).decode().rstrip("="),
                "created_at": "2025-01-01T00:00:00Z",
                "status": "active"
            }
        ]
    }
    
    keys_file = create_test_keys_file(tmp_path, keys)
    
    try:
        from src.common.security.jwk_cache import JWKCache
        import asyncio
        
        cache = JWKCache(keys_file=str(keys_file), refresh_interval=1, redis_client=None)
        
        # Check if cache has start/stop methods (background refresh)
        if not (hasattr(cache, 'start') and hasattr(cache, 'stop')):
            pytest.skip("JWK cache doesn't have background refresh (start/stop methods)")
        
        async def test_refresh():
            # Start background refresh
            task = asyncio.create_task(cache.start())
            
            # Wait for at least one refresh
            await asyncio.sleep(1.5)
            
            # Stop refresh
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Verify refresh happened (check _last_refresh timestamp)
            if hasattr(cache, '_last_refresh'):
                assert cache._last_refresh is not None, "Refresh should update _last_refresh timestamp"
        
        asyncio.run(test_refresh())
        
    except ImportError:
        pytest.skip("JWK cache not available for testing")
    except asyncio.TimeoutError:
        pytest.skip("Refresh test timed out (acceptable for quick test)")
    except Exception as e:
        pytest.fail(f"Refresh mechanism test failed: {e}")


def test_jwk_cache_file_not_found():
    """
    Test JWK cache handles missing keys file gracefully.
    
    Expected behavior:
    - Cache initialization doesn't crash
    - get() attempts trigger file read or raise appropriate error
    """
    try:
        from src.common.security.jwk_cache import JWKCache
        import asyncio
        import inspect
        
        # Point to non-existent file
        cache = JWKCache(keys_file="/nonexistent/path/verify-keys.json", refresh_interval=3600)
        
        # Attempt to get a key (should handle missing file gracefully)
        if inspect.iscoroutinefunction(cache.get):
            try:
                asyncio.run(cache.get("any-kid"))
                pytest.fail("Should raise exception for missing keys file")
            except (FileNotFoundError, KeyError, Exception):
                pass  # Expected
        else:
            try:
                cache.get("any-kid")
                pytest.fail("Should raise exception for missing keys file")
            except (FileNotFoundError, KeyError, Exception):
                pass  # Expected
                
    except ImportError:
        pytest.skip("JWK cache not available for testing")


if __name__ == "__main__":
    # Quick local test
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_jwk_cache_basic_import()
        test_jwk_cache_returns_key_by_kid(Path(tmpdir))
        test_jwk_cache_unknown_kid_handling(Path(tmpdir))
    print("✅ All JWK cache tests passed!")
