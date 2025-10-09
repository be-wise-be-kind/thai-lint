# CLI Reference

**Purpose**: Complete command-line interface reference for all thailint CLI commands

**Scope**: All CLI commands, flags, options, and usage examples for terminal users

**Overview**: Comprehensive CLI documentation covering all commands, flags, and options available
    in the thailint command-line interface. Documents global options, linting commands, configuration
    management, output formats, and exit codes. Provides practical examples for each command with
    expected outputs. Helps users leverage the full power of thailint from the terminal or in
    automation scripts and CI/CD pipelines.

**Dependencies**: Click framework, thailint CLI implementation

**Exports**: CLI usage documentation and examples

**Related**: getting-started.md for basic usage, deployment-modes.md for different execution modes

**Implementation**: Command reference with syntax, parameters, examples, and expected outputs

---

## Overview

thailint provides a comprehensive command-line interface built with Click framework. The CLI supports linting operations, configuration management, and multiple output formats.

## Installation

```bash
# From PyPI
pip install thailint

# From source
git clone https://github.com/YOUR_USERNAME/thai-lint.git
cd thai-lint
pip install -e .

# Verify installation
thailint --version
```

## Command Structure

```
thai-lint [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [PATH...]
```

**Important:** All linting commands now accept **multiple paths** (files or directories). You can pass:
- A single file: `thailint nesting src/main.py`
- Multiple files: `thailint nesting file1.py file2.py file3.py`
- Directories: `thailint nesting src/ tests/`
- Mixed: `thailint nesting src/ main.py utils.py`
- No paths (defaults to current directory): `thailint nesting`

## Global Options

Available for all commands:

```bash
thai-lint [OPTIONS] COMMAND [ARGS]
```

### --version

Show version and exit.

```bash
thai-lint --version
```

**Output:**
```
thai-lint, version 0.1.0
```

### --verbose, -v

Enable verbose output with debug information.

```bash
thai-lint --verbose file-placement .
```

**Output:**
```
2025-10-06 12:34:56 | DEBUG | Loading config from .thailint.yaml
2025-10-06 12:34:56 | DEBUG | Scanning directory: src/
2025-10-06 12:34:56 | DEBUG | Checking file: src/main.py
No violations found
```

### --config, -c PATH

Specify configuration file path.

```bash
thai-lint --config /path/to/config.yaml file-placement .
```

**Supported formats:**
- `.thailint.yaml` (YAML format)
- `.thailint.json` (JSON format)
- Custom path with `--config`

### --help

Show help message and exit.

```bash
thai-lint --help
```

## Commands

### lint

Linting commands for code analysis.

```bash
thai-lint lint [OPTIONS] COMMAND [ARGS]
```

**Subcommands:**
- `file-placement` - Lint files for proper file placement

#### lint file-placement

Lint files for proper file placement according to configuration rules.

```bash
thai-lint file-placement [OPTIONS] [PATH...]
```

**Note:** Accepts multiple paths (files and/or directories).

#### lint nesting

Check for excessive nesting depth in code.

```bash
thai-lint nesting [OPTIONS] [PATH...]
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `PATH...` | No | `.` (current directory) | One or more files/directories to lint |

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--config` | `-c` | PATH | Auto-discover | Path to config file |
| `--rules` | `-r` | TEXT | None | Inline JSON rules |
| `--format` | `-f` | CHOICE | `text` | Output format: `text` or `json` |
| `--recursive` | | FLAG | `True` | Scan directories recursively |
| `--no-recursive` | | FLAG | | Disable recursive scanning |

**Examples:**

**Basic usage:**
```bash
# Lint current directory
thai-lint file-placement

# Lint specific directory
thai-lint file-placement src/

# Lint specific file
thai-lint file-placement src/main.py

# Lint multiple files
thai-lint file-placement src/main.py src/utils.py tests/test_main.py

# Lint multiple directories
thai-lint file-placement src/ tests/

# Mix files and directories
thai-lint file-placement src/ main.py
```

**With configuration file:**
```bash
# Use specific config
thai-lint file-placement --config .thailint.yaml .

# Short form
thai-lint file-placement -c rules.json src/
```

