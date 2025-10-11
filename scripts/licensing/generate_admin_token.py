#!/usr/bin/env python3
"""Generate Ed25519 admin token for CRL Management API.

This script creates an admin token with:
- Ed25519 signature (32-byte key, 64-byte signature)
- Scope: "admin" (required for CRL API)
- Expiry: 1 year (configurable)
- Saved to: keys/admin/admin-token-{date}.jwt

Usage:
    python scripts/licensing/generate_admin_token.py
    python scripts/licensing/generate_admin_token.py --email admin@seatrace.org --days 365

For the Commons Good! 🌊
"""

from __future__ import annotations
import argparse
import base64
import json
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

try:
    from nacl.signing import SigningKey
    from nacl.exceptions import BadSignatureError
except ImportError:
    print("❌ ERROR: PyNaCl not installed")
    print("   Install: pip install pynacl")
    exit(1)


def b64url(data: bytes) -> str:
    """Base64url encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_json(obj: dict) -> str:
    """Encode dict as JSON then base64url."""
    return b64url(json.dumps(obj, separators=(",", ":")).encode("utf-8"))


def generate_admin_token(admin_email: str, expiry_days: int) -> dict:
    """Generate Ed25519-signed admin token.
    
    Args:
        admin_email: Admin email address (for audit trail)
        expiry_days: Token expiry in days
    
    Returns:
        dict with token, public_key, private_key, expiry, payload
    """
    # Generate Ed25519 key pair
    # NOTE: In production, load from secure key storage (e.g., Azure Key Vault)
    sk = SigningKey.generate()
    pk = sk.verify_key
    
    # Create JWT payload
    now = datetime.now(tz=timezone.utc)
    expiry = now + timedelta(days=expiry_days)
    
    header = {
        "alg": "EdDSA",
        "typ": "JWT",
        "kid": "admin-2025"  # Key ID for rotation
    }
    
    payload = {
        "typ": "ADMIN",
        "sub": admin_email,
        "scope": "admin crl:read crl:write",
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp()),
        "iss": "SeaTrace-ODOO",
        "aud": "crl-api",
        "commons_charter": "v1.0",  # 🌊 Commons Good commitment
    }
    
    # Encode header and payload
    enc_header = b64url_json(header)
    enc_payload = b64url_json(payload)
    signing_input = f"{enc_header}.{enc_payload}".encode("ascii")
    
    # Sign with Ed25519 private key
    signature = sk.sign(signing_input).signature
    enc_signature = b64url(signature)
    
    # Create JWT token (JWS compact serialization)
    jwt = f"{enc_header}.{enc_payload}.{enc_signature}"
    
    return {
        "token": jwt,
        "public_key": b64url(bytes(pk)),
        "private_key": b64url(bytes(sk)),  # ⚠️ NEVER commit this!
        "header": header,
        "payload": payload,
        "expiry": expiry.isoformat(),
    }


def save_admin_token(token_data: dict, output_dir: Path) -> Path:
    """Save admin token to file.
    
    Args:
        token_data: Token data from generate_admin_token()
        output_dir: Directory to save token (keys/admin/)
    
    Returns:
        Path to saved token file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save complete token data (token + keys)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    token_path = output_dir / f"admin-token-{date_str}.jwt"
    
    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)
    
    # Save public key separately (for verify-keys.json)
    pubkey_path = output_dir / f"admin-public-{date_str}.txt"
    with open(pubkey_path, "w") as f:
        f.write(token_data["public_key"])
    
    return token_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate Ed25519 admin token for CRL Management API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate token with default settings
  python scripts/licensing/generate_admin_token.py
  
  # Generate token for specific admin with custom expiry
  python scripts/licensing/generate_admin_token.py --email admin@seatrace.org --days 180
  
For the Commons Good! 🌊
        """
    )
    parser.add_argument(
        "--email",
        default=os.getenv("ADMIN_EMAIL", "admin@example.org"),
        help="Admin email address (default: admin@example.org or $ADMIN_EMAIL)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Token expiry in days (default: 365)"
    )
    args = parser.parse_args()
    
    print("\n🔑 Generating Admin Token...")
    print("━" * 75)
    
    # Generate token
    token_data = generate_admin_token(args.email, args.days)
    
    # Save to keys/admin/
    repo_root = Path(__file__).parent.parent.parent
    output_dir = repo_root / "keys" / "admin"
    token_path = save_admin_token(token_data, output_dir)
    
    # Display results
    print(f"\n✅ Admin Token Generated:")
    print("━" * 75)
    print(f"Email:      {args.email}")
    print(f"Scope:      {token_data['payload']['scope']}")
    print(f"Issued:     {datetime.fromtimestamp(token_data['payload']['iat'], tz=timezone.utc).isoformat()}")
    print(f"Expires:    {token_data['expiry']}")
    print(f"Key ID:     {token_data['header']['kid']}")
    print(f"Charter:    {token_data['payload']['commons_charter']} 🌊")
    print("━" * 75)
    
    print(f"\n🔒 Token (copy this for API Authorization header):")
    print(f"{token_data['token'][:64]}...")
    print(f"(Full token in {token_path})")
    
    print(f"\n📝 Public Key (add to docs/licensing/verify-keys.json):")
    print(token_data["public_key"])
    
    print(f"\n💾 Files Saved:")
    print(f"  - Token: {token_path}")
    print(f"  - Public Key: {output_dir / f'admin-public-{datetime.now(timezone.utc).strftime(\"%Y-%m-%d\")}.txt'}")
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("  1. Add public key to docs/licensing/verify-keys.json")
    print("  2. Keep private key secure (NEVER commit to git!)")
    print("  3. Add keys/admin/*.jwt to .gitignore")
    print("  4. Use Authorization: Bearer <token> header for API calls")
    print("  5. Rotate keys every 90-180 days for production")
    
    print("\n📋 verify-keys.json Entry:")
    print(json.dumps({
        "admin-2025": {
            "public_key": token_data["public_key"],
            "purpose": "CRL Management API",
            "issued": token_data['payload']['iat'],
            "expires": token_data['payload']['exp'],
        }
    }, indent=2))
    
    print("\n🌊 For the Commons Good!")
    print("━" * 75)


if __name__ == "__main__":
    main()
