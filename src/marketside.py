"""
MarketSide Pillar (WR1 - EXCHANGE/Public API)
For the Commons Good! 🌊

PUBLIC KEY INCOMING - Market exchange and consumer verification
Receives packets from WildFisheriesPacketSwitcher
OUTGOING DASHBOARD - PM Token access for investors/endorsers
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
    title="MarketSide - Exchange",
    description="WR1: EXCHANGE - Public API and consumer verification",
    version="1.0.0"
)

# Initialize packet switcher
packet_switcher = WildFisheriesPacketSwitcher()

# Prometheus metrics
requests_total = Counter('marketside_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('marketside_request_duration_seconds', 'Request duration')
packets_processed = Counter('marketside_packets_processed', 'Packets processed', ['source', 'status'])

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "pillar": "marketside", "role": "EXCHANGE"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "pillar": "MarketSide",
        "role": "EXCHANGE",
        "description": "Public API and consumer verification",
        "position": "WR1 (Wide Receiver)",
        "accepts": ["market packets", "transaction data", "PM tokens"],
        "pm_tokens": {
            "PM-SEAS-2024-001": "Fisheries Digital Monitoring",
            "PM-DECK-2024-002": "Seafood Contributors",
            "PM-DOCK-2024-003": "Business Managers",
            "PM-MARK-2024-004": "Investors (Demo Access)"
        }
    }

@app.post("/ingest/packet")
async def ingest_packet(packet_data: Dict[str, Any]):
    """
    🏈 SCORE - Process market transaction packet
    
    PUBLIC KEY INCOMING - Verify and record transaction
    """
    try:
        # Create incoming packet
        packet = IncomingPacket(
            source="market",
            payload=packet_data,
            signature=packet_data.get("signature")
        )
        
        # Process through packet switcher
        result = await packet_switcher._handle_marketside(packet)
        
        # Update metrics
        packets_processed.labels(source="market", status="success").inc()
        
        return {
            **result,
            "correlation_id": packet.correlation_id,
            "packet_hash": packet.hash()
        }
        
    except Exception as e:
        packets_processed.labels(source="market", status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pm/verify")
async def verify_pm_token(token: str):
    """
    🔐 PM TOKEN VERIFICATION - Investor/Endorser Access
    
    OUTGOING DASHBOARD - Grant demo access based on PM token
    """
    # TODO: Wire to database for token validation
    valid_tokens = {
        "PM-SEAS-2024-001": "Fisheries Digital Monitoring",
        "PM-DECK-2024-002": "Seafood Contributors",
        "PM-DOCK-2024-003": "Business Managers",
        "PM-MARK-2024-004": "Investors"
    }
    
    if token in valid_tokens:
        return {
            "valid": True,
            "access_level": valid_tokens[token],
            "pillar": "MarketSide",
            "dashboard_url": "/dashboard"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid PM token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