**Inline rules (no config file):**
```bash
# Simple rules
thai-lint file-placement --rules '{"allow": [".*\\.py$"]}' .

# Complex rules
thai-lint file-placement --rules '{
  "allow": [".*\\.py$"],
  "deny": ["test_.*\\.py$"],
  "ignore": ["__pycache__/"]
}' src/
```

**Output formats:**
```bash
# Text format (default, human-readable)
thai-lint file-placement --format text .

# JSON format (for parsing/CI/CD)
thai-lint file-placement --format json .
```

**Recursive vs non-recursive:**
```bash
# Recursive (default) - scan all subdirectories
thai-lint file-placement --recursive src/

# Non-recursive - scan only top-level files
thai-lint file-placement --no-recursive src/
```

**Output Examples:**

**Text format (violations found):**
```
Found 2 violations:

src/test_example.py:
  Rule: file-placement
  Message: Test files should be in tests/ directory
  Severity: ERROR

config.py:
  Rule: file-placement
  Message: Python files should be in src/ directory
  Severity: ERROR

Exit code: 1
```

**Text format (no violations):**
```
No violations found

Exit code: 0
```

**JSON format:**
```json
[
  {
    "file_path": "src/test_example.py",
    "rule_id": "file-placement",
    "message": "Test files should be in tests/ directory",
    "severity": "ERROR"
  },
  {
    "file_path": "config.py",
    "rule_id": "file-placement",
    "message": "Python files should be in src/ directory",
    "severity": "ERROR"
  }
]
```

---

### nesting

Check for excessive nesting depth in Python and TypeScript code.

```bash
thai-lint nesting [OPTIONS] [PATH...]
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `PATH...` | No | `.` (current directory) | One or more files/directories to check |

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--config` | `-c` | PATH | Auto-discover | Path to config file |
| `--max-depth` | `-d` | INTEGER | `4` | Maximum allowed nesting depth |
| `--format` | `-f` | CHOICE | `text` | Output format: `text` or `json` |

**Examples:**

**Basic usage:**
```bash
# Check current directory
thai-lint nesting

# Check specific directory
thai-lint nesting src/

# Check specific file
thai-lint nesting src/main.py

# Check multiple files
thai-lint nesting src/main.py src/utils.py src/handler.py

# Check multiple directories
thai-lint nesting src/ tests/

# Mix files and directories
thai-lint nesting src/ main.py helpers/
```

**With custom max depth:**
```bash
# Strict limit (depth 3)
thai-lint nesting --max-depth 3 src/

# Very strict (depth 2)
thai-lint nesting --max-depth 2 src/

# Lenient (depth 5)
thai-lint nesting --max-depth 5 src/
```

**With configuration file:**
```bash
# Use specific config
thai-lint nesting --config .thailint.yaml src/

# Short form
thai-lint nesting -c rules.yaml -d 3 src/
```

**Output formats:**
```bash
# Text format (default, human-readable)
thai-lint nesting src/

# JSON format (for parsing/CI/CD)
thai-lint nesting --format json src/
```

**Output Examples:**

**Text format (violations found):**
```
Found 2 violations:

src/processor.py:15
  Rule: nesting.excessive-depth
  Function: process_data
  Message: Function has nesting depth 5 (max: 3)
  Suggestion: Consider refactoring with guard clauses or extract method
  Severity: ERROR

src/handler.py:42
  Rule: nesting.excessive-depth
  Function: handle_request
  Message: Function has nesting depth 4 (max: 3)
  Suggestion: Use early returns to reduce nesting
  Severity: ERROR

Exit code: 1
```

**Text format (no violations):**
```
No violations found

Exit code: 0
```

**JSON format:**
```json
{
  "violations": [
    {
      "file_path": "src/processor.py",
      "line_number": 15,
      "rule_id": "nesting.excessive-depth",
      "message": "Function 'process_data' has nesting depth 5 (max: 3)",
      "severity": "ERROR"
    },
    {
      "file_path": "src/handler.py",
      "line_number": 42,
      "rule_id": "nesting.excessive-depth",
      "message": "Function 'handle_request' has nesting depth 4 (max: 3)",
      "severity": "ERROR"
    }
  ],
  "total": 2
}
```

