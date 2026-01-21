# Phase 5: CI/CD & Infrastructure

**Goal**: Complete the CI/CD pipeline and set up Fly.io infrastructure for deployment.

**Dependencies**: Phase 4 complete (all services functional)

**Task Summary**:
| Track | Tasks | IDs |
|-------|-------|-----|
| Dev | 2 | DEV-5.1 through DEV-5.2 |
| DevOps | 3 | DEVOPS-5.1 through DEVOPS-5.3 |
| QA | 3 | QA-5.1 through QA-5.3 |

---

## Dev Tasks

### DEV-5.1: Health Check Endpoints

Ensure all services have proper health checks.

**Scope**:
- Each service: `GET /health`
  - Return 200 if healthy
  - Check database connectivity (where applicable)
  - Check downstream service connectivity (Gateway)
- Liveness vs readiness probes (if differentiating)

**Acceptance Criteria**:
- [ ] All services have /health endpoint
- [ ] Health checks verify critical dependencies
- [ ] Unhealthy service returns 503

---

### DEV-5.2: Environment-Based Configuration

Ensure all services properly handle environment configuration.

**Scope**:
- Configuration via environment variables
- Required variables:
  - `DATABASE_URL` (Auth, Account, Key services)
  - `JWT_SECRET` (Auth, Gateway)
  - `ENVIRONMENT` (dev, staging, production)
  - Service URLs for Gateway routing
- Pydantic Settings for validation
- Fail fast on missing required config

**Acceptance Criteria**:
- [ ] All config from environment variables
- [ ] Missing required config causes startup failure
- [ ] Different configs for dev/staging/prod documented

---

## DevOps Tasks

### DEVOPS-5.1: Complete GitHub Actions Pipeline

Finalize the CI/CD pipeline.

**Scope**:
- Workflow stages:
  1. Lint and type check
  2. Unit tests with coverage
  3. Integration tests
  4. Build Docker images
  5. Push to container registry (on main)
  6. Deploy to staging (on main)
- Matrix builds for backend services
- Caching for dependencies
- Artifact retention policies

**Acceptance Criteria**:
- [ ] Full pipeline runs on PRs (without deploy)
- [ ] Main branch deploys to staging
- [ ] Docker images built and pushed
- [ ] Pipeline completes in reasonable time

---

### DEVOPS-5.2: Fly.io Infrastructure Setup

Provision Fly.io resources.

**Scope**:
- Create Fly.io applications:
  - `keyarc-frontend`
  - `keyarc-auth`
  - `keyarc-gateway`
  - `keyarc-account`
  - `keyarc-keys`
- PostgreSQL database:
  - `keyarc-postgres`
  - 10GB storage
  - Automated backups
- Private networking:
  - Account and Key services on .flycast
  - Only Gateway can reach private services
- Secrets configuration:
  - `DATABASE_URL` per service
  - `JWT_SECRET` for Auth and Gateway
- Domain configuration:
  - keyarc.io → frontend
  - auth.keyarc.io → Auth Service
  - api.keyarc.io → Gateway

**Acceptance Criteria**:
- [ ] All Fly apps created
- [ ] PostgreSQL provisioned
- [ ] Private networking configured
- [ ] Secrets set
- [ ] Domains configured (or documented)

---

### DEVOPS-5.3: Deployment Workflow

Create deployment automation.

**Scope**:
- fly.toml for each service
- Dockerfiles for each service
- Deployment workflow in GitHub Actions:
  - Triggered by push to main
  - Or manual trigger with environment selection
  - Rolling deployment
  - Health check verification
- Staging environment deployment
- Production deployment (manual approval)

**Acceptance Criteria**:
- [ ] fly.toml configured for each service
- [ ] Automated deployment to staging works
- [ ] Production deployment requires approval
- [ ] Rollback procedure documented

---

## QA Tasks

### QA-5.1: Integration Test Suite

Create comprehensive integration tests.

**Scope**:
- Full user journey tests:
  - Signup → Login → Create secrets → Create team → Share → View shared
- Cross-service validation:
  - Auth issues token, Gateway validates, services receive context
  - Changes in one service reflected in others
- Database consistency tests
- Error propagation tests

**Acceptance Criteria**:
- [ ] Key user journeys covered
- [ ] Tests run against real services (not mocks)
- [ ] Tests can run locally and in CI

**Learning Objectives**:
- Integration test design
- Multi-service testing
- Test environment management

---

### QA-5.2: Staging Environment Tests

Prepare tests for deployed environments.

**Scope**:
- Smoke test suite:
  - Each service health check passes
  - Basic operation works (signup, login, secret CRUD)
- Environment configuration validation:
  - Correct URLs
  - HTTPS enforced
  - Private services not publicly accessible
- Deployment verification tests:
  - Run after each deployment
  - Fail deployment if smoke tests fail

**Acceptance Criteria**:
- [ ] Smoke tests run against staging
- [ ] Tests verify environment configuration
- [ ] Can integrate with deployment pipeline

**Learning Objectives**:
- Environment-based testing
- Smoke test design
- Deployment verification

---

### QA-5.3: Health Check Tests

Write tests for health check endpoints.

**Scope**:
- Test: Each service /health returns 200
- Test: Unhealthy database causes health check failure
- Test: Health checks include dependency status

**Acceptance Criteria**:
- [ ] Health endpoints tested
- [ ] Failure scenarios tested

**Learning Objectives**:
- Health check testing
- Dependency failure testing

---

## Phase Completion Checklist

Before moving to Phase 6:

- [ ] All services have health checks
- [ ] Environment configuration complete
- [ ] Full CI/CD pipeline operational
- [ ] Fly.io infrastructure provisioned
- [ ] Staging environment deployed
- [ ] Deployment workflow automated
- [ ] Integration tests passing
- [ ] Smoke tests running against staging

**Previous Phase**: [Phase 4: Teams & Sharing](./phase-4-teams.md)
**Next Phase**: [Phase 6: Polish & Launch](./phase-6-launch.md)
