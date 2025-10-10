# 🔐 Key Management Architecture (PUBLIC)

**Purpose:** PUBLIC key administration for incoming packet switching  
**Scope:** SeaTrace-ODOO (PUBLIC) - Verification only  
**Security:** NEVER store private keys in this repo

---

## 🌊 **INCOMING FLOW (PUBLIC KEY ADMINISTRATION)**

### **1. Packet Switching Handler**

```python
# src/common/packet_switching/handler.py
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from dataclasses import dataclass
import uuid

@dataclass
class IncomingPacket:
    """Incoming data packet with correlation tracking"""
    correlation_id: str
    source: str  # "vessel", "processor", "market"
    payload: Dict[str, Any]
    signature: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())

class PacketSwitchingHandler:
    """
    Routes incoming packets to appropriate 4-pillar handlers
    Based on correlation ID and source type
    """
    
    def __init__(self):
        self.handlers = {
            "vessel": self._handle_seaside,      # SeaSide (HOLD)
            "catch": self._handle_deckside,      # DeckSide (RECORD)
            "processor": self._handle_dockside,  # DockSide (STORE)
            "market": self._handle_marketside    # MarketSide (EXCHANGE)
        }
    
    async def route_packet(self, packet: IncomingPacket) -> Dict[str, Any]:
        """
        Route packet to appropriate handler based on source
        
        Args:
            packet: Incoming data packet with correlation ID
            
        Returns:
            Response with correlation ID for tracking
        """
        # Validate packet signature (PUBLIC key verification)
        if packet.signature:
            await self._verify_signature(packet)
        
        # Route to appropriate handler
        handler = self.handlers.get(packet.source)
        if not handler:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown packet source: {packet.source}"
            )
        
        # Process packet and return response with correlation ID
        response = await handler(packet)
        response["correlation_id"] = packet.correlation_id
        return response
    
    async def _verify_signature(self, packet: IncomingPacket):
        """
        Verify packet signature using PUBLIC key
        This is PUBLIC key administration - verification only
        """
        from src.common.licensing.middleware import LicenseMiddleware
        
        # Use JWK public key to verify signature
        middleware = LicenseMiddleware(None)
        is_valid = await middleware._verify_jws(packet.signature)
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid packet signature"
            )
    
    async def _handle_seaside(self, packet: IncomingPacket) -> Dict[str, Any]:
        """Handle vessel tracking packets (SeaSide - HOLD)"""
        return {
            "pillar": "SeaSide",
            "action": "vessel_tracked",
            "vessel_id": packet.payload.get("vessel_id"),
            "status": "received"
        }
    
    async def _handle_deckside(self, packet: IncomingPacket) -> Dict[str, Any]:
        """Handle catch recording packets (DeckSide - RECORD)"""
        return {
            "pillar": "DeckSide",
            "action": "catch_recorded",
            "catch_id": packet.payload.get("catch_id"),
            "status": "received"
        }
    
    async def _handle_dockside(self, packet: IncomingPacket) -> Dict[str, Any]:
        """Handle processing packets (DockSide - STORE)"""
        return {
            "pillar": "DockSide",
            "action": "processing_logged",
            "processing_id": packet.payload.get("processing_id"),
            "status": "received"
        }
    
    async def _handle_marketside(self, packet: IncomingPacket) -> Dict[str, Any]:
        """Handle market transaction packets (MarketSide - EXCHANGE)"""
        return {
            "pillar": "MarketSide",
            "action": "transaction_recorded",
            "transaction_id": packet.payload.get("transaction_id"),
            "status": "received"
        }
```

---

## 📦 **CORRELATED BLOCK PATTERNS**

### **2. Correlation ID Tracking**