**Language Support:**
- Python (`.py`) - Full support
- TypeScript (`.ts`, `.tsx`) - Full support
- JavaScript (`.js`, `.jsx`) - Supported via TypeScript parser

**Common Patterns:**

```bash
# Strict project-wide check
thai-lint nesting --max-depth 3 .

# Check only source code
thai-lint nesting src/

# CI/CD integration
thai-lint nesting --format json src/ > nesting-report.json

# With verbose output
thai-lint --verbose nesting src/
```

**See Also:**
- `docs/nesting-linter.md` - Comprehensive nesting linter guide
- Refactoring patterns and best practices
- Configuration examples

---

### dry

Detect duplicate code using token-based hash analysis with SQLite caching.

```bash
thai-lint dry [OPTIONS] [PATH...]
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `PATH...` | No | `.` (current directory) | One or more files/directories to check |

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--config` | `-c` | PATH | Auto-discover | Path to config file |
| `--min-lines` | `-l` | INTEGER | `4` | Minimum duplicate lines |
| `--format` | `-f` | CHOICE | `text` | Output format: `text` or `json` |
| `--no-cache` | | FLAG | `False` | Disable SQLite caching |
| `--clear-cache` | | FLAG | `False` | Clear cache before running |
| `--recursive` | | FLAG | `True` | Scan directories recursively |

**Examples:**

**Basic usage:**
```bash
# Check current directory
thai-lint dry

# Check specific directory
thai-lint dry src/

# Check specific file
thai-lint dry src/main.py

# Check multiple files
thai-lint dry src/api.py src/handler.py src/processor.py

# Check multiple directories
thai-lint dry src/ lib/

# Mix files and directories
thai-lint dry src/ utils.py helpers/
```

**With custom thresholds:**
```bash
# Strict duplicate detection (3 lines)
thai-lint dry --min-lines 3 src/

# Lenient detection (6 lines)
thai-lint dry --min-lines 6 src/
```

**Cache management:**
```bash
# Run without cache
thai-lint dry --no-cache src/

# Clear cache before run
thai-lint dry --clear-cache src/

# Clear cache only
thai-lint dry --clear-cache .
```

**With configuration file:**
```bash
# Use specific config
thai-lint dry --config .thailint.yaml src/

# Short form
thai-lint dry -c rules.yaml src/
```

**Output formats:**
```bash
# Text format (default, human-readable)
thai-lint dry src/

# JSON format (for parsing/CI/CD)
thai-lint dry --format json src/
```

**Output Examples:**

**Text format (violations found):**
```
Found 3 duplicate code blocks:

Duplicate in 3 files (5 lines, 42 tokens):
  src/api.py:15-19
  src/handler.py:28-32
  src/processor.py:42-46
Suggestion: Extract common logic into shared function

Duplicate in 2 files (4 lines, 38 tokens):
  src/utils.py:55-58
  src/helpers.py:120-123
Suggestion: Consider creating utility function

Exit code: 1
```

**Text format (no violations):**
```
No duplicate code found

Exit code: 0
```

**JSON format:**
```json
{
  "violations": [
    {
      "duplicate_group": {
        "hash": "a1b2c3d4e5f6",
        "line_count": 5,
        "token_count": 42,
        "occurrences": [
          {
            "file_path": "src/api.py",
            "line_start": 15,
            "line_end": 19
          },
          {
            "file_path": "src/handler.py",
            "line_start": 28,
            "line_end": 32
          },
          {
            "file_path": "src/processor.py",
            "line_start": 42,
            "line_end": 46
          }
        ]
      },
      "message": "Duplicate code found in 3 locations",
      "severity": "WARNING"
    }
  ],
  "total": 1,
  "cache_stats": {
    "cache_hits": 45,
    "cache_misses": 12,
    "hit_rate": 0.79
  }
}
```

**Language Support:**
- Python (`.py`) - Full support with AST tokenization
- TypeScript (`.ts`, `.tsx`) - Full support with tree-sitter
- JavaScript (`.js`, `.jsx`) - Full support with tree-sitter

