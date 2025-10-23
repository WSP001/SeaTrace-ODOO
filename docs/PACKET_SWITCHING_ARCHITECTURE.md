# SeaTrace Packet Switching Handler Architecture

**Last Updated:** October 22, 2025  
**Purpose:** Core IP Documentation - Integration of 4-Pillar Microservices  
**Classification:** MODULAR STAGE 1 Foundation

---

## Executive Summary

The **Packet Switching Handler** is THE core invention of SeaTrace, implementing a sophisticated data routing system that enables:

1. **Claim 1 (SeaSide):** Secure ingestion and validation of vessel data with public key authentication
2. **Claim 2 (DeckSide):** Enrichment and FORKING of data into PUBLIC (Commons Good) and PRIVATE (Investor) chains
3. **Claim 3 (DockSide):** Transformation of parent packets into child lots with ML reconciliation
4. **Claim 4 (MarketSide):** Secure routing with reverse compute traceability

This architecture separates PUBLIC-UNLIMITED data (SeaTrace-ODOO) from PRIVATE-LIMITED IP (SeaTrace002/003), protecting proprietary algorithms while enabling Commons Good transparency.

---

## Repository Architecture

### SeaTrace002 (PRIVATE) - Core Implementation
**Location:** `C:\Users\Roberto002\OneDrive\Documents\GitHub\SeaTrace002`  
**License:** Mix of PUBLIC-UNLIMITED + PRIVATE-LIMITED  
**Purpose:** Core microservices with proprietary packet switching logic

**Structure:**
```
services/
  seaside/
    packet_handler.py          ← Claim 1: Ingestion/Validation
    ais_integration.py          ← GFW correlation
    hold_system.py              ← Vessel tracking
    
  deckside/
    app.py                      ← Claim 2: Enrichment/Forking (basic)
    api/                        ← Record endpoints
    
  dockside/
    handlers/
      store_handler.py          ← Claim 3: Transformation/Reconciliation
    analyzers/
      landing_cost.py           ← Cost analytics
    storage/                    ← Blockchain anchoring
    
  marketside/
    app.py                      ← Claim 4: Secure Routing (basic)
    exchange/                   ← Trading logic
    tests/                      ← Validation suites
```

### SeaTrace-ODOO (PUBLIC) - Integration Toolkit
**Location:** `C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO`  
**License:** PUBLIC-UNLIMITED (Commons Good)  
**Purpose:** Public API gateway wrapping private handlers

**Structure:**
```
src/
  public_models/               ← NEW: Public data contracts
    __init__.py                ← License boundary definitions
    public_catch.py            ← Claim 2 public chain output
    public_vessel.py           ← Claim 1 public output (pending)
    public_lot.py              ← Claim 3 public output (pending)
    public_verification.py     ← Claim 4 public output (pending)
    
  common/
    licensing/                 ← Dual-license middleware
    security/                  ← JWT, Ed25519 validation
    
  correlation/
    tracker.py                 ← GFW integration client
    
  marketside/
    licensing/
      entitlements.py          ← Private data access control
```

---

## Claim 1: Ingestion & Validation (SeaSide HOLD)

### Private Implementation (SeaTrace002)

**File:** `services/seaside/packet_handler.py`

**Core Functionality:**
```python
class PacketSwitchingHandler:
    """Handles secure and efficient switching of data packets."""
    
    async def validate_packet(self, packet: Dict[str, Any]) -> bool:
        """Validate packet integrity and required fields.
        
        Required Fields:
        - vessel_id: Unique vessel identifier
        - timestamp: ISO format UTC timestamp
        - data_type: One of ['ais', 'catch', 'environmental']
        - data: Packet payload
        """
        
    async def transform_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the packet data for downstream use.
        
        Adds processing metadata:
        - processed_at: Server timestamp
        - processor_version: Handler version
        - original_timestamp: Client-reported time
        """
        
    async def forward_packet(self, packet: Dict[str, Any]):
        """Forward the processed packet to appropriate services.
        
        Routing Logic:
        - 'ais' → GFW correlation (gfw_integration.py)
        - 'catch' → DeckSide enrichment
        - 'environmental' → Analytics pipeline
        """
```

**Key Features:**
- **Asynchronous Processing:** Non-blocking packet queue with `asyncio`
- **Prometheus Metrics:**
  - `seatrace_packet_processing_total`: Counter for processed packets
  - `seatrace_packet_validation_errors_total`: Validation failure counter
  - `seatrace_packet_processing_duration_seconds`: Histogram of processing time
