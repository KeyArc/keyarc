# Appendices

Reference material for the KeyArc implementation plan.

## Appendix A: Data Model Reference

From `ARCHITECTURE.md`:

### users
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| email | string | Unique |
| auth_hash | string | Hash of master key (for login) |
| encrypted_vault_key | blob | Vault key encrypted with master key |
| public_key | blob | Public key for sharing |
| encrypted_private_key | blob | Private key encrypted with master key |
| created_at | timestamp | |

### secrets
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| owner_type | enum | 'user' or 'team' |
| owner_id | uuid | References user or team |
| name | string | Display name (not encrypted) |
| encrypted_value | blob | The encrypted secret |
| type | enum | 'api_key', 'cert', 'other' |
| expires_at | timestamp | Nullable |
| rotation_reminder_days | integer | Nullable |
| environment | string | Nullable |
| folder_id | uuid | Nullable |
| tags | array | |
| created_at | timestamp | |
| updated_at | timestamp | |

### teams
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| name | string | Team name |
| created_at | timestamp | |

### team_memberships
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| team_id | uuid | References team |
| user_id | uuid | References user |
| encrypted_team_key | blob | Team key encrypted to user's public key |
| role | enum | 'owner', 'admin', 'member' |
| created_at | timestamp | |

### folders
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| owner_type | enum | 'user' or 'team' |
| owner_id | uuid | |
| name | string | |
| parent_folder_id | uuid | Nullable, for nesting |

### audit_log
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| user_id | uuid | Who |
| secret_id | uuid | What |
| action | enum | 'view', 'create', 'update', 'delete', 'share' |
| timestamp | timestamp | When |
| ip_address | string | From where |

---

## Appendix B: Cryptographic Parameters

From `keyarc-crypto-flows` skill:

| Operation | Algorithm | Parameters |
|-----------|-----------|------------|
| Master Key Derivation | Argon2id | time=3, mem=64MB, parallelism=4, hashLen=32 |
| Symmetric Encryption | AES-256-GCM | 256-bit key, 12-byte IV (random per encryption) |
| Asymmetric Encryption | RSA-OAEP | 2048-bit, SHA-256 hash |
| Auth Hash | PBKDF2-SHA256 | 100,000 iterations, 256-bit output |

### Key Hierarchy

```
Master Password (user input, never stored)
    │
    ├─► Master Key (Argon2id derivation)
    │       │
    │       ├─► Auth Hash (PBKDF2, sent to server for login)
    │       │
    │       ├─► Encrypted Vault Key (AES-256-GCM)
    │       │       │
    │       │       └─► Vault Key (decrypted client-side)
    │       │               │
    │       │               └─► Encrypts personal secrets
    │       │
    │       └─► Encrypted Private Key (AES-256-GCM)
    │               │
    │               └─► Private Key (decrypted client-side)
    │                       │
    │                       └─► Decrypts team keys shared to user
    │
    └─► (Never sent to server)
```

### Team Key Flow

```
Team Key (random AES-256)
    │
    ├─► Encrypted with Owner's Public Key → stored
    │
    ├─► Encrypted with Admin's Public Key → stored
    │
    └─► Encrypted with Member's Public Key → stored
        │
        └─► Each member decrypts with their Private Key
                │
                └─► Team Key used to decrypt team secrets
```

---

## Appendix C: Service Endpoint Summary

### Auth Service (keyarc.io/auth) - Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /signup | Create account with encrypted keys |
| POST | /login | Authenticate, receive JWT |
| POST | /token/refresh | Refresh JWT token |
| GET | /health | Health check |

### Gateway (keyarc.io/api) - Public

