#!/usr/bin/env python3
"""Generate stable digest of all public routes allowed under PUL.

This script creates a cryptographic hash of the exact list of API routes
that are accessible under the Public-Unlimited License (PUL). The digest
is used to prevent tampering and ensure license scope integrity.

Usage:
    python build_public_scope_digest.py

Outputs:
    - docs/licensing/public_scope_digest.txt (SHA-256 hash)
    - docs/licensing/public_scope_routes.json (Route list)
"""

import hashlib
import json
import sys
from pathlib import Path

# Define all public routes allowed under PUL
# Format: "METHOD:/path"
PUBLIC_ROUTES = sorted([
    # Health & Monitoring
    "GET:/api/health",
    "GET:/api/metrics",
    "GET:/api/status",
    
    # SeaSide (HOLD) - Vessel Operations
    "GET:/api/v1/seaside/status",
    "POST:/api/v1/seaside/activity",
    "GET:/api/v1/seaside/vessels",
    "POST:/api/v1/seaside/telemetry",
    "GET:/api/v1/seaside/vessels/{vessel_id}",
    "POST:/api/v1/seaside/ais",
    "GET:/api/v1/seaside/tracking",
    
    # DeckSide (RECORD) - Catch Recording
    "GET:/api/v1/deckside/status",
    "POST:/api/v1/deckside/catch",
    "GET:/api/v1/deckside/batches",
    "POST:/api/v1/deckside/verification",
    "GET:/api/v1/deckside/catch/{catch_id}",
    "POST:/api/v1/deckside/compliance",
    "GET:/api/v1/deckside/species",
    
    # DockSide (STORE) - Storage Management
    "GET:/api/v1/dockside/status",
    "POST:/api/v1/dockside/storage",
    "GET:/api/v1/dockside/inventory",
    "POST:/api/v1/dockside/compliance",
    "GET:/api/v1/dockside/storage/{storage_id}",
    "POST:/api/v1/dockside/chain-of-custody",
    "GET:/api/v1/dockside/temperature",
    
    # Public Demo Endpoints
    "GET:/api/demo/investor",
    "GET:/api/demo/public",
    "GET:/api/demo/qr/{qr_code}",
    
    # Public QR (Basic)
    "GET:/api/v1/qr/public/{qr_code}",
    "POST:/api/v1/qr/verify",
    
    # Public Documentation
    "GET:/api/docs",
    "GET:/api/openapi.json",
    "GET:/api/license/status",
])

def generate_scope_digest(routes: list[str]) -> str:
    """Generate SHA-256 digest of route list.
    
    Args:
        routes: Sorted list of route signatures
        
    Returns:
        SHA-256 digest prefixed with "sha256:"
    """
    # Create stable string representation
    routes_str = "\n".join(routes)
    
    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(routes_str.encode('utf-8'))
    digest = hash_obj.hexdigest()
    
    return f"sha256:{digest}"

def main():
    """Generate and save public scope digest."""
    # Generate digest
    digest = generate_scope_digest(PUBLIC_ROUTES)
    
    # Determine output paths
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent.parent / "docs" / "licensing"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    digest_file = docs_dir / "public_scope_digest.txt"
    routes_file = docs_dir / "public_scope_routes.json"
    
    # Write digest
    with open(digest_file, 'w') as f:
        f.write(digest + "\n")
    
    # Write routes JSON
    with open(routes_file, 'w') as f:
        json.dump(PUBLIC_ROUTES, f, indent=2)
    
    # Print results
    print(f"✓ Generated public scope digest")
    print(f"  Digest: {digest}")
    print(f"  Routes: {len(PUBLIC_ROUTES)}")
    print(f"  Output: {digest_file}")
    print(f"  Routes: {routes_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