- **Public Key Validation:** Cryptographic signature verification (referenced in code comments)
- **GFW Correlation:** Integration with Global Fishing Watch AIS data via `gfw_integration.py`

**Data Flow:**
```
Vessel PING → validate_packet() → transform_packet() → forward_packet()
     ↓              ↓                    ↓                    ↓
  Raw Data    Public Key Check    Add Metadata      Route to DeckSide
```

### Public Wrapper (SeaTrace-ODOO)

**File:** `src/public_models/public_vessel.py` (TO BE CREATED)

**Purpose:** Expose ONLY public vessel data, excluding sensitive coordinates and private keys

**Public Fields:**
- `vessel_public_id`: Non-sensitive vessel identifier
- `vessel_name`: Registered name
- `flag_state`: ISO country code
- `registration_port`: Home port
- `vessel_type`: Vessel classification
- `last_ping_timestamp`: Most recent AIS ping (timestamp only)
- `gfw_correlation_status`: One of ['correlated', 'pending', 'anomaly']

**EXCLUDED Private Fields:**
- `specific_coordinates`: Exact lat/lon (privacy)
- `private_key`: Cryptographic signature key
- `detailed_ais_data`: Full AIS telemetry (commercial sensitive)
- `fuel_consumption`: Operational metrics (competitive intel)

---

## Claim 2: Enrichment & Forking (DeckSide RECORD)

### Private Implementation (SeaTrace002)

**File:** `services/deckside/app.py`

**Core Functionality:**
```python
class ProcessingData(BaseModel):
    batch_id: str
    vessel_id: str
    species: str
    weight: float
    quality_grade: str
    processing_date: datetime

@app.post("/batch/process")
async def process_batch(data: ProcessingData):
    """Process catch batch and FORK into public/private chains."""
    # Store in MongoDB
    result = await db.batches.insert_one(data.dict())
```

**Current State:** Basic batch processing WITHOUT explicit public/private forking

**CRITICAL GAP:** DeckSide needs enhancement to implement packet forking logic:

```python
# REQUIRED ENHANCEMENT (Pseudocode)
async def enrich_and_fork(catch_data: CatchData):
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
    
    # Create public chain packet
    public_catch = {
        "packet_id": f"catch-pub-{uuid4()}",
        "vessel_public_id": catch_data.vessel_public_id,
        "species_code": catch_data.species_code,
        "general_catch_area": anonymize_location(catch_data.coordinates),
        "landed_timestamp": catch_data.timestamp,
        "landed_weight_kg": catch_data.weight,
        "compliance_status": validate_simp(catch_data)
    }
    
    # Create private chain packet
    private_catch = {
        "packet_id": f"catch-priv-{uuid4()}",
        "vessel_id": catch_data.vessel_id,  # Full vessel ID
        "species_code": catch_data.species_code,
        "specific_coordinates": catch_data.coordinates,
        "projected_check_value": predict_value(catch_data),
        "ml_quality_scores": run_ml_model(catch_data),
        "financial_data": calculate_financials(catch_data)
    }
    
    # Route public chain to Odoo (PUBLIC-UNLIMITED)
    await forward_to_odoo(public_catch)
    
    # Route private chain to SeaTrace003 (PRIVATE-LIMITED)
    await forward_to_investor_dashboard(private_catch)
    
    return {
        "public_packet_id": public_catch["packet_id"],
        "private_packet_id": private_catch["packet_id"]
    }
```

### Public Wrapper (SeaTrace-ODOO)

**File:** `src/public_models/public_catch.py` (CREATED - Structure Only)

**Purpose:** Receive and expose ONLY the public chain from DeckSide forking

**Public Fields (IMPLEMENTED):**
- `packet_id`: Public packet identifier
- `vessel_public_id`: Anonymized vessel reference
- `species_code`: FAO species classification
- `general_catch_area`: FAO fishing area (no specific coords)
- `landed_timestamp`: UTC timestamp of landing
- `landed_weight_kg`: Total catch weight
- `compliance_status`: SIMP compliance flag

**EXCLUDED Private Fields:**
- `projected_check_value`: Financial forecast (investor only)
- `specific_ping_coordinates`: Exact fishing location (competitive intel)
- `ml_quality_scores`: Predictive analytics (proprietary algorithm)
- `financial_reconciliation_data`: Cost/revenue data (PRIVATE-LIMITED)