**Performance:**
```bash
# First run (no cache)
thai-lint dry src/
# ~2-3 seconds for 100 files

# Subsequent runs (with cache)
thai-lint dry src/
# ~200-300ms for 100 files (10-50x speedup)
```

**Cache Location:**
```bash
# Default cache location
.thailint-cache/dry.db

# Check cache stats
sqlite3 .thailint-cache/dry.db "SELECT COUNT(*) FROM blocks;"

# Clear cache manually
rm -rf .thailint-cache/
```

**Common Patterns:**

```bash
# Strict project-wide check
thai-lint dry --min-lines 3 .

# Check only source code
thai-lint dry src/

# Check multiple specific files (useful for pre-commit hooks)
thai-lint dry file1.py file2.py file3.py

# CI/CD integration with fresh cache
thai-lint dry --clear-cache --format json src/ > dry-report.json

# Quick check without cache (for testing config)
thai-lint dry --no-cache --min-lines 5 src/

# With verbose output
thai-lint --verbose dry src/
```

**Configuration Examples:**

Simple config (`.thailint.yaml`):
```yaml
dry:
  enabled: true
  min_duplicate_lines: 4
  min_duplicate_tokens: 30
  min_occurrences: 2
```

Advanced config with language-specific thresholds:
```yaml
dry:
  enabled: true
  min_duplicate_lines: 4
  min_duplicate_tokens: 30
  min_occurrences: 2

  # Language-specific overrides
  python:
    min_occurrences: 3      # Python: require 3+ duplicates
    min_duplicate_lines: 5

  typescript:
    min_duplicate_tokens: 35

  # Cache settings
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
  cache_max_age_days: 30

  # Ignore patterns
  ignore:
    - "tests/"
    - "__init__.py"
    - "migrations/"

  # False positive filtering
  filters:
    keyword_argument_filter: true
    import_group_filter: true
```

**Troubleshooting:**

**Cache issues:**
```bash
# Clear and rebuild cache
thai-lint dry --clear-cache src/

# Disable cache temporarily
thai-lint dry --no-cache src/

# Remove cache directory
rm -rf .thailint-cache/
```

**No duplicates found:**
```bash
# Lower thresholds
thai-lint dry --min-lines 3 src/

# Check verbose output
thai-lint --verbose dry src/

# Verify files are being scanned
thai-lint --verbose dry --no-cache src/ 2>&1 | grep "Analyzing"
```

**False positives:**
```bash
# Enable filters in config
dry:
  filters:
    keyword_argument_filter: true
    import_group_filter: true

# Or ignore specific directories
dry:
  ignore:
    - "tests/"
    - "generated/"
```

**See Also:**
- `docs/dry-linter.md` - Comprehensive DRY linter guide
- Token-based detection algorithm
- Refactoring patterns for duplicates
- Cache management and performance

---

### config

Configuration management commands.

```bash
thai-lint config [OPTIONS] COMMAND [ARGS]
```

**Subcommands:**
- `show` - Display current configuration
- `get` - Get specific configuration value
- `set` - Set configuration value
- `reset` - Reset to default configuration

#### config show

Display current configuration.

```bash
thai-lint config show [OPTIONS]
```

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--format` | `-f` | CHOICE | `text` | Output format: `text`, `json`, or `yaml` |

**Examples:**

```bash
# Show config as text
thai-lint config show

# Show as JSON
thai-lint config show --format json

# Show as YAML
thai-lint config show --format yaml
```

**Output (text):**
```
Configuration:
  app_name: thai-lint
  log_level: INFO
  output_format: text
  greeting: Hello
  max_retries: 3
  timeout: 30
```

**Output (JSON):**
```json
{
  "app_name": "thai-lint",
  "log_level": "INFO",
  "output_format": "text",
  "greeting": "Hello",
  "max_retries": 3,
  "timeout": 30
}
```

#### config get

Get specific configuration value.

```bash
thai-lint config get KEY
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `KEY` | Yes | Configuration key to retrieve |

**Examples:**

