"""FastAPI application entry point for DockSide service"""
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .middleware import CorrelationIDMiddleware, SecurityHeadersMiddleware
from .routes import router
from .storage import storage

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
        "dockside_service_starting",
        port=settings.port,
        storage_mode=settings.storage_mode
    )
    yield
    # Cleanup on shutdown
    logger.info("dockside_service_shutting_down")


# Create FastAPI app
app = FastAPI(
    title="DockSide Service",
    description="STORE Layer - SeaTrace-ODOO Pillar 3",
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
app.include_router(router, tags=["dockside"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "dockside",
        "status": "running",
        "version": settings.service_version,
        "storage_mode": settings.storage_mode,
        "message": "For the Commons Good! 🌊"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "starting_dockside",
        host="0.0.0.0",
        port=settings.port,
        service_version=settings.service_version,
        storage_mode=settings.storage_mode
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.port,
        log_config=None  # Use structlog
    )
