# Version Freshness Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the version-freshness linter for detecting EOL and outdated runtime versions

    **Scope**: Configuration, usage, supported file types, data source, and CI/CD integration

    **Overview**: Comprehensive documentation for the version-freshness linter that checks infrastructure and runtime versions against endoflife.date lifecycle data. Covers supported file types (Dockerfiles, GitHub Actions, version-pinning files, Terraform), configuration options, CLI usage, caching behavior, and CI/CD integration. Helps teams avoid deploying on end-of-life runtimes that AI code generators frequently suggest.

    **Dependencies**: endoflife.date API (MIT-licensed, CDN-cached), requests library, packaging library

    **Exports**: Usage documentation, configuration examples, supported file types reference

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: File-type-specific extractors with endoflife.date API caching and configurable detection levels

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thailint
thailint version-freshness .
```

**Example output:**
```
Dockerfile:1
  [ERROR] version-freshness.eol-version: python 3.8 has reached end of life (EOL: 2024-10-14)
    Suggestion: Upgrade to 3.13
```

**Fix it:** Upgrade to a supported version of the runtime.

---

## Overview

The version-freshness linter checks infrastructure and runtime versions in your project against [endoflife.date](https://endoflife.date) lifecycle data. It detects end-of-life (EOL) versions and optionally flags outdated versions that are supported but not the latest.

### The AI Version Problem

AI code generators frequently suggest outdated runtime versions because their training data skews old. Developers accept these without checking because they look plausible:

```dockerfile
# AI-generated - looks fine but Python 3.8 reached EOL October 2024
FROM python:3.8-slim
```

```yaml
# AI-generated - Node 16 reached EOL September 2023
- uses: actions/setup-node@v4
  with:
    node-version: '16'
```

No existing tool catches this at lint time. Vulnerability scanners check CVEs, update bots create PRs, but nothing says "this version is EOL" during code review.

### What It Checks

This linter targets **infrastructure/runtime versions**, not library versions:

- Docker base images (`FROM python:3.9`)
- GitHub Actions setup steps (`python-version: '3.8'`)
- Version-pinning files (`.python-version`, `.nvmrc`)
- Terraform version constraints (`required_version`)

---

## Supported File Types

| File Type | Pattern | What It Extracts |
|-----------|---------|-----------------|
| Dockerfile | `Dockerfile*` | `FROM image:tag` lines |
| GitHub Actions | `.github/workflows/*.yml` | Version keys in `with:` blocks |
| Python version | `.python-version` | Single version string |
| Node version | `.nvmrc`, `.node-version` | Single version string |
| Tool versions | `.tool-versions` | `tool version` per line (asdf) |
| Mise config | `mise.toml` | `[tools]` section |
| Terraform | `*.tf` | `required_version = "..."` |
| pyproject.toml | `pyproject.toml` | Python version constraint |

### Supported Products

Any product tracked by [endoflife.date](https://endoflife.date/api) (450+ products), including:
Python, Node.js, Go, Java, Ruby, PHP, Rust, Elixir, PostgreSQL, MySQL, Redis, Nginx, Alpine, Ubuntu, Debian, and more.

---

## Rules

### `version-freshness.eol-version` (default: enabled)

Flags versions that have reached end of life. These versions no longer receive security patches.

```dockerfile
# Violation: python 3.8 has reached end of life (EOL: 2024-10-14)
FROM python:3.8-slim
```

### `version-freshness.outdated-runtime` (default: disabled)

Flags versions that are supported but not the latest cycle. This is a stricter check, useful for teams that want to stay on the latest.

```dockerfile
# Violation (with check_outdated: true): python 3.11 is not the latest supported version (latest: 3.13)
FROM python:3.11-slim
```

---

## Configuration

Add to `.thailint.yaml`:

```yaml
version-freshness:
  enabled: true

  # Flag end-of-life versions (default: true)
  check_eol: true

  # Flag non-latest supported versions (default: false, stricter)
  check_outdated: false

  # Cache refresh interval in hours (default: 24)
  cache_ttl_hours: 24

  # Files/patterns to ignore
  ignore:
    - "Dockerfile.legacy"
    - "tests/**"
    - ".github/workflows/compat-test.yml"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the linter |
| `check_eol` | bool | `true` | Flag end-of-life versions |
| `check_outdated` | bool | `false` | Flag non-latest supported versions |
| `cache_ttl_hours` | int | `24` | Hours before refreshing API data |
| `ignore` | list | `[]` | File patterns to skip |

---

## Data Source

Version lifecycle data comes from [endoflife.date](https://endoflife.date):

- **MIT licensed**, open source, 450+ products
- Static JSON on CDN, updated daily by automated bots
- 3,250+ GitHub stars, actively maintained for 7+ years
- No API key required, no rate limiting

### Caching

Data is cached locally at `~/.cache/thailint/endoflife/` with one JSON file per product. Cache behavior:

1. **Fresh cache** (within TTL): Use cached data, no network request
2. **Stale cache** (past TTL): Fetch from API, update cache
3. **Offline fallback**: If API unreachable, use stale cache
4. **No cache**: If no cache and API unreachable, skip product (no false positives)

---

## Ignoring Violations

### Line-level (inline comment)

```dockerfile
FROM python:3.9-slim  # thailint: ignore[version-freshness]
```

```yaml
python-version: '3.9'  # thailint: ignore[version-freshness.eol-version]
```

### Block-level

```yaml
# thailint: ignore-start version-freshness
- uses: actions/setup-python@v5
  with:
    python-version: '3.9'  # intentionally pinned for legacy compat
# thailint: ignore-end
```

### File-level

```dockerfile
# thailint: ignore-file[version-freshness]
FROM python:3.9-slim AS builder
```

### Repository-level

```yaml
# .thailint.yaml
version-freshness:
  ignore:
    - "Dockerfile.legacy"
    - ".python-version"
    - "tests/**"
```

### Comment-less files

Files like `.python-version` and `.nvmrc` have no comment syntax. Use repository-level ignore patterns to suppress violations in these files.

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Check version freshness
  run: |
    pip install thailint
    thailint version-freshness --format sarif . > version-freshness.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: version-freshness.sarif
```

### Pre-commit

```yaml
- repo: local
  hooks:
    - id: version-freshness
      name: Check version freshness
      entry: thailint version-freshness
      language: system
      pass_filenames: false
```

---

## Output Formats

```bash
# Human-readable (default)
thailint version-freshness .

# JSON for CI/CD
thailint version-freshness --format json .

# SARIF for GitHub Code Scanning
thailint version-freshness --format sarif . > results.sarif
```
