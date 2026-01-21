# Phase 6: Polish & Launch

**Goal**: Complete remaining features, production hardening, and final QA pass.

**Dependencies**: Phase 5 complete (infrastructure ready)

**Task Summary**:
| Track | Tasks | IDs |
|-------|-------|-----|
| Dev | 3 | DEV-6.1 through DEV-6.3 |
| DevOps | 2 | DEVOPS-6.1 through DEVOPS-6.2 |
| QA | 4 | QA-6.1 through QA-6.4 |

---

## Dev Tasks

### DEV-6.1: Client-Side API Validity Testing

Implement feature to test if API keys still work.

**Scope**:
- API test configuration per secret:
  - HTTP method, URL, header placement
  - Expected response (status code or body pattern)
- Test execution:
  - Browser makes request directly (no server proxy)
  - CORS considerations (may need proxy for some)
  - Display pass/fail result
- Common patterns:
  - Bearer token in Authorization header
  - API key in header
  - API key in query parameter

**Acceptance Criteria**:
- [ ] User can configure test for secret
- [ ] Test executes from browser
- [ ] Result displayed clearly
- [ ] Handles CORS limitations gracefully

**Security Requirements**:
- Decrypted key used only for test
- Test result doesn't expose key in logs/errors

---

### DEV-6.2: Dashboard & Overview

Implement main dashboard view.

**Scope**:
- Overview statistics:
  - Total secrets count
  - Expiring soon count
  - Teams count
- Expiring secrets widget:
  - List secrets expiring in next 30 days
  - Quick link to view/rotate
- Recent activity:
  - Recent secret access (from audit log)
  - Recent team activity

**Acceptance Criteria**:
- [ ] Dashboard displays after login
- [ ] Statistics accurate
- [ ] Expiring secrets shown
- [ ] Recent activity shown

---

### DEV-6.3: Search Functionality

Implement global search.

**Scope**:
- Search across:
  - Secret names
  - Tags
  - Folder names
- Typeahead/autocomplete
- Results grouped by type
- Quick navigation to result

**Acceptance Criteria**:
- [ ] Search returns relevant results
- [ ] Results navigable
- [ ] Performance acceptable

---

## DevOps Tasks

### DEVOPS-6.1: Production Deployment

Deploy to production environment.

**Scope**:
- Production Fly.io configuration
- Production database setup
- Production secrets
- Domain and SSL finalization
- CDN for frontend (optional)

**Acceptance Criteria**:
- [ ] Production environment deployed
- [ ] All services healthy
- [ ] Domains working with SSL
- [ ] Database backups configured

---

### DEVOPS-6.2: Monitoring & Alerting

Set up production monitoring.

**Scope**:
- Fly.io built-in monitoring:
  - CPU, memory, request rates
  - Health check status
- Application logging:
  - Structured JSON logs
  - Log aggregation
- Alerting:
  - Service down alerts
  - Error rate alerts
  - Email notifications

**Acceptance Criteria**:
- [ ] Metrics visible in Fly dashboard
- [ ] Logs searchable
- [ ] Alerts configured
- [ ] Runbook for common alerts

---

## QA Tasks

### QA-6.1: Full Regression Test Suite

Ensure all tests pass before launch.

**Scope**:
- Run all unit tests
- Run all integration tests
- Run all E2E tests
- Fix any failures
- Document known issues

**Acceptance Criteria**:
- [ ] All tests passing
- [ ] No critical/high severity bugs
- [ ] Known issues documented

**Learning Objectives**:
- Regression testing process
- Bug triage
- Release readiness assessment

---

### QA-6.2: Performance Tests

Implement basic performance testing.

**Scope**:
- API response time tests:
  - Login < X ms
  - Secret list < X ms
  - Search < X ms
- Load testing (basic):
  - Concurrent users
  - Request throughput
- Frontend performance:
  - Page load time
  - Time to interactive

**Acceptance Criteria**:
- [ ] Performance baselines established
- [ ] No major performance issues
- [ ] Results documented

**Learning Objectives**:
- Performance testing tools (k6, Locust, Lighthouse)
- Performance metrics
- Baseline establishment

---

### QA-6.3: Security Test Automation

Implement automated security scanning.

**Scope**:
- OWASP ZAP scan:
  - Run against staging
  - Address high/critical findings
- Dependency vulnerability scan:
  - Python: safety or pip-audit
  - JavaScript: npm audit
  - Integrate into CI
- SSL/TLS verification:
  - Certificate validity
  - Strong cipher suites

**Acceptance Criteria**:
- [ ] Security scans run in CI
- [ ] No high/critical vulnerabilities
- [ ] Scan reports archived

**Learning Objectives**:
- Security scanning tools
- Vulnerability assessment
- Security in CI/CD

---

### QA-6.4: Test Documentation & Reporting

Document test coverage and results.

**Scope**:
- Test coverage report:
  - Coverage percentages by service
  - Untested areas identified
- Test case documentation:
  - What's tested
  - How to run tests
- Test results dashboard (optional):
  - Historical test results
  - Trend visualization

**Acceptance Criteria**:
- [ ] Coverage report generated
- [ ] Test documentation complete
- [ ] Results accessible to team

**Learning Objectives**:
- Test documentation
- Coverage analysis
- Quality metrics

---

## Phase Completion Checklist

Before launch:

- [ ] API validity testing feature complete
- [ ] Dashboard with statistics implemented
- [ ] Search functionality working
- [ ] Production environment deployed
- [ ] Monitoring and alerting configured
- [ ] All regression tests passing
- [ ] Performance baselines established
- [ ] Security scans clean
- [ ] Documentation complete

## Launch Readiness

Final launch checklist:

- [ ] All phases complete
- [ ] No critical bugs open
- [ ] Performance acceptable
- [ ] Security review complete
- [ ] Monitoring active
- [ ] Backup/recovery tested
- [ ] Runbook documented
- [ ] Team trained on operations

**Previous Phase**: [Phase 5: CI/CD & Infrastructure](./phase-5-infrastructure.md)

---

## Post-Launch

After successful launch, consider:

1. **User feedback collection** - How are users finding the product?
2. **Performance monitoring** - Watch for real-world performance issues
3. **Security monitoring** - Monitor for suspicious activity
4. **Feature requests** - Track requests for v2 planning
5. **Technical debt** - Address any shortcuts taken for launch
