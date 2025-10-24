"""
MongoDB Atlas Demo Data Seeder - FULL FLEET VERSION
Seeds realistic fishing data for F/V 000 to F/V 137 (138 vessels total)
across 3 organizations (bluewave, pelagic, northstar) for investor demo
showing SeaTrace Four Pillars end-to-end flow with HIGHER PERFORMANCE.

Usage:
    set MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>/seatrace_demo
    cd C:/Users/Roberto002/Documents/GitHub/SeaTrace-ODOO
    python demo/atlas/seed_demo_full_fleet.py

Environment:
    Python: ~/CascadeProjects/SeaTrace-Docker-Migration/.venv/Scripts/python.exe
    
Performance Improvements:
    - 138 vessels (9x more than original 15)
    - 4,140 trips (23x more than original 180)
    - Higher data density for Grafana visualization
    - Realistic fleet distribution across 3 organizations
"""

import os
import random
import datetime as dt
from pymongo import MongoClient

# Demo configuration
MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
    raise ValueError("MONGODB_URI environment variable required")

# Full fleet configuration
TOTAL_VESSELS = 138  # F/V 000 to F/V 137
TRIPS_PER_VESSEL = 30  # 30 trips per vessel over 30 days
ORGS = ["bluewave", "pelagic", "northstar"]

# Fleet distribution by organization
ORG_VESSEL_COUNTS = {
    "bluewave": 50,    # F/V 000-049
    "pelagic": 45,     # F/V 050-094
    "northstar": 43    # F/V 095-137
}

SPECIES = [
    "Yellowfin Tuna", "Bigeye Tuna", "Albacore Tuna",
    "Pacific Cod", "Atlantic Cod", "Black Cod",
    "Chinook Salmon", "Coho Salmon", "Sockeye Salmon",
    "Pacific Halibut", "Atlantic Halibut",
    "Swordfish", "Mahi-Mahi", "Wahoo"
]

GEAR_TYPES = ["LL", "TW", "PS", "PT", "GN"]  # Longline, Trawl, Purse Seine, Pot/Trap, Gillnet
FLAGS = ["US", "CA", "NO", "JP", "NZ"]
PORTS = [
    "San Diego, CA", "Seattle, WA", "Honolulu, HI", "Anchorage, AK",
    "Vancouver, BC", "Portland, OR", "San Francisco, CA"
]

def generate_vessel_name(vessel_num: int, org: str) -> str:
    """Generate realistic vessel names based on fleet number"""
    prefixes = {
        "bluewave": ["Pacific", "Ocean", "Blue", "Wave", "Tide"],
        "pelagic": ["Pelagic", "Deep", "Far", "Horizon", "Marlin"],
        "northstar": ["North", "Arctic", "Polar", "Aurora", "Star"]
    }
    
    prefix = random.choice(prefixes.get(org, ["Vessel"]))
    suffix = random.choice(["Explorer", "Voyager", "Hunter", "Seeker", "Spirit", "Pride", "Glory"])
    
    return f"{prefix} {suffix} {vessel_num}"


