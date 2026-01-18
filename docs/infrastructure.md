# KeyArc: Infrastructure & Deployment

## Overview

This document outlines the infrastructure decisions, hosting architecture, and deployment strategy for KeyArc. It complements the main product document by focusing specifically on where and how the application will be deployed.


## Hosting Platform: Fly.io

## Authentication & Zero-Knowledge Model

KeyArc uses a Bitwarden-style authentication and encryption model, implemented with FastAPI. For full details on the cryptographic flow and security model, see the "Encryption Model (Bitwarden-style)" and "Crypto Flow Reference" sections in the product documentation.

**Summary:**
- All authentication and encryption is handled client-side; the server never sees user plaintext secrets or master password.
- Authentication is performed by validating a hash of the derived master key (`authHash`).
- All secret data is always encrypted before transmission and at rest.
- If a user forgets their master password, their data is unrecoverable (true zero-knowledge).

**Decision:** Use Fly.io as the primary hosting platform for POC and initial production.

### Why Fly.io?

- **Python support** - First-class support for Python applications via Dockerfile deployment
- **Simple deployment** - `fly deploy` handles building and deploying Docker containers
- **Managed Postgres** - Built-in PostgreSQL with automated backups
- **Automatic HTTPS** - Free SSL certificates via Let's Encrypt
- **Global edge network** - Apps run close to users (30+ regions)
- **Private networking** - Apps communicate securely over internal network
- **Low cost for POC** - Free tier covers development, ~$25-35/mo for production start
- **No vendor lock-in** - Standard Docker containers, easy to migrate

---

## Architecture

### POC Architecture (Simple)

For proof-of-concept and initial launch:

```
┌─────────────────────────────────────┐
│         Fly.io (Single Region)      │
│                                     │
│          ┌───────────────┐          │
│          │    Frontend   │          │
│          │    (SPA)      │          │
│          └──────┬────────┘          │
│                 │                   │
│                 │ HTTPS (public)    │
│                 │                   │
│          ┌──────▼────────┐          │
│          │   Backend API │          │
│          │   (Python)    │          │
│          └──────┬────────┘          │
│                 │                   │
│                 │ private network   │
│                 │                   │
│          ┌──────▼─────────┐         │
│          │  PostgreSQL    │         │
│          │  (Fly Postgres)│         │
│          └────────────────┘         │
└─────────────────────────────────────┘
```

**Components:**
- **Frontend:** Single shared-CPU VM serving SPA
- **Backend:** Single shared-CPU VM running Python API (FastAPI)
- **Database:** Single Postgres instance (3-10GB storage)

**No redundancy** - acceptable for POC, auto-restart on crashes (~5 seconds downtime)


---

## Custom Domain

**Domain:** keyarc.io (already owned)

### DNS Configuration

- **Frontend:** `keyarc.io` and `www.keyarc.io`
- **Backend API:** `api.keyarc.io`
- **SSL Certificates:** Free via Let's Encrypt (automatic renewal)

### Setup Steps
1. Add certificates via `fly certs add`
2. Update DNS A/AAAA records to point to Fly.io IPs
3. Fly.io automatically provisions SSL
4. Propagation: ~5 minutes to 1 hour

### Cost
- Custom domain: $0 (just DNS updates)
- SSL certificates: $0 (automatic)
- DNS hosting: Whatever current provider charges (or free with Cloudflare DNS)

---

## Network Architecture

### Public vs Private

**Public (internet-accessible):**
- Frontend app (keyarc.io)
- Backend API (api.keyarc.io)

**Private (internal Fly.io network only):**
- PostgreSQL database
- Any future internal services

### Fly.io Private Networking

- Apps communicate via `.flycast` internal domains
- Example: Backend connects to `postgres.flycast`
- Never exposed to public internet
- No additional cost
- Automatic service discovery

---

## CI/CD Strategy

### GitHub Actions Integration

**Approach:** Automated deployment on push to main branch

**Workflow:**
1. Developer pushes code to GitHub main branch
2. GitHub Actions triggers
3. Run automated tests (pytest for backend, frontend tests)
4. Deploy to Fly.io via official Actions (builds Docker image)
5. Fly.io deploys container (rolling deployment, zero downtime)

**Requirements:**
- Fly.io API token stored in GitHub Secrets
- Separate workflows for frontend and backend
- Path-based triggers (only deploy what changed)
- Dockerfile for backend Python application

**Decision:** Set up GitHub Actions early for consistent deployment process

### Environments

**POC Phase:**
- Single production environment
- No staging environment initially

**Future:**
- Staging environment on separate Fly.io apps
- Branch-based deployments (main → prod, staging → staging)
- Optional: PR preview deployments

---

## Database Strategy

### PostgreSQL on Fly.io

**Configuration (POC):**
- Single instance (no replication)
- 3-10GB storage
- Shared CPU
- Daily automated backups
- Region: Same as API (minimize latency)

**Backup Strategy:**
- Fly.io automated daily backups (retained 7 days)
- Manual snapshots before major schema changes
- Future: Point-in-time recovery for production

**Migrations:**
- Alembic (for SQLAlchemy)
- Applied via `fly ssh console` then migration command
- Or automated via CI/CD deployment step

**Python Database Libraries:**
- **SQLAlchemy** - industry standard ORM for FastAPI
- **asyncpg** or **psycopg3** - for async PostgreSQL drivers

### Connection Security

- Database only accessible via private Fly.io network
- Connection string stored as Fly.io secret
- SSL/TLS encryption for connections
- No public internet exposure

