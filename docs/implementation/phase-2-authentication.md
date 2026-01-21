# Phase 2: Authentication Flows

**Goal**: Implement the complete authentication system including client-side cryptography, Auth Service, Gateway, and frontend auth UI.

**Dependencies**: Phase 1 complete (project scaffolding, shared modules, test frameworks)

**Task Summary**:
| Track | Tasks | IDs |
|-------|-------|-----|
| Dev | 4 | DEV-2.1 through DEV-2.4 |
| DevOps | 1 | DEVOPS-2.1 |
| QA | 6 | QA-2.1 through QA-2.6 |

---

## Dev Tasks

### DEV-2.1: Frontend Crypto Module

Implement client-side cryptographic operations using WebCrypto API.

**Scope**:
- Argon2 key derivation:
  - `deriveMasterKey(password, email)` - returns CryptoKey
  - Parameters: Argon2id, time=3, mem=64MB, parallelism=4, hashLen=32
  - Use `argon2-browser` library (WebAssembly)
- AES-256-GCM encryption:
  - `encryptWithKey(plaintext, key)` - returns base64 ciphertext
  - `decryptWithKey(ciphertext, key)` - returns plaintext
  - Random 12-byte IV per encryption
- RSA-OAEP keypair:
  - `generateKeyPair()` - returns { publicKey, privateKey }
  - 2048-bit, SHA-256 hash
  - `encryptWithPublicKey(data, publicKey)`
  - `decryptWithPrivateKey(ciphertext, privateKey)`
- Auth hash computation:
  - `computeAuthHash(masterKey)` - PBKDF2-SHA256, 100k iterations
- Vault key operations:
  - `generateVaultKey()` - random AES-256 key
  - `encryptVaultKey(vaultKey, masterKey)`
  - `decryptVaultKey(encryptedVaultKey, masterKey)`

**Acceptance Criteria**:
- [ ] All crypto functions implemented using WebCrypto API
- [ ] Argon2 produces deterministic output for same inputs
- [ ] Encrypt/decrypt round-trip preserves data
- [ ] Wrong key fails decryption with appropriate error
- [ ] Keys are non-extractable where appropriate
- [ ] Unit tests for all crypto functions

**Security Requirements**:
- Master password never leaves the crypto module
- Keys stored only in memory, never persisted
- Clear keys from memory when session ends

---

### DEV-2.2: Auth Service Implementation

Implement authentication endpoints in the Auth Service.

**Scope**:
- `POST /signup`:
  - Request: email, auth_hash, encrypted_vault_key, encrypted_private_key, public_key
  - Validate email format and uniqueness
  - Store user with encrypted keys
  - Return: user_id, created_at
- `POST /login`:
  - Request: email, auth_hash
  - Validate auth_hash matches stored value
  - Generate JWT token (sub=user_id, exp=2 hours)
  - Return: access_token, token_type, encrypted_vault_key, encrypted_private_key, public_key
- `POST /token/refresh`:
  - Request: valid JWT (not expired or within grace period)
  - Return: new access_token
- Rate limiting:
  - Login: 5 attempts per minute per IP (SlowAPI)
  - Signup: 10 attempts per minute per IP
- Audit logging:
  - Log successful and failed login attempts
  - Log signup events

**Acceptance Criteria**:
- [ ] Signup creates user with encrypted keys
- [ ] Signup rejects duplicate email with 409
- [ ] Login validates auth_hash correctly
- [ ] Login returns JWT and encrypted keys
- [ ] Invalid auth_hash returns 401 (generic message)
- [ ] Rate limiting triggers after threshold
- [ ] JWT contains correct claims (sub, exp)
- [ ] Token refresh works within validity period
- [ ] Audit logs created for all auth events

**Security Requirements**:
- Never accept or validate passwords (only auth_hash)
- Error messages don't reveal whether email exists
- JWT secret from environment variable

---

### DEV-2.3: Gateway Service Implementation

Implement the API Gateway for JWT validation and routing.

**Scope**:
- JWT validation middleware:
  - Extract Bearer token from Authorization header
  - Validate signature and expiration
  - Extract user_id from token
- Request routing:
  - `/account/*` → Account Service (account.flycast in prod, localhost:X in dev)
  - `/keys/*` → Key Service (keys.flycast in prod, localhost:Y in dev)
- User context headers:
  - Add `X-User-ID` header to forwarded requests
  - Add `X-User-Email` header if available
- Error handling:
  - 401 for missing/invalid token
  - 502 for downstream service errors

**Acceptance Criteria**:
- [ ] Valid JWT passes through to downstream service
- [ ] Invalid JWT returns 401
- [ ] Expired JWT returns 401
- [ ] Missing Authorization header returns 401
- [ ] User context headers added to forwarded requests
- [ ] Routes correctly forward to account/keys services
- [ ] Downstream errors return appropriate status

**Security Requirements**:
- Gateway is stateless (no database connection)
- JWT secret matches Auth Service
- Private services only accessible through Gateway

---

### DEV-2.4: Frontend Auth UI & State Management

Implement authentication UI and state management in Angular.

**Scope**:
- Auth service (Angular):
  - `signup(email, password)` - orchestrates crypto + API call
  - `login(email, password)` - orchestrates crypto + API call
  - `logout()` - clears keys from memory
  - `isAuthenticated$` - observable for auth state
- Signup component:
  - Email and password form with validation
  - Password strength indicator
  - Confirm password field
  - Show loading state during key derivation
  - Handle success (redirect to dashboard)
  - Handle errors (display message)
- Login component:
  - Email and password form
  - Show loading state during key derivation
  - Handle success (store token, decrypt keys, redirect)
  - Handle errors (display message)
- Auth state management:
  - Store JWT in memory (not localStorage for security)
  - Store decrypted vaultKey and privateKey in memory
  - Provide keys to other services via DI
