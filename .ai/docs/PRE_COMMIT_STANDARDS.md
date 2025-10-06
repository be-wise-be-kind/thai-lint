# Pre-commit Hooks Standards

**Purpose**: Define standards and best practices for pre-commit hooks configuration in Docker-first development

**Scope**: Git hooks for automated code quality enforcement across all project languages and development stages

**Overview**: Establishes comprehensive standards for configuring and using pre-commit hooks in Docker-based
    development environments. Covers hook configuration patterns, execution stages (pre-commit and pre-push),
    language-specific tooling integration (Python: ruff, flake8, mypy, pylint, bandit, xenon; TypeScript:
    ESLint, Prettier, type checking, stylelint), Docker container execution, branch protection policies,
    auto-fix workflows, security scanning requirements, and emergency skip procedures. Defines when to use
    file-specific vs. comprehensive checks, how to balance speed and thoroughness, and standards for adding
    custom hooks. Ensures consistent code quality enforcement across all environments and team members.

**Dependencies**: Git, Docker, Docker Compose, pre-commit framework, language-specific plugins (Python, TypeScript)

**Exports**: Pre-commit configuration standards, hook design patterns, integration guidelines, best practices

**Related**: plugins/languages/python (Python tooling), plugins/languages/typescript (TypeScript tooling), plugins/standards/security (security scanning), plugins/infrastructure/containerization/docker (Docker execution)

**Implementation**: Standards-based configuration with Docker integration, staged validation, and comprehensive documentation

---

## Overview

Pre-commit hooks provide automated code quality enforcement at the git commit and push stages. This document defines standards for configuring hooks that:

1. **Execute in Docker containers** for consistency
2. **Detect languages dynamically** and run appropriate tools
3. **Balance speed and thoroughness** through staged validation
4. **Enforce critical policies** like branch protection and security
5. **Integrate with existing tooling** (Makefiles, CI/CD)

---

## Core Principles

### 1. Docker-First Execution

**Standard**: All hooks MUST execute in Docker containers

**Rationale**:
- Consistent tool versions across environments
- No local dependency conflicts
- Same tools in development and CI/CD
- Isolated execution environments

**Implementation**:
```yaml
- id: python-ruff
  name: Ruff (Python format + lint)
  entry: bash -c 'docker exec <container> ruff check $files'
  language: system
```

### 2. Dynamic Language Detection

**Standard**: Hooks MUST detect which languages are present and only run applicable tools

**Rationale**:
- Avoids errors in multi-language projects
- Faster execution (skip irrelevant tools)
- Flexible configuration for various project types

**Implementation**:
```yaml
# Python hooks only run on .py files
- id: python-ruff
  files: \.(py)$

# TypeScript hooks only run on .ts/.tsx files
- id: typescript-check
  files: ^frontend/.*\.(ts|tsx)$
```

### 3. Staged Validation

**Standard**: Use two validation stages with different thoroughness levels

| Stage | When | Scope | Speed | Purpose |
|-------|------|-------|-------|---------|
| Pre-commit | `git commit` | Changed files only | Fast (3-10s) | Catch obvious issues early |
| Pre-push | `git push` | All files + tests | Slow (1-5min) | Comprehensive validation |

**Rationale**:
- Fast feedback during development (pre-commit)
- Thorough validation before sharing code (pre-push)
- Balance between speed and quality

### 4. Auto-fix First

**Standard**: Always run auto-fix before validation hooks

**Rationale**:
- Reduces hook failures
- Developers don't waste time on formatting
- Consistent code style automatically enforced

**Implementation**:
```yaml
- id: make-lint-fix
  name: Auto-fix linting issues
  entry: bash -c 'make lint-fix && git add -u'
  language: system
  pass_filenames: false
  stages: [pre-commit]
```

### 5. Branch Protection

**Standard**: MUST prevent direct commits to protected branches

**Protected branches** (minimum):
- `main`
- `master`

**Optional protected branches**:
- `develop`
- `staging`
- `production`

**Implementation**:
```yaml
- id: no-commit-to-main
  name: Prevent commits to main branch
  entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then echo "❌ Direct commits to main/master branch are not allowed!"; exit 1; fi'
  language: system
  pass_filenames: false
  stages: [pre-commit]
  always_run: true
```

---

## Hook Configuration Standards

### File Structure

**Standard**: Pre-commit configuration MUST be in project root

