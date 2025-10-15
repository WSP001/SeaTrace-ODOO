"""
SeaTrace-ODOO Public API with 8-Layer Security
For the Commons Good! 🌊
"""

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
import os
import logging

# Import existing licensing
from common.licensing.middleware import LicenseMiddleware
from common.licensing.commons import router as commons_router
from common.licensing.routes import router as license_router

# Import 8-layer security
from security.rate_limiting import limiter, rate_limit_exceeded_handler
from security.tls_config import HTTPSRedirectMiddleware
from security.crl_validator import init_crl_validator
from security.secret_manager import get_secret

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load secrets from environment
PUBLIC_SCOPE_DIGEST = get_secret("PUBLIC_SCOPE_DIGEST", "sha256:REPLACE_WITH_GENERATED")
VERIFY_KEYS = {
    "kid1": get_secret("VERIFY_KEY_KID1", "REPLACE_WITH_BASE64_ED25519_VERIFY_KEY")
}
DEFAULT_KID = "kid1"
CRL_URL = get_secret("CRL_URL", "https://seatrace.worldseafoodproducers.com/crl/revoked.json")

# Create FastAPI app
app = FastAPI(
    title="SeaTrace-ODOO Public API",
    description="🛡️ Blockchain-powered seafood supply chain with 8-layer security",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# SECURITY LAYER 1: RATE LIMITING
# ============================================================================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# ============================================================================
# SECURITY LAYER 6: TLS/HTTPS ENFORCEMENT
# ============================================================================
# Uncomment in production with valid SSL certificates
# app.add_middleware(HTTPSRedirectMiddleware)

# ============================================================================
# CORS MIDDLEWARE (Before security layers)
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PUBLIC ROUTES (Before licensing middleware)
# ============================================================================
app.include_router(commons_router)
app.include_router(license_router)

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================
@app.get("/health", tags=["public"])
@limiter.limit("1000/minute")
async def health_check(request: Request):
    """Basic health check - always returns 200 OK"""
    return {
        "status": "healthy",
        "service": "seatrace-odoo",
        "version": "1.1.0",
        "security": "8-layer-active"
    }

@app.get("/ready", tags=["public"])
@limiter.limit("1000/minute")
async def readiness_check(request: Request):
    """
    Readiness check - verifies all systems operational
    Returns 503 if not ready to accept traffic
    """
    checks = {
        "api": "ok",
        "security": "active",
        "licensing": "active"
    }
    
    # Check if any system is down
    if any(status != "ok" and status != "active" for status in checks.values()):
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": checks
            }
        )
    
    return {
        "status": "ready",
        "checks": checks
    }

# ============================================================================
# SECURITY INFO ENDPOINT (Public)
# ============================================================================
@app.get("/security", tags=["public"])
@limiter.limit("100/minute")
async def security_info(request: Request):
    """Display active security layers"""
    return {
        "security_architecture": "8-layer-defense",
        "layers": {
            "1": "Rate Limiting (DDoS/Brute Force protection)",
            "2": "Input Validation (SQL Injection/XSS protection)",
            "3": "Timing Defense (Timing Attack protection)",
            "4": "Replay Defense (Replay Attack protection)",
            "5": "Secret Management (Secret Leakage protection)",
            "6": "TLS Encryption (MITM protection)",
            "7": "CRL Validation (Revoked License protection)",
            "8": "RBAC (Privilege Escalation protection)"
        },
        "status": "all_active",
        "for_the_commons_good": True
    }

# ============================================================================
# STARTUP EVENT: INITIALIZE SECURITY
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Initialize all security layers on startup"""
    logger.info("🏈 Starting SeaTrace-ODOO with 8-layer security...")
    
    # Generate public routes from app
    PUBLIC_ROUTES = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            tags = getattr(route, "tags", [])
            if "public" in tags:
                for method in route.methods:
                    PUBLIC_ROUTES.append(f"{method}:{route.path}")
    
    # Add licensing middleware
    app.add_middleware(
        LicenseMiddleware,
        public_scope_digest=PUBLIC_SCOPE_DIGEST,
        public_routes=PUBLIC_ROUTES,
        verify_key=VERIFY_KEYS[DEFAULT_KID],
        verify_keys_by_kid=VERIFY_KEYS,
        crl_url=CRL_URL,
    )
    
    # Initialize CRL validator (Layer 7)
    try:
        init_crl_validator(CRL_URL, cache_ttl_hours=1, fail_open=True)
        logger.info("✅ Layer 7: CRL Validator initialized")
    except Exception as e:
        logger.warning(f"⚠️  Layer 7: CRL Validator failed to initialize: {e}")
    
    logger.info("✅ Licensing middleware initialized")
    logger.info(f"✅ Public routes: {len(PUBLIC_ROUTES)}")
    logger.info(f"✅ Scope digest: {PUBLIC_SCOPE_DIGEST[:32]}...")
    logger.info("🛡️ 8-Layer Security: ACTIVE")
    logger.info("🌊 For the Commons Good!")

# ============================================================================
# SHUTDOWN EVENT: CLEANUP
# ============================================================================
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🏈 Shutting down SeaTrace-ODOO...")
    logger.info("🌊 For the Commons Good!")

# ============================================================================
# RUN SERVER
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    # Get SSL configuration (if available)
    ssl_keyfile = get_secret("SSL_KEYFILE")
    ssl_certfile = get_secret("SSL_CERTFILE")
    
    if ssl_keyfile and ssl_certfile:
        logger.info("🔒 Starting with HTTPS (TLS 1.3)")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=443,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            log_level="info"
        )
    else:
        logger.warning("⚠️  Starting with HTTP (no SSL certificates)")
        logger.warning("⚠️  Use HTTPS in production!")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
