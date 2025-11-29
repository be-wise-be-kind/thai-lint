# Quick Start Guide

Get up and running with thailint in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

### Option 1: From Source (Current)

```bash
# Clone the repository
git clone https://github.com/be-wise-be-kind/thai-lint.git
cd thai-lint

# Install with Poetry
poetry install

# Or install with pip
pip install -e ".[dev]"
```

### Option 2: From PyPI

```bash
pip install thai-lint
```

### Option 3: Docker

```bash
# Pull the image
docker pull washad/thailint:latest

# Verify installation
docker run --rm washad/thailint:latest --help
```

## Your First Lint (60 Seconds)

### Step 1: Verify Installation

```bash
thailint --help
```

You should see the help output with available commands.

### Step 2: Generate a Configuration File

thailint includes an `init-config` command that creates a `.thailint.yaml` file with preset configurations:

```bash
# Generate config with lenient preset (recommended for existing projects)
thailint init-config --preset lenient

# Or use interactive mode
thailint init-config
```

**Presets explained:**
- `strict`: Only -1, 0, 1 allowed (best for new projects)
- `standard`: Balanced defaults including 2, 10, 100, 1000
- `lenient`: Includes time conversions (60s, 3600s) and common sizes (1024)

### Step 3: Run Your First Lint

```bash
# Check for magic numbers in your source code
thailint magic-numbers src/

# Check nesting depth
thailint nesting src/

# Check for duplicate code
thailint dry src/
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
- `2` - Error occurred (config not found, invalid syntax, etc.)

## Common First Commands

### Magic Numbers

```bash
# Lint specific file
thailint magic-numbers src/app.py

# Lint directory recursively
thailint magic-numbers src/

# Use custom config
thailint magic-numbers --config .thailint.yaml src/

# Get JSON output (for CI/CD)
thailint magic-numbers --format json src/
```

### Nesting Depth

```bash
# Check with default max depth (4)
thailint nesting src/

# Use stricter limit
thailint nesting --max-depth 3 src/

# Check specific files
thailint nesting src/app.py src/utils.py
```

### Duplicate Code (DRY)

```bash
# Check for duplicates
thailint dry src/

# Override minimum duplicate lines
thailint dry --min-lines 5 src/

# Clear cache and run fresh
thailint dry --clear-cache src/
```

## Customizing Your Configuration

Edit `.thailint.yaml` to customize settings:

```yaml
magic-numbers:
  enabled: true
  # Add project-specific numbers
  allowed_numbers: [-1, 0, 1, 2, 10, 60, 100, 1000, 1024, 3600]
  max_small_integer: 10

  # Ignore specific files or patterns
  ignore:
    - "test/**"
    - "**/test_*.py"
    - "backend/app/famous_tracks.py"

nesting:
  enabled: true
  max_nesting_depth: 3  # Stricter than default (4)

dry:
  enabled: true
  min_duplicate_lines: 4
  ignore:
    - "tests/"
    - "__init__.py"
```

See the **[Configuration Reference](configuration.md)** for complete options.

## Ignoring Violations

### Line-Level Ignores

```python
# Ignore specific violation on this line
timeout = 3600  # thailint: ignore[magic-numbers]
```

### Method-Level Ignores

```python
def get_ports():  # thailint: ignore[magic-numbers]
    """Standard ports don't need extraction."""
    return {80: "HTTP", 443: "HTTPS", 8080: "HTTP-ALT"}
```

### File-Level Ignores

```python
# thailint: ignore-file[magic-numbers]
"""This entire file is ignored for magic numbers."""
```

### Config-Level Ignores

```yaml
magic-numbers:
  ignore:
    - "backend/app/famous_tracks.py"  # Specific file
    - "**/test_*.py"                  # Glob pattern
    - "tools/**"                      # Entire directory
```

See **[How to Ignore Violations](how-to-ignore-violations.md)** for the complete 5-level ignore system.

## Using with Docker

```bash
# Mount current directory and lint
docker run --rm -v $(pwd):/data washad/thailint:latest magic-numbers /data/src

# With custom config
docker run --rm -v $(pwd):/data \
  washad/thailint:latest magic-numbers --config /data/.thailint.yaml /data/src
```

**Important:** Paths must be absolute inside the container (`/data/...`).

## Integrating with CI/CD

### GitHub Actions

```yaml
name: Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Run linters
        run: |
          thailint magic-numbers src/
          thailint nesting src/
          thailint dry src/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test it works
pre-commit run --all-files
```

See **[Pre-commit Hooks Guide](pre-commit-hooks.md)** for complete setup.

## Next Steps

Now that you're up and running:

1. **Explore Configuration**: Read the [Configuration Reference](configuration.md) to customize thailint for your project
2. **Learn Linters**: Deep-dive into specific linters:
   - [Magic Numbers Linter](magic-numbers-linter.md)
   - [Nesting Depth Linter](nesting-linter.md)
   - [DRY Linter](dry-linter.md)
   - [SRP Linter](srp-linter.md)
3. **Troubleshooting**: Check the [Troubleshooting Guide](troubleshooting.md) for common issues
4. **Ignore System**: Master the [5-level ignore system](how-to-ignore-violations.md)

## Getting Help

- **Issues**: https://github.com/be-wise-be-kind/thai-lint/issues
- **Documentation**: Browse the [docs/](.) folder
- **Examples**: See [examples/](../examples/) for working code

## Common Questions

### Q: How do I know which preset to use?

- **New project?** Start with `strict`
- **Existing project?** Use `lenient` to minimize false positives
- **Want balance?** Try `standard`

You can always customize `allowed_numbers` in `.thailint.yaml` after generation.

### Q: Why am I getting so many violations?

This is normal for existing codebases! Options:

1. **Use lenient preset**: `thailint init-config --preset lenient`
2. **Add project-specific numbers**: Edit `allowed_numbers` in `.thailint.yaml`
3. **Use file-level ignores**: Add patterns to `ignore` list in config
4. **Gradual adoption**: Start with one linter at a time

### Q: Do I need a config file?

No! thailint works with sensible defaults. Config files are optional for customization.

### Q: Can I use multiple linters together?

Yes! Run them separately or combine in CI/CD:

```bash
thailint magic-numbers src/ && \
thailint nesting src/ && \
thailint dry src/
```

Each linter returns exit code 0 (success) or 1 (violations).

---

**Ready to go?** Start linting your code and check the [Configuration Reference](configuration.md) for advanced options!
