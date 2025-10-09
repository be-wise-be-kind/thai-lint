# thai-lint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-317%2F317%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](htmlcov/)

The AI Linter - Enterprise-ready linting and governance for AI-generated code across multiple languages.

## Overview

thailint is a modern, enterprise-ready multi-language linter designed specifically for AI-generated code. It enforces project structure, file placement rules, and coding standards across Python, TypeScript, and other languages.

## ✨ Features

### Core Capabilities
- **File Placement Linting** - Enforce project structure and organization
- **Nesting Depth Linting** - Detect excessive code nesting with AST analysis
  - Python and TypeScript support with tree-sitter
  - Configurable max depth (default: 4, recommended: 3)
  - Helpful refactoring suggestions (guard clauses, extract method)
- **SRP Linting** - Detect Single Responsibility Principle violations
  - Heuristic-based analysis (method count, LOC, keywords)
  - Language-specific thresholds (Python, TypeScript, JavaScript)
  - Refactoring patterns from real-world examples
- **Pluggable Architecture** - Easy to extend with custom linters
- **Multi-Language Support** - Python, TypeScript, JavaScript, and more
- **Flexible Configuration** - YAML/JSON configs with pattern matching
- **5-Level Ignore System** - Repo, directory, file, method, and line-level ignores

### Deployment Modes
- **CLI Mode** - Full-featured command-line interface
- **Library API** - Python library for programmatic integration
- **Docker Support** - Containerized deployment for CI/CD

### Enterprise Features
- **Performance** - <100ms for single files, <5s for 1000 files
- **Type Safety** - Full type hints and MyPy strict mode
- **Test Coverage** - 90% coverage with 317 tests
- **CI/CD Ready** - Proper exit codes and JSON output
- **Comprehensive Docs** - Complete documentation and examples

## Installation

### From Source

```bash
# Clone repository
git clone https://github.com/be-wise-be-kind/thai-lint.git
cd thai-lint

# Install dependencies
pip install -e ".[dev]"
```

### From PyPI (once published)

```bash
pip install thai-lint
```

### With Docker

```bash
# Pull from Docker Hub
docker pull washad/thailint:latest

# Run CLI
docker run --rm washad/thailint:latest --help
```

## Quick Start

### CLI Mode

```bash
# Check file placement
thailint file-placement .

# Check nesting depth
thailint nesting src/

# With config file
thailint nesting --config .thailint.yaml src/

# JSON output for CI/CD
thailint nesting --format json src/
```

### Library Mode

```python
from src import Linter

# Initialize linter
linter = Linter(config_file='.thailint.yaml')

# Lint directory
violations = linter.lint('src/', rules=['file-placement'])

# Process results
if violations:
    for v in violations:
        print(f"{v.file_path}: {v.message}")
```

### Docker Mode

```bash
# Run with volume mount
docker run --rm -v $(pwd):/data \
  washad/thailint:latest file-placement /data

# Check nesting depth
docker run --rm -v $(pwd):/data \
  washad/thailint:latest nesting /data
```

## Configuration

Create `.thailint.yaml` in your project root:

```yaml
# File placement linter configuration
file-placement:
  enabled: true

  # Global patterns apply to entire project
  global_patterns:
    deny:
      - pattern: "^(?!src/|tests/).*\\.py$"
        message: "Python files must be in src/ or tests/"

  # Directory-specific rules
  directories:
    src:
      allow:
        - ".*\\.py$"
      deny:
        - "test_.*\\.py$"

    tests:
      allow:
        - "test_.*\\.py$"
        - "conftest\\.py$"

  # Files/directories to ignore
  ignore:
    - "__pycache__/"
    - "*.pyc"
    - ".venv/"

# Nesting depth linter configuration
nesting:
  enabled: true
  max_nesting_depth: 4  # Maximum allowed nesting depth

  # Language-specific settings (optional)
  languages:
    python:
      max_depth: 4
    typescript:
      max_depth: 4
    javascript:
      max_depth: 4
```

**JSON format also supported** (`.thailint.json`):

