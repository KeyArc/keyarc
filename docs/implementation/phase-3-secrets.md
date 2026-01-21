# Phase 3: Secrets Management

**Goal**: Implement the Key Service for encrypted secret storage, organization features, and the frontend vault UI.

**Dependencies**: Phase 2 complete (authentication working, JWT validation, crypto module)

**Task Summary**:
| Track | Tasks | IDs |
|-------|-------|-----|
| Dev | 4 | DEV-3.1 through DEV-3.4 |
| DevOps | 1 | DEVOPS-3.1 |
| QA | 7 | QA-3.1 through QA-3.7 |

---

## Dev Tasks

### DEV-3.1: Key Service - Secret CRUD

Implement core secret management endpoints.

**Scope**:
- `GET /keys/secrets`:
  - List secrets owned by current user
  - Support filtering by folder_id, tags, environment
  - Return encrypted_value (client decrypts)
  - Pagination support
- `POST /keys/secrets`:
  - Request: name, encrypted_value, type, expires_at, rotation_reminder_days, environment, folder_id, tags
  - Validate encrypted_value is base64 ciphertext
  - Create audit log entry (action: create)
  - Return created secret
- `GET /keys/secrets/:id`:
  - Return secret if owned by current user
  - Create audit log entry (action: view)
  - 404 if not found or not owned (same response)
- `PUT /keys/secrets/:id`:
  - Update allowed fields
  - Validate ownership
  - Create audit log entry (action: update)
- `DELETE /keys/secrets/:id`:
  - Soft delete or hard delete (decide)
  - Validate ownership
  - Create audit log entry (action: delete)

**Acceptance Criteria**:
- [ ] CRUD operations work correctly
- [ ] Only owner can access their secrets
- [ ] Non-owner gets 404 (not 403) to prevent enumeration
- [ ] Encrypted payload validation rejects plaintext
- [ ] Audit logs created for all operations
- [ ] Filtering and pagination work

**Security Requirements**:
- User context from Gateway headers (X-User-ID)
- Never log encrypted_value contents
- Validate ciphertext format before storing

---

### DEV-3.2: Key Service - Folders & Organization

Implement folder and organization features.

**Scope**:
- `GET /keys/folders`:
  - List folders owned by current user
  - Include nested structure
- `POST /keys/folders`:
  - Create folder with name and optional parent_folder_id
  - Validate parent exists and is owned by user
- `PUT /keys/folders/:id`:
  - Update folder name or parent
  - Prevent circular references
- `DELETE /keys/folders/:id`:
  - Delete folder
  - Decide: cascade delete secrets or move to root?
- Tags:
  - Stored as array on secret
  - No separate tag management (inline with secrets)
- Environment:
  - String field (production, staging, development, or custom)
  - Filter support in list endpoint

**Acceptance Criteria**:
- [ ] Folder CRUD works
- [ ] Nested folders supported
- [ ] Secrets can be assigned to folders
- [ ] Circular folder references prevented
- [ ] Tags stored and queryable
- [ ] Environment filter works

---

### DEV-3.3: Key Service - Expiry Tracking

Implement expiration tracking for secrets.

**Scope**:
- Expiry fields on secrets:
  - `expires_at` - timestamp when secret expires
  - `rotation_reminder_days` - days before expiry to remind
- Query endpoint for expiring secrets:
  - `GET /keys/secrets/expiring?days=30`
  - Returns secrets expiring within N days
  - Computed on-demand (no background workers)
- Response includes:
  - Days until expiry
  - Whether reminder threshold passed

**Acceptance Criteria**:
- [ ] Secrets can have expiry dates
- [ ] Expiring secrets query works
- [ ] Reminder threshold calculated correctly
- [ ] Null expiry handled (never expires)

---

### DEV-3.4: Frontend Vault UI

Implement the secret management interface.

**Scope**:
- Secret list view:
  - Display secrets in folder hierarchy
  - Show name, type, environment, tags, expiry status
  - Click to view/edit
  - Search and filter
- Create secret form:
  - Name, value, type selector
  - Folder selector
  - Tags input
  - Expiry date picker
  - Rotation reminder days
  - Environment selector
  - Encrypt value before submission
- View/edit secret:
  - Decrypt and display value
  - Copy to clipboard
  - Edit fields
  - Delete confirmation
- Folder management:
  - Create/rename/delete folders
  - Drag-drop organization (optional, can defer)
- Expiry indicators:
  - Visual warning for expiring secrets
  - Expiring soon badge

**Acceptance Criteria**:
- [ ] Secrets display in list
- [ ] Create secret encrypts before save
- [ ] View secret decrypts for display
- [ ] Edit secret re-encrypts on save
- [ ] Delete requires confirmation
- [ ] Folder hierarchy displays correctly
- [ ] Search filters work
- [ ] Expiry warnings display

**Security Requirements**:
- Decrypted values only shown when explicitly requested
- Clear clipboard after timeout
- Don't log decrypted values

---

## DevOps Tasks