```
project-root/
├── .pre-commit-config.yaml    # Pre-commit configuration
├── .git/
│   └── hooks/
│       ├── pre-commit         # Installed by pre-commit framework
│       └── pre-push          # Installed by pre-commit framework
└── Makefile                   # Integration targets (lint-fix, lint-all)
```

### Configuration Format

**Standard**: Use YAML format with clear structure

```yaml
repos:
  - repo: local
    hooks:
      # Branch protection first
      - id: no-commit-to-main
        ...

      # Auto-fix second
      - id: make-lint-fix
        ...

      # Language-specific linting (alphabetical order)
      - id: python-ruff
        ...
      - id: typescript-check
        ...

      # Security scanning
      - id: python-bandit
        ...

      # Pre-push hooks (comprehensive)
      - id: pre-push-lint-all
        stages: [pre-push]
        ...
```

### Hook Naming

**Standard**: Use descriptive, consistent hook names

| Pattern | Example | Purpose |
|---------|---------|---------|
| `<language>-<tool>` | `python-ruff` | Language-specific tool |
| `<purpose>-<action>` | `make-lint-fix` | Utility hook |
| `no-<forbidden-action>` | `no-commit-to-main` | Protection hook |
| `pre-<stage>-<action>` | `pre-push-lint-all` | Stage-specific hook |

---

## Language-Specific Standards

### Python Hooks

**Required hooks** (minimum):
```yaml
- id: python-ruff          # Format + lint (fast)
- id: python-flake8        # Style checking
- id: python-mypy          # Type checking
- id: python-bandit        # Security scanning
```

**Recommended hooks**:
```yaml
- id: python-pylint        # Comprehensive analysis
- id: python-xenon         # Complexity checking
```

**Execution pattern**:
```yaml
- id: python-ruff
  name: Ruff (Python format + lint)
  entry: bash -c 'files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$" | grep -E "^(app|tools)/" || true); if [ -n "$files" ]; then make lint-ensure-containers >/dev/null 2>&1; docker exec <container> ruff check $files; fi'
  language: system
  files: \.(py)$
  pass_filenames: false
  stages: [pre-commit]
```

**Key patterns**:
1. **File detection**: Use `git diff --cached --name-only` for changed files
2. **Container check**: Ensure containers running with `make lint-ensure-containers`
3. **Conditional execution**: Only run if files match filter
4. **Docker execution**: Run tool in container, not locally

### TypeScript/JavaScript Hooks

**Required hooks** (minimum):
```yaml
- id: typescript-check     # Type checking
- id: eslint              # Linting
- id: prettier-check      # Format checking
```

**Recommended hooks**:
```yaml
- id: stylelint           # CSS linting
```

**Execution pattern**:
```yaml
- id: typescript-check
  name: TypeScript type checking
  entry: bash -c 'if git diff --cached --name-only --diff-filter=ACM | grep -qE "frontend/.*\.(ts|tsx)$"; then make lint-ensure-containers >/dev/null 2>&1; docker exec <container> sh -c "cd /workspace/frontend && npm run typecheck"; fi'
  language: system
  files: ^frontend/.*\.(ts|tsx)$
  pass_filenames: false
  stages: [pre-commit]
```

---

## Security Standards

### Required Security Hooks

**Standard**: Projects MUST include security scanning

**Python projects**:
```yaml
- id: python-bandit
  name: Bandit (Python security)
  # Scans for security vulnerabilities
```

**TypeScript projects**:
```yaml
- id: eslint
  name: ESLint (JavaScript/TypeScript)
  # Include eslint-plugin-security
```

### No-skip Enforcement

**Standard**: Security and critical hooks MUST NOT be skippable without explicit override

```yaml
- id: no-skip-enforcement
  name: Linting rule skip enforcement
  entry: bash -c 'docker exec <container> python -m design_linters --categories enforcement --fail-on-error $files'
  language: system
  files: \.(py|ts|tsx|tf|sh)$
  pass_filenames: false
  stages: [pre-commit]
```

**Checks for**:
- `# noqa` without justification
- `# nosec` without explanation
- Disabled ESLint rules without comments

---

## Pre-push Standards

### Comprehensive Validation

**Standard**: Pre-push hooks MUST run comprehensive checks

**Required pre-push hooks**:
```yaml
- id: check-uncommitted-changes
  name: Check for uncommitted changes
  # Ensure working directory is clean

- id: pre-push-lint-all
  name: Run comprehensive linting before push
  # Run all linters on all code

- id: pre-push-test-all
  name: Run all tests before push
  # Ensure all tests pass
```

### Emergency Skip Mechanism