```json
{
  "file-placement": {
    "enabled": true,
    "directories": {
      "src": {
        "allow": [".*\\.py$"],
        "deny": ["test_.*\\.py$"]
      }
    },
    "ignore": ["__pycache__/", "*.pyc"]
  },
  "nesting": {
    "enabled": true,
    "max_nesting_depth": 4,
    "languages": {
      "python": { "max_depth": 4 },
      "typescript": { "max_depth": 4 }
    }
  }
}
```

See [Configuration Guide](docs/configuration.md) for complete reference.

## Nesting Depth Linter

### Overview

The nesting depth linter detects deeply nested code (if/for/while/try statements) that reduces readability and maintainability. It uses AST analysis to accurately calculate nesting depth.

### Quick Start

```bash
# Check nesting depth in current directory
thailint nesting .

# Use strict limit (max depth 3)
thailint nesting --max-depth 3 src/

# Get JSON output
thailint nesting --format json src/
```

### Configuration

Add to `.thailint.yaml`:

```yaml
nesting:
  enabled: true
  max_nesting_depth: 3  # Default: 4, recommended: 3
```

### Example Violation

**Code with excessive nesting:**
```python
def process_data(items):
    for item in items:              # Depth 2
        if item.is_valid():         # Depth 3
            try:                    # Depth 4 ← VIOLATION (max=3)
                if item.process():
                    return True
            except Exception:
                pass
    return False
```

**Refactored with guard clauses:**
```python
def process_data(items):
    for item in items:              # Depth 2
        if not item.is_valid():
            continue
        try:                        # Depth 3 ✓
            if item.process():
                return True
        except Exception:
            pass
    return False
```

### Refactoring Patterns

Common patterns to reduce nesting:

1. **Guard Clauses (Early Returns)**
   - Replace `if x: do_something()` with `if not x: return`
   - Exit early, reduce nesting

2. **Extract Method**
   - Move nested logic to separate functions
   - Improves readability and testability

3. **Dispatch Pattern**
   - Replace if-elif-else chains with dictionary dispatch
   - More extensible and cleaner

4. **Flatten Error Handling**
   - Combine multiple try-except blocks
   - Use tuple of exception types

### Language Support

- ✅ **Python**: Full support (if/for/while/with/try/match)
- ✅ **TypeScript**: Full support (if/for/while/try/switch)
- ✅ **JavaScript**: Supported via TypeScript parser

See [Nesting Linter Guide](docs/nesting-linter.md) for comprehensive documentation and refactoring patterns.

## Single Responsibility Principle (SRP) Linter

### Overview

The SRP linter detects classes that violate the Single Responsibility Principle by having too many methods, too many lines of code, or generic naming patterns. It uses AST analysis with configurable heuristics to identify classes that likely handle multiple responsibilities.

### Quick Start

```bash
# Check SRP violations in current directory
thailint srp .

# Use custom thresholds
thailint srp --max-methods 10 --max-loc 300 src/

# Get JSON output
thailint srp --format json src/
```

### Configuration

Add to `.thailint.yaml`:

```yaml
srp:
  enabled: true
  max_methods: 7    # Maximum methods per class
  max_loc: 200      # Maximum lines of code per class

  # Language-specific thresholds
  python:
    max_methods: 8
    max_loc: 200

  typescript:
    max_methods: 10  # TypeScript more verbose
    max_loc: 250
```

### Detection Heuristics

The SRP linter uses three heuristics to detect violations:

1. **Method Count**: Classes with >7 methods (default) likely have multiple responsibilities
2. **Lines of Code**: Classes with >200 LOC (default) are often doing too much
3. **Responsibility Keywords**: Names containing "Manager", "Handler", "Processor", etc.

### Example Violation

**Code with SRP violation:**
```python
class UserManager:  # 8 methods, contains "Manager" keyword
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def send_email(self): pass      # ← Different responsibility
    def log_action(self): pass      # ← Different responsibility
    def validate_data(self): pass   # ← Different responsibility
    def generate_report(self): pass # ← Different responsibility
    def export_data(self): pass     # ← Violation at method 8
```

