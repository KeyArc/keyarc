---
name: devops-engineer
description: Use when working with Docker containers, creating Dockerfile configurations, writing docker-compose files, setting up CI/CD pipelines with GitHub Actions, or managing infrastructure deployments.
---

# DevOps Engineer

## Overview
Expert guidance for containerization, CI/CD pipelines, infrastructure automation, and deployment workflows focused on Docker, Docker Compose, and GitHub Actions.

## When to Use
- Creating or optimizing Dockerfiles
- Writing docker-compose.yml configurations
- Setting up GitHub Actions workflows
- Configuring multi-stage builds
- Managing container orchestration
- Implementing CI/CD pipelines
- Setting up development environments

## Core Patterns

### Multi-Stage Dockerfile (Python/FastAPI)
```dockerfile
# Good: Multi-stage build with optimization
FROM python:3.14-slim as builder

WORKDIR /app

# Install dependencies in builder stage
COPY pyproject.toml .
RUN pip install --user --no-cache-dir .

# Runtime stage
FROM python:3.14-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY ./app ./app

# Non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Make pip packages available
ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Bad: Single stage, runs as root, no optimization
FROM python:3.14

WORKDIR /app
COPY pyproject.toml .
RUN pip install .

CMD ["python", "app/main.py"]
```

### Docker Compose for Development
```yaml
# Good: Complete dev environment with health checks
# Note: version line is deprecated in Docker Compose v2+, but included for backward compatibility
version: '3.9'

services:
  api:
    build:
      context: .
      target: development
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app:ro
      - ./.env:/app/.env:ro
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/keyarc_dev
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --reload --host 0.0.0.0

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: keyarc_dev
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### GitHub Actions CI/CD Pipeline
```yaml
# Good: Comprehensive CI/CD workflow
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -e .[dev]

      - name: Run linters
        run: |
          black --check app/
          isort --check app/
          pylint app/

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myregistry/keyarc:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Quick Reference: DevOps Best Practices

| Pattern | Recommendation |
|---------|---------------|
| Dockerfile | Multi-stage builds, non-root user, minimal layers |
| Base images | Use Alpine or slim variants for smaller size |
| Security | Never run as root, scan for vulnerabilities |
| Secrets | Use .env files (gitignored) or secrets management |
| Health checks | Always implement health/readiness checks |
| Caching | Leverage build cache and layer caching |
| CI/CD | Test, lint, build, deploy in separate jobs |

## Common Mistakes

**Running containers as root:**
```dockerfile
# Bad: Default root user
FROM python:3.14
COPY . /app
CMD ["python", "app.py"]

# Good: Non-root user
FROM python:3.14
RUN useradd -m appuser
USER appuser
COPY --chown=appuser:appuser . /app
CMD ["python", "app.py"]
```

**Poor layer caching:**
```dockerfile
# Bad: Changes to code invalidate dependency layer
FROM python:3.14
COPY . /app
RUN pip install /app

# Good: Dependencies installed before copying code
FROM python:3.14
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY . .
```

**Missing health checks:**
```yaml
# Bad: No health check
services:
  api:
    image: myapi
    depends_on:
      - db

# Good: Proper health check and condition
services:
  api:
    image: myapi
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s
```

## Environment-Specific Configurations

```yaml
# docker-compose.override.yml (development, gitignored)
# Docker Compose v2+ does not require version line

services:
  api:
    build:
      target: development
    volumes:
      - ./app:/app/app:ro
    command: uvicorn app.main:app --reload --host 0.0.0.0
    environment:
      - DEBUG=true

# docker-compose.prod.yml (production)
# Docker Compose v2+ does not require version line

services:
  api:
    build:
      target: production
    restart: always
    environment:
      - DEBUG=false
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## Secrets Management

```yaml
# Good: Using environment files (gitignored)
services:
  api:
    env_file:
      - .env
    # .env file contains:
    # DATABASE_URL=postgresql://...
    # SECRET_KEY=...
```

```dockerfile
# Good: Multi-stage with build args
ARG VERSION=latest
FROM node:${VERSION} as builder

ARG API_URL
ENV VITE_API_URL=${API_URL}

RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

## Key Principles

1. **Multi-stage builds**: Minimize final image size
2. **Security first**: Non-root users, vulnerability scanning
3. **Health checks**: Always implement for dependencies
4. **Layer optimization**: Order Dockerfile to maximize cache hits
5. **Environment separation**: Different configs for dev/staging/prod
6. **Secrets safety**: Never commit secrets, use env files or secret managers
7. **CI/CD automation**: Automate testing, linting, building, deployment
