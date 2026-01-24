# Phase 1: Foundation & Environment Setup

**Goal**: Establish local development environment, project structure, and shared modules that all services will use.

**Dependencies**: None (starting point)

**Task Summary**:
| Track | Tasks | IDs |
|-------|-------|-----|
| Dev | 4 | DEV-1.1 through DEV-1.4 |
| DevOps | 2 | DEVOPS-1.1 through DEVOPS-1.2 |
| QA | 4 | QA-1.1 through QA-1.4 |

---

## Dev Tasks

### DEV-1.1: Docker Compose Local Environment

Set up a local development environment using Docker Compose.

**Scope**:
- PostgreSQL container with persistent volume
- Service stubs for all 4 backend services (auth, gateway, account, keys)
- Shared network for inter-service communication
- Environment variable configuration (.env files)
- Hot-reload support for development

**Acceptance Criteria**:
- [ ] `docker-compose up` starts PostgreSQL and all service stubs
- [ ] PostgreSQL accessible on localhost:5432
- [ ] Each service stub responds to health check requests
- [ ] Environment variables loaded from .env files
- [ ] README with setup instructions

---

### DEV-1.2: Backend Project Scaffolding

Create the FastAPI project structure for all backend services.

**Scope**:
- Project structure per service:
  ```
  services/
  ├── auth/
  │   ├── app/
  │   │   ├── __init__.py
  │   │   ├── main.py
  │   │   ├── routers/
  │   │   ├── schemas/
  │   │   └── dependencies.py
  │   ├── tests/
  │   └── pyproject.toml
  ├── gateway/
  ├── account/
  └── keys/
  ```
- FastAPI application factory pattern
- Async database session management (SQLAlchemy + asyncpg)
- Health check endpoint (`GET /health`) on each service
- Logging configuration (JSON format)
- Pydantic settings for configuration

**Acceptance Criteria**:
- [ ] All 4 services start without errors
- [ ] Each service has `/health` endpoint returning 200
- [ ] Database connection pool configured (not connected yet)
- [ ] Logging outputs JSON format
- [ ] `pyproject.toml` with dependencies for each service

---

### DEV-1.3: Frontend Project Scaffolding

Create the Angular project structure for the frontend.

**Scope**:
- Angular 20 project initialization
- Project structure:
  ```
  frontend/
  └── src/app/
      ├── components/
      ├── services/
      ├── models/
      ├── guards/
      └── shared/
  ```
- Styling setup (hybrid approach):
  - Angular Material for complex components (forms, tables, dialogs)
  - TailwindCSS for layout, spacing, and custom styling
  - CSS custom properties for unified theming between both
  - Tailwind config with `preflight: false` to avoid Material conflicts
- Routing module setup
- HTTP interceptor stub (for auth headers)
- Environment configuration (dev/prod)
- Basic layout component (header, sidebar, content area)

**Acceptance Criteria**:
- [ ] `ng serve` starts development server
- [ ] Angular Material installed and configured
- [ ] TailwindCSS installed with custom theme colors
- [ ] CSS custom properties defined for shared color palette
- [ ] Routing configured with lazy loading
- [ ] HTTP interceptor registered (empty implementation)
- [ ] Environment files for dev and production
- [ ] Basic layout renders without errors (using both Material and Tailwind)

---

### DEV-1.4: Shared Python Modules

Create shared modules used across all backend services.

**Scope**:
- SQLAlchemy models (from ARCHITECTURE.md data model):
  - `User` (id, email, auth_hash, encrypted_vault_key, public_key, encrypted_private_key, created_at)
  - `Secret` (id, owner_type, owner_id, name, encrypted_value, type, expires_at, rotation_reminder_days, environment, folder_id, tags, created_at, updated_at)
  - `Team` (id, name, created_at)
  - `TeamMembership` (id, team_id, user_id, encrypted_team_key, role, created_at)
  - `Folder` (id, owner_type, owner_id, name, parent_folder_id)
  - `AuditLog` (id, user_id, secret_id, action, timestamp, ip_address)
- Audit logging module:
  - `create_audit_log()` function
  - Action types: view, create, update, delete, share
  - Never logs secret values
- RBAC module:
  - `check_team_permission()` function
  - Role hierarchy: member < admin < owner
- Shared Pydantic schemas for common types

**Acceptance Criteria**:
- [ ] All SQLAlchemy models defined with relationships
- [ ] Models importable from `shared.models`
- [ ] Audit logging function creates log entries
- [ ] RBAC function raises 403 for insufficient permissions
- [ ] Alembic migration for initial schema
- [ ] Unit tests for RBAC logic

