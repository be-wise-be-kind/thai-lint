# Quick Start Guide

Get up and running with thailint in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

```bash
pip install thailint
```

Or run instantly with [`uvx`](https://docs.astral.sh/uv/concepts/tools/) (no install required):
```bash
uvx thailint dry src/
```

Or with Docker:
```bash
docker pull washad/thailint:latest
docker run --rm washad/thailint:latest --help
```

## Your First Lint

### Step 1: Verify Installation

```bash
thailint --help
```

### Step 2: Generate a Configuration File (Optional)

```bash
# Generate config with lenient preset (recommended for existing projects)
thailint init-config --preset lenient

# Or use interactive mode
thailint init-config
```

**Presets:**
- `strict`: Only -1, 0, 1 allowed (best for new projects)
- `standard`: Balanced defaults
- `lenient`: Includes time conversions (60s, 3600s) and common sizes

### Step 3: Run Your First Lint

```bash
# Pick any linter and point it at your code
thailint dry src/
thailint nesting src/
thailint magic-numbers src/
```

### Step 4: Understanding the Output

**Example output:**
```
src/app.py:42:15 - Magic number 3600 should be a named constant
  Suggestion: Extract 3600 to a named constant (e.g., TIMEOUT_SECONDS = 3600)
```

**What this means:**
- `src/app.py:42:15` - File path, line number, column number
- `Magic number 3600` - The issue detected
- `Suggestion` - How to fix it

**Exit codes:**
- `0` - No violations found (success)
- `1` - Violations found
- `2` - Error occurred

## Ignoring Violations

```python
# Line-level
timeout = 3600  # thailint: ignore[magic-numbers]

# File-level
# thailint: ignore-file[magic-numbers]
```

Or in config:
```yaml
magic-numbers:
  ignore:
    - "tests/"
    - "**/generated/**"
```

See **[How to Ignore Violations](how-to-ignore-violations.md)** for the complete 5-level ignore system.

## CI/CD Integration

```yaml
# GitHub Actions
- name: Run thailint
  run: |
    pip install thailint
    thailint dry src/
    thailint nesting src/
```

See **[Pre-commit Hooks Guide](pre-commit-hooks.md)** for automated checks on every commit.

## Next Steps

1. **[Configuration Reference](configuration.md)** - All config options
2. **[CLI Reference](cli-reference.md)** - All commands and flags
3. **[Troubleshooting Guide](troubleshooting.md)** - Common issues
4. **Browse linter guides** - Each linter has a detailed doc (see sidebar)

## FAQ

### Q: Why am I getting so many violations?

This is normal for existing codebases. Options:

1. Use lenient preset: `thailint init-config --preset lenient`
2. Add to ignore list in config
3. Start with one linter at a time

### Q: Do I need a config file?

No. thailint works with sensible defaults. Config files are optional.

---

**Ready to go?** Start linting and check the [Configuration Reference](configuration.md) for customization options.
