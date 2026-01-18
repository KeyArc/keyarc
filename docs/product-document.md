# KeyArc: API Key & Certificate Manager

## Product Overview

KeyArc is a secure, zero-knowledge API key and certificate manager designed for solo developers and small teams. It combines the security model of modern password managers with features tailored specifically for managing API credentials, certificates, and other secrets that developers and businesses rely on daily.

The core value proposition is simple: store your API keys and certificates securely, get reminded before they expire, verify they still work, and share them safely with your team—all without the server ever seeing your plaintext secrets.

---

## Target Users

- Solo developers managing personal projects and client work
- Small teams and startups who need shared access to credentials
- Small businesses with multiple departments needing organized secret management
- Anyone who finds enterprise solutions like HashiCorp Vault overkill for their needs

---

## Core Features

### Secure Storage with Client-Side Encryption
- All secrets are encrypted in the browser before being sent to the server
- The server only ever stores encrypted (ciphertext) secrets—never plaintext or master passwords
- The server cannot decrypt user data at any time; only the client can decrypt secrets
- Based on Bitwarden's proven encryption model
- User only needs to remember a single master password

### Expiry Tracking & Rotation Reminders
- Track expiration dates for certificates and time-limited API keys
- User-entered expiry dates or parsed client-side from certificate files
- Configurable rotation reminders (e.g., "remind me to rotate after 90 days")
- Dashboard view of upcoming expirations

### Client-Side Validity Testing
- Optional feature to test if an API key still works
- Tests executed from the browser, secrets never transit through our servers
- Support for common API patterns (REST endpoints, bearer tokens, etc.)

### Organization & Structure
- Folders for hierarchical organization
- Tags for flexible categorization
- Environment labels (production, staging, development, etc.)
- Search and filtering across all organizational dimensions

### Team Sharing
- Share secrets with team members without exposing plaintext to the server
- Role-based access (owner, admin, member)
- Users maintain both personal vaults and team vaults
- Adding/removing team members handled through public key cryptography

### Audit Logging
- Track who accessed which secrets and when
- Action history: view, create, update, delete, share
- Essential for team accountability and security reviews

---

## Development Environment Support

KeyArc is designed for a flexible, modern development workflow:

- **Supported OS for development:**
  - macOS (Apple Silicon/ARM)
  - Windows (x86/x64)
- **Development tooling:**
  - Docker Desktop (for both macOS and Windows)
  - All containers run Linux (ARM or x86), matching production
- **Recommended editors:**
  - Visual Studio Code
  - Claude Code

This setup ensures that developers on both Mac and Windows can contribute seamlessly, with consistent containerized environments and cross-platform tooling.

---

## Key Technical Decisions

### Backend Framework Choice

KeyArc uses **FastAPI** as the backend framework. FastAPI was chosen for its modern async support, automatic OpenAPI documentation, strong performance, and excellent developer experience. Flask and Django were considered, but FastAPI best fits the needs of a secure, API-first, async-enabled product.

#### Authentication & Zero-Knowledge Model (detailed)

KeyArc uses a Bitwarden-style authentication and encryption model, implemented with FastAPI:

- **Signup:**
	- User enters email and master password in the browser.
	- Browser derives a `masterKey` using Argon2 (password + email as salt).
	- Browser generates a random `vaultKey` (AES-256) to encrypt all secrets.
	- `vaultKey` is encrypted with the `masterKey` and stored on the server.
	- Browser generates a public/private keypair for sharing; private key is encrypted with the `masterKey` and stored on the server.
	- Browser computes an `authHash` (hash of the `masterKey`) and sends it to the server along with other encrypted keys.

- **Login:**
	- User enters email and master password in the browser.
	- Browser derives the `masterKey` and computes `authHash`.
	- Browser sends `authHash` to the server (never the password or masterKey).
	- FastAPI validates `authHash` against the stored value and issues a JWT token.
	- Server returns encrypted vault key and private key.
	- Browser uses `masterKey` to decrypt vault key and private key locally.