**Key Insight:** This model represents THE SEPARATION POINT between Commons Good (free) and Investor Value (paid license)

---

## Claim 3: Transformation & Reconciliation (DockSide STORE)

### Private Implementation (SeaTrace002)

**File:** `services/dockside/handlers/store_handler.py`

**Core Functionality:**
```python
class DockSideStoreHandler:
    """Enhanced DockSide handler for STORE operations with advanced metrics."""
    
    async def process_landing(
        self,
        landing: LandingMetrics,
        crew_data: List[CrewShiftData]
    ) -> Dict:
        """Process a new landing with enhanced metrics and forced-labor detection.
        
        Responsibilities:
        1. Calculate detailed landing costs (fuel, ice, processing time)
        2. Analyze crew shifts for forced-labor indicators
        3. Store results with blockchain anchoring
        4. Generate risk assessments and recommendations
        """
```

**Advanced Features:**
- **Landing Cost Analysis:**
  - Fuel consumption tracking
  - Ice usage monitoring
  - Processing time metrics
  - Total cost per landing (Prometheus histogram)
  
- **Forced Labor Detection:**
  - Excessive work hours detection (>14 hours/day)
  - Insufficient rest period analysis (<6 hours between shifts)
  - Location anomaly detection (crew >1km from vessel)
  - Risk scoring (0-100 scale with Prometheus gauge)
  
- **Prometheus Metrics:**
  - `landing_cost_total`: Histogram by vessel_id and species
  - `crew_hours_total`: Gauge by vessel_id and role
  - `forced_labor_risk_score`: Gauge by vessel_id

**Transformation Logic:**
```
Parent Catch Packet → DockSide Processing → Child Lot Packets A/B/C

Example:
Parent: 3,500 kg Yellowfin Tuna
  ↓
Lot A: 1,200 kg (Grade AAA, premium sushi)
Lot B: 1,800 kg (Grade AA, retail fillets)
Lot C: 500 kg (Grade A, canned product)

Each lot includes:
- blockchain_anchor_hash (immutable proof)
- parent_catch_packet_id (cryptographic linkage)
- ml_reconciliation_score (projected vs actual weight accuracy)
```

**ML Reconciliation:**
- Compare captain's projected catch weight vs actual landed weight
- Generate predictive accuracy metrics for investor confidence
- Feed back into ML models to improve future projections

### Public Wrapper (SeaTrace-ODOO)

**File:** `src/public_models/public_lot.py` (TO BE CREATED)

**Purpose:** Expose transformed lot data WITHOUT financial valuations or ML scores

**Public Fields:**
- `lot_id`: Unique lot identifier
- `parent_catch_packet_id`: Link to public catch packet
- `lot_designation`: One of ['A', 'B', 'C']
- `weight_kg`: Lot weight
- `processing_timestamp`: UTC timestamp
- `storage_location`: General location (no specific coords)
- `blockchain_anchor_hash`: Immutability proof
- `sustainability_certifications`: List of certifications

**EXCLUDED Private Fields:**
- `ml_reconciliation_score`: Predictive accuracy (investor insight)
- `financial_valuation`: Market pricing data (PRIVATE-LIMITED)
- `specific_storage_coordinates`: Exact warehouse location
- `quality_degradation_forecast`: Predictive analytics

---

## Claim 4: Secure Routing & Reverse Compute (MarketSide EXCHANGE)

### Private Implementation (SeaTrace002)

**File:** `services/marketside/app.py`

**Core Functionality:**
```python
@app.post("/product/trace")
async def create_trace(data: TraceabilityData):
    """Create traceability record with QR code generation.
    
    Generates:
    - QR code linking to verification endpoint
    - Complete traceability chain (vessel → deck → dock → market)
    - Base64-encoded QR image for printing
    """

@app.get("/product/{product_id}")
async def get_product_trace(product_id: str):
    """Retrieve complete traceability chain.
    
    Reverse Compute Path:
    Lot C (retail) → Dock (processing) → Deck (catch) → Sea (vessel)
    
    Returns:
    - product: Current product data
    - vessel_data: Originating vessel info
    - processing_data: Batch/lot processing history
    - storage_history: Chain of custody
    """
```