---

## Secrets Management

### Application Secrets

Stored as Fly.io secrets (encrypted at rest):
- Database connection strings
- JWT signing keys
- Any API keys for third-party services

**Management:**
```bash
fly secrets set JWT_SECRET=xxx --app keyarc-api
fly secrets set DATABASE_URL=postgresql://... --app keyarc-api
```

### User Secrets (KeyArc Data)

**NOT stored as infrastructure secrets** - these are the encrypted user secrets managed by the KeyArc application itself:
- Stored in PostgreSQL as encrypted blobs
- Client-side encryption before transmission
- Server never sees plaintext

---

## Monitoring & Observability

### Built-in Fly.io Features

- **Logs:** `fly logs --app keyarc-api`
- **Metrics:** Dashboard shows CPU, memory, request rates
- **Health checks:** Automatic HTTP health endpoint monitoring
- **Alerts:** Email notifications for app crashes

### Python-Specific Monitoring

**Application logging:**
- Standard Python `logging` module
- Structured logging (JSON format) for easier parsing
- Log levels: DEBUG (dev), INFO (prod), ERROR, CRITICAL

**Error tracking (future):**
- Sentry integration for error tracking
- Exception notifications and stack traces

---

## Cost Estimate

### POC / Development (Free Tier)

- Frontend VM: Free (within allowance)
- Backend VM: Free (within allowance)
- Postgres 3GB: Free (within allowance)
- **Total: $0/month**

### Initial Production

- Frontend VM (shared-cpu-1x): ~$5/mo
- Backend VM (shared-cpu-1x): ~$5/mo
- Postgres 10GB: ~$15/mo
- Bandwidth: Included (up to 100GB)
- **Total: ~$25/month**

### Scaling Considerations

Python applications scale well on Fly.io:
- Horizontal scaling: Add more VMs (auto-scaling available)
- Vertical scaling: Upgrade to dedicated CPUs
- ASGI servers (uvicorn, gunicorn) handle concurrent requests efficiently

---

## Security Considerations

### Infrastructure Security

- **HTTPS only:** All traffic encrypted in transit (automatic via Fly.io)
- **Private database:** No public internet access
- **Secret management:** Encrypted at rest via Fly.io secrets
- **Platform security:** Fly.io handles OS patches and security updates

### Application-Level Security

- **Zero-knowledge architecture:** Server never sees plaintext secrets (handled at application layer)
- **Client-side encryption:** All crypto operations in browser
- **Private networking:** Database accessible only via Fly.io internal network

### Python Security Best Practices

- **Dependency scanning:** Use `pip-audit` or `safety` to check for vulnerable packages
- **Virtual environments:** Isolate dependencies
- **Requirements pinning:** Lock all dependency versions
- **Security headers:** Implement via middleware (CORS, CSP, etc.)

---

## Tech Stack Summary

### Infrastructure Layer

- **Hosting:** Fly.io
- **Database:** PostgreSQL (Fly.io managed)
- **DNS:** Current registrar or Cloudflare
- **SSL:** Let's Encrypt (via Fly.io)
- **Secrets:** Fly.io secrets management
- **CI/CD:** GitHub Actions
- **Container:** Docker (Python base image)

### Application Layer

**Backend:**
- **Language:** Python 3.14+ (or 3.13)
- **Framework:** FastAPI (modern, async, automatic API docs)
- **ASGI Server:** uvicorn (for FastAPI/async) or gunicorn
- **Database ORM:** SQLAlchemy
- **Database Driver:** asyncpg (async) or psycopg3 (sync)
- **Migrations:** Alembic (SQLAlchemy)
- **Authentication:** JWT tokens via PyJWT or python-jose

**Frontend:**

**Frontend:**
- **Framework:** Angular (TypeScript, LTS, Angular 20)
- **Build tool:** Vite or similar
- **Cryptography:** WebCrypto API (client)

---

## Python Deployment Details

### Dockerfile Structure

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run migrations (if not done via fly.toml)
# RUN alembic upgrade head

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### fly.toml Configuration

```toml
app = "keyarc-api"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80
    force_https = true

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

  [[services.http_checks]]
    interval = 10000
    grace_period = "5s"
    method = "get"
    path = "/health"
    protocol = "http"
    timeout = 2000
```

### Package Management

**Requirements file:**
```
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pyjwt==2.8.0
cryptography==41.0.7
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
```

**Development dependencies:**
```
# requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.11.0
ruff==0.1.6
mypy==1.7.1
```

---


## Summary

KeyArc's infrastructure strategy uses Fly.io for hosting, providing simple deployment via Docker, managed PostgreSQL, automatic HTTPS, and global edge capabilities. The architecture is intentionally minimal for the POC phase, with single instances of frontend, backend, and database running in a single region.

The backend is built with Python, leveraging the mature ecosystem of cryptographic libraries (`cryptography`, PyJWT) and modern web frameworks (FastAPI recommended for async performance and developer experience). The platform uses standard Docker containers and PostgreSQL, avoiding vendor lock-in while maintaining operational simplicity.

Fly.io was chosen for its straightforward Docker-based deployment workflow and cost-effective pricing starting at $0 for development and ~$25/month for initial production use.

### Region Selection

For lowest latency to central Mississippi and Atlanta, GA, the primary Fly.io deployment region will be **Ashburn, Virginia (iad)**. This region is closest to both collaborators and provides excellent connectivity for the Southeast US. If capacity is unavailable, fallback options include Dallas, TX (dfw) or Chicago, IL (ord).
