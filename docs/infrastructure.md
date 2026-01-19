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

### Service Architecture

KeyArc uses a "not too micro" microservices approach with clear service boundaries.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Fly.io (Single Region)                      │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PUBLIC (internet)                         │   │
│  │                                                              │   │
│  │   ┌──────────────┐   ┌──────────────┐    ┌────────────┐     │   │
│  │   │   Frontend   │   │ Auth Service │    │  Gateway   │     │   │
│  │   │  (Angular)   │   │  (FastAPI)   │    │ (FastAPI)  │     │   │
│  │   │ keyarc.io    │   │auth.keyarc.io│    │api.keyarc.io     │   │
│  │   └──────────────┘   └──────────────┘    └─────┬──────┘     │   │
│  │                             │                  │            │   │
│  └─────────────────────────────│──────────────────│────────────┘   │
│                                │                  │                │
│  ┌─────────────────────────────│──────────────────│────────────┐   │
│  │                    PRIVATE (.flycast)          │            │   │
│  │                             │           ┌──────┴──────┐     │   │
│  │                             │           │  /account/* │     │   │
│  │                             │           ▼             ▼     │   │
│  │                             │    ┌──────────┐ ┌──────────┐  │   │
│  │                             │    │ Account  │ │   Key    │  │   │
│  │                             │    │ Service  │ │ Service  │  │   │
│  │                             │    └────┬─────┘ └────┬─────┘  │   │
│  │                             │         │           │         │   │
│  │    ┌────────────────┐       │         │           │         │   │
│  │    │  PostgreSQL    │◄──────┴─────────┴───────────┘         │   │
│  │    │postgres.flycast│                                       │   │
│  │    └────────────────┘                                       │   │
│  │                                                             │   │
│  │    Shared Modules: [Audit Logging] [RBAC]                   │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Services Overview

| Service | Visibility | URL | Responsibility |
|---------|------------|-----|----------------|
| **Frontend** | Public | keyarc.io | Angular SPA, static files |
| **Auth Service** | Public | auth.keyarc.io | Signup, login, password reset, token refresh |
| **Gateway** | Public | api.keyarc.io | JWT validation, routing to private services |
| **Account Service** | Private | account.flycast | User profiles, teams, memberships |
| **Key Service** | Private | keys.flycast | Encrypted secrets, folders, tags |
| **PostgreSQL** | Private | postgres.flycast | Shared database |

### Service Details

**Frontend (keyarc.io)**
- Angular SPA served as static files
- Not behind the Gateway (no JWT needed to load)
- Handles all client-side cryptography

**Auth Service (auth.keyarc.io)**
- Public-facing, handles unauthenticated flows
- Signup, login, password reset, token refresh
- Issues JWT tokens after successful authentication
- Future: OAuth provider callbacks (Google, GitHub)

**Gateway (api.keyarc.io)**
- Thin, stateless, lambda-like proxy
- Validates JWT tokens on all requests
- Extracts user context and adds to request headers
- Routes to Account Service or Key Service based on path
- No database connections

**Account Service (account.flycast)**
- Private, only accessible via Gateway
- User profile management
- Team CRUD and membership management
- Uses shared RBAC module for permission checks

**Key Service (keys.flycast)**
- Private, only accessible via Gateway
- Encrypted secret storage and retrieval
- Folder and tag management
- Expiry tracking (computed on-demand, no background workers)
- Uses shared RBAC module for team secret permissions

### Shared Modules

Both Account Service and Key Service use shared Python modules:

- **Audit Logging Module**: Writes to shared audit_log table
- **RBAC Module**: Checks team role permissions (owner, admin, member)

### POC Resource Allocation

**Components (POC):**
- **Frontend:** Single shared-CPU VM serving SPA
- **Auth Service:** Single shared-CPU VM
- **Gateway:** Single shared-CPU VM (minimal resources)
- **Account Service:** Single shared-CPU VM
- **Key Service:** Single shared-CPU VM
- **Database:** Single Postgres instance (3-10GB storage)

**No redundancy** - acceptable for POC, auto-restart on crashes (~5 seconds downtime)


---

## Custom Domain

**Domain:** keyarc.io (already owned)

### DNS Configuration

- **Frontend:** `keyarc.io` and `www.keyarc.io`
- **Auth Service:** `auth.keyarc.io`
- **Gateway (API):** `api.keyarc.io`
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
- Frontend app (keyarc.io) - Static SPA
- Auth Service (auth.keyarc.io) - Unauthenticated flows
- Gateway (api.keyarc.io) - JWT validation + routing

**Private (internal Fly.io network only):**
- Account Service (account.flycast) - User/team management
- Key Service (keys.flycast) - Secret management
- PostgreSQL database (postgres.flycast)

### Fly.io Private Networking

- Private services communicate via `.flycast` internal domains
- Gateway routes to `account.flycast` and `keys.flycast`
- All services connect to `postgres.flycast`
- Private services never exposed to public internet
- No additional cost
- Automatic service discovery

### Traffic Flow

```
Internet Traffic:
  keyarc.io         → Frontend (static files)
  auth.keyarc.io    → Auth Service (signup, login)
  api.keyarc.io/*   → Gateway → Account/Key Service

Internal Traffic (via .flycast):
  Gateway           → account.flycast (user/team endpoints)
  Gateway           → keys.flycast (secret endpoints)
  All services      → postgres.flycast (database)
```

---

## CI/CD Strategy

### GitHub Actions Integration

**Approach:** Automated deployment on push to main branch

**Workflow:**
1. Developer pushes code to GitHub main branch
2. GitHub Actions triggers
3. Run automated tests (pytest for services, frontend tests)
4. Deploy changed services to Fly.io via official Actions
5. Fly.io deploys containers (rolling deployment, zero downtime)

**Requirements:**
- Fly.io API token stored in GitHub Secrets
- Separate workflows per service (auth, gateway, account, keys, frontend)
- Path-based triggers (only deploy what changed)
- Dockerfile for each Python service

**Service Deployment Matrix:**

| Service | Fly App Name | Trigger Path |
|---------|--------------|--------------|
| Frontend | keyarc-frontend | `frontend/**` |
| Auth Service | keyarc-auth | `services/auth/**`, `shared/**` |
| Gateway | keyarc-gateway | `services/gateway/**` |
| Account Service | keyarc-account | `services/account/**`, `shared/**` |
| Key Service | keyarc-keys | `services/keys/**`, `shared/**` |

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

## Semantic Versioning & Release Strategy

KeyArc follows [Semantic Versioning 2.0.0](https://semver.org/):

**Version format:** `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `1.2.3`)

### Version Components

- **MAJOR:** Breaking changes (e.g., API breaking changes, database schema incompatibility requiring migration)
- **MINOR:** New features, backward-compatible (e.g., new secret types, UI improvements)
- **PATCH:** Bug fixes, security patches (e.g., fixing encryption edge cases, dependency updates)

### Release Cadence

- **POC phase:** Ad-hoc releases as features stabilize
- **Production:** Minor releases roughly monthly; patches as needed for critical fixes
- **Versioning starts at:** v0.1.0 (POC phase), v1.0.0 (feature-complete MVP)

### Release Process

1. **Tag on main branch:** `git tag v1.2.3`
2. **GitHub release:** Create release with changelog on GitHub
3. **Docker image tagged:** `keyarc:1.2.3` (in addition to `keyarc:latest`)
4. **Fly.io deployment:** Manual promotion to production (or automatic based on tag)
5. **Changelog:** Maintained in `CHANGELOG.md` with user-facing summaries of changes

### Branch Strategy

- **main:** Production-ready code, always deployable
- **work/*:** Feature and bug fix branches, merged to main via PR
- **release/*:** Release branches for preparing production releases (e.g., `release/1.2.0`)

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

### Fly.io Secrets

KeyArc uses Fly.io's built-in secrets management:
- Encrypted at rest
- Not visible in `fly.toml`, logs, or deploy output
- Simple CLI management
- Per-app isolation

### Application Secrets

Stored as Fly.io secrets (injected as environment variables at runtime):
- Database connection strings
- JWT signing keys
- Any API keys for third-party services

**Per-Service Secrets:**

| Service | Required Secrets |
|---------|------------------|
| Auth Service | `DATABASE_URL`, `JWT_SECRET` |
| Gateway | `JWT_SECRET` (for validation only) |
| Account Service | `DATABASE_URL` |
| Key Service | `DATABASE_URL` |

**Management:**
```bash
# Set secrets per service
fly secrets set JWT_SECRET=xxx --app keyarc-auth
fly secrets set DATABASE_URL=postgresql://... --app keyarc-auth
fly secrets set JWT_SECRET=xxx --app keyarc-gateway
fly secrets set DATABASE_URL=postgresql://... --app keyarc-account
fly secrets set DATABASE_URL=postgresql://... --app keyarc-keys

# List secrets (values hidden)
fly secrets list --app keyarc-auth

# Remove a secret
fly secrets unset OLD_SECRET --app keyarc-auth
```

### Security Best Practices

Since secrets are injected as environment variables:
- **Never log environment variables** - sanitize logs
- **Don't include in error messages** - use generic errors
- **Don't expose in stack traces** - configure error handling
- **Access via `os.getenv()`** - don't hardcode fallbacks with real values

### User Secrets (KeyArc Data)

**NOT stored as infrastructure secrets** - these are the encrypted user secrets managed by the KeyArc application itself:
- Stored in PostgreSQL as encrypted blobs
- Client-side encryption before transmission
- Server never sees plaintext

---

## Monitoring & Observability

### Built-in Fly.io Features

- **Logs:** `fly logs --app keyarc-<service>` (auth, gateway, account, keys)
- **Metrics:** Dashboard shows CPU, memory, request rates per service
- **Health checks:** Automatic HTTP health endpoint monitoring (`/health`)
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
- Auth Service VM: Free (within allowance)
- Gateway VM: Free (within allowance)
- Account Service VM: Free (within allowance)
- Key Service VM: Free (within allowance)
- Postgres 3GB: Free (within allowance)
- **Total: $0/month** (may exceed free tier with 5 VMs)

### Initial Production

- Frontend VM (shared-cpu-1x): ~$5/mo
- Auth Service VM (shared-cpu-1x): ~$5/mo
- Gateway VM (shared-cpu-1x): ~$3/mo (minimal resources)
- Account Service VM (shared-cpu-1x): ~$5/mo
- Key Service VM (shared-cpu-1x): ~$5/mo
- Postgres 10GB: ~$15/mo
- Bandwidth: Included (up to 100GB)
- **Total: ~$38/month**

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
- **Private networking:** Account and Key services accessible only via Gateway
- **Gateway authentication:** All API requests validated at Gateway before reaching services
- **RBAC enforcement:** Shared module enforces team role permissions

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

### Service Architecture

- **Frontend:** Angular SPA (keyarc.io)
- **Auth Service:** FastAPI - signup, login, token management (auth.keyarc.io)
- **Gateway:** FastAPI/Starlette - JWT validation, routing (api.keyarc.io)
- **Account Service:** FastAPI - user/team management (private)
- **Key Service:** FastAPI - secret management (private)
- **Shared Modules:** Audit logging, RBAC

### Application Layer

**Backend Services:**
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
COPY pyproject.toml .
RUN pip install .

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

**Project configuration:**
```toml
# pyproject.toml
[project]
name = "keyarc"
version = "0.1.0"
description = "Secure, zero-knowledge API key and certificate manager"
requires-python = ">=3.14"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy",
    "asyncpg",
    "alembic",
    "pyjwt",
    "cryptography",
    "python-multipart",
    "pydantic",
    "pydantic-settings",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "httpx",
    "black",
    "ruff",
    "mypy",
]
```

---


## Summary

KeyArc's infrastructure strategy uses Fly.io for hosting, providing simple deployment via Docker, managed PostgreSQL, automatic HTTPS, and global edge capabilities. The architecture follows a "not too micro" microservices approach with five services:

- **Frontend** (public) - Angular SPA
- **Auth Service** (public) - Authentication and token management
- **Gateway** (public) - JWT validation and request routing
- **Account Service** (private) - User and team management
- **Key Service** (private) - Secret management

The backend services are built with Python/FastAPI, leveraging the mature ecosystem of cryptographic libraries (`cryptography`, PyJWT) and modern async web frameworks. Shared modules for audit logging and RBAC keep services consistent without adding extra microservices. The platform uses standard Docker containers and PostgreSQL, avoiding vendor lock-in while maintaining operational simplicity.

Fly.io was chosen for its straightforward Docker-based deployment workflow and cost-effective pricing starting at $0 for development and ~$38/month for initial production use.

### Region Selection

For lowest latency to central Mississippi and Atlanta, GA, the primary Fly.io deployment region will be **Ashburn, Virginia (iad)**. This region is closest to both collaborators and provides excellent connectivity for the Southeast US. If capacity is unavailable, fallback options include Dallas, TX (dfw) or Chicago, IL (ord).
