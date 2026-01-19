# KeyArc Claude Code Configuration

This directory contains Claude Code configuration, skills, and project context for KeyArc development.

## Files

- **CLAUDE.md** - Main project context file. Read this first to understand KeyArc's architecture and zero-knowledge security model.
- **skills/** - Claude Code skills that provide specialized guidance for development tasks.

## Skills Overview

### Community Skills (Cloned)

These are battle-tested patterns from the Claude Code community:

1. **python-fastapi-expert** - FastAPI patterns, Pydantic validation, SQLAlchemy ORM, async Python
2. **frontend-web-dev** - Angular, TypeScript, RxJS, reactive forms, component architecture
3. **devops-engineer** - Docker, Docker Compose, GitHub Actions CI/CD
4. **tdd-workflow** - Test-Driven Development with RED-GREEN-REFACTOR cycle
5. **planning-research** - Research and planning before implementation

### KeyArc Custom Skills

These enforce KeyArc's zero-knowledge security architecture:

6. **keyarc-zero-knowledge** - Zero-knowledge encryption patterns, ensures server never sees plaintext
7. **keyarc-crypto-flows** - Implementation patterns for signup, login, and team sharing flows
8. **keyarc-api-security** - JWT authentication, encrypted payload validation, audit logging, OWASP prevention

## Skill Activation

Skills activate automatically based on semantic matching of your requests. For example:

- "Create a FastAPI endpoint" → activates `python-fastapi-expert`
- "Implement the signup flow" → activates `keyarc-zero-knowledge` and `keyarc-crypto-flows`
- "Add JWT authentication" → activates `keyarc-api-security`
- "Write tests first" → activates `tdd-workflow`

## MCP Servers

KeyArc uses Model Context Protocol (MCP) servers for enhanced capabilities:

### Docker MCP

Provides Docker Hub search and Docker Compose generation.

**Setup:**
```bash
claude mcp add docker npx -- -y @modelcontextprotocol/server-docker
```

**Usage:**
- "Generate a Docker Compose file with FastAPI and PostgreSQL"
- "Search Docker Hub for postgres images"

### PostgreSQL MCP

Provides database exploration, query generation, and schema design.

**Setup:**
```bash
claude mcp add postgres npx -- -y @modelcontextprotocol/server-postgres
```

**Configuration (after database is running):**
Edit your Claude Code MCP config to add connection string:
```json
{
  "mcpServers": {
    "postgres": {
      "env": {
        "DATABASE_URL": "postgresql://localhost:5432/keyarc_dev"
      }
    }
  }
}
```

**Usage:**
- "Show me the database schema"
- "Generate a query to find all secrets for user 123"

## Verification

After setup, verify skills are loaded:

1. Run `claude` in the keyarc directory
2. Skills should be automatically detected
3. Try a prompt like: "How should I implement the signup flow?"
4. KeyArc zero-knowledge skill should activate

## Best Practices

### When to Use Skills

**Always use:**
- Zero-knowledge skill when implementing cryptography
- Crypto flows skill for signup/login/sharing
- API security skill for new endpoints
- TDD skill for new features
- Planning skill for complex changes

**How to use:**
- Skills activate automatically - just describe what you need
- Reference specific patterns: "Use the signup flow pattern from the crypto flows skill"
- Combine skills: "Create a FastAPI endpoint following zero-knowledge principles with TDD"

### Security-First Development

All KeyArc development must follow zero-knowledge principles:

1. **Never send plaintext secrets to server**
2. **Always encrypt client-side first**
3. **Use authHash for authentication, not passwords**
4. **Validate encrypted payloads on server**
5. **Audit log access, never values**

The `keyarc-zero-knowledge` skill enforces these principles. Review it before implementing any feature involving secrets.

## Skill Structure

Each skill follows this pattern:

```
skills/skill-name/
├── SKILL.md              # Main skill definition (< 500 lines)
├── supporting-doc-1.md   # Detailed reference (if needed)
└── supporting-doc-2.md   # Code examples (if needed)
```

**SKILL.md** contains:
- Frontmatter (name, description)
- When to use
- Core patterns
- Quick reference
- Common mistakes
- Examples

**Supporting docs** provide detailed implementation guides without bloating the main skill.

## Updating Skills

Skills can evolve as patterns emerge in the codebase:

1. **Add new patterns** - As you solve problems, add proven patterns to skills
2. **Remove outdated patterns** - When code supersedes skills, remove old guidance
3. **Reference actual code** - Link to implemented code instead of duplicating patterns

Once a pattern is implemented in the codebase, the code becomes the source of truth. Skills are for patterns not yet in code or for enforcing critical principles (like zero-knowledge).

## Troubleshooting

**Skills not loading:**
- Verify you're in the keyarc directory
- Check SKILL.md frontmatter is valid YAML
- Ensure SKILL.md filename is exact (case-sensitive)

**Skill not activating:**
- Make description more trigger-rich
- Explicitly reference skill: "using the keyarc-zero-knowledge skill"
- Check if context matches skill's "When to Use" section

**MCP server not connecting:**
- Run `claude mcp list` to see configured servers
- Check server installation: `npx @modelcontextprotocol/server-docker --version`
- Verify DATABASE_URL for PostgreSQL MCP (when DB is running)

## Resources

**Skill Creation Guide:**
- See `skills/planning-research/SKILL.md` for skill writing best practices
- Keep SKILL.md under 500 lines
- Use trigger-rich descriptions
- Include good/bad examples
- Test skills under pressure scenarios

**External Resources:**
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [obra/superpowers](https://github.com/obra/superpowers) - Core skills library
- [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills) - Community skills

## Contributing to Skills

When you discover useful patterns:

1. Add them to appropriate skill
2. Include code examples
3. Show good vs bad patterns
4. Update this README if adding new skills

**Principle:** Skills are living documents that evolve with the project.

---

**Start here:** Read `CLAUDE.md` to understand KeyArc's architecture, then refer to skills as needed during development.