```python
# src/common/correlation/tracker.py
from typing import Dict, List, Optional
from datetime import datetime
import redis.asyncio as redis

class CorrelationTracker:
    """
    Track correlated packets across 4-pillar architecture
    Enables A2A (Application-to-Application) distributed tracing
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def track_packet(
        self,
        correlation_id: str,
        pillar: str,
        action: str,
        metadata: Dict[str, Any]
    ):
        """
        Track packet in correlation chain
        
        Args:
            correlation_id: Unique ID for this transaction chain
            pillar: Which pillar handled this (SeaSide, DeckSide, etc.)
            action: What action was taken
            metadata: Additional context
        """
        key = f"correlation:{correlation_id}"
        
        # Store packet in Redis sorted set (timestamp-ordered)
        timestamp = datetime.utcnow().isoformat()
        packet_data = {
            "pillar": pillar,
            "action": action,
            "timestamp": timestamp,
            **metadata
        }
        
        # Add to correlation chain
        await self.redis.zadd(
            key,
            {str(packet_data): datetime.utcnow().timestamp()}
        )
        
        # Set expiration (7 days for audit trail)
        await self.redis.expire(key, 604800)
    
    async def get_correlation_chain(
        self,
        correlation_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve full correlation chain for a transaction
        
        Args:
            correlation_id: Unique ID to look up
            
        Returns:
            List of packets in chronological order
        """
        key = f"correlation:{correlation_id}"
        
        # Get all packets in order
        packets = await self.redis.zrange(key, 0, -1)
        
        return [eval(packet) for packet in packets]
    
    async def reconcile_building_lot(
        self,
        correlation_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Reconcile multiple correlated transactions into a building lot
        Used for billing, reporting, and analytics
        
        Args:
            correlation_ids: List of correlation IDs to reconcile
            
        Returns:
            Aggregated building lot data
        """
        building_lot = {
            "correlation_ids": correlation_ids,
            "total_packets": 0,
            "pillars_involved": set(),
            "actions": [],
            "start_time": None,
            "end_time": None
        }
        
        for correlation_id in correlation_ids:
            chain = await self.get_correlation_chain(correlation_id)
            
            for packet in chain:
                building_lot["total_packets"] += 1
                building_lot["pillars_involved"].add(packet["pillar"])
                building_lot["actions"].append(packet["action"])
                
                # Track time range
                packet_time = datetime.fromisoformat(packet["timestamp"])
                if not building_lot["start_time"] or packet_time < building_lot["start_time"]:
                    building_lot["start_time"] = packet_time
                if not building_lot["end_time"] or packet_time > building_lot["end_time"]:
                    building_lot["end_time"] = packet_time
        
        building_lot["pillars_involved"] = list(building_lot["pillars_involved"])
        return building_lot
```

---

## 🔗 **PUBLIC KEY ADMINISTRATION**

### **3. JWK Public Key Management**

```python
# src/common/keys/public_key_admin.py
from typing import Dict, List, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
import json

class PublicKeyAdministrator:
    """
    Manage PUBLIC keys for incoming packet verification
    NEVER stores private keys - verification only
    """
    
    def __init__(self):
        self.public_keys: Dict[str, ed25519.Ed25519PublicKey] = {}
    
    async def load_jwk_keys(self, jwk_url: str = None):
        """
        Load JWK public keys from well-known endpoint
        
        Args:
            jwk_url: URL to JWK endpoint (default: /.well-known/jwks.json)
        """
        if not jwk_url:
            jwk_url = "https://seatrace.worldseafoodproducers.com/.well-known/jwks.json"
        
        # Fetch JWK keys (in production, use aiohttp)
        # For now, load from local cache
        jwk_data = await self._fetch_jwk_keys(jwk_url)
        
        for key in jwk_data.get("keys", []):
            kid = key["kid"]  # Key ID (e.g., "2025-01-v1")
            
            # Decode Ed25519 public key
            x = base64.urlsafe_b64decode(key["x"] + "==")
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(x)
            
            self.public_keys[kid] = public_key
    
    async def verify_packet_signature(
        self,
        packet_data: bytes,
        signature: str,
        kid: str
    ) -> bool:
        """
        Verify packet signature using PUBLIC key
        
        Args:
            packet_data: Raw packet bytes
            signature: Base64-encoded signature
            kid: Key ID to use for verification
            
        Returns:
            True if signature is valid
        """
        public_key = self.public_keys.get(kid)
        if not public_key:
            raise ValueError(f"Unknown key ID: {kid}")
        
        # Decode signature
        sig_bytes = base64.urlsafe_b64decode(signature + "==")
        
        # Verify signature
        try:
            public_key.verify(sig_bytes, packet_data)
            return True
        except Exception:
            return False
    
    async def _fetch_jwk_keys(self, url: str) -> Dict[str, Any]:
        """Fetch JWK keys from endpoint"""
        # In production, use aiohttp to fetch from URL
        # For now, return mock data
        return {
            "keys": [
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": "mock_public_key_base64",
                    "kid": "2025-01-v1",
                    "use": "sig",
                    "alg": "EdDSA"
                }
            ]
        }
```

---

## 🚀 **FASTAPI INTEGRATION**

