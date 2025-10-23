# Public/Private Key Development Guide
## 4-Pillar Pair Practices for SeaTrace

**Last Updated:** October 22, 2025  
**Purpose:** Development team guide for implementing public/private key cryptography across the 4-Pillar architecture  
**Classification:** MODULAR STAGE 1 - Security Foundation

---

## 🔑 Public/Private Keys: The Core of SeaTrace Trust & Value

Think of the keys as **digital ID cards and unique signature stamps**:

* **Public Key:** Like a verifiable ID card. It proves *who* you are (authentication) and allows others to send you encrypted messages only you can open. Used for **access control** and **identification**.
* **Private Key:** Like your unique, unforgeable signature stamp. You use it to *sign* data, proving *you* created or approved it (integrity, non-repudiation). It also decrypts messages sent to your public key. Used for **data signing** and **decryption**.

### Key Hierarchy & Trust Model

```
┌─────────────────────────────────────────────────────────────────┐
│                     ROOT CERTIFICATE AUTHORITY                   │
│                    (SeaTrace Master Key Pair)                    │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
        ┌────────────────────┴────────────────────┐
        ↓                                         ↓
┌──────────────────┐                    ┌──────────────────┐
│ SERVICE KEYS     │                    │ ENTITY KEYS      │
│ (Internal Trust) │                    │ (External Trust) │
└────────┬─────────┘                    └────────┬─────────┘
         ↓                                       ↓
    ┌────┴────┐                        ┌─────────┴──────────┐
    ↓         ↓                        ↓                    ↓
 SeaSide  DeckSide                  Vessels            Processors
 DockSide MarketSide                Facilities          Traders
                                    Regulators          Consumers
```

**Trust Levels:**
1. **Root CA:** SeaTrace Master Key (offline, hardware security module)
2. **Service Keys:** Each pillar service has its own signing key
3. **Entity Keys:** External actors (vessels, processors, etc.) have registered keys

---

## 1. SeaSide (HOLD): Establishing Trusted Origin 🚢

### Primary Function
**Authenticate incoming vessel data and sign the initial packet to establish chain of custody.**

---

### Use Case 1A: Vessel Authentication (F/V PING)

**Scenario:** A fishing vessel transmits its position (AIS data) to SeaSide

**Public Key Use Case:**
The Fishing Vessel (`F/V`) authenticates itself to the `SeaSide` API endpoint (`POST /api/v1/seaside/vessels/{id}/positions`) by presenting proof of ownership of its **public key** via:
- **Option 1:** JWT token signed by vessel's private key
- **Option 2:** mTLS client certificate containing vessel's public key
- **Option 3:** Ed25519 signature in request header

**Implementation Flow:**
```python
# services/seaside/api/vessels.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from src.common.security.crypto import verify_vessel_signature
from src.common.security.jwk_cache import get_vessel_public_key

router = APIRouter()
security = HTTPBearer()

@router.post("/vessels/{vessel_id}/positions")
async def record_vessel_position(
    vessel_id: str,
    position_data: VesselPositionData,
    token: str = Depends(security)
):
    """
    CLAIM 1: Vessel PING ingestion with public key authentication
    
    Public Key Validation:
    1. Extract vessel_id from JWT or mTLS cert
    2. Retrieve vessel's public key from central registry
    3. Verify signature on position_data payload
    4. Confirm vessel_id matches authenticated identity
    """
    
    # Step 1: Get vessel's public key from registry
    vessel_public_key = await get_vessel_public_key(vessel_id)
    if not vessel_public_key:
        raise HTTPException(
            status_code=401,
            detail=f"Vessel {vessel_id} not registered or public key not found"
        )
    
    # Step 2: Verify signature on incoming data
    signature = token.credentials  # From Authorization: Bearer header
    is_valid = await verify_vessel_signature(
        data=position_data.dict(),
        signature=signature,
        public_key=vessel_public_key
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid signature: vessel authentication failed"
        )
    
    # Step 3: Correlate with GFW (optional, for anomaly detection)
    gfw_status = await correlate_with_gfw(vessel_id, position_data)
    
    # Step 4: Create validated packet (to be signed by SeaSide)
    validated_packet = {
        "vessel_id": vessel_id,
        "position": position_data.dict(),
        "gfw_correlation": gfw_status,
        "validated_at": datetime.utcnow().isoformat(),
        "validator": "seaside"
    }
    
    # Forward to packet handler for SeaSide signing
    await packet_handler.process_ping(validated_packet)
    
    return {"status": "accepted", "packet_id": validated_packet["packet_id"]}
```

---

### Use Case 1B: SeaSide Internal Signing (Packet Creation)

**Scenario:** After validating the vessel PING, SeaSide signs the packet before forwarding to message queue

**Private Key Use Case:**
The `SeaSide` service uses its *own internal* **private key** to **sign** the complete, validated packet. This signature proves the data originated from *and was validated by* the trusted SeaSide system.

**Implementation Flow:**
```python
# services/seaside/packet_handler.py

from src.common.security.crypto import sign_with_service_key
from datetime import datetime
import uuid

class PacketSwitchingHandler:
    """Handles secure packet validation and signing."""
    
    def __init__(self):
        self.service_private_key = load_service_private_key("seaside")
        self.service_public_key_id = "seaside-2025-10"  # Key rotation identifier
    
    async def process_ping(self, validated_packet: Dict[str, Any]):
        """
        CLAIM 1: Sign validated vessel PING packet
        
        Private Key Usage:
        1. Add SeaSide metadata to validated packet
        2. Sign entire packet with SeaSide's private key
        3. Attach signature and public key ID
        4. Forward to message queue (Kafka/RabbitMQ)
        """
        
        # Step 1: Add SeaSide processing metadata
        packet_id = f"ping-{uuid.uuid4()}"
        seaside_packet = {
            "packet_id": packet_id,
            "packet_type": "vessel_ping",
            "data": validated_packet,
            "processed_by": "seaside",
            "processed_at": datetime.utcnow().isoformat(),
            "public_key_id": self.service_public_key_id
        }
        
        # Step 2: Sign the entire packet with SeaSide private key
        packet_json = json.dumps(seaside_packet, sort_keys=True)
        signature = await sign_with_service_key(
            data=packet_json,
            private_key=self.service_private_key
        )
        
        # Step 3: Attach signature
        seaside_packet["signature"] = signature
        
        # Step 4: Forward to message queue
        await self.message_queue.publish(
            topic="seaside.validated_pings",
            message=seaside_packet
        )
        
        # Step 5: Update Prometheus metrics
        PACKET_PROCESSING_TOTAL.inc()
        
        logger.info(
            "Signed vessel PING packet",
            packet_id=packet_id,
            vessel_id=validated_packet["vessel_id"],
            signature_key_id=self.service_public_key_id
        )
        
        return packet_id
```