**Key Features:**
- **QR Code Generation:** Consumer-facing traceability via scanning
- **Reverse Compute:** Trace finished product back to originating vessel
- **Complete Chain:** Integrates data from all 4 pillars
- **Certifications:** Links sustainability certifications to products

**Routing Decision Logic:**
```
Consumer Scans QR Code → Retrieve Traceability Chain → Route Data
                                                            ↓
                        ┌───────────────────────────────────┴──────────────────────┐
                        ↓                                                           ↓
                PUBLIC CHAIN DATA                                      PRIVATE CHAIN DATA
                (Commons Good)                                         (Investor Dashboard)
                        ↓                                                           ↓
          ┌─────────────────────────┐                            ┌──────────────────────────┐
          │ - Vessel name            │                            │ - Projected check value   │
          │ - Species                │                            │ - Specific coordinates    │
          │ - General catch area     │                            │ - ML quality scores       │
          │ - Compliance status      │                            │ - Financial reconciliation│
          │ - Sustainability certs   │                            │ - Cost/revenue analytics  │
          └─────────────────────────┘                            └──────────────────────────┘
                        ↓                                                           ↓
            Consumer Mobile App                                   Investor Dashboard
         (SeaTrace-ODOO Public API)                            (SeaTrace003 Private API)
```

### Public Wrapper (SeaTrace-ODOO)

**File:** `src/public_models/public_verification.py` (TO BE CREATED)

**Purpose:** Consumer-facing verification response, routing public chain only

**Public Fields:**
- `qr_code`: Scanned QR code value
- `lot_id`: Finished product lot identifier
- `trace_path`: List of packet IDs showing journey (sea → deck → dock)
- `origin_vessel`: Public vessel name
- `catch_species`: Species name (consumer-friendly)
- `catch_area`: FAO area description
- `sustainability_certifications`: List of certification names

**EXCLUDED Private Fields:**
- `investor_dashboard_url`: Link to private analytics (requires authentication)
- `private_financial_data`: Cost/revenue data
- `specific_coordinates`: Exact fishing location
- `quality_scores`: ML-generated metrics

**Routing Logic:**
```python
# Public API endpoint in SeaTrace-ODOO
@app.get("/api/v1/public/verify/{qr_code}")
async def verify_catch(qr_code: str) -> PublicVerification:
    # Call PRIVATE MarketSide handler via internal mTLS
    full_trace = await call_private_marketside(qr_code)
    
    # Filter to PUBLIC chain only
    public_trace = {
        "qr_code": qr_code,
        "lot_id": full_trace["lot_id"],
        "trace_path": full_trace["public_trace_path"],  # Exclude private IDs
        "origin_vessel": full_trace["vessel"]["public_name"],
        "catch_species": full_trace["species"]["common_name"],
        "catch_area": full_trace["area"]["fao_description"],
        "sustainability_certifications": full_trace["certifications"]
    }
    
    return PublicVerification(**public_trace)
```

---

## Integration Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          VESSEL PING (AIS DATA)                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ↓
                    ┌────────────────────────────────┐
                    │  CLAIM 1: SeaSide (HOLD)       │
                    │  - Validate public key         │
                    │  - Correlate with GFW          │
                    │  - Authenticate packet         │
                    │  File: packet_handler.py       │
                    └────────────────┬───────────────┘
                                     ↓
                    ┌────────────────────────────────┐
                    │  CLAIM 2: DeckSide (RECORD)    │
                    │  *** FORKING POINT ***         │
                    │  File: app.py (needs enhancement)│
                    └──────────┬─────────────┬───────┘
                               ↓             ↓
                  ┌────────────────┐  ┌─────────────────┐
                  │ PUBLIC CHAIN   │  │ PRIVATE CHAIN   │
                  │ (SIMP data)    │  │ (Financial data)│
                  └────────┬───────┘  └────────┬────────┘
                           ↓                    ↓
              ┌────────────────────┐  ┌──────────────────────┐
              │ SeaTrace-ODOO      │  │ SeaTrace002/003      │
              │ (Commons Good)     │  │ (Investor Dashboard) │
              │ PUBLIC-UNLIMITED   │  │ PRIVATE-LIMITED      │
              └────────┬───────────┘  └────────┬─────────────┘
                       ↓                        ↓
        ┌──────────────────────────┐  ┌──────────────────────┐
        │  CLAIM 3: DockSide       │  │  CLAIM 3: DockSide   │
        │  Public Lot Tracking     │  │  ML Reconciliation   │
        │  File: public_lot.py     │  │  File: store_handler.py│
        └──────────┬───────────────┘  └────────┬─────────────┘
                   ↓                            ↓
        ┌──────────────────────────┐  ┌──────────────────────┐
        │  CLAIM 4: MarketSide     │  │  CLAIM 4: MarketSide │
        │  Consumer QR Verify      │  │  Investor Analytics  │
        │  File: public_verification.py│ │  File: app.py      │
        └──────────────────────────┘  └──────────────────────┘
                   ↓                            ↓
        ┌──────────────────────────┐  ┌──────────────────────┐
        │  Consumer Mobile App     │  │  Investor Dashboard  │
        │  (Free Access)           │  │  (Paid License)      │
        └──────────────────────────┘  └──────────────────────┘
