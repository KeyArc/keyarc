# KeyArc: Deployment & Infrastructure

## Hosting Platform

**Fly.io** - chosen for simple deployment, managed Postgres, automatic HTTPS, private networking, and low cost.

## Network Architecture

### Public Services
- Frontend (keyarc.io) - Static SPA
- Auth Service (keyarc.io/auth) - Unauthenticated flows
- Gateway (keyarc.io/api) - JWT validation + routing

### Private Services (via .flycast)
- Account Service (account.flycast)
- Key Service (keys.flycast)
- PostgreSQL (postgres.flycast)

### Traffic Flow
```
Internet:
  keyarc.io         → Frontend
  keyarc.io/auth/*  → Auth Service
  keyarc.io/api/*   → Gateway → Account/Key Service

Internal:
  Gateway           → account.flycast, keys.flycast
  All services      → postgres.flycast
```

## CI/CD

### GitHub Actions

Automated deployment on push to main:
1. Run tests (pytest, frontend tests)
2. Deploy changed services to Fly.io
3. Rolling deployment, zero downtime

### Deployment Matrix

| Service | Fly App | Trigger Path |
|---------|---------|--------------|
| Frontend | keyarc-frontend | `src/frontends/web/**` |
| Auth Service | keyarc-auth | `src/services/auth/**`, `src/shared/**` |
| Gateway | keyarc-gateway | `src/services/gateway/**` |
| Account Service | keyarc-account | `src/services/account/**`, `src/shared/**` |
| Key Service | keyarc-keys | `src/services/keys/**`, `src/shared/**` |

## Database

### PostgreSQL on Fly.io

- Single instance (POC)
- 3-10GB storage
- Daily automated backups
- Alembic for migrations
- SQLAlchemy + asyncpg

### Connection Security
- Only accessible via private network
- Connection string stored as Fly.io secret
- SSL/TLS encryption

## Secrets Management

### Fly.io Secrets

- Encrypted at rest
- Not visible in logs or deploy output
- Per-app isolation

### Per-Service Secrets

| Service | Secrets |
|---------|---------|
| Auth Service | `DATABASE_URL`, `JWT_SECRET` |
| Gateway | `JWT_SECRET` |
| Account Service | `DATABASE_URL` |
| Key Service | `DATABASE_URL` |

### Commands
```bash
fly secrets set JWT_SECRET=xxx --app keyarc-auth
fly secrets list --app keyarc-auth
fly secrets unset OLD_SECRET --app keyarc-auth
```

### Best Practices
- Never log environment variables
- Don't include in error messages
- Access via `os.getenv()`

## Monitoring

### Fly.io Built-in
- Logs: `fly logs --app keyarc-<service>`
- Metrics: CPU, memory, request rates
- Health checks: `/health` endpoint
- Alerts: Email on crashes

### Application Logging
- Python `logging` module
- JSON format for parsing
- Levels: DEBUG (dev), INFO (prod)

## Cost Estimate

### POC (Free Tier)
- ~$0/month (may exceed with 5 VMs)

### Production
| Component | Cost |
|-----------|------|
| Frontend VM | ~$5/mo |
| Auth Service VM | ~$5/mo |
| Gateway VM | ~$3/mo |
| Account Service VM | ~$5/mo |
| Key Service VM | ~$5/mo |
| Postgres 10GB | ~$15/mo |
| **Total** | **~$38/mo** |

## Versioning

Semantic versioning: `MAJOR.MINOR.PATCH`

- v0.x.x - POC phase
- v1.0.0 - Feature-complete MVP

### Branch Strategy
- `main` - Production-ready
- `work/*` - Feature branches
- `release/*` - Release preparation

## Region

Primary: **Ashburn, Virginia (iad)**

Fallback: Dallas (dfw), Chicago (ord)

## Dockerfile Example

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## fly.toml Example

```toml
app = "keyarc-auth"

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

  [[services.http_checks]]
    interval = 10000
    method = "get"
    path = "/health"
    timeout = 2000
```