**Standard**: Provide documented emergency skip for pre-push hooks ONLY

**Implementation**:
```yaml
- id: pre-push-lint-all
  entry: bash -c 'if [ -z "$PRE_PUSH_SKIP" ]; then make lint-all; else echo "⚠️  Linting skipped via PRE_PUSH_SKIP"; fi'
```

**Usage** (emergency only):
```bash
PRE_PUSH_SKIP=1 git push
```

**Documentation requirement**: Document when skipping is acceptable:
- Production hotfixes requiring immediate deployment
- Temporary workarounds (with immediate follow-up commit required)
- Infrastructure failures blocking normal validation

**Never skip for**:
- "I'm in a hurry"
- "Tests are flaky"
- "Linter is wrong"

---

## Performance Standards

### Execution Time Targets

| Stage | Target | Maximum |
|-------|--------|---------|
| Pre-commit (changed files) | < 10s | 30s |
| Pre-push (all files + tests) | < 2min | 5min |

### Optimization Requirements

**Standard**: Hooks MUST be optimized for speed

**Required optimizations**:
1. **File filtering**: Only check changed files in pre-commit
2. **Container reuse**: Don't restart containers for each hook
3. **Parallel execution**: Independent hooks can run in parallel
4. **Tool caching**: Cache tool downloads and results

**Implementation**:
```yaml
# Only check changed files
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$" || true)

# Skip if no matching files
if [ -n "$files" ]; then
  # Run check
fi

# Reuse running containers
docker exec <existing-container> <command>
```

---

## Integration Standards

### Makefile Integration

**Standard**: Pre-commit hooks MUST integrate with project Makefile

**Required Makefile targets**:
```makefile
# Auto-fix issues
lint-fix:
    docker exec <container> ruff format .
    docker exec <container> ruff check --fix .

# Ensure containers are running
lint-ensure-containers:
    docker compose up -d <linting-containers>

# Run all linters
lint-all:
    docker exec <container> ruff check .
    docker exec <container> flake8 .
    docker exec <container> mypy .
    # ... all linting tools

# Run all tests
test-all:
    docker exec <container> pytest
```

### CI/CD Integration

**Standard**: Run same hooks in CI/CD pipeline

**GitHub Actions example**:
```yaml
- name: Run pre-commit hooks
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

**Benefits**:
- Consistent validation locally and in CI/CD
- Catch issues before code review
- Enforce quality gates

---

## Custom Hook Standards

### When to Add Custom Hooks

**Add custom hooks for**:
- Project-specific validation rules
- Business logic constraints
- Organization standards
- Security policies

**Don't add custom hooks for**:
- Standard linting (use existing tools)
- Formatting (use ruff, prettier)
- One-off checks (use CI/CD instead)

### Custom Hook Requirements

**Standard**: Custom hooks MUST follow these patterns

```yaml
- id: custom-check-<purpose>
  name: <Descriptive Name>
  entry: bash -c '<command>'
  language: system
  files: <file-pattern>        # File filter
  pass_filenames: false        # Usually false for custom checks
  stages: [pre-commit]         # Or pre-push
```

**Required elements**:
1. **Descriptive ID**: `custom-<purpose>`
2. **Clear name**: Describes what it checks
3. **File filtering**: Only run on relevant files
4. **Error messages**: Clear explanation of failures
5. **Exit codes**: 0 = pass, non-zero = fail

**Example**:
```yaml
- id: custom-check-todos
  name: Check for unresolved TODOs
  entry: bash -c 'if git diff --cached | grep -i "# TODO:.*FIXME"; then echo "⚠️  Unresolved critical TODOs found"; exit 1; fi'
  language: system
  pass_filenames: false
  stages: [pre-commit]
```

---

## Documentation Standards

### Required Documentation

**Standard**: Projects using pre-commit hooks MUST document

1. **Installation instructions**: `.ai/howto/how-to-install-pre-commit.md`
2. **Custom hook guide**: `.ai/howto/how-to-add-custom-hook.md`
3. **Troubleshooting**: `.ai/howto/how-to-debug-failing-hooks.md`
4. **Standards document**: `.ai/docs/PRE_COMMIT_STANDARDS.md` (this document)

### Configuration Comments

**Standard**: Add comments to `.pre-commit-config.yaml` for clarity

```yaml
# Branch Protection - MUST be first
- id: no-commit-to-main
  ...

# Auto-fix - Runs before validation
- id: make-lint-fix
  ...

# Python Linting - Runs in python-linter container
- id: python-ruff
  ...