**Refactored following SRP:**
```python
class UserRepository:  # 3 methods ✓
    def create(self, user): pass
    def update(self, user): pass
    def delete(self, user): pass

class EmailService:  # 1 method ✓
    def send(self, user, template): pass

class UserAuditLog:  # 1 method ✓
    def log(self, action, user): pass

class UserValidator:  # 1 method ✓
    def validate(self, data): pass

class ReportGenerator:  # 1 method ✓
    def generate(self, users): pass
```

### Refactoring Patterns

Common patterns to fix SRP violations (discovered during dogfooding):

1. **Extract Class**
   - Split god classes into focused classes
   - Each class handles one responsibility

2. **Split Configuration and Logic**
   - Separate config loading from business logic
   - Create dedicated ConfigLoader classes

3. **Extract Language-Specific Logic**
   - Separate Python/TypeScript analysis
   - Use analyzer classes per language

4. **Utility Module Pattern**
   - Group related helper methods
   - Create focused utility classes

### Language Support

- ✅ **Python**: Full support with method counting and LOC analysis
- ✅ **TypeScript**: Full support with tree-sitter parsing
- ✅ **JavaScript**: Supported via TypeScript parser

### Real-World Example

**Large class refactoring:**
- **Before**: FilePlacementLinter (33 methods, 382 LOC) - single class handling config, patterns, validation
- **After**: Extract Class pattern applied - 5 focused classes (ConfigLoader, PatternValidator, RuleChecker, PathResolver, FilePlacementLinter)
- **Result**: Each class ≤8 methods, ≤150 LOC, single responsibility

See [SRP Linter Guide](docs/srp-linter.md) for comprehensive documentation and refactoring patterns.

## Pre-commit Hooks

Automate code quality checks before every commit and push with pre-commit hooks.

### Quick Setup

```bash
# 1. Install pre-commit framework
pip install pre-commit

# 2. Install git hooks
pre-commit install
pre-commit install --hook-type pre-push

# 3. Test it works
pre-commit run --all-files
```

### What You Get

**On every commit:**
- 🚫 Prevents commits to main/master branch
- 🎨 Auto-fixes formatting issues
- ✅ Runs thailint on changed files (fast)

**On every push:**
- 🔍 Full linting on entire codebase
- 🧪 Runs complete test suite

### Example Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # Prevent commits to protected branches
      - id: no-commit-to-main
        name: Prevent commits to main branch
        entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ]; then echo "❌ Use a feature branch!"; exit 1; fi'
        language: system
        pass_filenames: false
        always_run: true

      # Auto-format code
      - id: format
        name: Auto-fix formatting
        entry: just format
        language: system
        pass_filenames: false

      # Run thailint on changed files
      - id: lint-changed
        name: Lint changed files
        entry: just lint-full FILES=changed
        language: system
        pass_filenames: false
```

See **[Pre-commit Hooks Guide](docs/pre-commit-hooks.md)** for complete documentation, troubleshooting, and advanced configuration.

## Common Use Cases

### CI/CD Integration

```yaml
# GitHub Actions example
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install thailint
        run: pip install thailint
      - name: Run file placement linter
        run: thailint file-placement .
      - name: Run nesting linter
        run: thailint nesting src/ --config .thailint.yaml
```

### Editor Integration

```python
# VS Code extension example
from src import Linter

linter = Linter(config_file='.thailint.yaml')
violations = linter.lint(file_path)
```

### Test Suite

```python
# pytest integration
import pytest
from src import Linter

def test_no_violations():
    linter = Linter()
    violations = linter.lint('src/')
    assert len(violations) == 0
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if using)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_cli.py::test_hello_command
```

### Code Quality

```bash
# Lint code
ruff check src tests

# Format code
ruff format src tests

# Type checking
mypy src/
```

### Building

```bash
# Build Python package
poetry build

# Build Docker image locally (optional)
docker build -t washad/thailint:latest .
```

## Docker Usage

```bash
# Pull published image
docker pull washad/thailint:latest

# Run CLI help
docker run --rm washad/thailint:latest --help

# Run file-placement linter
docker run --rm -v $(pwd):/data washad/thailint:latest file-placement /data

# Run nesting linter
docker run --rm -v $(pwd):/data washad/thailint:latest nesting /data

