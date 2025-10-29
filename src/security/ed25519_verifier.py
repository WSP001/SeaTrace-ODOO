"""
🔐 Ed25519 JWS Token Verifier (PUBLIC REPO - VERIFICATION ONLY)
For the Commons Good! 🌊🏈

Compatible with Proceeding Master's routes.py verify_ed25519_jws() pattern

⚠️ SECURITY BOUNDARY:
- ✅ PUBLIC KEY verification (safe for public repo)
- ❌ NO PRIVATE KEY signing (keep in private repo only!)

This module ONLY verifies JWS tokens signed by the PRIVATE repo.
It NEVER signs tokens or handles private keys.
"""

import os
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature
import structlog

logger = structlog.get_logger()


def _b64url_enc(data: bytes) -> str:
    """
    Encode bytes to base64url format (no padding)
    
    Args:
        data: Bytes to encode
        
    Returns:
        Base64url-encoded string (no padding)
    """
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def _b64url_dec(s: str) -> bytes:
    """
    Decode base64url format (extracted from Proceeding Master routes.py:31)
    
    Args:
        s: Base64url-encoded string (may be missing padding)
        
    Returns:
        Decoded bytes
    """
    # Add padding if needed
    padding = '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


class Ed25519Verifier:
    """
    Ed25519 JWS Token Verifier (PUBLIC REPO - READ-ONLY)
    
    Compatible with Proceeding Master's verify_ed25519_jws() function
    
    Usage:
        verifier = Ed25519Verifier()
        payload = verifier.verify_jws(token)
    """
    
    def __init__(self, verify_key_b64: Optional[str] = None):
        """
        Initialize verifier with PUBLIC key
        
        Args:
            verify_key_b64: Base64-encoded Ed25519 public key
                           If None, loads from SEATRACE_VERIFY_KEY env var
        """
        self.public_key = None
        
        # Load public key
        if verify_key_b64 is None:
            verify_key_b64 = os.getenv('SEATRACE_VERIFY_KEY')
        
        if not verify_key_b64:
            logger.warning(
                "No SEATRACE_VERIFY_KEY configured - token verification disabled",
                security_risk="Unsigned tokens will be accepted"
            )
            return
        
        try:
            # Decode public key from base64
            verify_key_bytes = base64.b64decode(verify_key_b64)
            self.public_key = ed25519.Ed25519PublicKey.from_public_bytes(verify_key_bytes)
            
            logger.info(
                "Ed25519 verifier initialized",
                key_length=len(verify_key_bytes),
                algorithm="EdDSA"
            )
        except Exception as e:
            logger.error(
                "Failed to load SEATRACE_VERIFY_KEY",
                error=str(e),
                hint="Check that key is valid base64-encoded Ed25519 public key"
            )
            raise ValueError(f"Invalid SEATRACE_VERIFY_KEY: {e}")
    
    def verify_jws(self, token: str, require_exp: bool = False) -> Dict[str, Any]:
        """
        Verify JWS token signed with Ed25519 (PUBLIC KEY ONLY)
        
        Compatible with Proceeding Master's verify_ed25519_jws() function
        
        Args:
            token: JWS token in format header.payload.signature
            require_exp: If True, reject tokens without 'exp' field or expired tokens
            
        Returns:
            Decoded payload dict if valid
            
        Raises:
            ValueError: If signature is invalid, token malformed, or expired
        """
        if not self.public_key:
            logger.warning(
                "Token verification skipped - no public key configured",
                security_risk="Accepting unsigned token"
            )
            # Parse token without verification (for development/testing)
            try:
                _, payload_b64, _ = token.split('.')
                return json.loads(_b64url_dec(payload_b64).decode('utf-8'))
            except Exception as e:
                raise ValueError(f"Invalid JWS format: {e}")
        
        # Parse JWS token
        try:
            header_b64, payload_b64, signature_b64 = token.split('.')
        except ValueError:
            raise ValueError("Invalid JWS format: expected header.payload.signature")
        
        # Decode components
        try:
            header = json.loads(_b64url_dec(header_b64).decode('utf-8'))
            payload = json.loads(_b64url_dec(payload_b64).decode('utf-8'))
            signature = _b64url_dec(signature_b64)
        except Exception as e:
            raise ValueError(f"Failed to decode JWS components: {e}")
        
        # Verify algorithm
        alg = header.get('alg')
        if alg != 'EdDSA':
            raise ValueError(f"Unsupported algorithm: {alg} (expected EdDSA)")
        
        # Verify signature
        message = f"{header_b64}.{payload_b64}".encode('utf-8')
        try:
            self.public_key.verify(signature, message)
        except InvalidSignature:
            logger.warning(
                "Invalid JWS signature",
                algorithm=alg,
                kid=header.get('kid')
            )
            raise ValueError("Invalid signature")
        
        # Check expiration (if required)
        if require_exp:
            exp = payload.get('exp')
            if not exp:
                raise ValueError("Token missing 'exp' field")
            
            if isinstance(exp, str):
                # Parse ISO format timestamp
                exp_dt = datetime.fromisoformat(exp.replace('Z', '+00:00'))
                exp = exp_dt.timestamp()
            
            now = datetime.utcnow().timestamp()
            if exp < now:
                expired_seconds = int(now - exp)
                logger.warning(
                    "Token expired",
                    exp=exp,
                    now=now,
                    expired_seconds=expired_seconds
                )
                raise ValueError(f"Token expired {expired_seconds} seconds ago")
        
        logger.info(
            "JWS token verified",
            algorithm=alg,
            kid=header.get('kid'),
            typ=header.get('typ'),
            user=payload.get('user'),
            exp=payload.get('exp')
        )
        
        return payload
    
    def verify_packet_signature(
        self,
        packet_data: Dict[str, Any],
        signature_b64: str
    ) -> bool:
        """
        Verify Ed25519 signature on raw packet data
        
        Args:
            packet_data: Dictionary to verify
            signature_b64: Base64-encoded signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.public_key:
            logger.warning("Signature verification skipped - no public key")
            return True  # Allow unsigned in development
        
        try:
            # Serialize packet data (deterministic)
            message = json.dumps(packet_data, sort_keys=True).encode('utf-8')
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            self.public_key.verify(signature, message)
            
            logger.info(
                "Packet signature verified",
                packet_size=len(message),
                signature_size=len(signature)
            )
            
            return True
            
        except InvalidSignature:
            logger.warning("Invalid packet signature")
            return False
        except Exception as e:
            logger.error(
                "Signature verification failed",
                error=str(e)
            )
            return False


# Global verifier instance (lazy-loaded)
_verifier_instance: Optional[Ed25519Verifier] = None


def get_verifier() -> Ed25519Verifier:
    """
    Get global Ed25519Verifier instance (singleton)
    
    Returns:
        Shared verifier instance
    """
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = Ed25519Verifier()
    return _verifier_instance


def verify_ed25519_jws(token: str, verify_key_b64: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify JWS token (convenience function compatible with Proceeding Master)
    
    This is the main function called by API endpoints and packet handlers.
    Compatible with Proceeding Master's verify_ed25519_jws() in routes.py.
    
    Args:
        token: JWS token in format header.payload.signature
        verify_key_b64: Optional public key (uses SEATRACE_VERIFY_KEY env if None)
        
    Returns:
        Decoded payload dict if valid
        
    Raises:
        ValueError: If signature is invalid or token malformed
        
    Example:
        >>> payload = verify_ed25519_jws(token)
        >>> print(payload['user'])
        'fisher@example.com'
    """
    if verify_key_b64:
        # Use provided key
        verifier = Ed25519Verifier(verify_key_b64=verify_key_b64)
    else:
        # Use global instance
        verifier = get_verifier()
    
    return verifier.verify_jws(token)