### DEVOPS-3.1: Code Coverage Reporting

Add code coverage reporting to CI.

**Scope**:
- Backend: pytest-cov with coverage report
- Frontend: Karma coverage reporter
- Upload coverage to artifact or service (Codecov optional)
- Display coverage badge in README
- Set minimum coverage thresholds (e.g., 70%)

**Acceptance Criteria**:
- [ ] Coverage reports generated in CI
- [ ] Coverage visible in PR comments or checks
- [ ] Coverage thresholds enforced (warnings initially, then failures)

---

## QA Tasks

### QA-3.1: Key Service API Tests - Create Secret

Write API tests for secret creation.

**Scope**:
- Test: Create secret with valid encrypted payload succeeds
- Test: Create secret with plaintext (non-base64) returns 400
- Test: Create secret with missing name returns 422
- Test: Created secret returned in response
- Test: Audit log created with action 'create'

**Acceptance Criteria**:
- [ ] All test cases pass
- [ ] Encrypted payload validation tested

**Learning Objectives**:
- Testing encrypted payloads
- Validation testing

---

### QA-3.2: Key Service API Tests - Read Secrets

Write API tests for reading secrets.

**Scope**:
- Test: List secrets returns only user's secrets
- Test: Get secret by ID works for owner
- Test: Get secret by ID returns 404 for non-owner
- Test: Get secret by ID returns 404 for non-existent
- Test: Audit log created with action 'view'
- Test: Filtering by folder_id works
- Test: Filtering by tags works

**Acceptance Criteria**:
- [ ] Authorization tested (no cross-user access)
- [ ] Filters tested
- [ ] 404 responses identical for not-found and not-owned

**Learning Objectives**:
- Authorization testing
- Preventing information leakage

---

### QA-3.3: Key Service API Tests - Update & Delete

Write API tests for updating and deleting secrets.

**Scope**:
- Test: Update secret works for owner
- Test: Update secret returns 404 for non-owner
- Test: Update validates encrypted_value format
- Test: Delete secret works for owner
- Test: Delete secret returns 404 for non-owner
- Test: Deleted secret no longer retrievable
- Test: Audit logs created for update/delete

**Acceptance Criteria**:
- [ ] All CRUD operations tested
- [ ] Authorization consistent

**Learning Objectives**:
- Complete CRUD test coverage
- Audit log verification

---

### QA-3.4: Key Service API Tests - Folders

Write API tests for folder management.

**Scope**:
- Test: Create folder succeeds
- Test: Create nested folder succeeds
- Test: List folders returns hierarchy
- Test: Delete folder works
- Test: Cannot create circular folder reference

**Acceptance Criteria**:
- [ ] Folder operations tested
- [ ] Edge cases covered

**Learning Objectives**:
- Testing hierarchical data
- Edge case identification

---

### QA-3.5: Key Service API Tests - Expiry

Write API tests for expiry tracking.

**Scope**:
- Test: Create secret with expiry date
- Test: Expiring secrets endpoint returns correct secrets
- Test: Secrets past expiry included
- Test: Secrets with no expiry excluded
- Test: Reminder days threshold works

**Acceptance Criteria**:
- [ ] Expiry queries tested
- [ ] Edge cases (null expiry, past expiry)

**Learning Objectives**:
- Date-based testing
- Query parameter testing

---

### QA-3.6: Frontend Component Tests - Secret Form

Write component tests for secret creation/edit form.

**Scope**:
- Test: Form validates required fields
- Test: Form shows error for invalid input
- Test: Submit calls encryption function
- Test: Encrypted value sent to API (not plaintext)
- Test: Loading state shown during submission

**Acceptance Criteria**:
- [ ] Form validation tested
- [ ] Crypto integration tested
- [ ] API call verified

**Learning Objectives**:
- Angular component testing
- Mocking services
- Verifying outgoing calls

---

### QA-3.7: E2E Tests - Secret Management

Write E2E tests for secret management flows.

**Scope**:
- Test: Create a secret, verify it appears in list
- Test: View a secret, verify decrypted value shown
- Test: Edit a secret, verify changes persist
- Test: Delete a secret, verify removal from list
- Test: Create folder, add secret to folder
- Test: Filter secrets by search term

**Acceptance Criteria**:
- [ ] Full CRUD flow tested E2E
- [ ] Organization features tested
- [ ] Tests stable and independent

**Learning Objectives**:
- Complex E2E scenarios
- Data verification in E2E
- Test independence

---

## Phase Completion Checklist

Before moving to Phase 4:

- [ ] Key Service CRUD operations complete
- [ ] Folder and tag organization working
- [ ] Expiry tracking and queries functional
- [ ] Frontend vault UI complete
- [ ] Client-side encryption/decryption working
- [ ] All API tests passing
- [ ] E2E tests for secret management passing
- [ ] Audit logging for all secret operations

**Previous Phase**: [Phase 2: Authentication](./phase-2-authentication.md)
**Next Phase**: [Phase 4: Teams & Sharing](./phase-4-teams.md)
