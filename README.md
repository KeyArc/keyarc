# KeyArc

[![CI](https://github.com/KeyArc/keyarc/actions/workflows/ci.yml/badge.svg)](https://github.com/KeyArc/keyarc/actions/workflows/ci.yml)

Secure, zero-knowledge API key and certificate manager for solo developers, small teams, and startups.

## Documentation

- [Product Documentation](docs/PRODUCT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Contributing](CONTRIBUTING.md)

## Core Principle

**Zero-knowledge architecture** - the server NEVER sees plaintext secrets or master passwords. All encryption and decryption happens client-side in the browser.

## Tech Stack

- **Backend:** FastAPI (Python), PostgreSQL, SQLAlchemy
- **Frontend:** Angular (TypeScript), RxJS
- **Infrastructure:** Docker, Fly.io, GitHub Actions
- **Security:** WebCrypto API, Argon2, AES, RSA/ECC