# Pre-push - Comprehensive checks before pushing
- id: pre-push-lint-all
  stages: [pre-push]
  ...
```

---

## Best Practices

### Development Workflow

1. **Always create feature branches**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Run auto-fix before committing**
   ```bash
   make lint-fix
   git add -u
   ```

3. **Commit with automatic hook execution**
   ```bash
   git commit -m "Clear, descriptive message"
   ```

4. **Push triggers comprehensive validation**
   ```bash
   git push origin feature/my-feature
   ```

### Hook Maintenance

1. **Update hooks regularly**: `pre-commit autoupdate`
2. **Test after updates**: `pre-commit run --all-files`
3. **Document custom hooks**: Add comments explaining purpose
4. **Review hook output**: Understand failures before skipping
5. **Monitor performance**: Track execution times

### Team Collaboration

1. **Share documentation**: Point team to `.ai/howto/` guides
2. **Standardize skip policies**: Define acceptable use cases
3. **Review hook failures in PRs**: Don't merge with failures
4. **Update hooks together**: Coordinate tool version updates
5. **Document exceptions**: Record when and why hooks were skipped

---

## Troubleshooting Standards

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Hooks not running | Not installed | `pre-commit install` |
| Docker errors | Containers not running | `make lint-ensure-containers` |
| Slow hooks | First run downloads tools | Subsequent runs faster |
| False positives | Tool configuration | Update tool config, not hook |
| Skip not working | Wrong syntax | Use `--no-verify` or `PRE_PUSH_SKIP=1` |

### Debugging Process

**Standard**: Follow this debugging sequence

1. **Check hook installation**
   ```bash
   ls -la .git/hooks/pre-commit
   ```

2. **Test specific hook**
   ```bash
   pre-commit run <hook-id> --all-files --verbose
   ```

3. **Check Docker containers**
   ```bash
   docker ps | grep linter
   ```

4. **Run command manually**
   ```bash
   docker exec <container> <command>
   ```

5. **Review hook configuration**
   ```bash
   cat .pre-commit-config.yaml | grep -A 10 "id: <hook-id>"
   ```

---

## Validation

### Pre-commit Hook Checklist

- [ ] `.pre-commit-config.yaml` exists in project root
- [ ] Pre-commit framework installed
- [ ] Git hooks installed (pre-commit and pre-push)
- [ ] Branch protection configured (no-commit-to-main)
- [ ] Auto-fix runs before validation
- [ ] Language-specific hooks configured
- [ ] Security scanning enabled
- [ ] Pre-push comprehensive validation configured
- [ ] Emergency skip mechanism documented
- [ ] Docker containers configured and running
- [ ] Makefile targets integrated (lint-fix, lint-all, test-all)
- [ ] Documentation complete (installation, usage, troubleshooting)

### Testing Procedure

**Standard**: Test hooks before committing configuration

```bash
# 1. Test all hooks on existing codebase
pre-commit run --all-files

# 2. Test branch protection
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "Test"  # Should fail

# 3. Test feature branch workflow
git checkout -b test-branch
git add test.txt
git commit -m "Test"  # Should succeed

# 4. Test pre-push hooks
git push origin test-branch  # Should run comprehensive checks

# 5. Clean up
git checkout main
git branch -D test-branch
rm test.txt
```

---

## Summary

### Key Standards

1. **Docker-first execution**: All hooks run in containers
2. **Dynamic detection**: Only run hooks for present languages
3. **Staged validation**: Fast pre-commit, thorough pre-push
4. **Auto-fix first**: Fix issues before validating
5. **Branch protection**: Prevent direct commits to main
6. **Security required**: Security scanning is mandatory
7. **Documented skip**: Emergency skip only with documentation
8. **Performance targets**: < 10s pre-commit, < 2min pre-push
9. **Makefile integration**: Integrate with project build system
10. **Complete documentation**: Installation, usage, troubleshooting

### Benefits

- **Consistent quality**: Same tools, same results, always
- **Fast feedback**: Catch issues immediately
- **Comprehensive validation**: Nothing merges without passing checks
- **Team alignment**: Everyone uses same standards
- **CI/CD integration**: Local and remote validation match

---

## References

- **Pre-commit Framework**: https://pre-commit.com/
- **Git Hooks Documentation**: https://git-scm.com/docs/githooks
- **Plugin README**: `README.md`
- **Agent Instructions**: `AGENT_INSTRUCTIONS.md`
- **How-to Guides**: `.ai/howto/how-to-*.md`