- HTTP interceptor:
  - Add Authorization header to API requests
  - Handle 401 responses (redirect to login)
- Route guards:
  - `AuthGuard` - redirect to login if not authenticated
  - `GuestGuard` - redirect to dashboard if authenticated

**Acceptance Criteria**:
- [ ] Signup form validates input
- [ ] Signup derives keys and calls API
- [ ] Login form validates input
- [ ] Login decrypts keys on success
- [ ] JWT added to API requests automatically
- [ ] 401 response triggers logout and redirect
- [ ] Protected routes redirect to login
- [ ] Auth state persists during session (memory only)
- [ ] Logout clears all sensitive data

**Security Requirements**:
- Password never stored or transmitted
- Keys exist only in memory during session
- Clear all sensitive data on logout

---

## DevOps Tasks

### DEVOPS-2.1: Add Test Stage to CI Pipeline

Expand CI to run tests for all services.

**Scope**:
- Run Pytest for each backend service
- Run Angular tests
- Parallel job execution where possible
- Test database setup in CI (PostgreSQL service container)
- Environment variables for test configuration

**Acceptance Criteria**:
- [ ] All backend service tests run in CI
- [ ] Frontend tests run in CI
- [ ] Tests use isolated database
- [ ] Jobs run in parallel where possible
- [ ] Test results visible in PR checks

---

## QA Tasks

### QA-2.1: Auth Service API Tests - Signup

Write API tests for the signup endpoint.

**Scope**:
- Test: Signup with valid data returns 201 and user_id
- Test: Signup with duplicate email returns 409
- Test: Signup with invalid email format returns 422
- Test: Signup with missing fields returns 422
- Test: Signup stores encrypted keys (verify in DB)
- Test: Signup creates audit log entry

**Acceptance Criteria**:
- [ ] All test cases implemented
- [ ] Tests are independent (no shared state)
- [ ] Tests clean up test data
- [ ] Tests run in CI

**Learning Objectives**:
- API testing with pytest and httpx
- Database assertions
- Test data management

---

### QA-2.2: Auth Service API Tests - Login

Write API tests for the login endpoint.

**Scope**:
- Test: Login with correct auth_hash returns JWT and encrypted keys
- Test: Login with wrong auth_hash returns 401
- Test: Login with non-existent email returns 401 (same error)
- Test: Login creates audit log entry
- Test: JWT contains correct user_id claim
- Test: JWT expires after configured duration

**Acceptance Criteria**:
- [ ] All test cases implemented
- [ ] JWT parsing and validation in tests
- [ ] Error responses don't leak information

**Learning Objectives**:
- JWT token testing
- Security-focused test cases
- Information leakage testing

---

### QA-2.3: Auth Service API Tests - Rate Limiting

Write API tests for rate limiting behavior.

**Scope**:
- Test: 5th login attempt within minute returns 429
- Test: Rate limit resets after window expires
- Test: Different IPs have separate limits
- Test: Signup has separate rate limit

**Acceptance Criteria**:
- [ ] Rate limiting tests pass
- [ ] Tests handle timing appropriately

**Learning Objectives**:
- Testing rate-limited endpoints
- Time-sensitive test strategies

---

### QA-2.4: Crypto Module Unit Tests

Write unit tests for frontend cryptographic operations.

**Scope**:
- Test: `deriveMasterKey` is deterministic (same password + email = same key)
- Test: `deriveMasterKey` differs for different passwords
- Test: `deriveMasterKey` differs for different emails (salt)
- Test: Encrypt/decrypt round-trip preserves data
- Test: Decryption with wrong key throws error
- Test: Each encryption produces different ciphertext (random IV)
- Test: RSA keypair encrypt/decrypt round-trip works
- Test: Auth hash is deterministic for same master key

**Acceptance Criteria**:
- [ ] All crypto functions have test coverage
- [ ] Tests verify security properties
- [ ] Tests run in browser environment (Karma)

**Learning Objectives**:
- Testing cryptographic code
- Property-based testing concepts
- Browser-based unit testing

---

### QA-2.5: E2E Tests - Signup Flow

Write E2E tests for the signup user journey.

**Scope**:
- Test: User can navigate to signup page
- Test: User can fill form and submit
- Test: Success redirects to dashboard
- Test: Duplicate email shows error
- Test: Invalid password shows validation error

**Acceptance Criteria**:
- [ ] E2E tests cover happy path
- [ ] E2E tests cover common error cases
- [ ] Tests are stable (no flakiness)

**Learning Objectives**:
- E2E test structure
- Handling async operations in E2E
- Form interaction testing

---

### QA-2.6: E2E Tests - Login Flow

Write E2E tests for the login user journey.

**Scope**:
- Test: User can navigate to login page
- Test: User can login with valid credentials
- Test: Success redirects to dashboard
- Test: Wrong password shows error
- Test: User can logout

**Acceptance Criteria**:
- [ ] E2E tests cover happy path
- [ ] E2E tests cover error cases
- [ ] Tests are independent (each creates own user)

**Learning Objectives**:
- Test data setup in E2E tests
- State management testing
- Session testing

---

## Phase Completion Checklist

Before moving to Phase 3:

- [ ] Frontend crypto module complete with all operations
- [ ] Auth Service handles signup, login, token refresh
- [ ] Gateway validates JWTs and routes requests
- [ ] Frontend auth UI complete with forms and guards
- [ ] Rate limiting active on auth endpoints
- [ ] All auth-related tests passing
- [ ] E2E tests for signup and login flows
- [ ] Audit logging for all auth events

**Previous Phase**: [Phase 1: Foundation](./phase-1-foundation.md)
**Next Phase**: [Phase 3: Secrets Management](./phase-3-secrets.md)