---

### 🛠️ Pair Practice Task 1: Auth Pair (SeaSide Authentication)

**Team:** Auth Pair (2 developers)  
**Sprint:** Week 1-2  
**Priority:** P0 (Blocking)

**Deliverables:**
1. **Implement FastAPI authentication middleware**
   - File: `src/common/security/vessel_auth.py`
   - Function: `verify_vessel_token(token: str) -> VesselIdentity`
   - Test: `tests/security/test_vessel_auth.py`

2. **Create vessel public key registry client**
   - File: `src/common/security/jwk_cache.py`
   - Function: `get_vessel_public_key(vessel_id: str) -> PublicKey`
   - Cache: Redis TTL 1 hour
   - Test: `tests/security/test_jwk_cache.py`

3. **Implement Ed25519 signature verification**
   - File: `src/common/security/crypto.py`
   - Function: `verify_vessel_signature(data, signature, public_key) -> bool`
   - Test: `tests/security/test_crypto.py`

**Acceptance Criteria:**
- ✅ Vessel can authenticate with JWT containing Ed25519 signature
- ✅ Invalid signatures rejected with 401 Unauthorized
- ✅ Public key cache reduces registry lookups by 95%
- ✅ Test coverage >90% for authentication flow

---

### 🛠️ Pair Practice Task 2: Packet Handling Pair (SeaSide Signing)

**Team:** Packet Handling Pair (2 developers)  
**Sprint:** Week 2-3  
**Priority:** P0 (Blocking)

**Deliverables:**
1. **Enhance packet_handler.py with signing logic**
   - File: `services/seaside/packet_handler.py`
   - Method: `PacketSwitchingHandler.process_ping(validated_packet)`
   - Test: `tests/seaside/test_packet_handler.py`

2. **Implement service key management**
   - File: `src/common/security/service_keys.py`
   - Function: `load_service_private_key(service_name: str) -> PrivateKey`
   - Storage: AWS Secrets Manager or HashiCorp Vault
   - Test: `tests/security/test_service_keys.py`

3. **Create message queue publisher**
   - File: `src/common/messaging/queue_client.py`
   - Function: `publish(topic, message) -> MessageId`
   - Test: `tests/messaging/test_queue_client.py`

**Acceptance Criteria:**
- ✅ SeaSide packet signed with Ed25519 private key
- ✅ Signature verifiable using SeaSide public key
- ✅ Signed packets published to `seaside.validated_pings` topic
- ✅ Prometheus metric `seaside_packets_signed_total` increments
- ✅ Test coverage >95% for signing logic

---

## 2. DeckSide (RECORD): Signing the Catch & Forking the Chains 🎣

### Primary Function
**Verify the official catch record (e-Log) and create separate, signed public/private data streams.**

---

### Use Case 2A: Captain's e-Log Submission (Dual Signature)

**Scenario:** Captain submits catch data via e-Log, creating the official record

**Public Key Use Case:**
The Captain/Vessel authenticates to the `DeckSide` API endpoint (`POST /api/v1/deckside/catches`) using their **public key**, similar to SeaSide authentication.

**Private Key Use Case (Vessel):**
The Captain/Vessel uses their **private key** to *sign* the submitted `e-Log` data payload. DeckSide verifies this signature using the vessel's public key. This creates the **non-repudiable** record of the catch declaration.

**Implementation Flow:**
```python
# services/deckside/api/catches.py

from fastapi import APIRouter, Depends, HTTPException
from src.common.security.crypto import verify_vessel_signature
from src.common.security.jwk_cache import get_vessel_public_key

router = APIRouter()

@router.post("/catches")
async def record_catch(
    catch_data: CatchSubmissionData,
    vessel_auth: VesselIdentity = Depends(verify_vessel_auth)
):
    """
    CLAIM 2: Captain's e-Log submission with dual signature verification
    
    Dual Signature Validation:
    1. Verify vessel authenticated (public key check)
    2. Verify captain signed the catch_data payload (private key signature)
    3. Create non-repudiable record linking vessel to catch declaration
    """
    
    # Step 1: Vessel already authenticated via dependency injection
    vessel_id = vessel_auth.vessel_id
    
    # Step 2: Verify captain's signature on catch data
    vessel_public_key = await get_vessel_public_key(vessel_id)
    is_valid_signature = await verify_vessel_signature(
        data=catch_data.catch_payload,
        signature=catch_data.captain_signature,
        public_key=vessel_public_key
    )
    
    if not is_valid_signature:
        raise HTTPException(
            status_code=401,
            detail="Invalid captain signature: catch record rejected"
        )
    
    # Step 3: Create non-repudiable catch record
    catch_record = {
        "catch_id": f"catch-{uuid.uuid4()}",
        "vessel_id": vessel_id,
        "captain_signature": catch_data.captain_signature,
        "catch_data": catch_data.catch_payload,
        "recorded_at": datetime.utcnow().isoformat(),
        "signature_verified": True,
        "public_key_id": vessel_public_key.key_id
    }
    
    # Step 4: Forward to forking handler
    await fork_handler.process_catch_record(catch_record)
    
    return {
        "status": "accepted",
        "catch_id": catch_record["catch_id"],
        "public_packet_id": "pending",  # Will be set by fork_handler
        "private_packet_id": "pending"
    }
```

---

### Use Case 2B: DeckSide Packet Forking (THE CRITICAL SEPARATION POINT)