```

### Inter-Repository Communication

**SeaTrace-ODOO (Public) → SeaTrace002 (Private):**

```python
# src/public_api/gateway.py (TO BE CREATED)

import httpx
from src.public_models.public_catch import PublicCatch

class PrivateServiceGateway:
    """Secure gateway to call private SeaTrace002 handlers."""
    
    def __init__(self):
        self.base_url = "https://internal.seatrace002.local"
        self.mtls_cert = "/path/to/client.crt"
        self.mtls_key = "/path/to/client.key"
        
    async def get_public_catch_data(self, packet_id: str) -> PublicCatch:
        """Retrieve public chain data from DeckSide forking.
        
        Internal API Call:
        POST https://internal.seatrace002.local/api/deckside/public-chain
        
        Authentication: mTLS (mutual TLS)
        Response: Only public chain fields, private fields excluded
        """
        async with httpx.AsyncClient(
            cert=(self.mtls_cert, self.mtls_key),
            verify="/path/to/ca.crt"
        ) as client:
            response = await client.get(
                f"{self.base_url}/api/deckside/public-chain/{packet_id}"
            )
            response.raise_for_status()
            return PublicCatch(**response.json())
```

**Security:**
- **mTLS (Mutual TLS):** Both client and server authenticate with certificates
- **IP Whitelisting:** Only SeaTrace-ODOO servers can call internal APIs
- **JWT Token Validation:** Short-lived tokens (15-minute expiry)
- **Rate Limiting:** Prevent abuse of internal APIs

---

## Dual Licensing Model

### PUBLIC-UNLIMITED License (Commons Good)

**Covered Modules:**
- SeaSide (HOLD): Vessel tracking, AIS integration
- DeckSide (RECORD): Catch recording, public chain data
- DockSide (STORE): Public lot tracking, chain of custody

**Covered Files in SeaTrace-ODOO:**
- `src/public_models/` (all files)
- `demo/` (all demo infrastructure)
- `docs/DEMO_GUIDE.md`
- `src/common/licensing/commons.py`

**Access Rights:**
- ✅ Free access for NGOs, regulators, consumers
- ✅ SIMP-required data for international trade
- ✅ Sustainability certifications
- ✅ General catch area (FAO zones)
- ✅ Species identification
- ✅ Compliance status

**Exclusions:**
- ❌ Specific fishing coordinates
- ❌ Financial projections/valuations
- ❌ ML quality scores
- ❌ Predictive analytics
- ❌ Cost/revenue data

### PRIVATE-LIMITED License (Investor Value)

**Covered Modules:**
- MarketSide (EXCHANGE): Investor analytics, proprietary pricing

**Covered Files in SeaTrace002:**
- `services/seaside/packet_handler.py` (validation algorithms)
- `services/deckside/` (forking logic - TO BE ENHANCED)
- `services/dockside/handlers/store_handler.py` (ML reconciliation)
- `services/marketside/app.py` (routing logic)

**Covered Files in SeaTrace003:**
- Investor dashboard source code
- Proprietary ML models
- Financial analytics algorithms

**Access Rights:**
- ✅ Fishing fleet owners (for their own vessel data)
- ✅ Investors (with paid license)
- ✅ Financiers (supply chain lending)
- ✅ Premium processors (quality forecasting)

**Requires:**
- 🔑 Valid private key license
- 🔑 Paid subscription (tiered pricing)
- 🔑 Authentication via JWT + Ed25519 signatures
- 🔑 Entitlement verification via `entitlements.py`

---

## Implementation Roadmap

### Phase 1: Packet Handler Discovery (COMPLETED ✅)

**Objective:** Locate and document existing packet handler implementations in SeaTrace002

**Completed Tasks:**
- ✅ Found `services/seaside/packet_handler.py` (Claim 1)
- ✅ Found `services/dockside/handlers/store_handler.py` (Claim 3)
- ✅ Analyzed `services/deckside/app.py` (Claim 2 - needs forking enhancement)
- ✅ Analyzed `services/marketside/app.py` (Claim 4 - basic routing)
- ✅ Created this architecture document

### Phase 2: DeckSide Forking Enhancement (CRITICAL)

**Objective:** Implement explicit public/private chain forking in DeckSide

**Required Files (SeaTrace002 - PRIVATE):**
- `services/deckside/handlers/fork_handler.py` (NEW)
  - `fork_catch_data()` method
  - Public chain packet creator
  - Private chain packet creator
  - Routing logic to Odoo vs SeaTrace003

**Required Changes (SeaTrace002 - PRIVATE):**
- `services/deckside/app.py`
  - Add `/batch/fork` endpoint
  - Call `fork_handler.fork_catch_data()`
  - Return both public and private packet IDs

**Test Coverage:**
- Unit tests for forking logic
- Integration tests for public/private routing
- Validation of field exclusions

### Phase 3: Public Model Implementation (IN PROGRESS)

**Objective:** Complete public data models in SeaTrace-ODOO

**Required Files (SeaTrace-ODOO - PUBLIC):**
- ✅ `src/public_models/public_catch.py` (structure created, needs Pydantic implementation)
- ⏳ `src/public_models/public_vessel.py` (cancelled, needs restart)
- ⏳ `src/public_models/public_lot.py` (not started)
- ⏳ `src/public_models/public_verification.py` (not started)

**Implementation Details:**
```python
# src/public_models/public_catch.py (COMPLETE IMPLEMENTATION)

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class PublicCatch(BaseModel):
    """Public chain output from Claim 2 (DeckSide forking).
    
    This model represents ONLY the public chain data, excluding
    all financial projections, specific coordinates, and ML scores.
    """
    
    packet_id: str = Field(
        description="Public packet identifier",
        example="catch-pub-a1b2c3d4"
    )
    
    vessel_public_id: str = Field(
        description="Anonymized vessel identifier",
        example="bl-001"
    )
    
    species_code: str = Field(
        description="FAO species classification code",
        example="YFT",  # Yellowfin Tuna
        min_length=3,
        max_length=3
    )
    
    general_catch_area: str = Field(
        description="FAO fishing area (no specific coordinates)",
        example="FAO-77",  # Eastern Central Pacific
        pattern=r"^FAO-\d{2}$"
    )
    
    landed_timestamp: datetime = Field(
        description="UTC timestamp when catch was landed",
        example="2025-10-20T14:30:00Z"
    )
    
    landed_weight_kg: float = Field(
        description="Total catch weight in kilograms",
        example=3500.0,
        ge=0
    )
    
    compliance_status: Literal["compliant", "pending", "violation"] = Field(
        description="SIMP compliance status",
        example="compliant"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "packet_id": "catch-pub-abc123",
                "vessel_public_id": "bl-001",
                "species_code": "YFT",
                "general_catch_area": "FAO-77",
                "landed_timestamp": "2025-10-20T14:30:00Z",
                "landed_weight_kg": 3500.0,
                "compliance_status": "compliant"
            }
        }
