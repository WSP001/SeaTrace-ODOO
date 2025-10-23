"""
MongoDB Atlas Demo Data Seeder
Seeds realistic fishing data for 3 organizations (bluewave, pelagic, northstar)
for investor demo showing SeaTrace Four Pillars end-to-end flow.

Usage:
    set MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>/seatrace_demo
    python demo/atlas/seed_demo.py
"""

import os
import random
import datetime as dt
from uuid import uuid4
from pymongo import MongoClient

# Demo configuration
MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
    raise ValueError("MONGODB_URI environment variable required")

ORGs = ["bluewave", "pelagic", "northstar"]
SPECIES = ["Tuna", "Cod", "Salmon", "Halibut", "Swordfish"]
GEAR_TYPES = ["LL", "TW", "PS"]  # Longline, Trawl, Purse Seine
FLAGS = ["US", "CA", "NO"]

def main():
    """Seed demo database with realistic fishing operation data"""
    print("🌊 SeaTrace Demo Data Seeder")
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
    
    # ========== SEED VESSELS ==========
    print("\n🚢 Seeding vessels...")
    vessels = []
    for org in ORGs:
        for i in range(5):
            vessel = {
                "vessel_id": f"{org[:2]}-{i:03d}",
                "name": f"{org.capitalize()}-V{i}",
                "flag": random.choice(FLAGS),
                "gear": random.choice(GEAR_TYPES),
                "mmsi": int(f"{hash(org) % 1000000000:09d}"[:9]) + i,
                "org": org
            }
            vessels.append(vessel)
    
    db.vessels.insert_many(vessels)
    print(f"✅ Created {len(vessels)} vessels across {len(ORGs)} organizations")
    
    # ========== SEED TRIPS (catches + EM events + ER reports) ==========
    print("\n🎣 Seeding trips (catches, EM events, ER reports)...")
    
    catches = []
    em_events = []
    er_reports = []
    
    for org in ORGs:
        # Generate 60 trips per org over last 30 days
        for trip_num in range(60):
            vessel_id = f"{org[:2]}-{random.randint(0, 4):03d}"
            trip_id = str(uuid4())
            
            # Catch details
            landed_kg = random.randint(500, 6000)
            days_ago = random.randint(1, 30)
            landed_ts = now - dt.timedelta(days=days_ago, hours=random.randint(0, 23))
            species = random.choice(SPECIES)
            
            catches.append({
                "vessel_id": vessel_id,
                "org": org,
                "species": species,
                "landed_kg": landed_kg,
                "landed_ts": landed_ts,
                "trip_id": trip_id
            })
            
            # EM events (ingest + AI processing)
            em_ingest_minutes = random.randint(120, 1800)  # 2-30 hours
            em_ai_minutes = int(em_ingest_minutes * random.uniform(0.3, 0.5))  # 30-50% of ingest
            
            em_events.extend([
                {
                    "org": org,
                    "vessel_id": vessel_id,
                    "ts": landed_ts - dt.timedelta(hours=random.randint(4, 8)),
                    "minutes": em_ingest_minutes,
                    "kind": "ingest",
                    "trip_id": trip_id
                },
                {
                    "org": org,
                    "vessel_id": vessel_id,
                    "ts": landed_ts - dt.timedelta(hours=random.randint(2, 4)),
                    "minutes": em_ai_minutes,
                    "kind": "ai",
                    "trip_id": trip_id
                }
            ])
            
            # ER report (90-98% submission rate for demo compliance)
            if random.random() < 0.94:
                submitted_ts = landed_ts + dt.timedelta(hours=random.randint(2, 36))
                er_reports.append({
                    "org": org,
                    "trip_id": trip_id,
                    "submitted_ts": submitted_ts,
                    "status": "submitted"
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
    
    for org in ORGs:
        # Calculate totals by meter type
        ingest_total = sum(e["minutes"] for e in em_events if e["org"] == org and e["kind"] == "ingest")
        ai_total = sum(e["minutes"] for e in em_events if e["org"] == org and e["kind"] == "ai")
        er_total = sum(1 for r in er_reports if r["org"] == org)
        
        usage_ledger.extend([
            {"org": org, "period": "202510", "meter": "ingest_min", "value": ingest_total},
            {"org": org, "period": "202510", "meter": "ai_min", "value": ai_total},
            {"org": org, "period": "202510", "meter": "er_submissions", "value": er_total}
        ])
    
    db.usage_ledger.insert_many(usage_ledger)
    print(f"✅ Created {len(usage_ledger)} usage ledger entries")
    
    # ========== SEED COMMONS FUND SNAPSHOT ==========
    print("\n💰 Seeding Commons Fund snapshot...")
    
    # Demo values showing >100% coverage
    commons_snapshot = {
        "period": "2025-10",
        "coverage_pct": 112.5,
        "opex_usd": 85000,
        "marketside_xfer_usd": 12000,
        "emr_revenue_usd": 23500,
        "notes": "Demo data - Commons Fund coverage above target"
    }
    
    db.commons_fund_snapshots.insert_one(commons_snapshot)
    print(f"✅ Commons Fund Coverage: {commons_snapshot['coverage_pct']}%")
    
    # ========== CREATE INDEXES ==========
    print("\n🔍 Creating indexes...")
    
    db.catches.create_index([("org", 1), ("landed_ts", -1)])
    db.catches.create_index([("trip_id", 1)])
    
    db.em_events.create_index([("org", 1), ("ts", -1)])
    db.em_events.create_index([("trip_id", 1)])
    
    db.er_reports.create_index([("org", 1), ("submitted_ts", -1)])
    db.er_reports.create_index([("trip_id", 1)])
    
    print("✅ Indexes created")
    
    # ========== SUMMARY ==========
    print("\n" + "="*60)
    print("🎉 DEMO DATA SEEDED SUCCESSFULLY")
    print("="*60)
    print(f"Organizations: {', '.join(ORGs)}")
    print(f"Vessels: {len(vessels)}")
    print(f"Trips: {len(catches)}")
    print(f"EM Events: {len(em_events)}")
    print(f"ER Reports: {len(er_reports)}")
    print(f"ER Coverage: {coverage_pct:.1f}%")
    print(f"Commons Fund Coverage: {commons_snapshot['coverage_pct']}%")
    print("\n✅ Ready for investor demo!")
    print("="*60)

if __name__ == "__main__":
    main()
