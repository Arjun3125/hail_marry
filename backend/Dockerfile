FROM python:3.11-slim as builder

WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && python -m venv /opt/venv && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN grep -v -iE '^(torch|torchvision)(==|$)' requirements.txt > requirements-build.txt && \
    pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.10.0 && \
    pip install --no-cache-dir -r requirements-build.txt


FROM python:3.11-slim

# Create a non-root user for enterprise compliance
RUN groupadd -r vidyaos && useradd -r -g vidyaos -d /app -s /sbin/nologin -c "Docker image user" vidyaos \
    && apt-get update && apt-get install -y --no-install-recommends libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

COPY . .

# Ensure scripts are executable and set ownership
RUN chmod +x /app/start-api.sh /app/start-worker.sh && \
    chown -R vidyaos:vidyaos /app

USER vidyaos

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["sh", "/app/start-api.sh"]
