# KeyArc Project

## Project Identity

**Name:** KeyArc

**Purpose:** Secure, zero-knowledge API key and certificate manager for solo developers, small teams, and startups.

**Target Users:**
- Solo developers managing multiple API keys
- Small teams (2-10 people) needing to share credentials
- Startups requiring simple secret management

**Value Proposition:**
Store API keys and certificates securely, get reminders before they expire, verify they still work, and share them safely with your team—all without the server ever seeing your plaintext secrets.

**Core Principle:** Zero-knowledge architecture - the server NEVER sees plaintext secrets or master passwords.

## Technical Stack

**Backend:**
- FastAPI (Python async web framework)
- PostgreSQL (relational database)
- SQLAlchemy ORM (database access)

**Frontend:**
- Angular (TypeScript framework)
- RxJS (reactive programming)
- Angular Material (complex components: forms, tables, dialogs)
- TailwindCSS (layout, spacing, custom styling)
- CSS custom properties (shared theming between Material and Tailwind)

**Infrastructure:**
- Docker (containerization)
- Fly.io (hosting platform)
- Fly.io Secrets (application secrets management)
- GitHub Actions (CI/CD)

**Security:**
- WebCrypto API (client-side encryption)
- Argon2 (password-based key derivation)
- AES (symmetric encryption)
- RSA/ECC (asymmetric encryption for sharing)

## Service Architecture

KeyArc follows a right-sized services approach—pragmatic microservices with clear boundaries, avoiding both monolith complexity and microservice sprawl.

### Services Overview

| Service | Visibility | URL | Responsibility |
|---------|------------|-----|----------------|
| **Frontend** | Public | keyarc.io | Angular SPA, static files |
| **Auth Service** | Public | auth.keyarc.io | Signup, login, password reset, token refresh |
| **Gateway** | Public | api.keyarc.io | JWT validation, routing to private services |
| **Account Service** | Private | account.flycast | User profiles, teams, memberships, invitations |
| **Key Service** | Private | keys.flycast | Encrypted secrets, folders, tags, sharing |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Fly.io                                      │
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

### Service Responsibilities

**Auth Service (Public)**
- Handles unauthenticated flows only
- Signup with encrypted key storage
- Login with authHash validation
- Password reset flow
- Token refresh
- Future: OAuth provider callbacks (Google, etc.)

**Gateway (Public)**
- Thin, stateless, lambda-like
- Validates JWT tokens
- Extracts user context (user ID, etc.)
- Routes requests to private services based on path
- No database connections
- Adds user context headers for downstream services

**Account Service (Private)**
- User profile management
- Team CRUD operations
- Team membership management
- Invitation handling
- All endpoints require valid JWT (via Gateway)

**Key Service (Private)**
- Encrypted secret storage
- Folder and tag management
- Team secret sharing
- Expiry tracking (computed on-demand, no background workers)
- All endpoints require valid JWT (via Gateway)

### Shared Modules

**Audit Logging Module**
- Used by Auth Service, Account Service, and Key Service
- Writes to shared audit_log table in PostgreSQL
- Logs: who, what action, which resource, when, from where
- Never logs secret values

**RBAC Module**
- Used by Account Service and Key Service
- Checks team role permissions (owner, admin, member)
- Enforces access control at service level

### Traffic Flows

| Action | Flow |
|--------|------|
| Signup | Frontend → Auth Service |
| Login | Frontend → Auth Service |
| Get profile | Frontend → Gateway → Account Service |
| Manage team | Frontend → Gateway → Account Service |
| Get secrets | Frontend → Gateway → Key Service |
| Update secret | Frontend → Gateway → Key Service |

### Future OAuth Support

The architecture supports adding OAuth providers (Google, GitHub, etc.) while maintaining zero-knowledge:
- OAuth proves identity (who you are)
- Vault password still required to decrypt data (access to secrets)
- Auth Service handles OAuth callbacks
- Zero-knowledge principle preserved

## Zero-Knowledge Architecture

### Fundamental Principle

**The server MUST NEVER be able to decrypt user data.**