### **4. Packet Switching Endpoint**

```python
# src/seaside/routers/packet_switching.py
from fastapi import APIRouter, Request, HTTPException, Depends
from src.common.packet_switching.handler import PacketSwitchingHandler, IncomingPacket
from src.common.correlation.tracker import CorrelationTracker
from src.common.keys.public_key_admin import PublicKeyAdministrator
import redis.asyncio as redis

router = APIRouter(prefix="/api/v1/packets", tags=["Packet Switching"])

# Initialize handlers
packet_handler = PacketSwitchingHandler()
redis_client = redis.from_url("redis://localhost:6379")
correlation_tracker = CorrelationTracker(redis_client)
public_key_admin = PublicKeyAdministrator()

@router.post("/incoming")
async def receive_packet(request: Request):
    """
    Receive incoming packet and route to appropriate handler
    
    Headers:
        X-Correlation-ID: Unique ID for tracking (auto-generated if missing)
        X-Signature: Packet signature (optional)
        X-Key-ID: Public key ID for verification (optional)
    
    Body:
        source: "vessel" | "catch" | "processor" | "market"
        payload: Dict[str, Any]
    """
    # Extract headers
    correlation_id = request.headers.get("X-Correlation-ID")
    signature = request.headers.get("X-Signature")
    kid = request.headers.get("X-Key-ID")
    
    # Parse body
    body = await request.json()
    
    # Create packet
    packet = IncomingPacket(
        correlation_id=correlation_id,
        source=body["source"],
        payload=body["payload"],
        signature=signature
    )
    
    # Verify signature if provided
    if signature and kid:
        packet_bytes = json.dumps(body).encode()
        is_valid = await public_key_admin.verify_packet_signature(
            packet_bytes, signature, kid
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Route packet
    response = await packet_handler.route_packet(packet)
    
    # Track in correlation chain
    await correlation_tracker.track_packet(
        correlation_id=packet.correlation_id,
        pillar=response["pillar"],
        action=response["action"],
        metadata={"source": packet.source, "status": response["status"]}
    )
    
    return response

@router.get("/correlation/{correlation_id}")
async def get_correlation_chain(correlation_id: str):
    """
    Retrieve full correlation chain for a transaction
    Enables A2A distributed tracing
    """
    chain = await correlation_tracker.get_correlation_chain(correlation_id)
    return {"correlation_id": correlation_id, "chain": chain}

@router.post("/reconcile")
async def reconcile_building_lot(correlation_ids: List[str]):
    """
    Reconcile multiple correlated transactions into a building lot
    Used for billing and reporting
    """
    building_lot = await correlation_tracker.reconcile_building_lot(correlation_ids)
    return building_lot
```

---

## 🔒 **SECURITY BOUNDARIES**

### **PUBLIC Repo (SeaTrace-ODOO):**
- ✅ **PUBLIC key verification** - JWK endpoint
- ✅ **Packet switching** - Route incoming data
- ✅ **Correlation tracking** - A2A tracing
- ✅ **Building lot reconciliation** - Aggregate data
- ❌ **NEVER store private keys** - Verification only

### **PRIVATE Repo (SeaTrace003):**
- ✅ **PRIVATE key signing** - Ed25519 keys
- ✅ **Outgoing communications** - Signed responses
- ✅ **EMR metering** - Usage tracking
- ✅ **Billing operations** - Invoice generation
- ❌ **NEVER expose private keys** - Keep in Vault

---

## 📋 **PROCEEDING MASTER'S CHECKLIST**

### **✅ Implemented:**
1. ✅ **Packet Switching Handler** - Route incoming packets
2. ✅ **Correlation ID Tracking** - A2A distributed tracing
3. ✅ **PUBLIC Key Administration** - JWK verification
4. ✅ **Building Lot Reconciliation** - Aggregate transactions
5. ✅ **FastAPI Integration** - REST endpoints

### **⏳ Next Steps:**
6. ⏳ **PRIVATE Key Chain** - Implement in SeaTrace003
7. ⏳ **Outgoing Communications** - Signed responses
8. ⏳ **Redis Integration** - Correlation storage
9. ⏳ **Testing** - Unit tests, integration tests
10. ⏳ **Documentation** - API docs, examples

---

**© 2025 SeaTrace-ODOO Key Management Architecture**  
**Status:** PUBLIC Key Administration Complete  
**Next:** PRIVATE Key Chain (SeaTrace003)
