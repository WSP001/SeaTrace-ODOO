"""
DeckSide Pillar (RB - RECORD/Processing)
For the Commons Good! 🌊

PUBLIC KEY INCOMING - Catch processing and ledger management
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
    title="DeckSide - Processing",
    description="RB: RECORD - Catch processing and ledger append",
    version="1.0.0"
)

# Initialize packet switcher
packet_switcher = WildFisheriesPacketSwitcher()

# Prometheus metrics
requests_total = Counter('deckside_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('deckside_request_duration_seconds', 'Request duration')
packets_processed = Counter('deckside_packets_processed', 'Packets processed', ['source', 'status'])

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "pillar": "deckside", "role": "RECORD"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "pillar": "DeckSide",
        "role": "RECORD",
        "description": "Processing and ledger management",
        "position": "RB (Running Back)",
        "accepts": ["catch packets", "EMR data", "logbook entries"]
    }

@app.post("/ingest/packet")
async def ingest_packet(packet_data: Dict[str, Any]):
    """
    🏈 HANDOFF - Process catch recording packet
    
    PUBLIC KEY INCOMING - Verify and record catch data
    """
    try:
        # Create incoming packet
        packet = IncomingPacket(
            source="catch",
            payload=packet_data,
            signature=packet_data.get("signature")
        )
        
        # Process through packet switcher
        result = await packet_switcher._handle_deckside(packet)
        
        # Update metrics
        packets_processed.labels(source="catch", status="success").inc()
        
        return {
            **result,
            "correlation_id": packet.correlation_id,
            "packet_hash": packet.hash()
        }
        
    except Exception as e:
        packets_processed.labels(source="catch", status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
