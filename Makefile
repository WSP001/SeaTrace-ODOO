# 🏈 SeaTrace Practice Gamebook Makefile
# For the Commons Good! 🌊

.PHONY: scaffold dev test smoke metrics fmt lint compose-up compose-down help

help:
	@echo "🏈 SeaTrace Practice Drills"
	@echo "  make scaffold SERVICE=seaside PORT=8001 MODULE=src.seaside"
	@echo "  make dev SERVICE=seaside"
	@echo "  make test"
	@echo "  make smoke"
	@echo "  make metrics"
	@echo "  make fmt"
	@echo "  make lint"
	@echo "  make compose-up"
	@echo "  make compose-down"

scaffold:
	@python scripts/scaffold.py $(SERVICE) $(PORT) $(MODULE)

dev:
	@cd services/$(SERVICE) && poetry install --no-interaction && poetry run uvicorn $(MODULE):app --reload --port $(shell grep -oE 'EXPOSE [0-9]+' services/$(SERVICE)/Dockerfile | awk '{print $$2}')

test:
	@pytest -q tests/

smoke:
	@echo "🏈 Running health checks..."
	@curl -fsS http://localhost:8001/health && echo " ✓ seaside" || echo " ✗ seaside"
	@curl -fsS http://localhost:8002/health && echo " ✓ deckside" || echo " ✗ deckside"
	@curl -fsS http://localhost:8003/health && echo " ✓ dockside" || echo " ✗ dockside"
	@curl -fsS http://localhost:8004/health && echo " ✓ marketside" || echo " ✗ marketside"

metrics:
	@echo "🏈 Checking metrics..."
	@curl -s http://localhost:8001/metrics | grep -E '^seatrace_' | head -20

fmt:
	@echo "🏈 Formatting code..."
	@ruff format src/ services/ || echo "Install ruff: pip install ruff"

lint:
	@echo "🏈 Linting code..."
	@ruff check src/ services/ || echo "Install ruff: pip install ruff"
	@bandit -r src/ services/ -q || echo "Install bandit: pip install bandit"

compose-up:
	@echo "🏈 Starting full formation..."
	@docker compose --profile all up -d

compose-down:
	@echo "🏈 Stopping formation..."
	@docker compose down