- **API Usage:**
	- All further API requests use the JWT for authentication.
	- All secret data sent to or from the API is always encrypted; server never sees plaintext secrets or user master password.

**Security tradeoff:** If a user forgets their master password, their data is unrecoverable. This is the standard tradeoff for true zero-knowledge systems.

We chose to follow Bitwarden's encryption architecture because it is battle-tested, well-documented, and provides true zero-knowledge security.

**How it works:**

1. User's master password is used to derive a `masterKey` via Argon2 (with email as salt)
2. A random symmetric `vaultKey` encrypts all personal secrets
3. The `vaultKey` is encrypted with the `masterKey` and stored on the server
4. A public/private keypair is generated for sharing purposes
5. The private key is encrypted with the `masterKey` and stored on the server
6. Authentication uses a hash of the `masterKey`, not the key itself

**Sharing mechanism:**

- Each team has a symmetric `teamKey` that encrypts team secrets
- When a user joins a team, the `teamKey` is encrypted to their public key
- Users can decrypt the `teamKey` with their private key (which they decrypt with their `masterKey`)
- Result: seamless sharing without the server ever seeing plaintext

**Tradeoff:** If a user forgets their master password, their data is unrecoverable. This is the standard tradeoff for zero-knowledge systems. A recovery key feature could be added later.

### Storage Model

We store the actual encrypted secrets, not just metadata. This makes the product a true credential manager rather than just a reminder service. Users can retrieve their keys when needed.

### Client-Side Operations

The following operations happen exclusively in the browser:
- All encryption and decryption
- Parsing certificate files to extract expiry dates
- API validity testing
- Key derivation from master password

This ensures that secrets are always stored encrypted on the server, minimizing server-side liability and maintaining the zero-knowledge guarantee.

### No External Integrations (v1)

For the initial version, we are not building:
- Browser extensions
- Desktop agents
- IDE plugins
- Syncing with external secret managers (AWS Secrets Manager, etc.)
- Import from other tools

The product is a standalone web application with a backend API and frontend client. Integrations may be added later but are explicitly out of scope for v1 to avoid scope creep.

### No Key Rotation Automation

The product will suggest when to rotate keys and remind users, but will not automatically rotate keys. Automatic rotation would require building integrations to every provider (AWS, Stripe, GitHub, etc.), which adds significant complexity and maintenance burden.

### Multi-Tenant SaaS Only

No self-hosted or on-premise deployment option. This simplifies operations and focuses development effort on a single deployment model.

---

## Data Model

### users
| Field                  | Type      | Description                           |
|------------------------|-----------|---------------------------------------|
| id                     | uuid      | Primary key                           |
| email                  | string    | User email, unique                    |
| auth_hash              | string    | Hash of master key for authentication |
| encrypted_vault_key    | blob      | Vault key encrypted with master key   |
| public_key             | blob      | Public key for sharing                |
| encrypted_private_key  | blob      | Private key encrypted with master key |
| created_at             | timestamp | Account creation time                 |

### secrets
| Field                   | Type      | Description                                       |
|-------------------------|-----------|---------------------------------------------------|
| id                      | uuid      | Primary key                                       |
| owner_type              | enum      | 'user' or 'team'                                  |
| owner_id                | uuid      | References user or team                           |
| name                    | string    | Display name                                      |
| encrypted_value         | blob      | The encrypted secret                              |
| type                    | enum      | 'api_key', 'cert', 'other'                        |
| expires_at              | timestamp | Nullable, expiration date                         |
| rotation_reminder_days  | integer   | Nullable, days after which to suggest rotation    |
| environment             | string    | Nullable (e.g., 'production', 'staging')          |
| folder_id               | uuid      | Nullable, references folder                       |
| tags                    | array     | List of tag strings                               |
| created_at              | timestamp | Creation time                                     |
| updated_at              | timestamp | Last modification time                            |

