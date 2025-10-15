#!/usr/bin/env bash
# 🏈 SeaTrace Red Zone Smoke Tests
# For the Commons Good! 🌊

set -e

echo "🏈 RED ZONE OFFENSE - 2-MINUTE DRILL"
echo "===================================="
echo ""

# 1. FIRST DOWN - Health checks
echo "1️⃣ FIRST DOWN - Health Checks"
for p in 8001 8002 8003 8004; do
  echo -n "  Port $p: "
  curl -fsS http://localhost:$p/health && echo " ✓" || echo " ✗"
done
echo ""

# 2. SECOND DOWN - Metrics
echo "2️⃣ SECOND DOWN - Metrics Sample"
curl -s http://localhost:8001/metrics | grep -E '^seatrace_' | head -5
echo ""

# 3. THIRD DOWN - Rate Limit Test
echo "3️⃣ THIRD DOWN - Rate Limit Test (expect some 429s)"
for i in $(seq 1 50); do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost/marketside/login 2>/dev/null || true
done | sort | uniq -c
echo ""

# 4. TOUCHDOWN - Full integration
echo "4️⃣ TOUCHDOWN - Integration Check"
echo "  Gateway: $(curl -fsS http://localhost/health && echo '✓' || echo '✗')"
echo "  Prometheus: $(curl -fsS http://localhost:9090/-/healthy && echo '✓' || echo '✗')"
echo "  Grafana: $(curl -fsS http://localhost:3000/api/health && echo '✓' || echo '✗')"
echo ""

echo "🏆 RED ZONE DRILL COMPLETE!"