**Scenario:** After verifying captain's signature, DeckSide FORKS the data into PUBLIC (Commons Good) and PRIVATE (Investor) chains

**Private Key Use Case (DeckSide):**
DeckSide uses its *own internal* **private key** to separately sign:
1. The **`public estimated #CATCH KEY PACKET_ID`** (for SIMP/Commons Good)
2. The **`projected PRIVATE $CHECK KEY`** packet (the financial "Prospectus" for investors)

**Implementation Flow:**
```python
# services/deckside/handlers/fork_handler.py

from src.common.security.crypto import sign_with_service_key
from src.public_models.public_catch import PublicCatch
import uuid

class CatchForkHandler:
    """
    CLAIM 2: THE DUAL-LICENSE SEPARATION POINT
    
    This handler implements the CRITICAL FORKING LOGIC that separates:
    - PUBLIC CHAIN (Commons Good, FREE, SIMP-compliant)
    - PRIVATE CHAIN (Investor Value, PAID, Financial data)
    """
    
    def __init__(self):
        self.deckside_private_key = load_service_private_key("deckside")
        self.public_key_id = "deckside-2025-10"
    
    async def process_catch_record(self, verified_catch: Dict[str, Any]):
        """
        THE CORE DUAL-LICENSE SEPARATION POINT
        
        When captain submits e-Log, create TWO parallel chains:
        
        PUBLIC CHAIN (Commons Good):
        - species_code (FAO standard)
        - general_catch_area (FAO area, no specific coords)
        - landed_timestamp
        - landed_weight_kg
        - compliance_status (SIMP-required)
        
        PRIVATE CHAIN (Investor Value):
        - projected_check_value (financial forecast)
        - specific_ping_coordinates (exact fishing location)
        - ml_quality_scores (predictive analytics)
        - financial_reconciliation_data (cost/revenue)
        """
        
        # === PUBLIC CHAIN CREATION ===
        public_packet_id = f"catch-pub-{uuid.uuid4()}"
        public_catch = {
            "packet_id": public_packet_id,
            "packet_type": "public_catch",
            "vessel_public_id": anonymize_vessel_id(verified_catch["vessel_id"]),
            "species_code": verified_catch["catch_data"]["species"],  # FAO code
            "general_catch_area": anonymize_location(
                verified_catch["catch_data"]["coordinates"]
            ),  # FAO-77 instead of exact lat/lon
            "landed_timestamp": verified_catch["catch_data"]["timestamp"],
            "landed_weight_kg": verified_catch["catch_data"]["estimated_weight"],
            "compliance_status": await validate_simp_compliance(verified_catch),
            "processed_by": "deckside",
            "processed_at": datetime.utcnow().isoformat(),
            "public_key_id": self.public_key_id
        }
        
        # Sign PUBLIC chain with DeckSide private key
        public_signature = await sign_with_service_key(
            data=json.dumps(public_catch, sort_keys=True),
            private_key=self.deckside_private_key
        )
        public_catch["signature"] = public_signature
        
        # === PRIVATE CHAIN CREATION ===
        private_packet_id = f"catch-priv-{uuid.uuid4()}"
        private_catch = {
            "packet_id": private_packet_id,
            "packet_type": "private_catch",
            "vessel_id": verified_catch["vessel_id"],  # Full vessel ID (not anonymized)
            "species_code": verified_catch["catch_data"]["species"],
            "specific_coordinates": verified_catch["catch_data"]["coordinates"],  # Exact lat/lon
            "projected_check_value": await predict_catch_value(verified_catch),  # Financial forecast
            "ml_quality_scores": await run_quality_ml_model(verified_catch),  # Predictive analytics
            "financial_data": await calculate_catch_financials(verified_catch),  # Cost/revenue
            "captain_signature": verified_catch["captain_signature"],  # Original signature
            "processed_by": "deckside",
            "processed_at": datetime.utcnow().isoformat(),
            "public_key_id": self.public_key_id
        }
        
        # Sign PRIVATE chain with DeckSide private key
        private_signature = await sign_with_service_key(
            data=json.dumps(private_catch, sort_keys=True),
            private_key=self.deckside_private_key
        )
        private_catch["signature"] = private_signature
        
        # === ROUTING LOGIC ===
        # Route PUBLIC chain to SeaTrace-ODOO (PUBLIC-UNLIMITED)
        await self.forward_to_public_api(public_catch)
        
        # Route PRIVATE chain to SeaTrace002/003 (PRIVATE-LIMITED)
        await self.forward_to_investor_dashboard(private_catch)
        
        # === LINK PACKETS FOR RECONCILIATION ===
        packet_link = {
            "public_packet_id": public_packet_id,
            "private_packet_id": private_packet_id,
            "catch_id": verified_catch["catch_id"],
            "linked_at": datetime.utcnow().isoformat()
        }
        await self.store_packet_link(packet_link)
        
        logger.info(
            "Forked catch into public/private chains",
            catch_id=verified_catch["catch_id"],
            public_packet_id=public_packet_id,
            private_packet_id=private_packet_id
        )
        
        return {
            "public_packet_id": public_packet_id,
            "private_packet_id": private_packet_id
        }
    
    async def forward_to_public_api(self, public_packet: Dict):
        """Forward public chain to SeaTrace-ODOO for Commons Good access."""
        await httpx.AsyncClient().post(
            "https://api.seatrace-odoo.local/internal/deckside/public-chain",
            json=public_packet,
            cert=("/path/to/deckside-client.crt", "/path/to/deckside-client.key")
        )
    
    async def forward_to_investor_dashboard(self, private_packet: Dict):
        """Forward private chain to SeaTrace002/003 for investor access."""
        await httpx.AsyncClient().post(
            "https://internal.seatrace002.local/api/deckside/private-chain",
            json=private_packet,
            cert=("/path/to/deckside-client.crt", "/path/to/deckside-client.key")
        )
```

---

### 🛠️ Pair Practice Task 1: API & Verification Pair (DeckSide Catch Submission)

**Team:** API & Verification Pair (2 developers)  
**Sprint:** Week 3-4  
**Priority:** P0 (Blocking - Critical Fork Implementation)

