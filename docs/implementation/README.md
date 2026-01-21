# KeyArc Implementation Plan

This folder contains the complete implementation plan for KeyArc, a zero-knowledge API key and certificate manager. Work is organized into 6 sequential phases with parallel work streams for Development, DevOps, and QA.

## Quick Links

| Phase | Focus | Status |
|-------|-------|--------|
| [Phase 1](./phase-1-foundation.md) | Foundation & Environment Setup | Not Started |
| [Phase 2](./phase-2-authentication.md) | Authentication Flows | Not Started |
| [Phase 3](./phase-3-secrets.md) | Secrets Management | Not Started |
| [Phase 4](./phase-4-teams.md) | Teams & Sharing | Not Started |
| [Phase 5](./phase-5-infrastructure.md) | CI/CD & Infrastructure | Not Started |
| [Phase 6](./phase-6-launch.md) | Polish & Launch | Not Started |
| [Appendices](./appendices.md) | Data Model, Crypto, Endpoints | Reference |

## How to Use This Plan

- **Structure**: Work is organized into 6 sequential phases with clear dependencies
- **Work Streams**: Each phase has Dev, DevOps, and QA tasks that can run in parallel
- **Dev/DevOps Tasks**: Chunked for AI-assisted development (larger scope per task)
- **QA Tasks**: Smaller, progressive tasks for skill building and mentorship
- **Dependencies**: Noted inline where tasks require prior work to be complete
- **GitHub Issues**: Each task section can be converted into one or more GitHub issues

## Team & Approach

| Aspect | Approach |
|--------|----------|
| Team Size | 1-3 people (potentially solo developer + QA engineer) |
| Development | AI-assisted (Claude Code), enabling larger task chunks |
| QA Focus | Test automation skill building, progressive complexity |
| Infrastructure | Local Docker first, CI early, Fly.io deployment when ready |

## QA Involvement Timeline

QA can begin contributing from Phase 1 and grows skills progressively:

| Phase | QA Focus | Skills Learned |
|-------|----------|----------------|
| 1 | Test framework setup | CI integration, project structure |
| 2 | Auth API & E2E tests | API testing, async patterns, mocking |
| 3 | Secrets & validation tests | Encrypted payloads, state management |
| 4 | Permission & sharing tests | Complex scenarios, security testing |
| 5 | Integration & staging tests | Environment testing, deployment verification |
| 6 | Regression, perf, security | Non-functional testing, automation |

## Task Counts by Phase

| Phase | Dev Tasks | DevOps Tasks | QA Tasks | Total |
|-------|-----------|--------------|----------|-------|
| Phase 1 | 4 | 2 | 4 | 10 |
| Phase 2 | 4 | 1 | 6 | 11 |
| Phase 3 | 4 | 1 | 7 | 12 |
| Phase 4 | 5 | 1 | 5 | 11 |
| Phase 5 | 2 | 3 | 3 | 8 |
| Phase 6 | 3 | 2 | 4 | 9 |
| **Total** | **22** | **10** | **29** | **61** |

## Dependency Graph

```
Phase 1: Foundation
    │
    ├── Project scaffolding
    ├── Shared modules
    └── Test frameworks
         │
         ▼
Phase 2: Authentication ─────────────────────┐
    │                                        │
    ├── Crypto module                        │
    ├── Auth Service                         │
    ├── Gateway                              │
    └── Auth UI                              │
         │                                   │
         ▼                                   │
Phase 3: Secrets Management                  │
    │                                        │
    ├── Key Service                          │
    ├── Organization (folders, tags)         │
    └── Vault UI                             │
         │                                   │
         ▼                                   │
Phase 4: Teams & Sharing ◄───────────────────┘
    │        (needs RSA keys from Phase 2)
    ├── Account Service
    ├── Team management
    ├── RBAC
    └── Sharing UI
         │
         ▼
Phase 5: CI/CD & Infrastructure
    │
    ├── Complete pipeline
    ├── Fly.io setup
    └── Staging deployment
         │
         ▼
Phase 6: Polish & Launch
    │
    ├── API validity testing
    ├── Dashboard
    ├── Production deployment
    └── Final QA
```

## Task ID Convention

Each task has a unique ID for tracking:

- **DEV-X.Y**: Development task (Phase X, Task Y)
- **DEVOPS-X.Y**: DevOps task (Phase X, Task Y)
- **QA-X.Y**: QA task (Phase X, Task Y)

Example: `DEV-2.1` = Development task, Phase 2, Task 1 (Frontend Crypto Module)

## Getting Started

1. Review [Phase 1](./phase-1-foundation.md) to understand the foundation work
2. Set up local development environment (Docker Compose)
3. Begin with project scaffolding tasks
4. QA can start test framework setup in parallel

## Related Documentation

- [PRODUCT.md](../PRODUCT.md) - Product vision and features
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Service architecture and data model
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Infrastructure and deployment details
- [CLAUDE.md](../../CLAUDE.md) - Development guidelines and project context
