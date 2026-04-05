# Compatibility backend image definition.
# Canonical file: /backend/Dockerfile
# Legacy compatibility copy remains at /Dockerfile.production.

FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.runtime.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.runtime.txt

FROM python:3.12-slim AS runtime

RUN groupadd -r vidyaos && useradd -r -g vidyaos -d /app vidyaos

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend/ .

RUN mkdir -p /app/uploads /app/logs && \
    chown -R vidyaos:vidyaos /app

USER vidyaos

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

CMD ["python", "run_api.py", "--host", "0.0.0.0"]