**Deliverables:**
1. **Implement `/api/v1/deckside/catches` endpoint**
   - File: `services/deckside/api/catches.py`
   - Function: `record_catch(catch_data, vessel_auth)`
   - Test: `tests/deckside/test_catches_api.py`

2. **Verify captain's signature on catch data**
   - Use existing `verify_vessel_signature()` from SeaSide
   - Validate signature matches vessel's public key
   - Test: `tests/deckside/test_captain_signature_verification.py`

3. **Create non-repudiable catch record**
   - Store in MongoDB/PostgreSQL with signature
   - Link to vessel's public key ID
   - Test: `tests/deckside/test_catch_record_storage.py`

**Acceptance Criteria:**
- ✅ Captain can submit e-Log with Ed25519 signature
- ✅ Invalid signatures rejected with 401
- ✅ Catch record includes captain_signature, public_key_id, signature_verified flag
- ✅ Test coverage >90%

---

### 🛠️ Pair Practice Task 2: Forking Logic Pair (THE MOST CRITICAL TASK)

**Team:** Forking Logic Pair (2 senior developers)  
**Sprint:** Week 4-6  
**Priority:** P0+ (CRITICAL - Blocking all downstream work)

**Deliverables:**
1. **Create `fork_handler.py` with packet forking logic**
   - File: `services/deckside/handlers/fork_handler.py`
   - Class: `CatchForkHandler`
   - Method: `process_catch_record(verified_catch)`
   - Test: `tests/deckside/test_fork_handler.py`

2. **Implement public chain packet creator**
   - Anonymize vessel_id (map to public_vessel_id)
   - Generalize coordinates (FAO area instead of lat/lon)
   - Include only SIMP-required fields
   - Sign with DeckSide private key
   - Test: `tests/deckside/test_public_chain_creation.py`

3. **Implement private chain packet creator**
   - Include full vessel_id (not anonymized)
   - Include specific coordinates (exact lat/lon)
   - Calculate projected_check_value (financial forecast)
   - Run ML quality model
   - Sign with DeckSide private key
   - Test: `tests/deckside/test_private_chain_creation.py`

4. **Implement routing logic**
   - Forward public chain to SeaTrace-ODOO via mTLS
   - Forward private chain to SeaTrace002 via mTLS
   - Store packet link for reconciliation
   - Test: `tests/deckside/test_packet_routing.py`

5. **Create anonymization utilities**
   - File: `services/deckside/utils/anonymization.py`
   - Function: `anonymize_vessel_id(vessel_id) -> public_vessel_id`
   - Function: `anonymize_location(coords) -> fao_area`
   - Test: `tests/deckside/test_anonymization.py`

**Acceptance Criteria:**
- ✅ Forking creates TWO distinct packets (public/private)
- ✅ PUBLIC packet contains ONLY non-sensitive fields
- ✅ PRIVATE packet contains financial + ML data
- ✅ Both packets signed with DeckSide Ed25519 private key
- ✅ Signatures verifiable using DeckSide public key
- ✅ Public chain routed to SeaTrace-ODOO
- ✅ Private chain routed to SeaTrace002/003
- ✅ Packet link stored for future reconciliation
- ✅ Prometheus metrics: `deckside_packets_forked_total`
- ✅ Test coverage >95% (this is THE critical component)

**Code Review Requirements:**
- 🔒 Security review by security team (validate no private data leaks to public chain)
- 🔒 Architecture review by tech lead (validate routing logic)
- 🔒 Finance review by product team (validate projected_check_value calculations)
- 🔒 Compliance review by legal (validate SIMP compliance)

---

## 3. DockSide (STORE): Securing the Reconciliation & Ledger 🐟

*(Note: User feedback - emoji should be holding fish, not steel. Using 🐟 for now)*

### Primary Function
**Authenticate processors/handlers and sign the final, reconciled, immutable records.**

---

### Use Case 3A: Processor Authentication & Lot Management

**Scenario:** Dock operators or processors manage lot splitting and reconciliation

**Public Key Use Case:**
Dock Operators or Processors use their **public keys** to authenticate when interacting with `DockSide` APIs:
- `POST /api/v1/dockside/processing` - Initiate processing
- `GET /api/v1/dockside/lots/{lot_id}` - Retrieve lot data
- `POST /api/v1/dockside/lots/{lot_id}/reconcile` - Reconcile projected vs actual

**Implementation Flow:**
```python
# services/dockside/api/processing.py

from fastapi import APIRouter, Depends
from src.common.security.crypto import verify_processor_signature

router = APIRouter()

@router.post("/processing")
async def initiate_processing(
    landing_data: LandingMetrics,
    processor_auth: ProcessorIdentity = Depends(verify_processor_auth)
):
    """
    CLAIM 3: Processor initiates landing/processing
    
    Public Key Authentication:
    1. Verify processor's public key against registry
    2. Validate processor authorized for this facility
    3. Create processing record linked to processor identity
    """
    
    processor_id = processor_auth.processor_id
    facility_id = processor_auth.facility_id
    
    # Verify processor authorized for this facility
    if not await verify_facility_authorization(processor_id, facility_id):
        raise HTTPException(
            status_code=403,
            detail=f"Processor {processor_id} not authorized for facility {facility_id}"
        )
    
    # Create processing record
    processing_record = {
        "processing_id": f"proc-{uuid.uuid4()}",
        "processor_id": processor_id,
        "facility_id": facility_id,
        "landing_data": landing_data.dict(),
        "initiated_at": datetime.utcnow().isoformat(),
        "status": "in_progress"
    }
    
    # Forward to store handler for reconciliation
    await store_handler.process_landing(processing_record)
    
    return {"processing_id": processing_record["processing_id"]}
```

---

### Use Case 3B: DockSide Signing (Immutable Ledger)

**Scenario:** After reconciling physical landed weight against DeckSide packets, DockSide signs the final immutable record

**Private Key Use Case (DockSide):**
The `DockSide` service uses its *own internal* **private key** to **sign** the final, verified data block for each lot. This signed block (containing links to parent packets, actual weights, processing steps, blockchain anchor hash) represents the "consensus" seal.