### teams
| Field      | Type      | Description       |
|------------|-----------|-------------------|
| id         | uuid      | Primary key       |
| name       | string    | Team display name |
| created_at | timestamp | Creation time     |

### team_memberships
| Field               | Type      | Description                              |
|---------------------|-----------|------------------------------------------|
| id                  | uuid      | Primary key                              |
| team_id             | uuid      | References team                          |
| user_id             | uuid      | References user                          |
| encrypted_team_key  | blob      | Team key encrypted to user's public key  |
| role                | enum      | 'owner', 'admin', 'member'               |
| created_at          | timestamp | When user joined team                    |

### folders
| Field             | Type   | Description               |
|-------------------|--------|---------------------------|
| id                | uuid   | Primary key               |
| owner_type        | enum   | 'user' or 'team'          |
| owner_id          | uuid   | References user or team   |
| name              | string | Folder name               |
| parent_folder_id  | uuid   | Nullable, for nesting     |

### audit_log
| Field     | Type      | Description                                      |
|-----------|-----------|--------------------------------------------------|
| id        | uuid      | Primary key                                      |
| user_id   | uuid      | Who performed the action                         |
| secret_id | uuid      | Which secret was accessed                        |
| action    | enum      | 'view', 'create', 'update', 'delete', 'share'    |
| timestamp | timestamp | When it happened                                 |
| ip_address| string    | Optional, client IP                              |

---

## Crypto Flow Reference

### Signup
1. User enters email + master password
2. Client derives `masterKey` = Argon2(password, email)
3. Client generates random `vaultKey` (AES-256)
4. Client computes `encryptedVaultKey` = encrypt(vaultKey, masterKey)
5. Client generates keypair (publicKey, privateKey)
6. Client computes `encryptedPrivateKey` = encrypt(privateKey, masterKey)
7. Client computes `authHash` = hash(masterKey)
8. Send to server: email, authHash, encryptedVaultKey, publicKey, encryptedPrivateKey

### Login
1. User enters email + master password
2. Client derives `masterKey`, computes `authHash`
3. Server validates authHash, returns encrypted keys
4. Client decrypts vaultKey and privateKey, holds in memory

### Store Personal Secret
1. Client encrypts secret with vaultKey
2. Send ciphertext + metadata to server

### Create Team
1. Client generates random `teamKey` (AES-256)
2. Client encrypts teamKey with creator's publicKey
3. Server stores team + membership record

### Invite to Team
1. Inviter's client decrypts teamKey
2. Client fetches invitee's publicKey from server
3. Client encrypts teamKey with invitee's publicKey
4. Server stores new membership record

### Store Team Secret
1. Client decrypts teamKey
2. Client encrypts secret with teamKey
3. Send ciphertext + metadata to server

---

## What's Explicitly Out of Scope for v1

- Browser extensions
- Desktop applications
- Mobile applications
- IDE plugins
- Import/export functionality
- Automatic key rotation
- Integration with external secret managers
- Self-hosted deployment option
- SSO/SAML authentication
- Compliance certifications (SOC2, HIPAA, etc.)

These may be revisited for future versions based on user feedback and business needs.

---

## Open Questions for Development Phase

1. **Backend framework** — FastAPI vs Flask vs Django for Python 3.14+ backend
2. **Frontend framework** — Angular (TypeScript), LTS (Angular 20)
3. **Specific cryptographic libraries** — Which implementations of Argon2, AES, RSA/ECC to use client-side
4. **Python crypto libraries** — `cryptography` vs PyNaCl for server-side validation and key handling
5. **ORM choice** — SQLAlchemy vs Django ORM vs Tortoise ORM
6. **MVP feature prioritization** — Exact scope for first usable version

---

## Summary

KeyArc addresses a real gap: developers and small teams need a simple, secure way to manage API keys and certificates without enterprise complexity or trusting a server with their plaintext secrets. By following Bitwarden's proven encryption model and focusing on the specific needs of credential management (expiry tracking, validity testing, rotation reminders), we can deliver a focused product that does one thing well.
