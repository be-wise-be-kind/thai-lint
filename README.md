# thai-lint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-795%2F795%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)](htmlcov/)
[![Documentation Status](https://readthedocs.org/projects/thai-lint/badge/?version=latest)](https://thai-lint.readthedocs.io/en/latest/?badge=latest)
[![SARIF 2.1.0](https://img.shields.io/badge/SARIF-2.1.0-orange.svg)](docs/sarif-output.md)

The AI Linter - Enterprise-ready linting and governance for AI-generated code across multiple languages.

## Documentation

**New to thailint?** Start here:
- **[Quick Start Guide](https://thai-lint.readthedocs.io/en/latest/quick-start/)** - Get running in 5 minutes
- **[Configuration Reference](https://thai-lint.readthedocs.io/en/latest/configuration/)** - Complete config options for all linters
- **[Troubleshooting Guide](https://thai-lint.readthedocs.io/en/latest/troubleshooting/)** - Common issues and solutions

**Full Documentation:** Browse the **[documentation site](https://thai-lint.readthedocs.io/)** for comprehensive guides covering installation, all linters, configuration patterns, and integration examples.

## Overview

thailint is a modern, enterprise-ready multi-language linter designed specifically for AI-generated code. It focuses on common mistakes and anti-patterns that AI coding assistants frequently introduce—issues that existing linters don't catch or don't handle consistently across languages.

**Why thailint?**

We're not trying to replace the wonderful existing linters like Pylint, ESLint, or Ruff. Instead, thailint fills critical gaps:

- **AI-Specific Patterns**: AI assistants have predictable blind spots (excessive nesting, magic numbers, SRP violations) that traditional linters miss
- **Cross-Language Consistency**: Detects the same anti-patterns across Python, TypeScript, and JavaScript with unified rules
- **No Existing Solutions**: Issues like excessive nesting depth, file placement violations, and cross-project code duplication lack comprehensive multi-language detection
- **Governance Layer**: Enforces project-wide structure and organization patterns that AI can't infer from local context

thailint complements your existing linting stack by catching the patterns AI tools repeatedly miss.

**Complete documentation available at [thai-lint.readthedocs.io](https://thai-lint.readthedocs.io/)** covering installation, configuration, all linters, and troubleshooting.

## Features

### Core Capabilities
- **File Placement Linting** - Enforce project structure and organization
- **File Header Linting** - Validate documentation headers in source files
  - Python, TypeScript, JavaScript, Bash, Markdown, CSS support
  - Mandatory field validation (Purpose, Scope, Overview)
  - Atemporal language detection (no dates, "currently", "now")
  - Language-specific header format parsing
- **Magic Numbers Linting** - Detect unnamed numeric literals that should be constants
  - Python and TypeScript support with AST analysis
  - Context-aware detection (ignores constants, test files, range() usage)
  - Configurable allowed numbers and thresholds
  - Helpful suggestions for extracting to named constants
- **Nesting Depth Linting** - Detect excessive code nesting with AST analysis
  - Python and TypeScript support with tree-sitter
  - Configurable max depth (default: 4, recommended: 3)
  - Helpful refactoring suggestions (guard clauses, extract method)
- **SRP Linting** - Detect Single Responsibility Principle violations
  - Heuristic-based analysis (method count, LOC, keywords)
  - Language-specific thresholds (Python, TypeScript, JavaScript)
  - Refactoring patterns from real-world examples
- **DRY Linting** - Detect duplicate code across projects
  - Token-based hash detection with SQLite storage
  - Fast duplicate detection (in-memory or disk-backed)
  - Configurable thresholds (lines, tokens, occurrences)
  - Language-specific detection (Python, TypeScript, JavaScript)
  - False positive filtering (keyword args, imports)
- **Collection Pipeline Linting** - Detect for loops with embedded filtering
  - Based on Martin Fowler's "Replace Loop with Pipeline" refactoring
  - Detects if/continue patterns that should use generator expressions
  - Generates refactoring suggestions with generator syntax
  - Configurable threshold (min_continues)
  - Python support with AST analysis
- **Method Property Linting** - Detect methods that should be @property decorators
  - Python AST-based detection
  - get_* prefix detection (Java-style getters)
  - Simple computed value detection
  - Action verb exclusion (to_*, finalize, serialize)
  - Test file detection
- **Stateless Class Linting** - Detect classes that should be module-level functions
  - Python AST-based detection
  - No constructor (__init__ or __new__) detection
  - No instance state (self.attr) detection
  - Excludes ABC, Protocol, and decorated classes
  - Helpful refactoring suggestions
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

### From PyPI

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

# Check multiple files
thailint nesting file1.py file2.py file3.py

# Check specific directory
thailint nesting src/

# Check for duplicate code
thailint dry .

# Check for magic numbers
thailint magic-numbers src/

# Check file headers
thailint file-header src/

# With config file
thailint dry --config .thailint.yaml src/

# JSON output for CI/CD
thailint dry --format json src/

# SARIF output for GitHub Code Scanning
thailint nesting --format sarif src/ > results.sarif
```

**New to thailint?** See the **[Quick Start Guide](https://thai-lint.readthedocs.io/en/latest/quick-start/)** for a complete walkthrough including config generation, understanding output, and next steps.

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
# Lint directory (recommended - lints all files inside)
docker run --rm -v $(pwd):/data \
  washad/thailint:latest file-placement /data

# Lint single file
docker run --rm -v $(pwd):/data \
  washad/thailint:latest file-placement /data/src/app.py

# Lint multiple specific files
docker run --rm -v $(pwd):/data \
  washad/thailint:latest nesting /data/src/file1.py /data/src/file2.py

# Check nesting depth in subdirectory
docker run --rm -v $(pwd):/data \
  washad/thailint:latest nesting /data/src
```

### Docker with Sibling Directories

For Docker environments with sibling directories (e.g., separate config and source directories), use `--project-root` or config path inference:

```bash
# Directory structure:
# /workspace/
# ├── root/           # Contains .thailint.yaml and .git
# ├── backend/        # Code to lint
# └── tools/

# Option 1: Explicit project root (recommended)
docker run --rm -v $(pwd):/data \
  washad/thailint:latest \
  --project-root /data/root \
  magic-numbers /data/backend/

# Option 2: Config path inference (automatic)
docker run --rm -v $(pwd):/data \
  washad/thailint:latest \
  --config /data/root/.thailint.yaml \
  magic-numbers /data/backend/

# With ignore patterns resolving from project root
docker run --rm -v $(pwd):/data \
  washad/thailint:latest \
  --project-root /data/root \
  --config /data/root/.thailint.yaml \
  magic-numbers /data/backend/
```

**Priority order:**
1. `--project-root` (highest priority - explicit specification)
2. Inferred from `--config` path directory
3. Auto-detection from file location (fallback)

See **[Docker Usage](#docker-usage)** section below for more examples.

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

# DRY linter configuration
dry:
  enabled: true
  min_duplicate_lines: 4         # Minimum lines to consider duplicate
  min_duplicate_tokens: 30       # Minimum tokens to consider duplicate
  min_occurrences: 2             # Report if appears 2+ times

  # Language-specific thresholds
  python:
    min_occurrences: 3           # Python: require 3+ occurrences

  # Storage settings (SQLite)
  storage_mode: "memory"         # Options: "memory" (default) or "tempfile"

  # Ignore patterns
  ignore:
    - "tests/"
    - "__init__.py"

# Magic numbers linter configuration
magic-numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 10, 100, 1000]  # Numbers allowed without constants
  max_small_integer: 10  # Max value allowed in range() or enumerate()
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
  },
  "dry": {
    "enabled": true,
    "min_duplicate_lines": 4,
    "min_duplicate_tokens": 30,
    "min_occurrences": 2,
    "python": {
      "min_occurrences": 3
    },
    "storage_mode": "memory",
    "ignore": ["tests/", "__init__.py"]
  },
  "magic-numbers": {
    "enabled": true,
    "allowed_numbers": [-1, 0, 1, 2, 10, 100, 1000],
    "max_small_integer": 10
  }
}
```

See [Configuration Guide](https://thai-lint.readthedocs.io/en/latest/configuration/) for complete reference.

**Need help with ignores?** See **[How to Ignore Violations](https://thai-lint.readthedocs.io/en/latest/how-to-ignore-violations/)** for complete guide to all ignore levels (line, method, class, file, repository).

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

- **Python**: Full support (if/for/while/with/try/match)
- **TypeScript**: Full support (if/for/while/try/switch)
- **JavaScript**: Supported via TypeScript parser

See [Nesting Linter Guide](https://thai-lint.readthedocs.io/en/latest/nesting-linter/) for comprehensive documentation and refactoring patterns.

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

- **Python**: Full support with method counting and LOC analysis
- **TypeScript**: Full support with tree-sitter parsing
- **JavaScript**: Supported via TypeScript parser

### Real-World Example

**Large class refactoring:**
- **Before**: FilePlacementLinter (33 methods, 382 LOC) - single class handling config, patterns, validation
- **After**: Extract Class pattern applied - 5 focused classes (ConfigLoader, PatternValidator, RuleChecker, PathResolver, FilePlacementLinter)
- **Result**: Each class ≤8 methods, ≤150 LOC, single responsibility

See [SRP Linter Guide](https://thai-lint.readthedocs.io/en/latest/srp-linter/) for comprehensive documentation and refactoring patterns.

## DRY Linter (Don't Repeat Yourself)

### Overview

The DRY linter detects duplicate code blocks across your entire project using token-based hashing with SQLite storage. It identifies identical or near-identical code that violates the Don't Repeat Yourself (DRY) principle, helping maintain code quality at scale.

### Quick Start

```bash
# Check for duplicate code in current directory
thailint dry .

# Use custom thresholds
thailint dry --min-lines 5 src/

# Use tempfile storage for large projects
thailint dry --storage-mode tempfile src/

# Get JSON output
thailint dry --format json src/
```

### Configuration

Add to `.thailint.yaml`:

```yaml
dry:
  enabled: true
  min_duplicate_lines: 4         # Minimum lines to consider duplicate
  min_duplicate_tokens: 30       # Minimum tokens to consider duplicate
  min_occurrences: 2             # Report if appears 2+ times

  # Language-specific thresholds
  python:
    min_occurrences: 3           # Python: require 3+ occurrences
  typescript:
    min_occurrences: 3           # TypeScript: require 3+ occurrences

  # Storage settings
  storage_mode: "memory"         # Options: "memory" (default) or "tempfile"

  # Ignore patterns
  ignore:
    - "tests/"           # Test code often has acceptable duplication
    - "__init__.py"      # Import-only files exempt

  # False positive filters
  filters:
    keyword_argument_filter: true   # Filter function call kwargs
    import_group_filter: true       # Filter import groups
```

### How It Works

**Token-Based Detection:**
1. Parse code into tokens (stripping comments, normalizing whitespace)
2. Create rolling hash windows of N lines
3. Store hashes in SQLite database with file locations
4. Query for hashes appearing 2+ times across project

**SQLite Storage:**
- In-memory mode (default): Stores in RAM for best performance
- Tempfile mode: Stores in temporary disk file for large projects
- Fresh analysis on every run (no persistence between runs)
- Fast duplicate detection using B-tree indexes

### Example Violation

**Code with duplication:**
```python
# src/auth.py
def validate_user(user_data):
    if not user_data:
        return False
    if not user_data.get('email'):
        return False
    if not user_data.get('password'):
        return False
    return True

# src/admin.py
def validate_admin(admin_data):
    if not admin_data:
        return False
    if not admin_data.get('email'):
        return False
    if not admin_data.get('password'):
        return False
    return True
```

**Violation message:**
```
src/auth.py:3 - Duplicate code detected (4 lines, 2 occurrences)
  Locations:
    - src/auth.py:3-6
    - src/admin.py:3-6
  Consider extracting to shared function
```

**Refactored (DRY):**
```python
# src/validators.py
def validate_credentials(data):
    if not data:
        return False
    if not data.get('email'):
        return False
    if not data.get('password'):
        return False
    return True

# src/auth.py & src/admin.py
from src.validators import validate_credentials

def validate_user(user_data):
    return validate_credentials(user_data)

def validate_admin(admin_data):
    return validate_credentials(admin_data)
```

### Performance

| Operation | Performance | Storage Mode |
|-----------|-------------|--------------|
| Scan (1000 files) | 1-3s | Memory (default) |
| Large project (5000+ files) | Use tempfile mode | Tempfile |

**Note**: Every run analyzes files fresh - no persistence between runs ensures accurate results

### Language Support

- **Python**: Full support with AST-based tokenization
- **TypeScript**: Full support with tree-sitter parsing
- **JavaScript**: Supported via TypeScript parser

### False Positive Filtering

Built-in filters automatically exclude common non-duplication patterns:
- **keyword_argument_filter**: Excludes function calls with keyword arguments
- **import_group_filter**: Excludes import statement groups

### Refactoring Patterns

1. **Extract Function**: Move repeated logic to shared function
2. **Extract Base Class**: Create base class for similar implementations
3. **Extract Utility Module**: Move helper functions to shared utilities
4. **Template Method**: Use function parameters for variations

See [DRY Linter Guide](https://thai-lint.readthedocs.io/en/latest/dry-linter/) for comprehensive documentation, storage modes, and refactoring patterns.

## Collection Pipeline Linter

### Overview

The collection-pipeline linter detects for loops with embedded filtering (if/continue patterns) that should be refactored to use generator expressions or other collection pipelines. Based on Martin Fowler's "Replace Loop with Pipeline" refactoring pattern.

### The Anti-Pattern

```python
# Anti-pattern: Embedded filtering in loop body
for file_path in dir_path.glob(pattern):
    if not file_path.is_file():
        continue
    if ignore_parser.is_ignored(file_path):
        continue
    violations.extend(lint_file(file_path))
```

### The Solution

```python
# Collection pipeline: Filtering separated from processing
valid_files = (
    f for f in dir_path.glob(pattern)
    if f.is_file() and not ignore_parser.is_ignored(f)
)
for file_path in valid_files:
    violations.extend(lint_file(file_path))
```

### Quick Start

```bash
# Check current directory
thailint pipeline .

# Check specific directory
thailint pipeline src/

# Only flag patterns with 2+ filter conditions
thailint pipeline --min-continues 2 src/

# JSON output
thailint pipeline --format json src/
```

### Configuration

```yaml
# .thailint.yaml
collection-pipeline:
  enabled: true
  min_continues: 1  # Minimum if/continue patterns to flag
  ignore:
    - "tests/**"
    - "**/legacy/**"
```

### Example Violation

**Detected Pattern:**
```python
def process_files(paths):
    for path in paths:
        if not path.is_file():
            continue
        analyze(path)
```

**Violation Message:**
```
src/processor.py:3 - For loop over 'paths' has embedded filtering.
  Consider using a generator expression:
  for path in (path for path in paths if path.is_file()):
```

**Refactored Code:**
```python
def process_files(paths):
    valid_paths = (p for p in paths if p.is_file())
    for path in valid_paths:
        analyze(path)
```

### Why This Matters

- **Separation of concerns**: Filtering logic is separate from processing logic
- **Readability**: Intent is clear at a glance
- **Testability**: Filtering can be tested independently
- **Based on**: Martin Fowler's "Replace Loop with Pipeline" refactoring

### Ignoring Violations

```python
# Line-level ignore
for item in items:  # thailint: ignore[collection-pipeline]
    if not item.valid:
        continue
    process(item)
```

See [Collection Pipeline Linter Guide](docs/collection-pipeline-linter.md) for comprehensive documentation and refactoring patterns.

## Magic Numbers Linter

### Overview

The magic numbers linter detects unnamed numeric literals (magic numbers) that should be extracted to named constants. It uses AST analysis to identify numeric literals that lack meaningful context.

### What are Magic Numbers?

**Magic numbers** are unnamed numeric literals in code without explanation:

```python
# Bad - Magic numbers
timeout = 3600  # What is 3600?
max_retries = 5  # Why 5?

# Good - Named constants
TIMEOUT_SECONDS = 3600
MAX_RETRY_ATTEMPTS = 5
```

### Quick Start

```bash
# Check for magic numbers in current directory
thailint magic-numbers .

# Check specific directory
thailint magic-numbers src/

# Get JSON output
thailint magic-numbers --format json src/
```

### Configuration

Add to `.thailint.yaml`:

```yaml
magic-numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 10, 100, 1000]
  max_small_integer: 10  # Max for range() to be acceptable
```

### Example Violation

**Code with magic numbers:**
```python
def calculate_timeout():
    return 3600  # Magic number - what is 3600?

def process_items(items):
    for i in range(100):  # Magic number - why 100?
        items[i] *= 1.5  # Magic number - what is 1.5?
```

**Violation messages:**
```
src/example.py:2 - Magic number 3600 should be a named constant
src/example.py:5 - Magic number 100 should be a named constant
src/example.py:6 - Magic number 1.5 should be a named constant
```

**Refactored code:**
```python
TIMEOUT_SECONDS = 3600
MAX_ITEMS = 100
PRICE_MULTIPLIER = 1.5

def calculate_timeout():
    return TIMEOUT_SECONDS

def process_items(items):
    for i in range(MAX_ITEMS):
        items[i] *= PRICE_MULTIPLIER
```

### Acceptable Contexts

The linter **does not** flag numbers in these contexts:

| Context | Example | Why Acceptable |
|---------|---------|----------------|
| Constants | `MAX_SIZE = 100` | UPPERCASE name provides context |
| Small `range()` | `range(5)` | Small loop bounds are clear |
| Test files | `test_*.py` | Test data can be literal |
| Allowed numbers | `-1, 0, 1, 2, 10` | Common values are self-explanatory |

### Refactoring Patterns

**Pattern 1: Extract to Module Constants**
```python
# Before
def connect():
    timeout = 30
    retries = 3

# After
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3

def connect():
    timeout = DEFAULT_TIMEOUT_SECONDS
    retries = DEFAULT_MAX_RETRIES
```

**Pattern 2: Extract with Units in Name**
```python
# Before
delay = 3600  # Is this seconds? Minutes?

# After
TASK_DELAY_SECONDS = 3600  # Clear unit

delay = TASK_DELAY_SECONDS
```

**Pattern 3: Use Standard Library**
```python
# Before
if status == 200:
    return "success"

# After
from http import HTTPStatus

if status == HTTPStatus.OK:
    return "success"
```

### Language Support

- **Python**: Full support (int, float, scientific notation)
- **TypeScript**: Full support (int, float, scientific notation)
- **JavaScript**: Supported via TypeScript parser

### Ignoring Violations

```python
# Line-level ignore
timeout = 3600  # thailint: ignore[magic-numbers] - Industry standard

# Method-level ignore
def get_ports():  # thailint: ignore[magic-numbers] - Standard ports
    return {80: "HTTP", 443: "HTTPS"}

# File-level ignore
# thailint: ignore-file[magic-numbers]
```

See **[How to Ignore Violations](https://thai-lint.readthedocs.io/en/latest/how-to-ignore-violations/)** and **[Magic Numbers Linter Guide](https://thai-lint.readthedocs.io/en/latest/magic-numbers-linter/)** for complete documentation.

## File Header Linter

### Overview

The file header linter validates that source files have proper documentation headers containing required fields (Purpose, Scope, Overview) and don't use temporal language (dates, "currently", "now"). It enforces consistent documentation patterns across entire codebases.

### Why File Headers?

File headers serve as **self-documentation** that helps developers (and AI assistants) quickly understand:

- **Purpose**: What does this file do?
- **Scope**: What area of the system does it cover?
- **Dependencies**: What does it rely on?
- **Exports**: What does it provide to other modules?

### Quick Start

```bash
# Check file headers in current directory
thailint file-header .

# Check specific directory
thailint file-header src/

# Get JSON output
thailint file-header --format json src/

# Get SARIF output for CI/CD
thailint file-header --format sarif src/ > results.sarif
```

### Configuration

Add to `.thailint.yaml`:

```yaml
file-header:
  enabled: true
  mandatory_fields:
    - Purpose
    - Scope
    - Overview
  ignore:
    - "**/__init__.py"
    - "**/migrations/**"
```

### Example Violation

**Code without proper header:**
```python
import os

def process_data():
    pass
```

**Violation messages:**
```
src/utils.py:1 - Missing mandatory field: Purpose
src/utils.py:1 - Missing mandatory field: Scope
src/utils.py:1 - Missing mandatory field: Overview
```

**Refactored with header:**
```python
"""
Purpose: Data processing utilities for ETL pipeline

Scope: Data transformation layer, used by batch processing jobs

Overview: Provides data transformation functions for the ETL pipeline.
    Handles parsing, validation, and normalization of incoming data.

Dependencies: os, json

Exports: process_data(), validate_input(), transform_record()
"""
import os

def process_data():
    pass
```

### Atemporal Language Detection

The linter detects temporal language that becomes stale:

**Temporal (flagged):**
```python
"""
Purpose: Authentication module

Overview: Currently handles OAuth. This was recently updated.
    Created: 2024-01-15. Will be extended in the future.
"""
```

**Atemporal (correct):**
```python
"""
Purpose: Authentication module

Overview: Handles OAuth authentication with Google and GitHub.
    Implements authorization code flow with PKCE for security.
"""
```

### Language Support

- **Python**: Module docstrings (`"""..."""`)
- **TypeScript/JavaScript**: JSDoc comments (`/** ... */`)
- **Bash**: Hash comments after shebang (`# ...`)
- **Markdown**: YAML frontmatter (`---...---`)
- **CSS/SCSS**: Block comments (`/* ... */`)

### Ignoring Violations

```python
# File-level ignore
# thailint: ignore-file[file-header]

# Line-level ignore for atemporal violation
"""
Overview: Created 2024-01-15.  # thailint: ignore[file-header]
"""
```

See **[How to Ignore Violations](https://thai-lint.readthedocs.io/en/latest/how-to-ignore-violations/)** and **[File Header Linter Guide](https://thai-lint.readthedocs.io/en/latest/file-header-linter/)** for complete documentation.

## Stateless Class Linter

### Overview

The stateless class linter detects Python classes that have no state (no constructor, no instance attributes) and should be refactored to module-level functions. This is a common anti-pattern in AI-generated code.

### What Are Stateless Classes?

Stateless classes are classes that:
- Have no `__init__` or `__new__` method
- Have no instance attributes (`self.attr` assignments)
- Have 2+ methods (grouped functionality without state)

```python
# Bad - Stateless class (no state, just grouped functions)
class TokenHasher:
    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(self, token: str, hash_value: str) -> bool:
        return self.hash_token(token) == hash_value

# Good - Module-level functions
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token(token: str, hash_value: str) -> bool:
    return hash_token(token) == hash_value
```

### Quick Start

```bash
# Check stateless classes in current directory
thailint stateless-class .

# Check specific directory
thailint stateless-class src/

# Get JSON output
thailint stateless-class --format json src/
```

### Configuration

Add to `.thailint.yaml`:

```yaml
stateless-class:
  enabled: true
  min_methods: 2  # Minimum methods to flag
```

### Example Violation

**Code with stateless class:**
```python
class StringUtils:
    def capitalize_words(self, text: str) -> str:
        return ' '.join(w.capitalize() for w in text.split())

    def reverse_words(self, text: str) -> str:
        return ' '.join(reversed(text.split()))
```

**Violation message:**
```
src/utils.py:1 - Class 'StringUtils' has no state and should be refactored to module-level functions
```

**Refactored code:**
```python
def capitalize_words(text: str) -> str:
    return ' '.join(w.capitalize() for w in text.split())

def reverse_words(text: str) -> str:
    return ' '.join(reversed(text.split()))
```

### Exclusion Rules

The linter does NOT flag classes that:
- Have `__init__` or `__new__` constructors
- Have instance attributes (`self.attr = value`)
- Have class-level attributes
- Inherit from ABC or Protocol
- Have any decorator (`@dataclass`, `@register`, etc.)
- Have 0-1 methods

### Ignoring Violations

```python
# Line-level ignore
class TokenHasher:  # thailint: ignore[stateless-class] - Legacy API
    def hash(self, token): ...

# File-level ignore
# thailint: ignore-file[stateless-class]
```

See **[How to Ignore Violations](https://thai-lint.readthedocs.io/en/latest/how-to-ignore-violations/)** and **[Stateless Class Linter Guide](https://thai-lint.readthedocs.io/en/latest/stateless-class-linter/)** for complete documentation.

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
- Prevents commits to main/master branch
- Auto-fixes formatting issues
- Runs thailint on changed files (fast, uses pass_filenames: true)

**On every push:**
- Full linting on entire codebase
- Runs complete test suite

### Example Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # Prevent commits to protected branches
      - id: no-commit-to-main
        name: Prevent commits to main branch
        entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ]; then echo "ERROR: Use a feature branch!"; exit 1; fi'
        language: system
        pass_filenames: false
        always_run: true

      # Auto-format code
      - id: format
        name: Auto-fix formatting
        entry: just format
        language: system
        pass_filenames: false

      # Run thailint on changed files (passes filenames directly)
      - id: thailint-changed
        name: Lint changed files
        entry: thailint nesting
        language: system
        files: \.(py|ts|tsx|js|jsx)$
        pass_filenames: true
```

See **[Pre-commit Hooks Guide](https://thai-lint.readthedocs.io/en/latest/pre-commit-hooks/)** for complete documentation, troubleshooting, and advanced configuration.

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
# Install dependencies and activate virtualenv
just init

# Or manually:
poetry install
source $(poetry env info --path)/bin/activate
```

### Running Tests

```bash
# Run all tests (parallel mode - fast)
just test

# Run with coverage (serial mode)
just test-coverage

# Run specific test
poetry run pytest tests/test_cli.py::test_hello_command -v
```

### Code Quality

```bash
# Fast linting (Ruff only - use during development)
just lint

# Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)
just lint-all

# Security scanning
just lint-security

# Complexity analysis (Radon + Xenon + Nesting)
just lint-complexity

# SOLID principles (SRP)
just lint-solid

# DRY principles (duplicate code detection)
just lint-dry

# ALL quality checks (runs everything)
just lint-full

# Auto-fix formatting issues
just format
```

### Dogfooding (Lint Our Own Code)

```bash
# Lint file placement
just lint-placement

# Check nesting depth
just lint-nesting

# Check for magic numbers
poetry run thai-lint magic-numbers src/
```

### Building and Publishing

```bash
# Build Python package
poetry build

# Build Docker image locally
docker build -t washad/thailint:latest .

# Publish to PyPI and Docker Hub (runs tests + linting + version bump)
just publish
```

### Quick Development Workflows

```bash
# Make changes, then run quality checks
just lint-full

# Share changes for collaboration (skips hooks)
just share "WIP: feature description"

# Clean up cache and artifacts
just clean
```

See `just --list` or `just help` for all available commands.

## Docker Usage

### Basic Docker Commands

```bash
# Pull published image
docker pull washad/thailint:latest

# Run CLI help
docker run --rm washad/thailint:latest --help

# Lint entire directory (recommended)
docker run --rm -v $(pwd):/data washad/thailint:latest file-placement /data

# Lint single file
docker run --rm -v $(pwd):/data washad/thailint:latest file-placement /data/src/app.py

# Lint multiple specific files
docker run --rm -v $(pwd):/data washad/thailint:latest nesting /data/src/file1.py /data/src/file2.py

# Lint specific subdirectory
docker run --rm -v $(pwd):/data washad/thailint:latest nesting /data/src

# Collection pipeline linter
docker run --rm -v $(pwd):/data washad/thailint:latest pipeline /data/src

# With custom config
docker run --rm -v $(pwd):/data \
    washad/thailint:latest nesting --config /data/.thailint.yaml /data

# JSON output for CI/CD
docker run --rm -v $(pwd):/data \
    washad/thailint:latest file-placement --format json /data
```

### Docker with Sibling Directories (Advanced)

For complex Docker setups with sibling directories, use `--project-root` for explicit control:

```bash
# Scenario: Monorepo with separate config and code directories
# Directory structure:
# /workspace/
# ├── config/           # Contains .thailint.yaml
# ├── backend/app/      # Python backend code
# ├── frontend/         # TypeScript frontend
# └── tools/            # Build tools

# Explicit project root (recommended for Docker)
docker run --rm -v /path/to/workspace:/workspace \
  washad/thailint:latest \
  --project-root /workspace/config \
  magic-numbers /workspace/backend/

# Config path inference (automatic - no --project-root needed)
docker run --rm -v /path/to/workspace:/workspace \
  washad/thailint:latest \
  --config /workspace/config/.thailint.yaml \
  magic-numbers /workspace/backend/

# Lint multiple sibling directories with shared config
docker run --rm -v /path/to/workspace:/workspace \
  washad/thailint:latest \
  --project-root /workspace/config \
  nesting /workspace/backend/ /workspace/frontend/
```

**When to use `--project-root` in Docker:**
- **Sibling directory structures** - When config/code aren't nested
- **Monorepos** - Multiple projects sharing one config
- **CI/CD** - Explicit paths prevent auto-detection issues
- **Ignore patterns** - Ensures patterns resolve from correct base directory

## Documentation

### Comprehensive Guides

- **[Getting Started](https://thai-lint.readthedocs.io/en/latest/getting-started/)** - Installation, first lint, basic config
- **[Configuration Reference](https://thai-lint.readthedocs.io/en/latest/configuration/)** - Complete config options (YAML/JSON)
- **[How to Ignore Violations](https://thai-lint.readthedocs.io/en/latest/how-to-ignore-violations/)** - Complete guide to all ignore levels
- **[API Reference](https://thai-lint.readthedocs.io/en/latest/api-reference/)** - Library API documentation
- **[CLI Reference](https://thai-lint.readthedocs.io/en/latest/cli-reference/)** - All CLI commands and options
- **[Deployment Modes](https://thai-lint.readthedocs.io/en/latest/deployment-modes/)** - CLI, Library, and Docker usage
- **[File Placement Linter](https://thai-lint.readthedocs.io/en/latest/file-placement-linter/)** - Detailed linter guide
- **[File Header Linter](https://thai-lint.readthedocs.io/en/latest/file-header-linter/)** - File header validation guide
- **[Magic Numbers Linter](https://thai-lint.readthedocs.io/en/latest/magic-numbers-linter/)** - Magic numbers detection guide
- **[Nesting Depth Linter](https://thai-lint.readthedocs.io/en/latest/nesting-linter/)** - Nesting depth analysis guide
- **[SRP Linter](https://thai-lint.readthedocs.io/en/latest/srp-linter/)** - Single Responsibility Principle guide
- **[DRY Linter](https://thai-lint.readthedocs.io/en/latest/dry-linter/)** - Duplicate code detection guide
- **[Collection Pipeline Linter](https://thai-lint.readthedocs.io/en/latest/collection-pipeline-linter/)** - Loop filtering refactoring guide
- **[Method Property Linter](https://thai-lint.readthedocs.io/en/latest/method-property-linter/)** - Method-to-property conversion guide
- **[Stateless Class Linter](https://thai-lint.readthedocs.io/en/latest/stateless-class-linter/)** - Stateless class detection guide
- **[Pre-commit Hooks](https://thai-lint.readthedocs.io/en/latest/pre-commit-hooks/)** - Automated quality checks
- **[SARIF Output Guide](docs/sarif-output.md)** - SARIF format for GitHub Code Scanning and CI/CD
- **[Publishing Guide](https://thai-lint.readthedocs.io/en/latest/releasing/)** - Release and publishing workflow
- **[Publishing Checklist](https://thai-lint.readthedocs.io/en/latest/publishing-checklist/)** - Post-publication validation

### Examples

See [`examples/`](examples/) directory for working code:

- **[basic_usage.py](examples/basic_usage.py)** - Simple library API usage
- **[advanced_usage.py](examples/advanced_usage.py)** - Advanced patterns and workflows
- **[ci_integration.py](examples/ci_integration.py)** - CI/CD integration example
- **[sarif_usage.py](examples/sarif_usage.py)** - SARIF output format examples
- **[file_header_usage.py](examples/file_header_usage.py)** - File header validation examples

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
| Single file lint | ~20ms | <100ms |
| 100 files | ~300ms | <1s |
| 1000 files | ~900ms | <5s |
| Config loading | ~10ms | <100ms |

*Performance benchmarks run on standard hardware, your results may vary.*

## Exit Codes

thailint uses standard exit codes for CI/CD integration:

- **0** - Success (no violations)
- **1** - Violations found
- **2** - Error occurred (invalid config, file not found, etc.)

```bash
thailint file-placement .
if [ $? -eq 0 ]; then
    echo "Linting passed"
else
    echo "Linting failed"
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