```

### Phase 4: Public API Gateway (HIGH PRIORITY)

**Objective:** Create secure gateway in SeaTrace-ODOO to call private handlers

**Required Files (SeaTrace-ODOO - PUBLIC):**
- `src/public_api/gateway.py` (NEW)
  - `PrivateServiceGateway` class
  - mTLS configuration
  - Internal API routing
  - Response filtering (public fields only)

- `src/public_api/verification_proxy.py` (ENHANCE EXISTING)
  - Add public/private routing logic
  - Implement JWT validation for investors
  - Rate limiting for public consumers

**Security Requirements:**
- mTLS certificates for internal communication
- JWT token validation (Ed25519 signatures)
- IP whitelisting for internal APIs
- Response filtering to remove private fields
- Audit logging for all private API calls

### Phase 5: Validation & Testing

**Objective:** Ensure complete separation of public/private data

**Test Suites:**
1. **Public Model Tests:**
   - Validate all public models only contain non-sensitive fields
   - Test Pydantic validation rules
   - Verify JSON schema generation for OpenAPI

2. **Gateway Integration Tests:**
   - Test mTLS authentication to SeaTrace002
   - Verify response filtering removes private fields
   - Test error handling for internal API failures

3. **License Separation Tests:**
   - Scan public models for accidental private field exposure
   - Validate licensing headers in all files
   - Test entitlement checks for private data access

4. **End-to-End Tests:**
   - Consumer QR scan → public verification response
   - Investor authentication → private dashboard access
   - NGO regulatory query → public catch data

### Phase 6: Git Commit Preparation

**Objective:** Commit ONLY Commons Good files to SeaTrace-ODOO, protect private IP

**File Classification:**

**PUBLIC (Commons Good) - Safe to Commit:**
- ✅ `demo/` (all 9 demo files)
- ✅ `docs/DEMO_GUIDE.md`
- ✅ `docs/PACKET_SWITCHING_ARCHITECTURE.md` (this file)
- ✅ `src/public_models/` (all files)
- ✅ `src/public_api/gateway.py`
- ✅ `src/public_api/verification_proxy.py` (enhanced version)
- ✅ `src/common/licensing/commons.py`

**PRIVATE (IP Protection) - DO NOT COMMIT:**
- ❌ Any files from SeaTrace002 directory
- ❌ Any files from SeaTrace003 directory
- ❌ Internal API credentials
- ❌ mTLS certificates/keys
- ❌ Detailed ML model implementations
- ❌ Financial algorithms

**Commit Message Template:**
```
feat(commons-good): Add MODULAR STAGE 1 packet switching integration

