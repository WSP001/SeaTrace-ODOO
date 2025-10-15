# MarketSide Dockerfile (WR1 - EXCHANGE)
FROM python:3.12-slim AS builder
ARG DEBIAN_FRONTEND=noninteractive
RUN useradd -m -u 10001 seatrace && apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git pkg-config libpq-dev ca-certificates \
 && rm -rf /var/lib/apt/lists/*
ENV POETRY_HOME=/opt/poetry POETRY_VERSION=1.8.3 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN curl -sSL https://install.python-poetry.org | python3 - \
 && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry
USER seatrace
WORKDIR /app
COPY --chown=seatrace:seatrace pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create true \
 && poetry config virtualenvs.in-project true \
 && poetry install --only main --no-root --no-interaction --no-ansi || pip install fastapi uvicorn prometheus-client
COPY --chown=seatrace:seatrace . ./

FROM python:3.12-slim AS runtime
ARG DEBIAN_FRONTEND=noninteractive
RUN useradd -m -u 10001 seatrace && apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
USER seatrace
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

LABEL org.opencontainers.image.source="https://github.com/WSP001/SeaTrace-ODOO" \
      org.opencontainers.image.title="marketside" \
      org.opencontainers.image.description="SeaTrace MarketSide (EXCHANGE) microservice"

EXPOSE 8004
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:8004/health || exit 1
CMD ["python", "-m", "uvicorn", "src.marketside:app", "--host", "0.0.0.0", "--port", "8004"]