---

## DevOps Tasks

### DEVOPS-1.1: Repository Structure & Branch Strategy

Establish repository conventions and branch protection.

**Scope**:
- Branch naming convention:
  - `main` - production-ready
  - `work/*` - feature/task branches
  - `release/*` - release preparation
- GitHub branch protection on `main`:
  - Require PR reviews
  - Require status checks to pass
- Conventional commit format (feat:, fix:, docs:, chore:, test:)
- PR template with checklist

**Acceptance Criteria**:
- [ ] Branch protection rules configured
- [ ] PR template created (`.github/PULL_REQUEST_TEMPLATE.md`)
- [ ] Contributing guide with branch/commit conventions
- [ ] `main` branch requires passing CI

---

### DEVOPS-1.2: Initial GitHub Actions Workflow

Set up basic CI pipeline for code quality.

**Scope**:
- Workflow triggers: push to main, pull requests
- Python jobs:
  - Linting (ruff or flake8)
  - Type checking (mypy)
  - Import sorting (isort)
- TypeScript jobs:
  - ESLint
  - TypeScript compilation check
- Job matrix for multiple Python versions (3.12, 3.13)

**Acceptance Criteria**:
- [ ] CI runs on every PR
- [ ] Lint failures block merge
- [ ] Type errors block merge
- [ ] Workflow completes in reasonable time
- [ ] Status checks visible on PRs

---

## QA Tasks

### QA-1.1: Backend Test Framework Setup

Set up Pytest infrastructure for backend services.

**Scope**:
- Pytest configuration (`pytest.ini` or `pyproject.toml`)
- Async test support (`pytest-asyncio`)
- Test database fixtures (use test PostgreSQL or SQLite for speed)
- Factory fixtures for creating test data (users, secrets, teams)
- Coverage configuration (`pytest-cov`)

**Acceptance Criteria**:
- [ ] `pytest` runs without errors from project root
- [ ] Async tests work correctly
- [ ] Test database isolated from development database
- [ ] At least one passing test exists
- [ ] Coverage report generates

**Learning Objectives**:
- Pytest configuration and fixtures
- Async testing patterns
- Test isolation strategies

---

### QA-1.2: Frontend Test Framework Setup

Set up Angular testing infrastructure.

**Scope**:
- Jasmine/Karma configuration (default Angular)
- Test utilities and helpers
- Mock service patterns
- Component testing harness setup

**Acceptance Criteria**:
- [ ] `ng test` runs without errors
- [ ] At least one passing component test
- [ ] Mock service pattern documented
- [ ] Tests run in headless mode for CI

**Learning Objectives**:
- Angular testing patterns
- Component test harnesses
- Mocking dependencies in Angular

---

### QA-1.3: E2E Framework Setup

Choose and configure an E2E testing framework.

**Scope**:
- Framework selection (Playwright recommended for modern features)
- Project configuration
- Base page objects or fixtures
- Test environment configuration
- Screenshot/video on failure

**Acceptance Criteria**:
- [ ] E2E framework installed and configured
- [ ] Can launch browser and navigate to frontend
- [ ] At least one passing E2E test (e.g., page loads)
- [ ] Screenshots captured on failure
- [ ] Runs in headless mode

**Learning Objectives**:
- E2E framework setup and configuration
- Page object pattern basics
- CI-friendly browser testing

---

### QA-1.4: Integrate Tests into CI

Add test execution to GitHub Actions workflow.

**Scope**:
- Add Pytest job to CI workflow
- Add Angular test job to CI workflow
- Add E2E test job (may run separately due to time)
- Upload coverage reports as artifacts
- Fail PR if tests fail

**Acceptance Criteria**:
- [ ] Backend tests run in CI
- [ ] Frontend tests run in CI
- [ ] E2E tests run in CI (can be optional initially)
- [ ] Coverage reports uploaded
- [ ] Test failures block merge

**Learning Objectives**:
- GitHub Actions workflow syntax
- CI test orchestration
- Artifact management

---

## Phase Completion Checklist

Before moving to Phase 2:

- [ ] Docker Compose starts all services and PostgreSQL
- [ ] All 4 backend services have health endpoints
- [ ] Frontend serves and displays layout
- [ ] Shared modules importable by services
- [ ] Database migrations run successfully
- [ ] CI pipeline runs lint, type checks
- [ ] Test frameworks set up for backend, frontend, and E2E
- [ ] Tests integrated into CI

**Next Phase**: [Phase 2: Authentication Flows](./phase-2-authentication.md)