Implements public API wrappers for 4-pillar microservices:
- Claim 1 (SeaSide): Public vessel data models
- Claim 2 (DeckSide): Public catch data from forked chain
- Claim 3 (DockSide): Public lot tracking with blockchain anchoring
- Claim 4 (MarketSide): Consumer verification routing

Protects PRIVATE IP:
- SeaTrace002 packet handler implementations remain private
- SeaTrace003 investor dashboard source code separate
- PUBLIC-UNLIMITED license applies to public models only
- PRIVATE-LIMITED license enforced via entitlements middleware

Architecture documented in:
- docs/PACKET_SWITCHING_ARCHITECTURE.md
- docs/DEMO_GUIDE.md (investor walkthrough)

Refs: 4 Claims patent application, dual licensing model
```

---

## Security Considerations

### Cryptographic Operations

**Ed25519 Signatures:**
- Used for EMR pricing card authentication
- Public keys distributed via `/api/emr/pubkey` endpoint
- Private keys stored in AWS Secrets Manager
- 30-day key rotation policy

**Public Key Validation (Claim 1):**
```python
# Pseudocode from packet_handler.py concept
async def validate_vessel_signature(packet: Dict) -> bool:
    """Validate vessel's cryptographic signature.
    
    Each vessel has Ed25519 key pair:
    - Private key: Stored on vessel hardware
    - Public key: Registered in SeaSide database
    
    Validation:
    1. Extract signature from packet header
    2. Retrieve vessel's public key
    3. Verify signature matches packet payload
    4. Check signature timestamp (prevent replay)
    """
    signature = packet["headers"]["signature"]
    vessel_id = packet["vessel_id"]
    
    public_key = await db.vessels.find_one({"vessel_id": vessel_id})
    
    is_valid = ed25519.verify(
        signature=signature,
        message=packet["data"],
        public_key=public_key["public_key"]
    )
    
    return is_valid
```

### Network Security

**Internal API Communication:**
- mTLS (Mutual TLS) between SeaTrace-ODOO and SeaTrace002
- Client certificate authentication required
- Server certificate validation
- IP whitelisting on firewall

**External API Endpoints:**
- TLS 1.3 for all public endpoints
- Rate limiting (100 requests/minute per IP)
- JWT authentication for investor endpoints
- OAuth2 for NGO/regulator access

### Data Privacy

**GDPR Compliance:**
- Crew member data anonymized in public chains
- Specific coordinates excluded from public models
- Right to erasure implemented for personal data
- Data processing agreements with vessel operators

**SIMP Compliance:**
- Catch certificates linked to public catch packets
- Harvest event timestamps immutable
- Species validation against approved lists
- Chain of custody maintained across 4 pillars

---

## Prometheus Metrics

### SeaSide (Claim 1) Metrics

```prometheus
# Packet processing totals
seatrace_packet_processing_total{data_type="ais|catch|environmental"} 1234