```bash
# Get log level
thai-lint config get log_level
# Output: INFO

# Get greeting
thai-lint config get greeting
# Output: Hello

# Get non-existent key
thai-lint config get nonexistent
# Output: Error: Key 'nonexistent' not found
```

#### config set

Set configuration value.

```bash
thai-lint config set KEY VALUE
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `KEY` | Yes | Configuration key to set |
| `VALUE` | Yes | Value to set |

**Examples:**

```bash
# Set log level
thai-lint config set log_level DEBUG
# Output: Set log_level = DEBUG

# Set greeting
thai-lint config set greeting "Hi"
# Output: Set greeting = Hi

# Verify change
thai-lint config get log_level
# Output: DEBUG
```

#### config reset

Reset configuration to defaults.

```bash
thai-lint config reset [OPTIONS]
```

**Options:**

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--yes` | `-y` | FLAG | Skip confirmation prompt |

**Examples:**

```bash
# Reset with confirmation
thai-lint config reset
# Prompt: Are you sure? [y/N]:

# Reset without confirmation
thai-lint config reset --yes
# Output: Configuration reset to defaults
```

### hello

Print a greeting message (example command).

```bash
thai-lint hello [OPTIONS]
```

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--name` | `-n` | TEXT | `World` | Name to greet |
| `--uppercase` | `-u` | FLAG | `False` | Convert to uppercase |

**Examples:**

```bash
# Basic greeting
thai-lint hello
# Output: Hello, World!

# Custom name
thai-lint hello --name Alice
# Output: Hello, Alice!

# Uppercase
thai-lint hello --name Bob --uppercase
# Output: HELLO, BOB!

# Short form
thai-lint hello -n Charlie -u
# Output: HELLO, CHARLIE!
```

## Exit Codes

thailint uses standard exit codes for CI/CD integration:

| Exit Code | Meaning | Description |
|-----------|---------|-------------|
| `0` | Success | No violations found |
| `1` | Violations Found | Linting failed, violations detected |
| `2` | Error | Command error (invalid config, file not found, etc.) |

**Examples:**

```bash
# Check exit code (bash)
thai-lint file-placement .
echo $?  # 0 = success, 1 = violations, 2 = error

# Use in script
thai-lint file-placement src/
if [ $? -eq 0 ]; then
    echo "Linting passed"
else
    echo "Linting failed"
    exit 1
fi

# GitHub Actions
- name: Run linter
  run: |
    thai-lint file-placement .
    # Non-zero exit code will fail the job
```

## Common Usage Patterns

### Quick Linting

```bash
# Lint current directory
thai-lint file-placement

# Lint with auto-discovered config
thai-lint file-placement .

# Lint specific directory
thai-lint file-placement src/
```

### CI/CD Integration

```bash
# GitHub Actions / GitLab CI
thai-lint file-placement . --format json > lint-report.json
if [ $? -ne 0 ]; then
    echo "Linting failed - see lint-report.json"
    exit 1
fi

# Jenkins
thai-lint file-placement --config .thailint.yaml . || exit 1

# Azure Pipelines
thai-lint file-placement --format json . | tee lint-report.json
test ${PIPESTATUS[0]} -eq 0
```

### Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running thailint..."
thai-lint file-placement .

if [ $? -ne 0 ]; then
    echo "Pre-commit linting failed"
    echo "Fix violations or use 'git commit --no-verify' to skip"
    exit 1
fi

echo "Pre-commit linting passed"
```

### Multiple Configs

```bash
# Development config
thai-lint file-placement --config .thailint.dev.yaml .

# Production config
thai-lint file-placement --config .thailint.prod.yaml .

# Test config
thai-lint file-placement --config .thailint.test.yaml tests/
```

### Combined with Other Tools

```bash
# With pytest
pytest && thai-lint file-placement .

# With mypy
mypy src/ && thai-lint file-placement src/

# With ruff
ruff check src/ && thai-lint file-placement src/

# All checks
pytest && mypy src/ && ruff check src/ && thai-lint file-placement .
```

### Filtering Output

