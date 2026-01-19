# KeyArc: Architecture

## Service Architecture

KeyArc uses a "not too micro" microservices approach with clear service boundaries.

```
┌─────────────────────────────────────────────────────────────────────┐
│                              Fly.io                                 │
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

### Services

| Service | Visibility | URL | Purpose |
|---------|------------|-----|---------|
| **Frontend** | Public | keyarc.io | Angular SPA |
| **Auth Service** | Public | auth.keyarc.io | Signup, login, password reset, tokens |
| **Gateway** | Public | api.keyarc.io | JWT validation, routing |
| **Account Service** | Private | account.flycast | User profiles, teams, memberships |
| **Key Service** | Private | keys.flycast | Encrypted secrets, folders, tags |

### Service Responsibilities

**Auth Service** - Handles unauthenticated flows, issues JWTs, future OAuth callbacks

**Gateway** - Thin, stateless proxy that validates JWTs and routes to private services

**Account Service** - User/team management, uses shared RBAC module

**Key Service** - Encrypted secret storage, expiry tracking (on-demand), uses shared RBAC module

### Shared Modules

- **Audit Logging** - Writes to shared audit_log table
- **RBAC** - Checks team role permissions (owner, admin, member)

## Zero-Knowledge Model

**Core principle:** The server can never decrypt user data.

### What the Server Stores
- Encrypted vault key (encrypted with user's master key)
- Encrypted private key (encrypted with user's master key)
- Public key (for sharing)
- Auth hash (for login validation)
- Encrypted secrets (ciphertext only)

### What the Server Never Sees
- Master password
- Master key
- Decrypted vault key
- Decrypted private key
- Plaintext secrets

### Crypto Flows

**Signup:**
1. Client derives `masterKey` = Argon2(password, email)
2. Client generates random `vaultKey` (AES-256)
3. Client generates keypair (publicKey, privateKey)
4. Client encrypts vaultKey and privateKey with masterKey
5. Client computes `authHash` = hash(masterKey)
6. Send to server: email, authHash, encryptedVaultKey, publicKey, encryptedPrivateKey

**Login:**
1. Client derives masterKey, computes authHash
2. Server validates authHash, returns encrypted keys
3. Client decrypts vaultKey and privateKey locally

**Team Sharing:**
1. Team has a symmetric `teamKey` that encrypts team secrets
2. Each member gets `teamKey` encrypted with their public key
3. Server stores N encrypted copies, can't decrypt any

## Data Model

### users
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| email | string | Unique |
| auth_hash | string | Hash of master key |
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
| name | string | Display name |
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

## Tech Stack

**Backend:**
- Python 3.13+
- FastAPI
- SQLAlchemy + asyncpg
- Alembic (migrations)
- PyJWT

**Frontend:**
- Angular 20
- TypeScript
- WebCrypto API

**Cryptography:**
- Argon2id (key derivation)
- AES-256-GCM (symmetric encryption)
- RSA-OAEP (asymmetric encryption for sharing)
