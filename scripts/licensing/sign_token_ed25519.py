#!/usr/bin/env python3
"""Ed25519 token signer for SeaTrace licensing.

Generates signed JWS tokens for PUL (Public Unlimited) and PL (Private Limited) licenses.

Usage:
    # Generate Ed25519 keypair (do once, store securely)
    python -c "from nacl.signing import SigningKey; sk=SigningKey.generate(); print('Secret:', sk.encode().hex()); print('Public:', sk.verify_key.encode().hex())"
    
    # Create payload JSON
    cat > pul.json << EOF
    {
      "typ": "PUL",
      "ver": 1,
      "license_id": "pul-2025-01",
      "org": "any",
      "pillars": ["seaside", "deckside", "dockside"],
      "features": ["qr_public", "schemas_v1", "otel_metrics"],
      "scope_digest": "sha256:abc123...",
      "exp": 4070908800,
      "notice": "Public Unlimited (FREE). No MarketSide premium access."
    }
    EOF
    
    # Sign token
    python sign_token_ed25519.py --sk-hex <secret_key_hex> --payload pul.json --kid v1 > pul-2025-01.token
    
    # Verify token
    python sign_token_ed25519.py --verify --token $(cat pul-2025-01.token) --vk-hex <public_key_hex>
"""

import argparse
import base64
import json
import sys
from pathlib import Path

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.exceptions import BadSignatureError
except ImportError:
    print("Error: PyNaCl required. Install with: pip install pynacl", file=sys.stderr)
    sys.exit(1)


def b64url_encode(data: bytes) -> str:
    """Base64url encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(data: str) -> bytes:
    """Base64url decode with padding."""
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def sign_token(payload: dict, sk_hex: str, kid: str = "v1") -> str:
    """Sign a license token using Ed25519.
    
    Args:
        payload: License payload dictionary
        sk_hex: Hex-encoded Ed25519 secret key (64 bytes)
        kid: Key ID for rotation support
        
    Returns:
        JWS compact serialization (header.payload.signature)
    """
    # Create signing key
    sk = SigningKey(bytes.fromhex(sk_hex))
    
    # Create header
    header = {
        "alg": "EdDSA",
        "typ": "JWT",
        "kid": kid
    }
    
    # Encode header and payload
    h = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    
    # Sign
    msg = f"{h}.{p}".encode()
    sig = sk.sign(msg).signature
    s = b64url_encode(sig)
    
    return f"{h}.{p}.{s}"


def verify_token(token: str, vk_hex: str) -> dict:
    """Verify a signed license token.
    
    Args:
        token: JWS compact serialization
        vk_hex: Hex-encoded Ed25519 public key (32 bytes)
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        BadSignatureError: If signature is invalid
        ValueError: If token format is invalid
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWS format")
    
    h64, p64, s64 = parts
    
    # Decode header
    header = json.loads(b64url_decode(h64))
    if header.get("alg") not in ("EdDSA", "Ed25519"):
        raise ValueError(f"Unsupported algorithm: {header.get('alg')}")
    
    # Verify signature
    vk = VerifyKey(bytes.fromhex(vk_hex))
    msg = f"{h64}.{p64}".encode()
    sig = b64url_decode(s64)
    vk.verify(msg, sig)
    
    # Decode payload
    payload = json.loads(b64url_decode(p64))
    
    return payload


def main():
    parser = argparse.ArgumentParser(
        description="Sign or verify Ed25519 license tokens",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Signing mode
    parser.add_argument("--sk-hex", help="Secret key (hex, 64 bytes)")
    parser.add_argument("--payload", help="Payload JSON file")
    parser.add_argument("--kid", default="v1", help="Key ID (default: v1)")
    
    # Verification mode
    parser.add_argument("--verify", action="store_true", help="Verify mode")
    parser.add_argument("--token", help="Token to verify")
    parser.add_argument("--vk-hex", help="Verify key (hex, 32 bytes)")
    
    args = parser.parse_args()
    
    if args.verify:
        # Verify mode
        if not args.token or not args.vk_hex:
            parser.error("--verify requires --token and --vk-hex")
        
        try:
            payload = verify_token(args.token, args.vk_hex)
            print("✓ Signature valid", file=sys.stderr)
            print(json.dumps(payload, indent=2))
            return 0
        except BadSignatureError:
            print("✗ Invalid signature", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Verification failed: {e}", file=sys.stderr)
            return 1
    
    else:
        # Sign mode
        if not args.sk_hex or not args.payload:
            parser.error("Signing requires --sk-hex and --payload")
        
        # Load payload
        payload_file = Path(args.payload)
        if not payload_file.exists():
            print(f"Error: Payload file not found: {args.payload}", file=sys.stderr)
            return 1
        
        payload = json.loads(payload_file.read_text())
        
        # Sign token
        token = sign_token(payload, args.sk_hex, args.kid)
        print(token)
        
        return 0


if __name__ == "__main__":
    sys.exit(main())
