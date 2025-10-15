"""
🏈 SeaTrace Packet Router
For the Commons Good! 🌊

Central routing hub for EM (Enterprise Message) packets
Routes to appropriate 4-pillar microservice based on source
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .handler import IncomingPacket, WildFisheriesPacketSwitcher

app = FastAPI(
    title="SeaTrace Packet Router",
    description="Central routing hub for 4-pillar packet switching",
    version="1.0.0"
)

# Initialize packet switcher
packet_switcher = WildFisheriesPacketSwitcher()

# Prometheus metrics
packets_routed = Counter('router_packets_routed', 'Packets routed', ['source', 'pillar', 'status'])
routing_duration = Histogram('router_duration_seconds', 'Routing duration')

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "packet_router",
        "pillars": list(packet_switcher.pillar_routes.values())
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint with routing information"""
    return {
        "service": "SeaTrace Packet Router",
        "version": "1.0.0",
        "routes": packet_switcher.pillar_routes,
        "endpoints": {
            "/route": "POST - Route packet to appropriate pillar",
            "/health": "GET - Health check",
            "/metrics": "GET - Prometheus metrics"
        }
    }

@app.post("/route")
async def route_packet(packet_data: Dict[str, Any]):
    """
    🏈 ROUTE THE PLAY - Central packet routing
    
    Routes incoming EM packets to appropriate pillar:
    - vessel → SeaSide (HOLD)
    - catch → DeckSide (RECORD)
    - processor → DockSide (STORE)
    - market → MarketSide (EXCHANGE)
    """
    try:
        # Create incoming packet
        packet = IncomingPacket(
            source=packet_data.get("source", ""),
            payload=packet_data.get("payload", {}),
            signature=packet_data.get("signature")
        )
        
        # Validate source
        if packet.source not in packet_switcher.pillar_routes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source: {packet.source}. "
                       f"Valid sources: {list(packet_switcher.pillar_routes.keys())}"
            )
        
        # Route through packet switcher
        result = await packet_switcher.process_packet(packet)
        
        # Update metrics
        pillar = packet_switcher.pillar_routes[packet.source]
        packets_routed.labels(
            source=packet.source,
            pillar=pillar,
            status="success"
        ).inc()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        packets_routed.labels(
            source=packet_data.get("source", "unknown"),
            pillar="unknown",
            status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
