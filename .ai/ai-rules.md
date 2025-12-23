"""
File: .ai/ai-rules.md

Purpose: Mandatory development rules and quality gates for thai-lint

Exports: Quality gates, coding standards, git rules, documentation rules

Depends: ai-context.md, docs/FILE_HEADER_STANDARDS.md

Overview: Defines all mandatory rules for working on this project. Includes quality
    gate requirements, coding standards, git workflow rules, and documentation
    maintenance requirements. All rules must be followed for code to be accepted.
"""

# AI Development Rules

**Purpose**: Mandatory rules for working on this project

---

## Quality Gates

All code must pass before commit:

| Tool | Requirement | Command |
|------|-------------|---------|
| Ruff | All checks pass | `just lint` |
| Pylint | Score 10.00/10 | `poetry run pylint src/` |
| MyPy | Zero errors | `poetry run mypy src/` |
| Xenon | ALL blocks A-grade | `just lint-complexity` |
| Bandit | All security checks | `just lint-security` |
| Tests | All passing | `just test` |

**Run all checks**: `just lint-full`

**Success criteria**: Exit code 0 from `just lint-full` AND `just test`

---

## Coding Standards

1. **Type hints everywhere** - MyPy strict mode must pass
2. **Docstrings required** - Google-style for all public functions
3. **Maximum complexity A** - Every function/method must be A-grade (Xenon)
4. **Proper file headers** - See `.ai/docs/FILE_HEADER_STANDARDS.md`
5. **Atemporal language** - No "currently", "now", "new", "old", dates
6. **No print statements** - Use proper logging or Click output

---

## Suppression Rules

**NEVER add linter suppression comments without explicit user permission:**
- `# type: ignore` (MyPy)
- `# pylint: disable=rule` (Pylint)
- `# noqa` (Ruff)
- `# nosec` (Bandit)

**Required Process:**
1. STOP - Don't add the suppression yet
2. EXPLAIN the problem clearly to the user
3. PROPOSE why suppression might be needed
4. ASK for explicit permission
5. WAIT for approval before adding

**Permission is issue-specific** - approval for one issue does NOT grant permission for others.

---

## Git Rules

1. **No commits to main** - Always use feature branches
2. **No `--no-verify`** - Except with documented exceptions
3. **Run quality gates** - `just lint-full` before committing
4. **Conventional commits** - Format: `type(scope): description`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`

---

## Documentation Rules

1. **Keep docs up-to-date** - Update documentation when behavior changes
2. **Update index.yaml** - When adding, removing, or renaming files in `.ai/`
3. **Update AGENTS.md** - When adding new CLI commands or features
4. **Use atemporal language** - No temporal references
5. **File headers required** - All new files need proper headers

---

## Branch Naming

Use descriptive branch names:
- `feature/<description>` - New features
- `fix/<description>` - Bug fixes
- `refactor/<description>` - Code refactoring
- `docs/<description>` - Documentation updates
- `perf/<description>` - Performance improvements

---

## Before Committing Checklist

- [ ] `just lint-full` exits with code 0
- [ ] `just test` exits with code 0
- [ ] Pylint shows exactly 10.00/10
- [ ] Xenon shows NO errors (all A-grade)
- [ ] All files have proper headers
- [ ] Documentation updated if needed
- [ ] No secrets committed
