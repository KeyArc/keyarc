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

KeyArc follows a "not too micro" microservices approach with clear service boundaries.

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
├── frontend/                 # Angular SPA
│   └── src/app/
│       ├── components/
│       ├── services/
│       ├── models/
│       └── guards/
├── services/
│   ├── auth/                 # Auth Service (FastAPI)
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   ├── schemas/
│   │   │   └── main.py
│   │   └── tests/
│   ├── gateway/              # Gateway Service (FastAPI/Starlette)
│   │   ├── app/
│   │   │   ├── routing.py
│   │   │   └── main.py
│   │   └── tests/
│   ├── account/              # Account Service (FastAPI)
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   ├── schemas/
│   │   │   └── main.py
│   │   └── tests/
│   └── keys/                 # Key Service (FastAPI)
│       ├── app/
│       │   ├── routers/
│       │   ├── schemas/
│       │   └── main.py
│       └── tests/
├── shared/                   # Shared modules
│   ├── models/               # SQLAlchemy models
│   ├── audit/                # Audit logging module
│   ├── rbac/                 # RBAC module
│   └── schemas/              # Shared Pydantic schemas
├── migrations/               # Alembic migrations
└── docs/
```

[PLACEHOLDER] Exact structure will be refined during implementation.

### Shared Components

- **shared/models/**: SQLAlchemy models shared across services
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

[PLACEHOLDER] Python code style will be defined.
Expected: Black formatting, isort for imports, pylint for linting

[PLACEHOLDER] TypeScript code style will be defined.
Expected: ESLint + Prettier, Angular style guide

[PLACEHOLDER] Git commit message format.
Expected: Conventional Commits (feat:, fix:, docs:, etc.)

[PLACEHOLDER] Branch naming convention.
Expected: feature/, bugfix/, hotfix/ prefixes

[PLACEHOLDER] Pull request template.

[PLACEHOLDER] Code review checklist.
Expected: Security review checklist for crypto code, general review for other code

## References

**Existing Documentation:**
- Product documentation: `/docs/product-document.md`
- Infrastructure documentation: `/docs/infrastructure.md`

**Skills Documentation:**
- Zero-knowledge architecture: `.claude/skills/keyarc-zero-knowledge/SKILL.md`
- Cryptographic flows: `.claude/skills/keyarc-crypto-flows/SKILL.md`
- API security: `.claude/skills/keyarc-api-security/SKILL.md`

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
