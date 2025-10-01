"""SeaTrace-ODOO Public API with dual licensing enforcement."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os

from common.licensing.middleware import LicenseMiddleware
from common.licensing.commons import router as commons_router
from common.licensing.routes import router as license_router

# Load from environment in production
PUBLIC_SCOPE_DIGEST = os.getenv("PUBLIC_SCOPE_DIGEST", "sha256:REPLACE_WITH_GENERATED")
PUBLIC_ROUTES = []  # Generated at startup from router
VERIFY_KEYS = {
    "kid1": os.getenv("VERIFY_KEY_KID1", "REPLACE_WITH_BASE64_ED25519_VERIFY_KEY")
}
DEFAULT_KID = "kid1"

app = FastAPI(
    title="SeaTrace-ODOO Public API",
    description="Blockchain-powered seafood supply chain with dual licensing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include public routers BEFORE middleware
app.include_router(commons_router)
app.include_router(license_router)

# Health check
@app.get("/api/health", tags=["public"])
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "seatrace-odoo"}

# Generate public routes from app
def get_public_routes():
    """Extract public routes from FastAPI app."""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            tags = getattr(route, "tags", [])
            if "public" in tags:
                for method in route.methods:
                    routes.append(f"{method}:{route.path}")
    return sorted(set(routes))

# Attach licensing middleware AFTER routes are registered
@app.on_event("startup")
async def startup_event():
    """Initialize licensing middleware on startup."""
    global PUBLIC_ROUTES
    PUBLIC_ROUTES = get_public_routes()
    
    # Add middleware
    app.add_middleware(
        LicenseMiddleware,
        public_scope_digest=PUBLIC_SCOPE_DIGEST,
        public_routes=PUBLIC_ROUTES,
        verify_key=VERIFY_KEYS[DEFAULT_KID],
        verify_keys_by_kid=VERIFY_KEYS,
        crl_url="https://seatrace.worldseafoodproducers.com/crl/revoked.json",
    )
    
    print(f"✓ Licensing middleware initialized")
    print(f"✓ Public routes: {len(PUBLIC_ROUTES)}")
    print(f"✓ Scope digest: {PUBLIC_SCOPE_DIGEST[:32]}...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
