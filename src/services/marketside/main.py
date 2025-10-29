"""FastAPI application entry point for MarketSide service"""
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .middleware import CorrelationIDMiddleware, SecurityHeadersMiddleware
from .routes import router
from .publisher import publisher
from .pm_tokens import pm_token_manager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle"""
    logger.info(
        "marketside_service_starting",
        port=settings.port,
        pm_tokens_enabled=settings.enable_pm_tokens,
        market_exchange_enabled=settings.enable_market_exchange
    )
    yield
    # Cleanup on shutdown
    logger.info("marketside_service_shutting_down")


# Create FastAPI app
app = FastAPI(
    title="MarketSide Service",
    description="EXCHANGE Layer - SeaTrace-ODOO Pillar 4 (PRIVATE KEY OUTGOING)",
    version=settings.service_version,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*", "X-Correlation-ID"],
)

# Include routes
app.include_router(router, tags=["marketside"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "marketside",
        "role": "EXCHANGE",
        "status": "running",
        "version": settings.service_version,
        "security": "PRIVATE KEY OUTGOING (signs outgoing data)",
        "features": {
            "pm_tokens": settings.enable_pm_tokens,
            "market_exchange": settings.enable_market_exchange
        },
        "message": "For the Commons Good! 🌊"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "starting_marketside",
        host="0.0.0.0",
        port=settings.port,
        service_version=settings.service_version
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.port,
        log_config=None  # Use structlog
    )
