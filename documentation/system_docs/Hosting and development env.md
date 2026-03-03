# Hosting and Development Environment

**Project:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Pilot → Scale Ready)  
**Architecture Model:** Hybrid (Cloud Control Plane + Local AI Data Plane)

---

## 1. Hosting Strategy Overview

| Plane | Location | Purpose |
|---|---|---|
| **Control Plane** | Cloud VPS | ERP, API Gateway, Auth, Usage/Billing |
| **Data Plane** | Local GPU Server | AI Inference, Vector DB, Embedding Engine |

This separation ensures:
- Low AI cost during pilot (no GPU rental)
- Secure GPU exposure (no public IP)
- Cloud migration flexibility (swap data plane without touching control plane)
- Infrastructure modularity

---

## 2. Cloud Hosting (Control Plane)

### 2.1 VPS Minimum Specs (Pilot)

| Resource | Minimum |
|---|---|
| CPU | 2 vCPU |
| RAM | 4GB |
| Storage | 80GB SSD |
| Bandwidth | 2TB/month |
| OS | Ubuntu 22.04 LTS |

**Cost:** ₹800–₹1500/month  
**Recommended Providers:** Hetzner, DigitalOcean, Linode

### 2.2 Software Stack on VPS

- Nginx (reverse proxy + TLS termination)
- FastAPI backend (Uvicorn + Gunicorn)
- PostgreSQL (primary database)
- Redis (caching + rate limiting)
- Let's Encrypt (SSL)
- UFW firewall
- Fail2ban (SSH protection)

### 2.3 VPS Responsibilities

- HTTPS termination
- JWT validation
- Tenant routing
- ERP logic
- Rate limiting
- API logging
- Secure forwarding to AI node

**GPU never exposed publicly.**

---

## 3. Local AI Server (Data Plane)

### 3.1 Hardware Specification

| Component | Spec |
|---|---|
| GPU | RTX 4090 (24GB VRAM) |
| RAM | 64GB DDR5 |
| CPU | 12–16 core |
| Storage | 2TB NVMe |
| Power | UPS (30 min backup) |

**One-time cost:** ≈ ₹3,00,000

### 3.2 Software Stack

- Ubuntu 22.04
- Ollama (LLM model runner)
- nomic-embed-text (embedding model)
- FAISS / Qdrant (vector database)
- FastAPI AI microservice
- Docker (containerized services)

### 3.3 Network Setup

**Never expose raw GPU server IP.**

Secure connection options:
- Reverse SSH tunnel
- Tailscale (zero-config VPN)
- Cloudflare Tunnel

Connection must be: encrypted, IP-restricted, API-key authenticated.

---

## 4. Environment Separation

### 4.1 Development Environment

Local machine setup:
- Python 3.11+
- Node 20+
- Docker Desktop
- PostgreSQL (local)
- Redis (local)
- Ollama (optional, small model for testing)

### 4.2 Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/aiaas

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=<256-bit-secret>
GOOGLE_CLIENT_ID=<google-oauth-client-id>
GOOGLE_CLIENT_SECRET=<google-oauth-secret>

# AI Service
AI_SERVICE_URL=http://localhost:8001
AI_SERVICE_KEY=<internal-api-key>

# Application
APP_ENV=development
APP_URL=http://localhost:3000
```

**Never commit `.env` files.** Use `.env.example` as template.

### 4.3 Staging Environment

- Separate VPS (smaller instance)
- Mock AI model (for fast integration tests)
- Test domain (staging.aiaas.app)
- Used for: integration testing, performance testing, schema migrations

### 4.4 Production Environment

- Stronger firewall rules
- Monitoring tools active
- Automated daily backups
- Production secrets rotated quarterly

---

## 5. Configuration Management

YAML-based settings per environment (inspired by PrivateGPT):

```
settings.yaml              # Default configuration
settings-local.yaml         # Development overrides
settings-docker.yaml        # Docker Compose deployment
settings-staging.yaml       # Staging environment
settings-production.yaml    # Production deployment
```

Each file overrides defaults. Environment variables can override YAML values.

---

## 6. Containerization Strategy

### Pilot (Docker Compose)

```yaml
services:
  api:           # FastAPI backend
  postgres:      # PostgreSQL database
  redis:         # Cache + rate limiting
  ai-service:    # AI inference microservice
```

### Scale Phase (Kubernetes)

Separate pods:
- API gateway pod
- Worker pod (background jobs)
- AI inference pod (GPU node)
- Vector DB pod
- Horizontal pod autoscaler

---

## 7. Deployment Workflow

### 7.1 CI/CD Pipeline

```
Push to main
    → Run tests (pytest + Playwright)
    → Lint + type check (mypy + ruff)
    → Build Docker image
    → Deploy to staging
    → Manual approval
    → Deploy to production
    → Restart services (zero-downtime)
```

Tool: GitHub Actions

### 7.2 Database Migrations

Tool: Alembic (Python)

- Never manually modify production schema
- All changes via versioned migration scripts
- Migrations tested in staging before production

---

## 8. Monitoring & Observability

### On VPS

- **Uptime Kuma** — service health checks
- **Prometheus** — metrics collection
- **Grafana** — dashboards
- **Nginx access logs** — request tracking
- **Sentry** — error tracking

### On AI Node

- GPU utilization (`nvidia-smi`)
- VRAM usage
- Query latency
- Error rate
- Queue length

---

## 9. Backup Strategy

| Asset | Method | Frequency | Retention |
|---|---|---|---|
| PostgreSQL | `pg_dump` → S3-compatible | Daily | 30 days |
| Vector DB | Snapshot → secondary drive | Every 24h | 14 days |
| Config files | Git repository | On change | Permanent |
| Application logs | Log rotation → S3 | Daily | 7 days |

Weekly restore test mandatory.

---

## 10. Security Hardening

### VPS
- Disable root login
- SSH key only (no passwords)
- UFW firewall (allow 80/443 + SSH from limited IPs)
- Fail2ban installed
- Auto security updates enabled

### AI Node
- Private network only
- Firewall allows only VPS IP
- No public ports exposed
- API key required for all requests

---

## 11. Cost Breakdown (Pilot)

| Item | Monthly Cost |
|---|---|
| VPS | ₹1,000 |
| Internet | ₹2,000 |
| Electricity | ₹2,500 |
| Misc | ₹1,000 |
| **Total** | **≈ ₹6,500/month** |

One-time AI server: ≈ ₹3,00,000

---

## 12. Failure Scenarios & Recovery

| Scenario | Action |
|---|---|
| Power outage | UPS + auto restart services |
| GPU crash | Health check + restart Ollama |
| DB corruption | Restore from daily backup |
| Tunnel failure | Auto reconnect script (retry every 30s) |
| VPS outage | DNS failover + alerts |