**Implementation Flow:**
```python
# services/dockside/handlers/store_handler.py

from src.common.security.crypto import sign_with_service_key
from src.common.blockchain.anchor import anchor_to_blockchain

class DockSideStoreHandler:
    """
    CLAIM 3: Secure reconciliation and immutable ledger signing
    """
    
    def __init__(self):
        self.dockside_private_key = load_service_private_key("dockside")
        self.public_key_id = "dockside-2025-10"
    
    async def process_landing(
        self,
        landing: LandingMetrics,
        crew_data: List[CrewShiftData]
    ) -> Dict:
        """
        Process landing with reconciliation and sign immutable record.
        
        Signing Logic:
        1. Reconcile projected (DeckSide) vs actual (DockSide) weights
        2. Split into child lots (A/B/C by grade)
        3. Calculate ML reconciliation score
        4. Create signed immutable data block
        5. Anchor to blockchain
        """
        
        # Step 1: Retrieve parent catch packets (from DeckSide)
        parent_public_packet = await get_public_catch_packet(landing.catch_id)
        parent_private_packet = await get_private_catch_packet(landing.catch_id)
        
        # Step 2: Reconciliation - compare projected vs actual
        reconciliation = {
            "projected_weight_kg": parent_private_packet["projected_weight"],
            "actual_landed_weight_kg": landing.weight_kg,
            "variance_kg": landing.weight_kg - parent_private_packet["projected_weight"],
            "variance_pct": (
                (landing.weight_kg - parent_private_packet["projected_weight"])
                / parent_private_packet["projected_weight"]
            ) * 100,
            "ml_accuracy_score": await calculate_ml_accuracy(
                parent_private_packet,
                landing
            )
        }
        
        # Step 3: Split into child lots by grade
        lots = await split_into_lots(landing)
        # Example: Lot A (Grade AAA), Lot B (Grade AA), Lot C (Grade A)
        
        # Step 4: For each lot, create signed immutable record
        signed_lots = []
        for lot in lots:
            lot_data = {
                "lot_id": f"lot-{uuid.uuid4()}",
                "parent_catch_public_packet_id": parent_public_packet["packet_id"],
                "parent_catch_private_packet_id": parent_private_packet["packet_id"],
                "lot_designation": lot["grade"],  # A, B, or C
                "weight_kg": lot["weight"],
                "processing_timestamp": datetime.utcnow().isoformat(),
                "storage_location": landing.facility_id,
                "reconciliation": reconciliation,
                "processed_by": "dockside",
                "public_key_id": self.public_key_id
            }
            
            # Sign the lot data with DockSide private key
            lot_signature = await sign_with_service_key(
                data=json.dumps(lot_data, sort_keys=True),
                private_key=self.dockside_private_key
            )
            lot_data["signature"] = lot_signature
            
            # Anchor to blockchain (immutable proof)
            blockchain_hash = await anchor_to_blockchain(lot_data)
            lot_data["blockchain_anchor_hash"] = blockchain_hash
            
            signed_lots.append(lot_data)
        
        # Step 5: Store signed lots in immutable ledger (PostgreSQL + blockchain)
        await self.store_immutable_lots(signed_lots)
        
        # Step 6: Update Prometheus metrics
        self.landing_cost_histogram.labels(
            vessel_id=landing.vessel_id,
            species=landing.species
        ).observe(calculate_total_cost(landing))
        
        logger.info(
            "Signed and anchored lot reconciliation",
            landing_id=landing.landing_id,
            lots_created=len(signed_lots),
            reconciliation_variance_pct=reconciliation["variance_pct"]
        )
        
        return {
            "status": "success",
            "lots": signed_lots,
            "reconciliation": reconciliation
        }
```

---

### 🛠️ Pair Practice Task 1: API & Odoo Pair (DockSide Processing Endpoints)

**Team:** API & Odoo Pair (2 developers)  
**Sprint:** Week 5-6  
**Priority:** P1 (Important)

**Deliverables:**
1. **Implement DockSide processing API endpoints**
   - File: `services/dockside/api/processing.py`
   - Endpoint: `POST /api/v1/dockside/processing`
   - Endpoint: `GET /api/v1/dockside/lots/{lot_id}`
   - Endpoint: `POST /api/v1/dockside/lots/{lot_id}/reconcile`
   - Test: `tests/dockside/test_processing_api.py`

2. **Integrate with Odoo stock/lot management**
   - File: `services/dockside/odoo/stock_integration.py`
   - Function: `create_stock_lot(lot_data) -> OdooLotId`
   - Function: `update_lot_weight(lot_id, actual_weight)`
   - Test: `tests/dockside/test_odoo_integration.py`

3. **Implement processor authentication**
   - Use existing vessel_auth pattern
   - Verify processor public key
   - Check facility authorization
   - Test: `tests/dockside/test_processor_auth.py`

**Acceptance Criteria:**
- ✅ Processor can authenticate with public key
- ✅ Processing endpoints create Odoo stock.lot records
- ✅ Facility authorization enforced
- ✅ Test coverage >85%

---

### 🛠️ Pair Practice Task 2: Ledger & Signing Pair (Immutable Record Creation)

**Team:** Ledger & Signing Pair (2 developers)  
**Sprint:** Week 6-7  
**Priority:** P0 (Blocking - Immutability Required)

**Deliverables:**
1. **Enhance `store_handler.py` with signing logic**
   - File: `services/dockside/handlers/store_handler.py`
   - Method: `process_landing(landing, crew_data)`
   - Add reconciliation calculation
   - Add lot splitting logic
   - Add DockSide signing
   - Test: `tests/dockside/test_store_handler_signing.py`

2. **Implement blockchain anchoring**
   - File: `src/common/blockchain/anchor.py`
   - Function: `anchor_to_blockchain(data) -> BlockchainHash`
   - Use Ethereum/Polygon for immutable proof
   - Test: `tests/blockchain/test_anchor.py`