| Method | Endpoint | Routes To |
|--------|----------|-----------|
| * | /account/* | Account Service |
| * | /keys/* | Key Service |
| GET | /health | Health check |

### Account Service (via Gateway) - Private

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /account/profile | Get user profile |
| PUT | /account/profile | Update profile |
| GET | /account/teams | List user's teams |
| POST | /account/teams | Create team |
| GET | /account/teams/:id | Get team details |
| PUT | /account/teams/:id | Update team |
| DELETE | /account/teams/:id | Delete team |
| POST | /account/teams/:id/members | Add member |
| PUT | /account/teams/:id/members/:userId | Update member role |
| DELETE | /account/teams/:id/members/:userId | Remove member |
| GET | /account/users/search | Search users by email |
| GET | /health | Health check |

### Key Service (via Gateway) - Private

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /keys/secrets | List secrets |
| POST | /keys/secrets | Create secret |
| GET | /keys/secrets/:id | Get secret |
| PUT | /keys/secrets/:id | Update secret |
| DELETE | /keys/secrets/:id | Delete secret |
| GET | /keys/secrets/expiring | Get expiring secrets |
| GET | /keys/folders | List folders |
| POST | /keys/folders | Create folder |
| PUT | /keys/folders/:id | Update folder |
| DELETE | /keys/folders/:id | Delete folder |
| GET | /health | Health check |

---

## Appendix D: QA Skill Progression

Summary of skills QA engineer develops through the project:

| Phase | Skills Gained |
|-------|---------------|
| 1 | Test framework setup, CI integration, project structure |
| 2 | API testing, async patterns, mocking, JWT testing, E2E basics |
| 3 | Encrypted payload testing, validation testing, state management |
| 4 | Permission testing, security testing, complex scenarios, multi-user E2E |
| 5 | Integration testing, environment testing, deployment verification |
| 6 | Performance testing, security scanning, regression testing, documentation |

### Tools & Technologies Learned

By end of project, QA engineer will have experience with:

**Testing Frameworks**:
- Pytest for Python API testing
- Angular testing (Jasmine/Karma)
- E2E testing (Playwright or Cypress)

**CI/CD**:
- GitHub Actions workflow syntax
- Test automation in pipelines
- Artifact management

**Security Testing**:
- OWASP ZAP scanning
- Dependency vulnerability scanning
- Permission/authorization testing

**Performance Testing**:
- k6 or Locust for load testing
- Lighthouse for frontend performance
- Performance baseline establishment

**General Skills**:
- Test documentation
- Coverage analysis
- Bug triage and reporting
- Release readiness assessment

---

## Appendix E: Task ID Reference

Quick reference for all task IDs:

### Phase 1: Foundation
| ID | Description |
|----|-------------|
| DEV-1.1 | Docker Compose Local Environment |
| DEV-1.2 | Backend Project Scaffolding |
| DEV-1.3 | Frontend Project Scaffolding |
| DEV-1.4 | Shared Python Modules |
| DEVOPS-1.1 | Repository Structure & Branch Strategy |
| DEVOPS-1.2 | Initial GitHub Actions Workflow |
| QA-1.1 | Backend Test Framework Setup |
| QA-1.2 | Frontend Test Framework Setup |
| QA-1.3 | E2E Framework Setup |
| QA-1.4 | Integrate Tests into CI |

### Phase 2: Authentication
| ID | Description |
|----|-------------|
| DEV-2.1 | Frontend Crypto Module |
| DEV-2.2 | Auth Service Implementation |
| DEV-2.3 | Gateway Service Implementation |
| DEV-2.4 | Frontend Auth UI & State Management |
| DEVOPS-2.1 | Add Test Stage to CI Pipeline |
| QA-2.1 | Auth Service API Tests - Signup |
| QA-2.2 | Auth Service API Tests - Login |
| QA-2.3 | Auth Service API Tests - Rate Limiting |
| QA-2.4 | Crypto Module Unit Tests |
| QA-2.5 | E2E Tests - Signup Flow |
| QA-2.6 | E2E Tests - Login Flow |

### Phase 3: Secrets
| ID | Description |
|----|-------------|
| DEV-3.1 | Key Service - Secret CRUD |
| DEV-3.2 | Key Service - Folders & Organization |
| DEV-3.3 | Key Service - Expiry Tracking |
| DEV-3.4 | Frontend Vault UI |
| DEVOPS-3.1 | Code Coverage Reporting |
| QA-3.1 | Key Service API Tests - Create Secret |
| QA-3.2 | Key Service API Tests - Read Secrets |
| QA-3.3 | Key Service API Tests - Update & Delete |
| QA-3.4 | Key Service API Tests - Folders |
| QA-3.5 | Key Service API Tests - Expiry |
| QA-3.6 | Frontend Component Tests - Secret Form |
| QA-3.7 | E2E Tests - Secret Management |

### Phase 4: Teams
| ID | Description |
|----|-------------|
| DEV-4.1 | Account Service - User Profiles |
| DEV-4.2 | Account Service - Team Management |
| DEV-4.3 | Account Service - Team Membership |
| DEV-4.4 | Key Service - Team Secrets |
| DEV-4.5 | Frontend Team UI |
| DEVOPS-4.1 | Multi-Service Integration Tests |
| QA-4.1 | Account Service API Tests - Teams |
| QA-4.2 | Account Service API Tests - Membership |
| QA-4.3 | RBAC Permission Matrix Tests |
| QA-4.4 | Team Sharing Flow Tests |
| QA-4.5 | E2E Tests - Team Workflows |

### Phase 5: Infrastructure
| ID | Description |
|----|-------------|
| DEV-5.1 | Health Check Endpoints |
| DEV-5.2 | Environment-Based Configuration |
| DEVOPS-5.1 | Complete GitHub Actions Pipeline |
| DEVOPS-5.2 | Fly.io Infrastructure Setup |
| DEVOPS-5.3 | Deployment Workflow |
| QA-5.1 | Integration Test Suite |
| QA-5.2 | Staging Environment Tests |
| QA-5.3 | Health Check Tests |

### Phase 6: Launch
| ID | Description |
|----|-------------|
| DEV-6.1 | Client-Side API Validity Testing |
| DEV-6.2 | Dashboard & Overview |
| DEV-6.3 | Search Functionality |
| DEVOPS-6.1 | Production Deployment |
| DEVOPS-6.2 | Monitoring & Alerting |
| QA-6.1 | Full Regression Test Suite |
| QA-6.2 | Performance Tests |
| QA-6.3 | Security Test Automation |
| QA-6.4 | Test Documentation & Reporting |