```bash
# Grep for specific files
thai-lint file-placement . | grep "test_"

# Count violations
thai-lint file-placement . --format json | jq length

# Extract file paths
thai-lint file-placement . --format json | jq -r '.[].file_path'

# Filter by severity
thai-lint file-placement . --format json | jq '.[] | select(.severity == "ERROR")'
```

## Shell Completion

### Bash

```bash
# Add to ~/.bashrc
eval "$(_THAI_LINT_COMPLETE=bash_source thai-lint)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_THAI_LINT_COMPLETE=zsh_source thai-lint)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
eval (env _THAI_LINT_COMPLETE=fish_source thai-lint)
```

## Environment Variables

### THAILINT_CONFIG

Override default config file location.

```bash
export THAILINT_CONFIG=/path/to/config.yaml
thai-lint file-placement .
```

### THAILINT_LOG_LEVEL

Set log level without config.

```bash
export THAILINT_LOG_LEVEL=DEBUG
thai-lint file-placement .
```

### PYTHONPATH

Required for running examples.

```bash
export PYTHONPATH=/path/to/thai-lint
python examples/basic_usage.py
```

## Debugging

### Verbose Mode

```bash
# Enable debug logging
thai-lint --verbose file-placement .

# With environment variable
THAILINT_LOG_LEVEL=DEBUG thai-lint file-placement .
```

### Dry Run (Check Config)

```bash
# Show what would be linted
thai-lint --verbose file-placement --no-recursive . 2>&1 | grep "Checking file"

# Validate config
thai-lint config show --format yaml
```

### Common Issues

**Issue: Command not found**
```bash
# Solution 1: Use python module
python -m src.cli lint file-placement .

# Solution 2: Install package
pip install -e .
thai-lint --help
```

**Issue: Config not found**
```bash
# Solution: Specify explicitly
thai-lint file-placement --config .thailint.yaml .

# Or check current directory
ls -la .thailint.*
```

**Issue: No violations shown**
```bash
# Solution: Use verbose mode
thai-lint --verbose file-placement .

# Check config is valid
thai-lint config show
```

## Advanced Usage

### Programmatic CLI Usage

```python
import subprocess

result = subprocess.run(
    ['thai-lint', 'lint', 'file-placement', 'src/', '--format', 'json'],
    capture_output=True,
    text=True
)

exit_code = result.returncode  # 0, 1, or 2
output = result.stdout

if exit_code == 0:
    print("No violations")
elif exit_code == 1:
    import json
    violations = json.loads(output)
    print(f"Found {len(violations)} violations")
elif exit_code == 2:
    print(f"Error: {result.stderr}")
```

### Custom Scripts

```bash
#!/bin/bash
# custom-lint.sh - Custom linting script

CONFIG="${1:-.thailint.yaml}"
TARGET="${2:-.}"

echo "Linting $TARGET with $CONFIG..."

thai-lint file-placement \
    --config "$CONFIG" \
    --format json \
    "$TARGET" > lint-report.json

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "No violations found"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "Violations found:"
    jq -r '.[] | "  - \(.file_path): \(.message)"' lint-report.json
else
    echo "Error occurred"
fi

exit $EXIT_CODE
```

Usage:
```bash
./custom-lint.sh .thailint.yaml src/
```

## Quick Reference

### Essential Commands

```bash
# Basic linting
thai-lint file-placement .

# With config
thai-lint file-placement -c .thailint.yaml .

# JSON output
thai-lint file-placement -f json .

# Verbose mode
thai-lint -v lint file-placement .

# Show config
thai-lint config show

# Help
thai-lint --help
thai-lint lint --help
thai-lint file-placement --help
```

### Common Flags

```
-v, --verbose         Enable debug output
-c, --config PATH     Specify config file
-f, --format FORMAT   Output format (text/json)
-r, --rules TEXT      Inline JSON rules
--recursive           Scan recursively (default)
--no-recursive        Scan top-level only
```

## Next Steps

- **[Getting Started](getting-started.md)** - Basic CLI usage
- **[Configuration](configuration.md)** - Config file reference
- **[API Reference](api-reference.md)** - Library usage
- **[Deployment Modes](deployment-modes.md)** - CLI, Library, Docker
