# Canonical worker image definition.
# Legacy compatibility copy remains at /backend/Dockerfile.worker.

FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

RUN groupadd -r vidyaos && useradd -r -g vidyaos -d /app -s /sbin/nologin -c "Docker image user" vidyaos \
    && apt-get update && apt-get install -y --no-install-recommends libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY backend/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY backend/ .

RUN chmod +x /app/start-api.sh /app/start-worker.sh && \
    chown -R vidyaos:vidyaos /app

USER vidyaos

CMD ["sh", "/app/start-worker.sh"]
