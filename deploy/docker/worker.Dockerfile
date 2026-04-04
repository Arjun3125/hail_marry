# Canonical worker image definition.
# Legacy compatibility copy remains at /backend/Dockerfile.worker.

FROM python:3.11-slim as builder

WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && python -m venv /opt/venv && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.runtime.txt .
RUN pip install --no-cache-dir -r requirements.runtime.txt

FROM python:3.11-slim

RUN groupadd -r vidyaos && useradd -r -g vidyaos -d /app -s /sbin/nologin -c "Docker image user" vidyaos \
    && apt-get update && apt-get install -y --no-install-recommends libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

COPY backend/ .

RUN chmod +x /app/start-api.sh /app/start-worker.sh && \
    chown -R vidyaos:vidyaos /app

USER vidyaos

CMD ["sh", "/app/start-worker.sh"]
