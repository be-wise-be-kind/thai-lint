# thai-lint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-296%2F296%20passing-brightgreen.svg)](https://github.com/be-wise-be-kind/thai-lint/tree/main/tests)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)](https://github.com/be-wise-be-kind/thai-lint)
[![Documentation Status](https://readthedocs.org/projects/thai-lint/badge/?version=latest)](https://thai-lint.readthedocs.io/en/latest/?badge=latest)

The AI Linter - Enterprise-ready linting and governance for AI-generated code across multiple languages.

## Welcome

**thai-lint** is a modern, enterprise-ready multi-language linter designed specifically for AI-generated code. It focuses on common mistakes and anti-patterns that AI coding assistants frequently introduce—issues that existing linters don't catch or don't handle consistently across languages.

### Quick Links

- **[Quick Start Guide](quick-start.md)** - Get running in 5 minutes
- **[Configuration Reference](configuration.md)** - Complete config options for all linters
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

## Why thai-lint?

We're not trying to replace the wonderful existing linters like Pylint, ESLint, or Ruff. Instead, thai-lint fills critical gaps:

- **AI-Specific Patterns**: AI assistants have predictable blind spots (excessive nesting, magic numbers, SRP violations) that traditional linters miss
- **Cross-Language Consistency**: Detects the same anti-patterns across Python, TypeScript, and JavaScript with unified rules
- **No Existing Solutions**: Issues like excessive nesting depth, file placement violations, and cross-project code duplication lack comprehensive multi-language detection
- **Governance Layer**: Enforces project-wide structure and organization patterns that AI can't infer from local context

thai-lint complements your existing linting stack by catching the patterns AI tools repeatedly miss.

## Features

### Core Capabilities

- **File Placement Linting** - Enforce project structure and organization
- **Magic Numbers Linting** - Detect unnamed numeric literals that should be constants
- **Method Property Linting** - Detect methods that should be @property decorators
- **Nesting Depth Linting** - Detect excessive code nesting with AST analysis
- **Performance Linting** - Detect O(n^2) patterns in loops (string concat, regex)
- **SRP Linting** - Detect Single Responsibility Principle violations
- **DRY Linting** - Detect duplicate code across projects
- **Collection Pipeline Linting** - Detect for loops with embedded filtering
- **Stringly-Typed Linting** - Detect string patterns that should use enums
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
- **Test Coverage** - 90% coverage with 296+ tests
- **CI/CD Ready** - Proper exit codes and JSON output
- **Comprehensive Docs** - Complete documentation and examples

## Installation

### From PyPI

```bash
pip install thai-lint
```

### From Source

```bash
# Clone repository
git clone https://github.com/be-wise-be-kind/thai-lint.git
cd thai-lint

# Install dependencies
pip install -e ".[dev]"
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

# Check for magic numbers
thailint magic-numbers src/

# Check nesting depth
thailint nesting src/

# Check for duplicate code
thailint dry .

# Check for embedded filtering patterns
thailint pipeline src/

# Check for performance anti-patterns
thailint perf src/

# Check for stringly-typed patterns
thailint stringly-typed src/

# With config file
thailint dry --config .thailint.yaml src/

# JSON output for CI/CD
thailint dry --format json src/
```

See the **[Quick Start Guide](quick-start.md)** for a complete walkthrough.

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

## Available Linters

### [File Placement Linter](file-placement-linter.md)
Enforce project structure and organization rules.

### [Magic Numbers Linter](magic-numbers-linter.md)
Detect unnamed numeric literals that should be named constants.

### [Method Property Linter](method-property-linter.md)
Detect methods that should be @property decorators.

### [Nesting Depth Linter](nesting-linter.md)
Detect deeply nested code that reduces readability.

### [Performance Linter](performance-linter.md)
Detect O(n^2) performance anti-patterns: string concatenation and regex compilation in loops.

### [SRP Linter](srp-linter.md)
Detect Single Responsibility Principle violations in classes.

### [DRY Linter](dry-linter.md)
Detect duplicate code blocks across your project.

### [Collection Pipeline Linter](collection-pipeline-linter.md)
Detect for loops with embedded filtering that should use collection pipelines.

### [Stringly-Typed Linter](stringly-typed-linter.md)
Detect string-based type patterns that should use enums or typed alternatives.

## Documentation

- **[Getting Started](getting-started.md)** - Installation and first lint
- **[Configuration Reference](configuration.md)** - Complete config options (YAML/JSON)
- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete guide to all ignore levels
- **[API Reference](api-reference.md)** - Library API documentation
- **[CLI Reference](cli-reference.md)** - All CLI commands and options
- **[Deployment Modes](deployment-modes.md)** - CLI, Library, and Docker usage
- **[Pre-commit Hooks](pre-commit-hooks.md)** - Automated quality checks

## Support

- **GitHub Issues**: [https://github.com/be-wise-be-kind/thai-lint/issues](https://github.com/be-wise-be-kind/thai-lint/issues)
- **Repository**: [https://github.com/be-wise-be-kind/thai-lint](https://github.com/be-wise-be-kind/thai-lint)
- **PyPI**: [https://pypi.org/project/thailint/](https://pypi.org/project/thailint/)

## License

MIT License - see [LICENSE](https://github.com/be-wise-be-kind/thai-lint/blob/main/LICENSE) file for details.
