"""
EMR Usage Simulator for Investor Demo
Simulates real-time EM/ER usage flowing into EMR metering service.
Shows live updates for investor demo dashboard.

Usage:
    $env:EMR_API="http://localhost:8001"
    $env:EMR_TOKEN="<demo_token_from_private_repo>"
    python demo/simulator/emr_simulator.py
"""

import os
import time
import random
import requests
import datetime as dt
from typing import Optional

# Configuration
EMR_API = os.getenv("EMR_API", "http://localhost:8001")
EMR_TOKEN = os.getenv("EMR_TOKEN")
ORGs = ["bluewave", "pelagic", "northstar"]
LOOP_INTERVAL_SECONDS = 5  # Push usage every 5 seconds

if not EMR_TOKEN:
    print("⚠️  EMR_TOKEN not set - using demo mode (will fail auth)")
    EMR_TOKEN = "demo-token-placeholder"


def record_usage(
    org: str,
    meter: str,
    value: int,
    idempotency_key: str,
    timeout: int = 5
) -> Optional[dict]:
    """Record usage event to EMR API"""
    headers = {
        "Authorization": f"Bearer {EMR_TOKEN}",
        "X-Idempotency-Key": idempotency_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "org": org,
        "meter": meter,
        "value": value
    }
    
    try:
        response = requests.post(
            f"{EMR_API}/api/emr/usage/record",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error recording {meter} for {org}: {e}")
        return None


def main():
    """Run continuous usage simulator"""
    print("🌊 SeaTrace EMR Usage Simulator")
    print(f"📡 EMR API: {EMR_API}")
    print(f"🏢 Organizations: {', '.join(ORGs)}")
    print(f"⏱️  Update interval: {LOOP_INTERVAL_SECONDS}s")
    print("\n🚀 Starting simulation...\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            timestamp = dt.datetime.utcnow().isoformat()
            
            for org in ORGs:
                # Simulate varying usage patterns per org
                ingest_minutes = random.randint(200, 1200)
                ai_minutes = random.randint(80, 400)
                er_submissions = random.randint(5, 20)
                
                # Generate unique idempotency keys
                idem_ingest = f"{org}-ing-{int(time.time())}-{iteration}"
                idem_ai = f"{org}-ai-{int(time.time())}-{iteration}"
                idem_er = f"{org}-er-{int(time.time())}-{iteration}"
                
                # Record usage
                record_usage(org, "ingest_min", ingest_minutes, idem_ingest)
                record_usage(org, "ai_min", ai_minutes, idem_ai)
                record_usage(org, "er_submissions", er_submissions, idem_er)
                
                print(
                    f"[{timestamp}] {org}: "
                    f"ingest={ingest_minutes}min, "
                    f"ai={ai_minutes}min, "
                    f"er={er_submissions}"
                )
            
            print(f"✅ Iteration {iteration} complete\n")
            time.sleep(LOOP_INTERVAL_SECONDS)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Simulator stopped by user")
        print(f"📊 Total iterations: {iteration}")


if __name__ == "__main__":
    main()