KeyArc implements a Bitwarden-inspired zero-knowledge encryption model where:
- All cryptographic operations happen client-side in the browser
- Server stores only encrypted ciphertext and authentication hashes
- Even if the server is compromised, user secrets remain encrypted

### Client-Side vs Server-Side Responsibilities

**Client (Browser) Responsibilities:**
- Master password handling (NEVER sent to server)
- Key derivation using Argon2
- All encryption and decryption operations
- Key generation (vault keys, keypairs)
- Computing authentication hashes

**Server Responsibilities:**
- Store encrypted data (ciphertext only)
- Validate authentication hashes (NOT passwords)
- Serve encrypted keys back to client
- Enforce access control on encrypted data
- Audit logging (metadata only, never secret values)

### What the Server Knows vs Never Knows

**Server CAN see:**
- Encrypted vault key (encrypted with user's master key)
- Encrypted private key (encrypted with user's master key)
- Public keys (used for sharing, not sensitive)
- Authentication hash (derived from master key, for login)
- Encrypted secrets (ciphertext)
- Metadata (names, timestamps, folder structure)

**Server NEVER sees:**
- Master password
- Master key (derived from password)
- Decrypted vault key
- Decrypted private key
- Plaintext secrets

## Cryptographic Flows

### Signup Flow

1. User provides email + master password (client-side only)
2. Derive `masterKey` from password using Argon2 (client)
3. Generate random `vaultKey` - AES-256 key for encrypting secrets (client)
4. Generate RSA/ECC keypair for team sharing (client)
5. Encrypt `vaultKey` with `masterKey` (client)
6. Encrypt `privateKey` with `masterKey` (client)
7. Compute `authHash` from `masterKey` (client)
8. Send to server: `email`, `authHash`, `encrypted(vaultKey)`, `encrypted(privateKey)`, `publicKey`
9. Server stores encrypted keys + authHash (server cannot decrypt them)

### Login Flow

1. User provides email + master password (client-side only)
2. Derive `masterKey` from password using Argon2 (client, same params as signup)
3. Compute `authHash` from `masterKey` (client)
4. Send to server: `email`, `authHash` (NOT the password or masterKey!)
5. Server validates `authHash` matches stored value
6. Server issues JWT token and returns encrypted keys
7. Client decrypts `vaultKey` and `privateKey` using `masterKey` (client)
8. Keys stored in memory for session duration (never persisted)

### Team Sharing Flow

1. Team owner generates `teamKey` - random AES-256 key (client)
2. Owner encrypts `teamKey` with their `publicKey` (client)
3. Send encrypted `teamKey` to server
4. To add member: current member decrypts `teamKey` with their `privateKey` (client)
5. Re-encrypt `teamKey` with new member's `publicKey` (client)
6. Server stores new member's encrypted copy of `teamKey`
7. Each member has `teamKey` encrypted with their own public key
8. Server stores N copies of `teamKey` (one per member), can't decrypt any of them

**Key Insight:** Server stores multiple encrypted copies of the same `teamKey`, each encrypted with a different member's public key. The server cannot decrypt any of them!

## Security Guidelines

### Mandatory Security Rules

**NEVER:**
- Send plaintext secrets to server
- Send master password to server
- Log sensitive data (passwords, keys, secret values)
- Decrypt data server-side
- Accept plaintext in API endpoints (only encrypted payloads)

**ALWAYS:**
- Encrypt all secrets client-side before sending
- Use `authHash` for authentication (never password)
- Perform ALL encryption/decryption in browser
- Validate that API payloads are encrypted (not plaintext)
- Log access (who, what, when) but NEVER secret values

### Development Requirements

**Security Review Required For:**
- All cryptographic code (signup, login, encryption)
- API endpoints handling secrets
- Key derivation or storage
- Authentication/authorization logic

**API Endpoint Requirements:**
- Validate JWT token on all protected endpoints
- Validate encrypted payload format
- Create audit log entry for secret access
- Use Pydantic for input validation
- Return generic error messages (don't leak data)

**Testing Requirements:**
- Test that server cannot decrypt user data
- Test that master password never transits network
- Test encryption/decryption round-trips
- Test key sharing between users
- Test audit logging completeness
- Test authentication with wrong password fails

### OWASP Top 10 Prevention

- **Injection:** SQLAlchemy ORM with parameterized queries
- **Broken Authentication:** JWT tokens, rate limiting, authHash validation
- **Sensitive Data Exposure:** All secrets encrypted client-side, HTTPS only
- **Broken Access Control:** RBAC enforced at API level
- **Security Misconfiguration:** Secure defaults, no debug in production
- **Insecure Deserialization:** Pydantic validation for all inputs
- **Insufficient Logging:** Comprehensive audit logs (access, not values)

## Project Structure

### Repository Layout

```
keyarc/
├── src/
│   ├── services/
│   │   ├── auth/                 # Auth Service (FastAPI)
│   │   │   ├── app/
│   │   │   │   ├── routers/
│   │   │   │   ├── schemas/
│   │   │   │   └── main.py
│   │   │   └── tests/
│   │   ├── gateway/              # Gateway Service (FastAPI/Starlette)
│   │   │   ├── app/
│   │   │   │   ├── routing.py
│   │   │   │   └── main.py
│   │   │   └── tests/
│   │   ├── account/              # Account Service (FastAPI)
│   │   │   ├── app/
│   │   │   │   ├── routers/
│   │   │   │   ├── schemas/
│   │   │   │   └── main.py
│   │   │   └── tests/
│   │   └── keys/                 # Key Service (FastAPI)
│   │       ├── app/
│   │       │   ├── routers/
│   │       │   ├── schemas/
│   │       │   └── main.py
│   │       └── tests/
│   ├── frontends/
│   │   └── web/                  # Main Angular SPA
│   │       └── src/app/
│   │           ├── components/
│   │           ├── services/
│   │           ├── models/
│   │           └── guards/
│   └── shared/                   # Shared Python modules
│       ├── models/               # SQLAlchemy models
│       ├── audit/                # Audit logging module
│       ├── rbac/                 # RBAC module
│       └── schemas/              # Shared Pydantic schemas
├── migrations/                   # Alembic migrations
└── docs/
```

### Shared Components

- **src/shared/models/**: SQLAlchemy models shared across services
- **shared/audit/**: Audit logging functions used by all services
- **shared/rbac/**: Role-based access control checks
- **shared/schemas/**: Common Pydantic schemas

### Testing Structure

- Backend: `services/<service>/tests/` using pytest
- Frontend: `frontend/src/app/**/*.spec.ts` using Jasmine/Karma
- Integration: TBD

## API Conventions

### Service Endpoints

**Auth Service (auth.keyarc.io)** - Public, unauthenticated:
- `POST /signup` - Create account
- `POST /login` - Authenticate, receive JWT
- `POST /password-reset` - Request password reset
- `POST /password-reset/confirm` - Confirm password reset
- `POST /token/refresh` - Refresh JWT token

**Gateway (api.keyarc.io)** - Public, requires JWT:
- `GET/POST/PUT/DELETE /account/*` → Routes to Account Service
- `GET/POST/PUT/DELETE /keys/*` → Routes to Key Service

**Account Service (via Gateway)** - Private:
- `GET /account/profile` - Get user profile
- `PUT /account/profile` - Update user profile
- `GET /account/teams` - List user's teams
- `POST /account/teams` - Create team
- `GET /account/teams/:id` - Get team details
- `POST /account/teams/:id/members` - Invite member
- `DELETE /account/teams/:id/members/:userId` - Remove member

**Key Service (via Gateway)** - Private:
- `GET /keys/secrets` - List secrets
- `POST /keys/secrets` - Create secret
- `GET /keys/secrets/:id` - Get secret
- `PUT /keys/secrets/:id` - Update secret
- `DELETE /keys/secrets/:id` - Delete secret
- `GET /keys/folders` - List folders
- `POST /keys/folders` - Create folder

[PLACEHOLDER] Exact endpoint paths will be refined during implementation.

### Error Handling

- Consistent error responses with status codes
- Generic messages that don't leak sensitive data
- Format: `{"detail": "Error message"}`

### Authentication

- JWT tokens in `Authorization: Bearer <token>` header
- Gateway validates JWT and adds user context headers
- Private services trust Gateway's user context headers

### Rate Limiting

- Auth endpoints: 5 attempts/minute per IP (using SlowAPI)
- API endpoints: Higher limits based on plan

### API Versioning

Expected: v1 prefix (e.g., `/v1/keys/secrets`) or version in headers

## Development Standards

### Python Code Style

- Lint and format with [ruff](https://docs.astral.sh/ruff/) (configured in root `pyproject.toml`)
- Type check with mypy
- Run `ruff check .` for linting, `ruff format .` for formatting

### TypeScript Code Style

- ESLint + Angular style guide
- Strict TypeScript settings

### Git Workflow

**Commit Message Format:**
Use [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages:

```
<type>(<scope>): <description> (#<issue-number>)

[optional body]

Closes #<issue-number>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**IMPORTANT:** Always include the issue number in the commit title (e.g., `feat(auth): add login endpoint (#42)`). This ensures PRs automatically link to issues since PR titles default to the commit message.

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`

Common scopes: `auth`, `gateway`, `account`, `keys`, `frontend`, `crypto`, `shared`

Examples:
- `docs: add PR template and contributing guide (#11)`
- `feat(keys): add folder organization for secrets (#42)`
- `fix(auth): correct token refresh timing (#15)`

**Branch Naming Convention:**
Format: `<type>/<issue-number>-<short-description>`

- Issue number MUST be included in branch name
- Use kebab-case for descriptions

Examples:
- `feat/42-add-folder-support`
- `fix/15-login-token-refresh`
- `docs/11-branch-protection-workflow`
- `chore/23-update-dependencies`

Types:
- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks
- `test/` - Test additions/changes

**Before Starting Work on an Issue:**
1. Checkout and pull main: `git checkout main && git pull`
2. Create branch with issue number: `git checkout -b <type>/<issue-number>-<description>`
3. Update project board status to "In Progress" (see GitHub Project Board Updates section)

**Pull Request Process:**
- PR title must follow conventional commit format (enforced by CI)
- All PRs require "Validate PR Title" status check to pass
- PRs are squash-merged to keep history clean
- Review threads must be resolved before merging

See `CONTRIBUTING.md` for detailed contributing guidelines.

[PLACEHOLDER] Code review checklist.
Expected: Security review checklist for crypto code, general review for other code

## References

**Existing Documentation:**
- Product documentation: `/docs/PRODUCT.md`
- Architecture documentation: `/docs/ARCHITECTURE.md`
- Deployment documentation: `/docs/DEPLOYMENT.md`

**Skills Documentation:**
- Zero-knowledge architecture: `.claude/skills/keyarc-zero-knowledge/SKILL.md`
- Cryptographic flows: `.claude/skills/keyarc-crypto-flows/SKILL.md`
- API security: `.claude/skills/keyarc-api-security/SKILL.md`
- GitHub issues: `.claude/skills/github-issues/SKILL.md`
- GitHub PRs: `.claude/skills/github-prs/SKILL.md`

**Future Documentation:**
[PLACEHOLDER] API documentation (OpenAPI/Swagger) will be generated

[PLACEHOLDER] Frontend component library documentation

[PLACEHOLDER] Database schema documentation

[PLACEHOLDER] Deployment runbook

## Key Features (from Product Docs)

1. **Secure Client-Side Encryption** - Zero-knowledge architecture
2. **Expiry Tracking & Rotation Reminders** - Track certificate/key expiration
3. **Client-Side API Validity Testing** - Test if keys still work
4. **Organization & Structure** - Folders, tags, environments
5. **Team Sharing with RBAC** - Share secrets securely with role-based access
6. **Comprehensive Audit Logging** - Track who accessed what and when

## What's Out of Scope for v1

- Browser extensions, desktop apps, mobile apps
- IDE plugins
- Import/export functionality
- Automatic key rotation
- External service integrations (beyond basic API testing)
- Self-hosted deployment
- SSO/SAML authentication
- Compliance certifications

## Development Workflow

1. **Plan first** - Use planning skill for complex features
2. **TDD** - Write tests before implementation
3. **Security review** - All crypto code requires review
4. **Audit logging** - Every secret access must be logged
5. **Zero-knowledge enforcement** - Use KeyArc security skills
6. **Update project board** - When starting work on GitHub issues, update status on the project board

### Creating New Issues

When creating new GitHub issues, follow the complete workflow in `.claude/skills/github-issues/SKILL.md`:
1. Create issue with milestone and labels via `gh issue create`
2. Add to project board via `gh project item-add`
3. Set project fields (status, phase, track) via GraphQL mutations

### Handling PR Feedback (Agents)

When responding to PR comments or review feedback, follow `.claude/skills/github-prs/SKILL.md`:
- Always identify yourself as an AI agent in PR comments
- Use MCP GitHub tools (`mcp__github__*`) for PR operations when available
- Acknowledge all feedback with a response

### GitHub Project Board Updates

When working on GitHub issues, update the project board status. **Note:** Only move issues to "In Progress" or "Ready" - never mark issues as "Done" (that's for manual review).

**Starting work on an issue:**
```bash
# Get the project item ID for the issue
gh project item-list 1 --owner KeyArc --format json | jq '.items[] | select(.content.number == ISSUE_NUMBER) | .id'

# Update status to "In Progress"
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDODzuJ-c4BNYGm"
    itemId: "ITEM_ID"
    fieldId: "PVTSSF_lADODzuJ-c4BNYGmzg8Y71s"
    value: {singleSelectOptionId: "b3644764"}
  }) { projectV2Item { id } }
}'
```

**Unblocking an issue (moving to Ready):**
```bash
# Update status to "Ready" when dependencies are resolved
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDODzuJ-c4BNYGm"
    itemId: "ITEM_ID"
    fieldId: "PVTSSF_lADODzuJ-c4BNYGmzg8Y71s"
    value: {singleSelectOptionId: "e5dd8d9b"}
  }) { projectV2Item { id } }
}'
```

**Status option IDs:**
- Ready: `e5dd8d9b`
- Blocked: `a149a0a4`
- In Progress: `b3644764`
- In Review: `9a932cb4`
- Done: `f3192413` (manual only - do not use programmatically)

**Phase option IDs:**
- Phase 1: Foundation: `acaef4ee`
- Phase 2: Authentication: `205962fc`

**Track option IDs:**
- Dev: `e916e7bd`
- DevOps: `8612f72a`
- QA: `a28706f5`

**Project reference:**
- Project ID: `PVT_kwDODzuJ-c4BNYGm`
- Status field ID: `PVTSSF_lADODzuJ-c4BNYGmzg8Y71s`
- Phase field ID: `PVTSSF_lADODzuJ-c4BNYGmzg8Y8FI`
- Track field ID: `PVTSSF_lADODzuJ-c4BNYGmzg8Y8FM`
- Project URL: https://github.com/orgs/KeyArc/projects/1

## Quick Start (When Codebase Exists)

[PLACEHOLDER] Local development setup instructions will be added.

Expected:
```bash
# Backend
docker-compose up -d  # Start PostgreSQL
cd backend
pip install -e .[dev]
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
ng serve
```

[PLACEHOLDER] Environment variables configuration.

Expected: `.env` files for backend with `DATABASE_URL`, `SECRET_KEY`, etc.

## Deployment

[PLACEHOLDER] Deployment procedures will be documented.

Expected: Fly.io deployment with GitHub Actions CI/CD

## Contact & Support

[PLACEHOLDER] Team contact information
[PLACEHOLDER] Support channels

---

**Remember:** The server must be able to operate with ZERO KNOWLEDGE of user secrets. This is the foundational principle that drives every architectural decision in KeyArc.
