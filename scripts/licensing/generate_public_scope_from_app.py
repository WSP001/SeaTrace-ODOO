#!/usr/bin/env python3
"""Generate public scope digest from live FastAPI app.

This prevents route drift by extracting routes directly from the app.
"""

import hashlib
import json
import sys
from importlib import import_module
from pathlib import Path

APP_PATH = "src.app:app"  # module:var


def main():
    """Generate public routes and digest from FastAPI app."""
    try:
        # Import the app
        mod_name, var_name = APP_PATH.split(":")
        mod = import_module(mod_name)
        app = getattr(mod, var_name)
        
        # Extract routes tagged as "public"
        routes = []
        for route in app.routes:
            if not hasattr(route, "methods") or not hasattr(route, "path"):
                continue
            
            tags = getattr(route, "tags", [])
            if "public" in tags:
                for method in sorted(route.methods):
                    routes.append(f"{method}:{route.path}")
        
        routes = sorted(set(routes))
        
        # Generate digest
        digest = "sha256:" + hashlib.sha256(
            "\n".join(routes).encode()
        ).hexdigest()
        
        # Write outputs
        output_dir = Path("docs/licensing")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "public_scope_routes.json", "w") as f:
            json.dump(routes, f, indent=2)
        
        with open(output_dir / "public_scope_digest.txt", "w") as f:
            f.write(digest + "\n")
        
        print(f"✓ Generated public scope digest: {digest}")
        print(f"✓ Routes: {len(routes)}")
        print(f"✓ Output: {output_dir}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
