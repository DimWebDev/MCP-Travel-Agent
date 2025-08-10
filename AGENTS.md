# AGENTS.md

> **How to Use These Project Files:**
> **1. Start by reading this AGENTS.md.**
> This file explains the workflow, code quality standards, and contribution process.
> **2. Next, read `PRD.md`** — Understand the project's requirements and goals.
> **3. Then, read `Planning.md`** — See the architecture and technical approach.
> **4. Finally, consult `Tasks.md`** — Find actionable implementation steps.

# MCP-Orchestrated AI Travel Agent

## 1. Development Workflow

1. **Review project documentation** before starting work (PRD.md, Planning.md, Tasks.md)
2. **Make focused changes** — one feature or fix per pull request with tests and documentation
3. **Never commit secrets** — use environment variables for API keys and credentials
4. **Document your reasoning** — explain complex logic and design decisions, in the form of very clear comments inside of of the code.
5. **Ask for clarification** when requirements or architecture are unclear

> **Principle:** Write clear, self-documenting code that demonstrates MCP orchestration patterns.

## 2. Responsibilities

- **Code Quality:** Write clean, well-documented code with descriptive names, very clear comments and comprehensive tests
- **Documentation:** Update relevant docs when making changes to maintain consistency
- **Testing:** Ensure high test coverage and validate agent decision-making behavior
- **Collaboration:** Communicate progress, blockers, and discoveries with the team


## 3. Code Standards

### General

- Use consistent formatting and linting tools
- Write comprehensive tests for new functionality
- Include type hints and documentation for public APIs
- Follow language-specific naming conventions


### MCP-Specific

- Document agent decision-making logic clearly
- Implement proper error handling and fallback strategies
- Use structured logging for debugging orchestration issues
- Validate external API responses before processing


## 4. Security Practices

- Never commit API keys, credentials, or sensitive data
- Validate and sanitize all user inputs
- Implement proper rate limiting for external APIs
- Apply least-privilege principles for access controls


## 5. Git Guidelines

### Commit Messages

```
[type]: brief description of change

WHY: Context or problem being solved
WHAT: Summary of the change made
```

**Types:** feat, fix, docs, test, refactor, mcp, agent, orchestration

### Pull Requests

- Include clear description of changes and testing instructions
- Reference related tasks or issues
- Ensure all tests pass and documentation is updated
- Request review from appropriate team members


### Branch Naming

- `feature/<description>` for new features
- `fix/<description>` for bug fixes
- `docs/<description>` for documentation
- `sprint-N/<feature>` for sprint-specific work


## 7. Task Management

When discovering new tasks during development:

1. **Document immediately** in Tasks.md
2. **Assess impact** on architecture and planning
3. **Prioritize** based on learning objectives and project goals
4. **Update** Planning.md if architectural changes are needed

> For detailed requirements, architecture, and implementation steps, see `PRD.md`, `Planning.md`, and `Tasks.md`.