# CLI testing
if __name__ == "__main__":
    import sys
    
    print("🔐 Ed25519 JWS Verifier Test (PUBLIC REPO)")
    print("=" * 60)
    
    # Check environment
    verify_key = os.getenv('SEATRACE_VERIFY_KEY')
    if not verify_key:
        print("❌ SEATRACE_VERIFY_KEY not set in environment")
        print("   Set it with: $env:SEATRACE_VERIFY_KEY = 'your-public-key'")
        sys.exit(1)
    
    print(f"✅ SEATRACE_VERIFY_KEY loaded ({len(verify_key)} chars)")
    
    # Initialize verifier
    try:
        verifier = Ed25519Verifier()
        print("✅ Ed25519Verifier initialized")
    except Exception as e:
        print(f"❌ Failed to initialize verifier: {e}")
        sys.exit(1)
    
    # Test with sample token (if provided)
    if len(sys.argv) > 1:
        test_token = sys.argv[1]
        print(f"\n📋 Testing token verification...")
        print(f"   Token: {test_token[:50]}...")
        
        try:
            payload = verifier.verify_jws(test_token)
            print(f"✅ Valid token!")
            print(f"   Payload: {json.dumps(payload, indent=2)}")
        except ValueError as e:
            print(f"❌ Invalid token: {e}")
            sys.exit(1)
    else:
        print("\n💡 To test token verification, pass token as argument:")
        print("   python -m src.security.ed25519_verifier 'eyJhbGc...'")
    
    print("\n🎉 Ed25519 verifier ready for Commons Good! 🌊🏈")