3. **Create immutable ledger storage**
   - File: `services/dockside/storage/immutable_ledger.py`
   - Function: `store_signed_lot(lot_data)`
   - PostgreSQL table: `immutable_lots` with JSONB column
   - Include: lot_data, signature, blockchain_anchor_hash
   - Test: `tests/dockside/test_immutable_storage.py`

4. **Implement ML reconciliation scoring**
   - File: `services/dockside/analytics/reconciliation.py`
   - Function: `calculate_ml_accuracy(projected, actual) -> Score`
   - Compare DeckSide projection vs DockSide actual
   - Feed back to ML model for training
   - Test: `tests/dockside/test_ml_reconciliation.py`

**Acceptance Criteria:**
- ✅ DockSide signs lot data with Ed25519 private key
- ✅ Signature verifiable using DockSide public key
- ✅ Lot data anchored to blockchain (immutable hash)
- ✅ Immutable ledger stores signed lot + blockchain hash
- ✅ ML reconciliation score calculated (projected vs actual)
- ✅ Prometheus metrics: `dockside_lots_signed_total`, `reconciliation_variance_pct`
- ✅ Test coverage >90%

---

## 4. MarketSide (EXCHANGE): Controlling Access & Verifying Endpoints 🏪

### Primary Function
**Authenticate different user types (consumers, regulators, investors) and serve appropriately scoped, verified data.**

---

### Use Case 4A: Public QR Code Verification (Consumer Transparency)

**Scenario:** Consumer scans QR code on retail packaging to verify seafood origin

**Public Key Use Case:**
Consumers access the public verification endpoint (`GET /api/v1/public/verify_packet/{packet_id}`) **without specific authentication** (or using a general API key). The system uses the *packet's internal signatures* (from SeaSide, DeckSide, DockSide) and their corresponding **public keys** to perform the "reverse compute" verification trace.

**Implementation Flow:**
```python
# src/public_api/verification_proxy.py

from fastapi import APIRouter, HTTPException
from src.common.security.crypto import verify_signature_with_public_key
from src.common.security.jwk_cache import get_service_public_key
from src.public_models.public_verification import PublicVerification

router = APIRouter()

@router.get("/public/verify_packet/{packet_id}")
async def verify_catch_public(packet_id: str) -> PublicVerification:
    """
    CLAIM 4: Public QR code verification (Commons Good)
    
    Reverse Compute Trace:
    1. Retrieve packet chain (Sea → Deck → Dock → Market)
    2. Verify each packet signature using service public keys
    3. Return ONLY public chain data (no financial/ML data)
    
    No authentication required - this is Commons Good data.
    """
    
    # Step 1: Retrieve packet chain from internal APIs
    try:
        # Get DockSide lot packet (final signed record)
        lot_packet = await get_lot_packet(packet_id)
        
        # Get DeckSide public catch packet (parent)
        public_catch_id = lot_packet["parent_catch_public_packet_id"]
        public_catch = await get_public_catch_packet(public_catch_id)
        
        # Get SeaSide vessel ping packet (origin)
        vessel_ping_id = public_catch["vessel_ping_id"]
        vessel_ping = await get_vessel_ping_packet(vessel_ping_id)
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Packet chain not found: {str(e)}"
        )
    
    # Step 2: VERIFY SIGNATURES (reverse compute)
    # Verify DockSide signature
    dockside_public_key = await get_service_public_key("dockside", lot_packet["public_key_id"])
    if not await verify_signature_with_public_key(
        data=lot_packet,
        signature=lot_packet["signature"],
        public_key=dockside_public_key
    ):
        raise HTTPException(
            status_code=400,
            detail="DockSide signature verification failed - data may be tampered"
        )
    
    # Verify DeckSide signature
    deckside_public_key = await get_service_public_key("deckside", public_catch["public_key_id"])
    if not await verify_signature_with_public_key(
        data=public_catch,
        signature=public_catch["signature"],
        public_key=deckside_public_key
    ):
        raise HTTPException(
            status_code=400,
            detail="DeckSide signature verification failed"
        )
    
    # Verify SeaSide signature
    seaside_public_key = await get_service_public_key("seaside", vessel_ping["public_key_id"])
    if not await verify_signature_with_public_key(
        data=vessel_ping,
        signature=vessel_ping["signature"],
        public_key=seaside_public_key
    ):
        raise HTTPException(
            status_code=400,
            detail="SeaSide signature verification failed"
        )
    
    # Step 3: Build PUBLIC verification response (no financial data)
    public_verification = PublicVerification(
        qr_code=packet_id,
        lot_id=lot_packet["lot_id"],
        trace_path=[vessel_ping_id, public_catch_id, lot_packet["lot_id"]],
        origin_vessel=vessel_ping["vessel_public_id"],  # Anonymized
        catch_species=public_catch["species_code"],
        catch_area=public_catch["general_catch_area"],  # FAO area, not specific coords
        sustainability_certifications=lot_packet.get("certifications", []),
        verified=True,  # All signatures verified
        verification_timestamp=datetime.utcnow().isoformat()
    )
    
    return public_verification
```

---

### Use Case 4B: Investor API Access (Private Analytics)

**Scenario:** Investor accesses predictive yield and financial analytics

**Public Key Use Case:**
Investors authenticate to private API endpoints (`GET /api/v1/investor/predictive_yield`) using **JWTs** which are signed by a private key and verified using the corresponding **public key**.

**Private Key Use Case:**
`MarketSide` (or the underlying auth service) uses its **private key** to issue JWTs to authenticated investors. When responding to sensitive investor queries, `MarketSide` might optionally use its **private key** to sign parts of the response payload for added assurance.

