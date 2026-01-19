# KeyArc: Product Overview

## What is KeyArc?

KeyArc is a secure, zero-knowledge API key and certificate manager designed for solo developers and small teams. It combines the security model of modern password managers with features tailored specifically for managing API credentials, certificates, and other secrets.

**Core value:** Store your API keys and certificates securely, get reminded before they expire, verify they still work, and share them safely with your team—all without the server ever seeing your plaintext secrets.

## Target Users

- Solo developers managing personal projects and client work
- Small teams and startups who need shared access to credentials
- Small businesses with multiple departments needing organized secret management
- Anyone who finds enterprise solutions like HashiCorp Vault overkill for their needs

## Core Features

### Secure Storage with Client-Side Encryption
- All secrets encrypted in the browser before being sent to the server
- Server only stores encrypted ciphertext—never plaintext or master passwords
- Based on Bitwarden's proven encryption model
- Single master password to remember

### Expiry Tracking & Rotation Reminders
- Track expiration dates for certificates and time-limited API keys
- Configurable rotation reminders
- Dashboard view of upcoming expirations

### Client-Side Validity Testing
- Test if an API key still works
- Tests executed from the browser, secrets never transit through our servers
- Support for common API patterns (REST endpoints, bearer tokens)

### Organization & Structure
- Folders for hierarchical organization
- Tags for flexible categorization
- Environment labels (production, staging, development)
- Search and filtering

### Team Sharing
- Share secrets with team members without exposing plaintext to the server
- Role-based access (owner, admin, member)
- Personal vaults and team vaults
- Public key cryptography for secure sharing

### Audit Logging
- Track who accessed which secrets and when
- Action history: view, create, update, delete, share

## Out of Scope (v1)

- Browser extensions
- Desktop/mobile applications
- IDE plugins
- Import/export functionality
- Automatic key rotation
- Integration with external secret managers
- Self-hosted deployment
- SSO/SAML authentication
- Compliance certifications (SOC2, HIPAA)

## Development Environment

- **macOS** (Apple Silicon/ARM) and **Windows** (x86/x64)
- Docker Desktop for containerized development
- VS Code or Claude Code recommended

## Summary

KeyArc addresses a real gap: developers and small teams need a simple, secure way to manage API keys and certificates without enterprise complexity or trusting a server with their plaintext secrets.
