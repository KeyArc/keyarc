## Description

<!-- Describe your changes in detail. What problem does this solve? -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] CI/CD or infrastructure changes

## Testing

- [ ] I have tested these changes locally
- [ ] I have added/updated tests that prove my fix is effective or my feature works
- [ ] All existing tests pass

## Security Review

<!-- Required for any changes to cryptographic code, authentication, or secret handling -->

- [ ] This PR does NOT touch cryptographic code, authentication, or secret handling
- [ ] **OR** This PR includes crypto/auth changes and I have verified:
  - [ ] No plaintext secrets are sent to the server
  - [ ] No master passwords are transmitted or logged
  - [ ] All encryption/decryption happens client-side
  - [ ] Audit logging captures access metadata (not secret values)

## Checklist

- [ ] My code follows the project's coding standards
- [ ] I have updated documentation as needed
- [ ] My commit messages follow conventional commit format (`feat:`, `fix:`, `docs:`, etc.)