# With custom config
docker run --rm -v $(pwd):/data \
    washad/thailint:latest nesting --config /data/.thailint.yaml /data
```

## Documentation

### Comprehensive Guides

- 📖 **[Getting Started](docs/getting-started.md)** - Installation, first lint, basic config
- ⚙️ **[Configuration Reference](docs/configuration.md)** - Complete config options (YAML/JSON)
- 📚 **[API Reference](docs/api-reference.md)** - Library API documentation
- 💻 **[CLI Reference](docs/cli-reference.md)** - All CLI commands and options
- 🚀 **[Deployment Modes](docs/deployment-modes.md)** - CLI, Library, and Docker usage
- 📁 **[File Placement Linter](docs/file-placement-linter.md)** - Detailed linter guide
- 🔄 **[Nesting Depth Linter](docs/nesting-linter.md)** - Nesting depth analysis guide
- 🪝 **[Pre-commit Hooks](docs/pre-commit-hooks.md)** - Automated quality checks
- 📦 **[Publishing Guide](docs/releasing.md)** - Release and publishing workflow
- ✅ **[Publishing Checklist](docs/publishing-checklist.md)** - Post-publication validation

### Examples

See [`examples/`](examples/) directory for working code:

- **[basic_usage.py](examples/basic_usage.py)** - Simple library API usage
- **[advanced_usage.py](examples/advanced_usage.py)** - Advanced patterns and workflows
- **[ci_integration.py](examples/ci_integration.py)** - CI/CD integration example

## Project Structure

```
thai-lint/
├── src/                      # Application source code
│   ├── api.py               # High-level Library API
│   ├── cli.py               # CLI commands
│   ├── core/                # Core abstractions
│   │   ├── base.py         # Base linter interfaces
│   │   ├── registry.py     # Rule registry
│   │   └── types.py        # Core types (Violation, Severity)
│   ├── linters/             # Linter implementations
│   │   └── file_placement/ # File placement linter
│   ├── linter_config/       # Configuration system
│   │   ├── loader.py       # Config loader (YAML/JSON)
│   │   └── ignore.py       # Ignore directives
│   └── orchestrator/        # Multi-language orchestrator
│       ├── core.py         # Main orchestrator
│       └── language_detector.py
├── tests/                   # Test suite (221 tests, 87% coverage)
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Pytest fixtures
├── docs/                    # Documentation
│   ├── getting-started.md
│   ├── configuration.md
│   ├── api-reference.md
│   ├── cli-reference.md
│   ├── deployment-modes.md
│   └── file-placement-linter.md
├── examples/                # Working examples
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   └── ci_integration.py
├── .ai/                     # AI agent documentation
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Docker orchestration
└── pyproject.toml           # Project configuration
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Follow existing code style (enforced by Ruff)
- Add type hints to all functions
- Update documentation for user-facing changes
- Run `pytest` and `ruff check` before committing

## Performance

thailint is designed for speed and efficiency:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file lint | ~20ms | <100ms ✅ |
| 100 files | ~300ms | <1s ✅ |
| 1000 files | ~900ms | <5s ✅ |
| Config loading | ~10ms | <100ms ✅ |

*Performance benchmarks run on standard hardware, your results may vary.*

## Exit Codes

thailint uses standard exit codes for CI/CD integration:

- **0** - Success (no violations)
- **1** - Violations found
- **2** - Error occurred (invalid config, file not found, etc.)

```bash
thailint file-placement .
if [ $? -eq 0 ]; then
    echo "✅ Linting passed"
else
    echo "❌ Linting failed"
fi
```

## Architecture

See [`.ai/docs/`](.ai/docs/) for detailed architecture documentation and [`.ai/howtos/`](.ai/howtos/) for development guides.

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: https://github.com/be-wise-be-kind/thai-lint/issues
- **Documentation**: `.ai/docs/` and `.ai/howtos/`

## Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - CLI framework
- [pytest](https://pytest.org/) - Testing framework
- [Ruff](https://docs.astral.sh/ruff/) - Linting and formatting
- [Docker](https://www.docker.com/) - Containerization

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
