"""
DockSide Pillar (TE - STORE/Storage)
For the Commons Good! 🌊

PUBLIC KEY INCOMING - Storage and analytics
Receives packets from WildFisheriesPacketSwitcher
"""

from fastapi import FastAPI, Request, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from typing import Dict, Any
import os

# Import packet switching handler
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from packet_switching.handler import IncomingPacket, WildFisheriesPacketSwitcher

app = FastAPI(
    title="DockSide - Storage",
    description="TE: STORE - Finished product storage and analytics",
    version="1.0.0"
)

# Initialize packet switcher
packet_switcher = WildFisheriesPacketSwitcher()

# Prometheus metrics
requests_total = Counter('dockside_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('dockside_request_duration_seconds', 'Request duration')
packets_processed = Counter('dockside_packets_processed', 'Packets processed', ['source', 'status'])

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "pillar": "dockside", "role": "STORE"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "pillar": "DockSide",
        "role": "STORE",
        "description": "Storage and analytics",
        "position": "TE (Tight End)",
        "accepts": ["processor packets", "product data", "storage requests"],
        "storage_tiers": ["hot (Redis)", "warm (Postgres)", "cold (S3)"]
    }

@app.post("/ingest/packet")
async def ingest_packet(packet_data: Dict[str, Any]):
    """
    🏈 CATCH - Store processing packet
    
    PUBLIC KEY INCOMING - Verify and store product data
    """
    try:
        # Create incoming packet
        packet = IncomingPacket(
            source="processor",
            payload=packet_data,
            signature=packet_data.get("signature")
        )
        
        # Process through packet switcher
        result = await packet_switcher._handle_dockside(packet)
        
        # Update metrics
        packets_processed.labels(source="processor", status="success").inc()
        
        return {
            **result,
            "correlation_id": packet.correlation_id,
            "packet_hash": packet.hash()
        }
        
    except Exception as e:
        packets_processed.labels(source="processor", status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
