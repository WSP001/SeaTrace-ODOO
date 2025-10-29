# 🌊 SeaSide FastAPI Service
# For the Commons Good!

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.seaside.models import (
    IncomingPacket,
    IngestResponse,
    HealthResponse
)
from services.seaside.routes import router

# Create FastAPI app
app = FastAPI(
    title="SeaSide Service",
    description="Vessel Operations - HOLD (Layer 1 of 4-pillar architecture)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "SeaSide",
        "status": "operational",
        "message": "For the Commons Good! 🌊",
        "docs": "/docs"
    }

# Health check (root level)
@app.get("/health", response_model=HealthResponse)
async def health():
    """Root-level health check"""
    return HealthResponse(
        status="healthy",
        service="seaside",
        version="1.0.0"
    )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🌊 SeaSide Service Starting...")
    print("📊 Service: Vessel Operations (HOLD)")
    print("🔐 Mode: PUBLIC KEY INCOMING")
    print("✅ Ready to receive packets on port 8001")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("🌊 SeaSide Service Shutting Down...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
