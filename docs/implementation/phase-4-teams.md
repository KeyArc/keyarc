# Phase 4: Teams & Sharing

**Goal**: Implement team management, role-based access control, and secure secret sharing using public key cryptography.

**Dependencies**: Phase 3 complete (Key Service working), Phase 2 (RSA keys available)

**Task Summary**:
| Track | Tasks | IDs |
|-------|-------|-----|
| Dev | 5 | DEV-4.1 through DEV-4.5 |
| DevOps | 1 | DEVOPS-4.1 |
| QA | 5 | QA-4.1 through QA-4.5 |

---

## Dev Tasks

### DEV-4.1: Account Service - User Profiles

Implement user profile management.

**Scope**:
- `GET /account/profile`:
  - Return current user's profile
  - Include public_key for sharing
- `PUT /account/profile`:
  - Update allowed fields (display name, etc.)
  - Cannot change email or keys via this endpoint

**Acceptance Criteria**:
- [ ] Profile retrieval works
- [ ] Profile update works
- [ ] Sensitive fields (auth_hash, encrypted keys) not exposed

---

### DEV-4.2: Account Service - Team Management

Implement team CRUD operations.

**Scope**:
- `GET /account/teams`:
  - List teams user is a member of
  - Include user's role in each team
- `POST /account/teams`:
  - Create new team
  - Request includes: name, encrypted_team_key (encrypted with creator's public key)
  - Creator becomes owner
- `GET /account/teams/:id`:
  - Return team details
  - Include member list with roles
  - Only accessible to team members
- `PUT /account/teams/:id`:
  - Update team name
  - Only owner/admin can update
- `DELETE /account/teams/:id`:
  - Delete team
  - Only owner can delete
  - Decide: cascade delete team secrets?

**Acceptance Criteria**:
- [ ] Team CRUD works
- [ ] Only members can view team
- [ ] Only owner can delete team
- [ ] Encrypted team key stored correctly

---

### DEV-4.3: Account Service - Team Membership

Implement team member management.

**Scope**:
- `POST /account/teams/:id/members`:
  - Invite user to team
  - Request: user_id (or email), role, encrypted_team_key
  - encrypted_team_key is team key encrypted with invitee's public key
  - Only admin/owner can invite
- `PUT /account/teams/:id/members/:userId`:
  - Update member role
  - Only owner can change roles
  - Cannot demote last owner
- `DELETE /account/teams/:id/members/:userId`:
  - Remove member from team
  - Admin can remove members, owner can remove admins
  - Cannot remove last owner
- `GET /account/users/search?email=`:
  - Search for users by email (for inviting)
  - Return public_key for encryption

**Acceptance Criteria**:
- [ ] Member invitation works
- [ ] Role updates enforce permissions
- [ ] Member removal enforces permissions
- [ ] Cannot remove last owner
- [ ] User search returns public key

---

### DEV-4.4: Key Service - Team Secrets

Extend Key Service to support team-owned secrets.

**Scope**:
- Secrets with `owner_type='team'`:
  - Accessible to all team members
  - Encrypted with team key (not user's vault key)
- `GET /keys/secrets?team_id=`:
  - Filter secrets by team
  - Verify user is team member
- Create secret with team ownership:
  - Specify owner_type and owner_id
  - Verify user has permission in team
- RBAC for team secrets:
  - All members can view
  - Admin+ can create/edit
  - Owner can delete

**Acceptance Criteria**:
- [ ] Team secrets retrievable by members
- [ ] Non-members cannot access team secrets
- [ ] RBAC enforced for create/edit/delete
- [ ] Audit logs include team context

---

### DEV-4.5: Frontend Team UI

Implement team management interface.

**Scope**:
- Team list view:
  - Show teams user belongs to
  - Show role in each team
- Create team:
  - Generate team key
  - Encrypt with own public key
  - Store encrypted team key
- Team detail view:
  - List members and roles
  - Manage team (if admin/owner)
- Invite member:
  - Search for user by email
  - Get their public key
  - Decrypt team key with own private key
  - Re-encrypt team key with invitee's public key
  - Submit invitation
- Team vault:
  - View team secrets
  - Decrypt with team key
  - Create/edit based on role
- Leave team:
  - Remove self from team
  - Cannot leave if last owner

**Acceptance Criteria**:
- [ ] Team creation works with key encryption
- [ ] Member invitation re-encrypts team key
- [ ] Team secrets decrypt correctly
- [ ] Role-based UI (hide actions user can't perform)
- [ ] Leave team works

**Security Requirements**:
- Team key only decrypted when needed
- Re-encryption happens client-side
- Clear team keys when switching contexts

---

## DevOps Tasks

### DEVOPS-4.1: Multi-Service Integration Tests

Set up infrastructure for cross-service testing.

**Scope**:
- Docker Compose for integration tests
  - All services running
  - Test database
  - Gateway routing
- Integration test fixtures
  - Create users via Auth Service
  - Get JWT tokens
  - Make authenticated requests through Gateway
- CI integration
  - Run integration tests in pipeline
  - Separate from unit tests

**Acceptance Criteria**:
- [ ] Integration tests can call through Gateway
- [ ] Tests can create/authenticate users
- [ ] Multi-service scenarios testable
- [ ] Runs in CI

---

## QA Tasks

### QA-4.1: Account Service API Tests - Teams

Write API tests for team management.

**Scope**:
- Test: Create team succeeds
- Test: List teams returns user's teams
- Test: Get team returns details for member
- Test: Get team returns 404 for non-member
- Test: Update team works for owner/admin
- Test: Update team fails for member
- Test: Delete team works for owner only

**Acceptance Criteria**:
- [ ] CRUD operations tested
- [ ] Role-based access tested

**Learning Objectives**:
- Testing role-based APIs
- Complex authorization scenarios

---

### QA-4.2: Account Service API Tests - Membership

Write API tests for team membership.

**Scope**:
- Test: Add member succeeds with correct role permission
- Test: Add member fails for regular member
- Test: Update role works for owner
- Test: Remove member works for admin+
- Test: Cannot remove last owner
- Test: Cannot demote last owner

**Acceptance Criteria**:
- [ ] All permission combinations tested
- [ ] Edge cases covered

**Learning Objectives**:
- Testing permission hierarchies
- Edge case identification

---

### QA-4.3: RBAC Permission Matrix Tests

Systematically test all role/action combinations.

**Scope**:
Create a permission matrix and test each cell:

| Action | Owner | Admin | Member | Non-Member |
|--------|-------|-------|--------|------------|
| View team | Pass | Pass | Pass | Fail |
| Update team | Pass | Pass | Fail | Fail |
| Delete team | Pass | Fail | Fail | Fail |
| Add member | Pass | Pass | Fail | Fail |
| Remove member | Pass | Pass* | Fail | Fail |
| Change roles | Pass | Fail | Fail | Fail |
| View secrets | Pass | Pass | Pass | Fail |
| Create secrets | Pass | Pass | Fail | Fail |
| Delete secrets | Pass | Fail | Fail | Fail |

*Admin can remove members but not other admins

**Acceptance Criteria**:
- [ ] Every cell in matrix tested
- [ ] Tests parameterized for maintainability
- [ ] Clear test names

**Learning Objectives**:
- Systematic security testing
- Parameterized tests
- Test matrix approach

---

### QA-4.4: Team Sharing Flow Tests

Write tests for the complete sharing flow.

**Scope**:
- Test: Team secret accessible by all members
- Test: New member can access existing secrets
- Test: Removed member loses access immediately
- Test: Secret shared to team not visible in personal vault
- Test: Correct team key used for decryption

**Acceptance Criteria**:
- [ ] Full sharing flow tested
- [ ] Access revocation tested
- [ ] Key management tested

**Learning Objectives**:
- Testing cryptographic workflows
- Access control testing

---

### QA-4.5: E2E Tests - Team Workflows

Write E2E tests for team features.

**Scope**:
- Test: Create team flow
- Test: Invite member flow (with second user)
- Test: Create team secret
- Test: Member views shared secret
- Test: Remove member, verify access lost

**Acceptance Criteria**:
- [ ] Multi-user E2E scenarios work
- [ ] Full team lifecycle tested
- [ ] Tests handle multiple browser contexts

**Learning Objectives**:
- Multi-user E2E testing
- Complex scenario orchestration
- Browser context management

---

## Phase Completion Checklist

Before moving to Phase 5:

- [ ] Account Service profile endpoints complete
- [ ] Team CRUD operations working
- [ ] Team membership management working
- [ ] Key Service supports team secrets
- [ ] RBAC enforced across team operations
- [ ] Frontend team UI complete
- [ ] Team key sharing works correctly
- [ ] All team-related tests passing
- [ ] E2E tests for team workflows passing

**Previous Phase**: [Phase 3: Secrets Management](./phase-3-secrets.md)
**Next Phase**: [Phase 5: CI/CD & Infrastructure](./phase-5-infrastructure.md)