**Implementation Flow:**
```python
# src/marketside/api/investor.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from src.common.security.jwt_validation import verify_investor_jwt
from src.common.security.entitlements import check_investor_entitlement

router = APIRouter()
security = HTTPBearer()

@router.get("/investor/predictive_yield/{vessel_id}")
async def get_predictive_yield(
    vessel_id: str,
    investor_auth: InvestorIdentity = Depends(verify_investor_jwt)
):
    """
    CLAIM 4: Investor access to private analytics (PRIVATE-LIMITED)
    
    JWT Verification:
    1. Verify JWT signature using auth service public key
    2. Check investor entitlement for this vessel/fleet
    3. Return private chain data (financial, ML scores)
    
    Requires PRIVATE-LIMITED license.
    """
    
    investor_id = investor_auth.investor_id
    
    # Step 1: Check entitlement (does investor have license for this vessel?)
    if not await check_investor_entitlement(investor_id, vessel_id):
        raise HTTPException(
            status_code=403,
            detail=f"Investor {investor_id} not entitled to access vessel {vessel_id} data"
        )
    
    # Step 2: Retrieve PRIVATE chain data (financial + ML)
    private_catches = await get_private_catch_packets(vessel_id)
    
    # Step 3: Calculate predictive analytics
    yield_predictions = []
    for catch in private_catches:
        prediction = {
            "catch_id": catch["packet_id"],
            "projected_check_value": catch["projected_check_value"],
            "ml_quality_score": catch["ml_quality_scores"],
            "financial_forecast": catch["financial_data"],
            "reconciliation_accuracy": catch.get("reconciliation", {}).get("ml_accuracy_score"),
        }
        yield_predictions.append(prediction)
    
    # Step 4: (Optional) Sign response with MarketSide private key
    response_data = {
        "vessel_id": vessel_id,
        "predictions": yield_predictions,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    marketside_private_key = load_service_private_key("marketside")
    response_signature = await sign_with_service_key(
        data=json.dumps(response_data, sort_keys=True),
        private_key=marketside_private_key
    )
    response_data["signature"] = response_signature
    
    return response_data
```

---

### 🛠️ Pair Practice Task 1: Public API Pair (QR Code Verification)

**Team:** Public API Pair (2 developers)  
**Sprint:** Week 7-8  
**Priority:** P1 (High - Consumer Transparency)

**Deliverables:**
1. **Implement public verification endpoint**
   - File: `src/public_api/verification_proxy.py`
   - Endpoint: `GET /api/v1/public/verify_packet/{packet_id}`
   - Test: `tests/public_api/test_verification.py`

2. **Implement reverse compute trace logic**
   - Fetch packet chain: DockSide → DeckSide → SeaSide
   - Verify signatures using service public keys
   - Build public verification response
   - Test: `tests/public_api/test_reverse_compute.py`

3. **Create PublicVerification model**
   - File: `src/public_models/public_verification.py` (already planned)
   - Fields: qr_code, lot_id, trace_path, origin_vessel, catch_species, catch_area, certifications
   - EXCLUDE: financial_data, ml_scores, specific_coordinates
   - Test: `tests/public_models/test_public_verification.py`

**Acceptance Criteria:**
- ✅ Consumer can verify QR code without authentication
- ✅ All packet signatures verified (SeaSide, DeckSide, DockSide)
- ✅ Response contains ONLY public chain data
- ✅ Invalid signatures return 400 Bad Request
- ✅ Prometheus metrics: `marketside_public_verifications_total`
- ✅ Test coverage >90%

---

### 🛠️ Pair Practice Task 2: Investor API Pair (Private Analytics)

**Team:** Investor API Pair (2 developers)  
**Sprint:** Week 8-9  
**Priority:** P1 (High - Investor Value)

**Deliverables:**
1. **Implement investor authentication endpoints**
   - File: `src/marketside/api/investor.py`
   - Endpoint: `GET /investor/predictive_yield/{vessel_id}`
   - Endpoint: `GET /investor/financial_forecast/{catch_id}`
   - Test: `tests/marketside/test_investor_api.py`

2. **Implement JWT validation middleware**
   - File: `src/common/security/jwt_validation.py`
   - Function: `verify_investor_jwt(token) -> InvestorIdentity`
   - Verify JWT signature using auth service public key
   - Extract investor_id, license_tier, expiry
   - Test: `tests/security/test_jwt_validation.py`

3. **Implement entitlement verification**
   - File: `src/common/security/entitlements.py` (enhance existing)
   - Function: `check_investor_entitlement(investor_id, vessel_id) -> bool`
   - Query license database
   - Check license tier (PRIVATE-LIMITED required)
   - Test: `tests/security/test_entitlements.py`

4. **Sign investor responses (optional)**
   - Use MarketSide private key to sign response payload
   - Include signature in response for added assurance
   - Test: `tests/marketside/test_response_signing.py`

**Acceptance Criteria:**
- ✅ Investor authenticates with JWT (Ed25519 signed)
- ✅ Invalid JWT rejected with 401
- ✅ Entitlement check enforced (403 if not licensed)
- ✅ Response includes PRIVATE chain data (financial, ML)
- ✅ Response optionally signed with MarketSide private key
- ✅ Prometheus metrics: `marketside_investor_queries_total`
- ✅ Test coverage >85%

---

## Cross-Cutting Concerns

### Key Rotation & Management

**Rotation Schedule:**
- **Service Keys (SeaSide, DeckSide, DockSide, MarketSide):** Rotate every 30 days
- **Root CA:** Rotate every 365 days (offline ceremony)
- **Entity Keys (Vessels, Processors):** Rotate every 90 days

**Implementation:**
```python
# src/common/security/key_rotation.py

import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()

class KeyRotationManager:
    """Manages automated key rotation for services."""
    
    async def rotate_service_key(self, service_name: str):
        """
        Rotate service private/public key pair.
        
        Steps:
        1. Generate new Ed25519 key pair
        2. Store new private key in AWS Secrets Manager
        3. Publish new public key to JWK endpoint
        4. Update service to use new key for signing
        5. Keep old public key available for verification (30-day overlap)
        6. After 30 days, retire old public key
        """
        
        # Step 1: Generate new key pair
        private_key, public_key = generate_ed25519_key_pair()
        key_id = f"{service_name}-{datetime.utcnow().strftime('%Y-%m')}"
        
        # Step 2: Store new private key securely
        await store_private_key(
            service_name=service_name,
            key_id=key_id,
            private_key=private_key
        )
        
        # Step 3: Publish new public key
        await publish_public_key(
            service_name=service_name,
            key_id=key_id,
            public_key=public_key
        )
        
        # Step 4: Update service configuration
        await update_service_config(
            service_name=service_name,
            active_key_id=key_id
        )
        
        logger.info(
            "Service key rotated",
            service_name=service_name,
            key_id=key_id
        )
        
        # Step 5: Schedule old key retirement (30 days)
        await schedule_key_retirement(
            service_name=service_name,
            old_key_id=get_previous_key_id(service_name),
            retirement_date=datetime.utcnow() + timedelta(days=30)
        )
```

