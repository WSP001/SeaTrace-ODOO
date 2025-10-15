#!/usr/bin/env python3
"""
🏈 SeaTrace Service Scaffolder
For the Commons Good! 🌊

Usage:
    python scripts/scaffold.py seaside 8001 src.seaside
    make scaffold SERVICE=seaside PORT=8001 MODULE=src.seaside
"""

import os
import sys
import textwrap
import pathlib

# Parse arguments
svc = os.environ.get("SERVICE") or (sys.argv[1] if len(sys.argv) > 1 else None)
port = int(os.environ.get("PORT") or (sys.argv[2] if len(sys.argv) > 2 else 8000))
module = os.environ.get("MODULE") or (sys.argv[3] if len(sys.argv) > 3 else f"src.{svc}")

if not svc:
    print("❌ Usage: scaffold.py SERVICE PORT MODULE")
    sys.exit(1)

# Map service to role
ROLES = {
    "seaside": "HOLD",
    "deckside": "RECORD",
    "dockside": "STORE",
    "marketside": "EXCHANGE"
}
role = ROLES.get(svc, "SERVICE")

# Create service directory structure
base = pathlib.Path(f"services/{svc}")
base.mkdir(parents=True, exist_ok=True)

# Read template
tmpl_path = pathlib.Path("templates/fastapi_pillar/app.py.tmpl")
if not tmpl_path.exists():
    print(f"❌ Template not found: {tmpl_path}")
    sys.exit(1)

tmpl = tmpl_path.read_text()

# Replace template variables
code = (tmpl.replace("{{SERVICE}}", svc)
            .replace("{{MODULE}}", module)
            .replace("{{ROLE}}", role))

# Write service module
module_path = pathlib.Path(f"services/{svc}/{module.replace('.', '/')}.py")
module_path.parent.mkdir(parents=True, exist_ok=True)
module_path.write_text(code)

# Create pyproject.toml
pyproject = f"""
[tool.poetry]
name = "seatrace-{svc}"
version = "0.1.0"
description = "SeaTrace {svc} pillar"
authors = ["SeaTrace <team@seatrace.org>"]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115"
uvicorn = {{extras = ["standard"], version = "^0.30"}}
prometheus-client = "^0.20"
python-multipart = "^0.0.9"
pydantic = "^2.8"
httpx = "^0.27"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3"
pytest-asyncio = "^0.23"
ruff = "^0.6"
bandit = "^1.7"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

pathlib.Path(f"services/{svc}/pyproject.toml").write_text(textwrap.dedent(pyproject))

# Create Dockerfile
dockerfile = f"""
# SeaTrace {svc.capitalize()} Dockerfile ({role})
FROM python:3.12-slim AS builder
ARG DEBIAN_FRONTEND=noninteractive
RUN useradd -m -u 10001 seatrace && apt-get update && apt-get install -y --no-install-recommends \\
    build-essential curl git pkg-config libpq-dev ca-certificates \\
 && rm -rf /var/lib/apt/lists/*
ENV POETRY_HOME=/opt/poetry POETRY_VERSION=1.8.3 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN curl -sSL https://install.python-poetry.org | python3 - \\
 && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry
USER seatrace
WORKDIR /app
COPY --chown=seatrace:seatrace pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create true \\
 && poetry config virtualenvs.in-project true \\
 && poetry install --only main --no-root --no-interaction --no-ansi || pip install fastapi uvicorn prometheus-client
COPY --chown=seatrace:seatrace . ./

FROM python:3.12-slim AS runtime
ARG DEBIAN_FRONTEND=noninteractive
RUN useradd -m -u 10001 seatrace && apt-get update && apt-get install -y --no-install-recommends \\
    libpq5 curl \\
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
USER seatrace
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

LABEL org.opencontainers.image.source="https://github.com/WSP001/SeaTrace-ODOO" \\
      org.opencontainers.image.title="{svc}" \\
      org.opencontainers.image.description="SeaTrace {svc.capitalize()} ({role}) microservice"

EXPOSE {port}
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:{port}/health || exit 1
CMD ["python", "-m", "uvicorn", "{module}:app", "--host", "0.0.0.0", "--port", "{port}"]
"""

pathlib.Path(f"services/{svc}/Dockerfile").write_text(textwrap.dedent(dockerfile))

# Create README
readme = f"""
# 🏈 SeaTrace {svc.capitalize()} ({role})

**For the Commons Good!** 🌊

## Position
- **Service:** {svc}
- **Role:** {role}
- **Port:** {port}
- **Module:** {module}

## Development

```bash
# Install dependencies
cd services/{svc}
poetry install

# Run locally
poetry run uvicorn {module}:app --reload --port {port}

# Or use Makefile
make dev SERVICE={svc}
```

## Endpoints

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /ingest/packet` - Ingest data packet (requires JWT)
- `GET /kpi` - KPI preview

## Docker

```bash
# Build
docker build -t seatrace-{svc}:latest services/{svc}

# Run
docker run -p {port}:{port} seatrace-{svc}:latest
```
"""

pathlib.Path(f"services/{svc}/README.md").write_text(textwrap.dedent(readme))

print(f"✅ Scaffolded {svc} on port {port} -> module {module}")
print(f"   📁 services/{svc}/")
print(f"   📄 {module_path}")
print(f"   📄 services/{svc}/pyproject.toml")
print(f"   📄 services/{svc}/Dockerfile")
print(f"   📄 services/{svc}/README.md")