# Validation errors
seatrace_packet_validation_errors_total{error_type="missing_field|invalid_timestamp|bad_signature"} 5

# Processing duration histogram
seatrace_packet_processing_duration_seconds_bucket{le="0.1"} 500
seatrace_packet_processing_duration_seconds_bucket{le="0.5"} 1200
seatrace_packet_processing_duration_seconds_bucket{le="1.0"} 1234

# Queue metrics
seatrace_incoming_packets_total 42
seatrace_processed_packets_total 1192
```

### DockSide (Claim 3) Metrics

```prometheus
# Landing costs histogram
landing_cost_total_bucket{vessel_id="bl-001",species="YFT",le="500"} 10
landing_cost_total_bucket{vessel_id="bl-001",species="YFT",le="1000"} 25
landing_cost_total_bucket{vessel_id="bl-001",species="YFT",le="2500"} 60

# Crew hours gauge
crew_hours_total{vessel_id="bl-001",role="captain"} 168.5
crew_hours_total{vessel_id="bl-001",role="deckhand"} 2016.0

# Forced labor risk scoring
forced_labor_risk_score{vessel_id="bl-001"} 15.0  # Low risk
forced_labor_risk_score{vessel_id="pl-003"} 75.0  # High risk - investigate
```

---

## Next Actions

### Immediate (Next Session)

1. **Complete Public Model Implementations:**
   - Finish `public_catch.py` with full Pydantic Field() definitions
   - Create `public_vessel.py` with Claim 1 output fields
   - Create `public_lot.py` with Claim 3 output fields
   - Create `public_verification.py` with Claim 4 output fields

2. **Create Public API Gateway:**
   - Implement `src/public_api/gateway.py` with mTLS
   - Configure internal API routing to SeaTrace002
   - Add response filtering for private fields
   - Implement error handling and retry logic

3. **Enhance DeckSide Forking (SeaTrace002 - Private Repo):**
   - Create `services/deckside/handlers/fork_handler.py`
   - Implement `fork_catch_data()` method
   - Add `/batch/fork` endpoint to `app.py`
   - Write unit tests for forking logic

### Short-Term (This Week)

4. **Testing & Validation:**
   - Write integration tests for gateway → private handlers
   - Test public model field exclusions
   - Validate licensing headers
   - Run separation audit script

5. **Git Commit Preparation:**
   - Run file classification audit
   - Review all files in `git status` (40+ untracked)
   - Stage ONLY Commons Good files
   - Create detailed commit message

### Long-Term (Next Sprint)

6. **Production Deployment:**
   - Configure mTLS certificates for staging environment
   - Deploy SeaTrace-ODOO public API to production
   - Set up monitoring with Grafana dashboards
   - Conduct investor demo walkthrough

7. **Documentation:**
   - Update API documentation with public endpoints
   - Create developer guide for public API usage
   - Write integration guide for third-party developers
   - Document entitlement verification process

---

## Conclusion

The **Packet Switching Handler** architecture represents the core innovation of SeaTrace, enabling:

✅ **Transparent Commons Good:** Public data for NGOs, regulators, consumers  
✅ **Protected Investor Value:** Private analytics for paid license holders  
✅ **Dual Licensing Compliance:** Clear separation of PUBLIC-UNLIMITED vs PRIVATE-LIMITED  
✅ **Operational Sustainability:** Commons Fund model without VC dependency  

This MODULAR STAGE 1 foundation integrates all 4 pillars while respecting IP boundaries between SeaTrace-ODOO (public integration toolkit) and SeaTrace002/003 (private implementation).

**Repository Owners:**
- **SeaTrace002 (PRIVATE):** Development team maintains core packet handler IP
- **SeaTrace-ODOO (PUBLIC):** Integration team maintains Commons Good API wrappers
- **SeaTrace003 (PRIVATE):** Investor demo team maintains limited-license monetization

**Contact:** For architecture questions or integration support, consult this document and `docs/DEMO_GUIDE.md`.

---

**End of Packet Switching Architecture Documentation**

*Last Updated: October 22, 2025*  
*Classification: MODULAR STAGE 1 - Core IP Documentation*