---

### Signature Verification Best Practices

**Always Verify:**
1. **Signature Format:** Ed25519 produces 64-byte signatures
2. **Key ID:** Ensure signature was created with claimed key
3. **Timestamp:** Prevent replay attacks (check packet timestamp within 5-minute window)
4. **Data Integrity:** Hash data before verification (canonical JSON with sorted keys)

**Example:**
```python
# src/common/security/crypto.py

import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import ed25519

async def verify_signature_with_public_key(
    data: Dict[str, Any],
    signature: str,
    public_key: ed25519.Ed25519PublicKey
) -> bool:
    """
    Verify Ed25519 signature on data packet.
    
    Steps:
    1. Extract signature from data (remove it for verification)
    2. Create canonical JSON (sorted keys, no whitespace)
    3. Verify signature using public key
    4. Check timestamp within acceptable window
    """
    
    # Step 1: Extract signature (don't include in verification data)
    data_copy = data.copy()
    signature_bytes = bytes.fromhex(signature)
    data_copy.pop("signature", None)
    
    # Step 2: Create canonical JSON
    canonical_json = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
    message_bytes = canonical_json.encode('utf-8')
    
    # Step 3: Verify signature
    try:
        public_key.verify(signature_bytes, message_bytes)
        
        # Step 4: Check timestamp (prevent replay)
        packet_timestamp = datetime.fromisoformat(data["processed_at"])
        if datetime.utcnow() - packet_timestamp > timedelta(minutes=5):
            logger.warning(
                "Packet timestamp outside acceptable window",
                packet_timestamp=packet_timestamp
            )
            return False
        
        return True
    except Exception as e:
        logger.error("Signature verification failed", error=str(e))
        return False
```

---

## Summary: How This Applies to Your Workflow

### ✅ YES, This Directly Applies to SeaTrace Workflow

Your breakdown is **EXACTLY CORRECT** and aligns perfectly with:

1. **4-Pillar Architecture:**
   - Each pillar (SeaSide, DeckSide, DockSide, MarketSide) has distinct public/private key responsibilities
   - Service keys sign packets at each stage
   - Entity keys (vessels, processors) authenticate and sign submissions

2. **Dual Licensing Model:**
   - **PUBLIC CHAIN (Commons Good):** Verified using service public keys, no authentication required
   - **PRIVATE CHAIN (Investor Value):** Requires JWT authentication, entitlement checks, paid license

3. **Packet Forking (CLAIM 2):**
   - DeckSide fork_handler.py is THE critical implementation
   - Public chain: anonymized, SIMP-compliant, signed by DeckSide
   - Private chain: financial data, ML scores, specific coords, signed by DeckSide

4. **Non-Repudiation:**
   - Captain signs e-Log with private key (can't deny submission)
   - Services sign packets at each stage (provable chain of custody)
   - Blockchain anchoring provides immutable timestamp proof

5. **Trust Model:**
   - Root CA → Service Keys → Entity Keys
   - Each signature verifiable using published public keys
   - Reverse compute verification (MarketSide) validates entire chain

### 🎯 Development Pair Priorities

**Week 1-2 (P0):**
- Auth Pair: SeaSide vessel authentication
- Packet Handling Pair: SeaSide packet signing

**Week 3-4 (P0):**
- API & Verification Pair: DeckSide catch submission

**Week 4-6 (P0+ CRITICAL):**
- **Forking Logic Pair: DeckSide packet forking** ← THE MOST IMPORTANT TASK

**Week 5-7 (P1):**
- API & Odoo Pair: DockSide processing endpoints
- Ledger & Signing Pair: DockSide immutable records

**Week 7-9 (P1):**
- Public API Pair: MarketSide QR verification
- Investor API Pair: MarketSide private analytics

---

## 🔐 Security Checklist for Each Pillar

### SeaSide (HOLD)
- ✅ Vessel public key registered in central registry
- ✅ Vessel private key stored securely on vessel hardware
- ✅ SeaSide service private key in AWS Secrets Manager
- ✅ AIS data signatures verified before acceptance
- ✅ GFW correlation for anomaly detection
- ✅ Signed packets published to message queue

### DeckSide (RECORD)
- ✅ Captain signature verified on e-Log submission
- ✅ Packet forking creates distinct public/private chains
- ✅ Public chain: anonymized, no financial data
- ✅ Private chain: financial forecast, ML scores, specific coords
- ✅ Both chains signed with DeckSide private key
- ✅ Public chain routed to SeaTrace-ODOO (Commons Good)
- ✅ Private chain routed to SeaTrace002/003 (Investor)

### DockSide (STORE)
- ✅ Processor public key verified for facility authorization
- ✅ Reconciliation: projected vs actual weights
- ✅ Lot splitting by grade (A/B/C)
- ✅ ML reconciliation score calculated
- ✅ Signed immutable record created with DockSide private key
- ✅ Blockchain anchor hash stored for immutability proof
- ✅ Ledger storage in PostgreSQL + blockchain

### MarketSide (EXCHANGE)
- ✅ Public verification: no authentication required
- ✅ Reverse compute: verify all packet signatures
- ✅ Public response: ONLY Commons Good data
- ✅ Investor JWT: verified using auth service public key
- ✅ Entitlement check: PRIVATE-LIMITED license required
- ✅ Private response: financial data, ML scores, signed by MarketSide

---

**This guide is THE foundation for implementing SeaTrace's public/private key cryptography across all 4 pillars. Each development pair should reference this document when building their respective components.**

---

**End of Public/Private Key Development Guide**

*Last Updated: October 22, 2025*  
*Classification: MODULAR STAGE 1 - Security Foundation*  
*Contact: Security Team for key management questions*
