#!/usr/bin/env bash
# 🏈 SeaTrace Commit Preparation Script
# For the Commons Good! 🌊

set -e

MESSAGE="${1:-feat: Add 4-pillar architecture with monitoring}"
DRY_RUN="${2:-}"

echo "🏈 PREPARING COMMIT TO MASTER REPO"
echo "==================================="
echo ""

# Change to repo directory
cd "$(dirname "$0")/.."

# Check git status
echo "📊 Current Status:"
git status --short

echo ""
echo "📋 Files to Add:"
echo "  ✓ Makefile"
echo "  ✓ templates/fastapi_pillar/app.py.tmpl"
echo "  ✓ scripts/scaffold.py"
echo "  ✓ scripts/redzone.sh"
echo "  ✓ tests/test_health_metrics.py"
echo "  ✓ services/common/ratelimit.py"
echo "  ✓ src/seaside.py"
echo "  ✓ src/deckside.py"
echo "  ✓ src/dockside.py"
echo "  ✓ src/marketside.py"
echo "  ✓ services/*/Dockerfile"
echo "  ✓ docker-compose.yml"
echo "  ✓ infra/nginx/nginx.conf"
echo "  ✓ infra/prometheus/prometheus.yml"
echo ""

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "🔍 DRY RUN - No changes will be made"
    echo ""
    echo "Commands that would run:"
    echo "  git add Makefile"
    echo "  git add templates/"
    echo "  git add scripts/"
    echo "  git add tests/"
    echo "  git add services/"
    echo "  git add src/"
    echo "  git add infra/"
    echo "  git add docker-compose.yml"
    echo "  git commit -m '$MESSAGE'"
    exit 0
fi

# Confirm
echo "⚠️  Ready to stage and commit? (yes/no)"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "📦 Staging files..."

# Stage files
git add Makefile
git add templates/
git add scripts/
git add tests/
git add services/
git add src/
git add infra/
git add docker-compose.yml
git add .env.dev || true

echo "✅ Files staged"
echo ""

# Show what will be committed
echo "📝 Changes to be committed:"
git status --short

echo ""
echo "💾 Creating commit..."

# Commit
git commit -m "$MESSAGE"

echo ""
echo "🏆 COMMIT READY!"
echo ""
echo "Next steps:"
echo "  1. Review: git log -1 --stat"
echo "  2. Push: git push origin main"
echo "  3. Test: make smoke"
echo ""