def main():
    """Seed demo database with FULL FLEET (F/V 000-137) fishing operation data"""
    print("🌊 SeaTrace FULL FLEET Demo Data Seeder")
    print(f"Total Vessels: {TOTAL_VESSELS} (F/V 000-137)")
    print(f"Trips per Vessel: {TRIPS_PER_VESSEL}")
    print(f"Total Trips: {TOTAL_VESSELS * TRIPS_PER_VESSEL}")
    print(f"Connecting to: {MONGO_URI.split('@')[1] if '@' in MONGO_URI else 'localhost'}")
    
    cli = MongoClient(MONGO_URI)
    db = cli["seatrace_demo"]
    
    # Drop existing collections for clean slate
    print("\n🗑️  Dropping existing collections...")
    db.vessels.drop()
    db.catches.drop()
    db.em_events.drop()
    db.er_reports.drop()
    db.usage_ledger.drop()
    db.commons_fund_snapshots.drop()
    
    now = dt.datetime.utcnow()
    
    # ========== SEED VESSELS (F/V 000-137) ==========
    print("\n🚢 Seeding FULL FLEET (138 vessels)...")
    vessels = []
    vessel_num = 0
    
    for org in ORGS:
        vessel_count = ORG_VESSEL_COUNTS[org]
        
        for i in range(vessel_count):
            vessel_id = f"fv-{vessel_num:03d}"  # F/V 000, F/V 001, ..., F/V 137
            vessel = {
                "vessel_id": vessel_id,
                "vessel_public_id": vessel_id,
                "name": generate_vessel_name(vessel_num, org),
                "flag": random.choice(FLAGS),
                "gear": random.choice(GEAR_TYPES),
                "mmsi": 366000000 + vessel_num,  # Realistic US MMSI range
                "org": org,
                "certifications": random.sample(["MSC", "FairTrade", "BAP", "ASC"], k=random.randint(1, 3)),
                "active_status": "ACTIVE",
                "home_port": random.choice(PORTS)
            }
            vessels.append(vessel)
            vessel_num += 1
    
    db.vessels.insert_many(vessels)
    print(f"✅ Created {len(vessels)} vessels")
    print(f"   - Bluewave: {ORG_VESSEL_COUNTS['bluewave']} vessels (F/V 000-049)")
    print(f"   - Pelagic: {ORG_VESSEL_COUNTS['pelagic']} vessels (F/V 050-094)")
    print(f"   - Northstar: {ORG_VESSEL_COUNTS['northstar']} vessels (F/V 095-137)")
    
    # ========== SEED TRIPS (catches + EM events + ER reports) ==========
    print(f"\n🎣 Seeding {TOTAL_VESSELS * TRIPS_PER_VESSEL} trips...")
    
    catches = []
    em_events = []
    er_reports = []
    
    trip_counter = 0
    
    for vessel in vessels:
        vessel_id = vessel["vessel_id"]
        org = vessel["org"]
        
        # Generate TRIPS_PER_VESSEL trips per vessel over last 30 days
        for trip_num in range(TRIPS_PER_VESSEL):
            trip_id = f"trip-{trip_counter:06d}"
            trip_counter += 1
            
            # Catch details
            landed_kg = random.randint(500, 8000)
            days_ago = random.randint(1, 30)
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            
            landed_ts = now - dt.timedelta(
                days=days_ago,
                hours=hours_offset,
                minutes=minutes_offset
            )
            
            species = random.choice(SPECIES)
            port = random.choice(PORTS)
            
            # PING packet (SeaSide - Claim 1)
            ping_packet_id = f"PING-2025-{vessel_id.upper()}-{trip_num:03d}"
            
            # CATCH packet (DeckSide - Claim 2)
            catch_packet_id = f"CATCH-2025-{vessel_id.upper()}-{trip_num:03d}"
            
            catches.append({
                "vessel_id": vessel_id,
                "vessel_public_id": vessel_id,
                "vessel_name": vessel["name"],
                "org": org,
                "species": species,
                "landed_kg": landed_kg,
                "landed_ts": landed_ts,
                "trip_id": trip_id,
                "packet_id": catch_packet_id,
                "parent_packet_id": ping_packet_id,
                "catch_area_general": random.choice([
                    "Eastern Pacific, FAO 77",
                    "Northeast Pacific, FAO 67",
                    "Western Pacific, FAO 71",
                    "North Atlantic, FAO 21",
                    "Bering Sea, FAO 67"
                ]),
                "port_of_landing": port,
                "compliance_status": "VERIFIED" if random.random() > 0.05 else "PENDING",
                "fish_ticket_id": f"CA-2025-{random.randint(10000, 99999)}"
            })
            
            # EM events (ingest + AI processing)
            # Higher performance: More minutes per trip for demo visibility
            em_ingest_minutes = random.randint(180, 2400)  # 3-40 hours
            em_ai_minutes = int(em_ingest_minutes * random.uniform(0.35, 0.50))
            
            em_events.extend([
                {
                    "org": org,
                    "vessel_id": vessel_id,
                    "ts": landed_ts - dt.timedelta(hours=random.randint(6, 12)),
                    "minutes": em_ingest_minutes,
                    "kind": "ingest",
                    "trip_id": trip_id
                },
                {
                    "org": org,
                    "vessel_id": vessel_id,
                    "ts": landed_ts - dt.timedelta(hours=random.randint(2, 5)),
                    "minutes": em_ai_minutes,
                    "kind": "ai",
                    "trip_id": trip_id
                }
            ])
            
            # ER report (94% submission rate for demo compliance)
            if random.random() < 0.94:
                submitted_ts = landed_ts + dt.timedelta(
                    hours=random.randint(2, 48),
                    minutes=random.randint(0, 59)
                )
                er_reports.append({
                    "org": org,
                    "trip_id": trip_id,
                    "submitted_ts": submitted_ts,
                    "status": "submitted",
                    "er_report_submitted": True
                })
    
    db.catches.insert_many(catches)
    db.em_events.insert_many(em_events)
    db.er_reports.insert_many(er_reports)
    
    print(f"✅ Created {len(catches)} catches")
    print(f"✅ Created {len(em_events)} EM events")
    print(f"✅ Created {len(er_reports)} ER reports")
    
    # ========== CALCULATE ER COVERAGE ==========
    total_trips = len(catches)
    submitted_trips = len(er_reports)
    coverage_pct = (submitted_trips / total_trips * 100) if total_trips > 0 else 0
    print(f"\n📊 ER Coverage: {coverage_pct:.1f}% ({submitted_trips}/{total_trips} trips)")
    
    # ========== SEED USAGE LEDGER (MONTHLY ROLLUP) ==========
    print("\n📈 Seeding usage ledger (monthly rollups)...")
    usage_ledger = []
    
    for org in ORGS:
        # Calculate totals by meter type
        ingest_total = sum(e["minutes"] for e in em_events if e["org"] == org and e["kind"] == "ingest")
        ai_total = sum(e["minutes"] for e in em_events if e["org"] == org and e["kind"] == "ai")
        er_total = sum(1 for r in er_reports if r["org"] == org)
        
        # Calculate cost per tonne (higher performance metric)
        org_catches = [c for c in catches if c["org"] == org]
        total_kg = sum(c["landed_kg"] for c in org_catches)
        total_tonnes = total_kg / 1000
        cost_per_tonne = 18.50  # Demo transparent pricing
        
        usage_ledger.extend([
            {"org": org, "period": "202510", "meter": "ingest_min", "value": ingest_total},
            {"org": org, "period": "202510", "meter": "ai_min", "value": ai_total},
            {"org": org, "period": "202510", "meter": "er_submissions", "value": er_total},
            {"org": org, "period": "202510", "meter": "total_tonnes", "value": total_tonnes},
            {"org": org, "period": "202510", "meter": "cost_per_tonne_usd", "value": cost_per_tonne}
        ])
    
    db.usage_ledger.insert_many(usage_ledger)
    print(f"✅ Created {len(usage_ledger)} usage ledger entries")
    
    # ========== SEED COMMONS FUND SNAPSHOT ==========
    print("\n💰 Seeding Commons Fund snapshot...")
    
    # Higher performance: 112.5% coverage (self-sustaining)
    total_tonnes = sum(c["landed_kg"] for c in catches) / 1000
    monthly_revenue = total_tonnes * 18.50
    opex_usd = monthly_revenue * 0.75  # 75% of revenue goes to OPEX
    commons_surplus = monthly_revenue - opex_usd
    coverage_pct = (monthly_revenue / opex_usd) * 100
    
    commons_snapshot = {
        "period": "2025-10",
        "coverage_pct": coverage_pct,
        "opex_usd": opex_usd,
        "emr_revenue_usd": monthly_revenue,
        "surplus_usd": commons_surplus,
        "total_tonnes": total_tonnes,
        "cost_per_tonne": 18.50,
        "notes": f"Full fleet demo ({TOTAL_VESSELS} vessels) - Commons Fund self-sustaining"
    }
    
    db.commons_fund_snapshots.insert_one(commons_snapshot)
    print(f"✅ Commons Fund Coverage: {commons_snapshot['coverage_pct']:.1f}%")
    
    # ========== CREATE INDEXES FOR PERFORMANCE ==========
    print("\n🔍 Creating indexes for higher performance...")
    
    db.vessels.create_index([("vessel_id", 1)])
    db.vessels.create_index([("org", 1)])
    db.vessels.create_index([("vessel_public_id", 1)])
    
    db.catches.create_index([("org", 1), ("landed_ts", -1)])
    db.catches.create_index([("trip_id", 1)])
    db.catches.create_index([("vessel_id", 1), ("landed_ts", -1)])
    db.catches.create_index([("packet_id", 1)])
    
    db.em_events.create_index([("org", 1), ("ts", -1)])
    db.em_events.create_index([("trip_id", 1)])
    db.em_events.create_index([("vessel_id", 1), ("ts", -1)])
    
    db.er_reports.create_index([("org", 1), ("submitted_ts", -1)])
    db.er_reports.create_index([("trip_id", 1)])
    
    db.usage_ledger.create_index([("org", 1), ("period", 1)])
    
    print("✅ Indexes created")
    
    # ========== SUMMARY ==========
    print("\n" + "="*70)
    print("🎉 FULL FLEET DEMO DATA SEEDED SUCCESSFULLY")
    print("="*70)
    print(f"Organizations: {', '.join(ORGS)}")
    print(f"Total Vessels: {len(vessels)} (F/V 000-137)")
    print(f"  - Bluewave: {ORG_VESSEL_COUNTS['bluewave']} vessels")
    print(f"  - Pelagic: {ORG_VESSEL_COUNTS['pelagic']} vessels")
    print(f"  - Northstar: {ORG_VESSEL_COUNTS['northstar']} vessels")
    print(f"Total Trips: {len(catches)}")
    print(f"EM Events: {len(em_events)}")
    print(f"ER Reports: {len(er_reports)}")
    print(f"ER Coverage: {coverage_pct:.1f}%")
    print(f"Total Landed: {total_tonnes:.1f} tonnes")
    print(f"Cost per Tonne: ${commons_snapshot['cost_per_tonne']:.2f}")
    print(f"Commons Fund Coverage: {commons_snapshot['coverage_pct']:.1f}%")
    print("\n⚡ HIGHER PERFORMANCE METRICS:")
    print(f"  - 9x more vessels than original (138 vs 15)")
    print(f"  - 23x more trips (4,140 vs 180)")
    print(f"  - Realistic fleet distribution")
    print(f"  - Enhanced Grafana visualization density")
    print("\n✅ Ready for investor demo at seatrace.worldseafoodproducers.com!")
    print("="*70)


if __name__ == "__main__":
    main()
