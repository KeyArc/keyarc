# OWASP Top 10 Prevention Checklist

Quick checklist for preventing OWASP top 10 vulnerabilities.

- [ ] **Injection**: Use SQLAlchemy ORM (not raw SQL)
- [ ] **Broken Auth**: JWT tokens + rate limiting + authHash (not password)
- [ ] **Sensitive Data Exposure**: All secrets encrypted client-side, HTTPS only
- [ ] **XXE**: Validate XML inputs if applicable
- [ ] **Broken Access Control**: Check user permissions at API layer (RBAC)
- [ ] **Security Misconfiguration**: No debug mode in production, secure defaults
- [ ] **XSS**: Angular handles client-side, validate API responses
- [ ] **Insecure Deserialization**: Use Pydantic for all input validation
- [ ] **Known Vulnerabilities**: Enable Dependabot, keep dependencies updated
- [ ] **Insufficient Logging**: Comprehensive audit logs for all secret access
