# Contributing to KeyArc

Thank you for your interest in contributing to KeyArc! This document outlines our development workflow and conventions.

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages. This enables automatic changelog generation and semantic versioning.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Changes that do not affect the meaning of the code (formatting, etc.) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding missing tests or correcting existing tests |
| `build` | Changes to build system or external dependencies |
| `ci` | Changes to CI configuration files and scripts |
| `chore` | Other changes that don't modify src or test files |

### Scope (Optional)

The scope provides additional context. Common scopes for KeyArc:

- `auth` - Authentication service
- `gateway` - Gateway service
- `account` - Account service
- `keys` - Key service
- `frontend` - Angular frontend
- `crypto` - Cryptographic code
- `shared` - Shared modules

### Examples

```bash
# Feature
feat(keys): add folder organization for secrets

# Bug fix
fix(auth): correct token refresh timing issue

# Documentation
docs: update API endpoint documentation

# Breaking change (note the ! after type)
feat(api)!: change secret response format

# With body and footer
fix(crypto): ensure proper key derivation parameters

The Argon2 parameters were not matching between signup and login flows,
causing authentication failures.

Fixes #123
```

## Pull Request Process

1. **Create a branch** from `main` for your changes
2. **Make your changes** following our coding standards
3. **Write/update tests** for your changes
4. **Commit** using conventional commit format
5. **Push** your branch and create a PR
6. **Fill out the PR template** completely
7. **Ensure CI passes** - PR title must follow conventional commits format
8. **Address any feedback** from reviewers

### PR Requirements

- PR title must follow conventional commit format (enforced by CI)
- All status checks must pass
- Review threads must be resolved before merging
- PRs are squash-merged to keep history clean

## Security Review Requirements

**Any changes to the following require careful security review:**

- Cryptographic code (encryption, key derivation, hashing)
- Authentication flows (signup, login, password reset)
- Secret handling (storing, transmitting, or displaying secrets)
- Authorization logic (RBAC, access control)

### Security Checklist for Crypto Changes

Before submitting a PR that touches security-sensitive code:

- [ ] No plaintext secrets are ever sent to the server
- [ ] Master passwords are never transmitted over the network
- [ ] All encryption/decryption happens client-side in the browser
- [ ] Server only stores encrypted ciphertext and authentication hashes
- [ ] Audit logging captures who/what/when but never secret values
- [ ] Input validation prevents injection attacks
- [ ] Error messages don't leak sensitive information

## Local Development Setup

### VS Code (Recommended)

Open the project in VS Code and install the recommended extensions when prompted. This configures automatic linting and formatting on save.

To manually install recommended extensions:
```bash
code --install-extension charliermarsh.ruff
code --install-extension ms-python.python
code --install-extension ms-python.mypy-type-checker
code --install-extension dbaeumer.vscode-eslint
code --install-extension angular.ng-template
code --install-extension exiasr.hadolint
```

### Running Linters Locally

Run these commands before creating a PR to catch issues early.

**Python:**
```bash
# Install tools (once)
pip install ruff mypy

# Lint and type check
ruff check services shared
ruff format --check services shared
mypy services shared --ignore-missing-imports

# Auto-fix formatting
ruff format services shared
```

**TypeScript (from frontend/ directory):**
```bash
cd frontend
npm run lint
npx tsc --noEmit --skipLibCheck
```

**Docker:**
```bash
# Install hadolint: https://github.com/hadolint/hadolint#install
hadolint Dockerfile
hadolint --ignore DL3008 --ignore DL3013 --ignore DL3018 Dockerfile
```

## Code Style

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Lint and format with [ruff](https://docs.astral.sh/ruff/)
- Type check with [mypy](https://mypy-lang.org/)

### TypeScript (Frontend)

- Follow Angular style guide
- Use strict TypeScript settings
- Lint with ESLint

### Docker

- Lint Dockerfiles with [hadolint](https://github.com/hadolint/hadolint)

## Testing

- Write tests for new functionality
- Ensure existing tests pass before submitting PR
- Backend: pytest
- Frontend: Jasmine/Karma

## Questions?

If you have questions about contributing, please open an issue for discussion.
