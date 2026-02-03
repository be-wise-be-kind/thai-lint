# Single Responsibility Principle (SRP) Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the SRP linter for detecting and fixing Single Responsibility Principle violations

    **Scope**: Configuration, usage, refactoring patterns, and best practices for SRP analysis

    **Overview**: Comprehensive documentation for the SRP linter that detects classes violating the Single Responsibility Principle in Python, TypeScript, and Rust code. Covers how the linter works using AST analysis and heuristics, configuration options, CLI and library usage, common refactoring patterns discovered during dogfooding, and integration with CI/CD pipelines. Helps teams maintain modular, maintainable code by enforcing configurable SRP thresholds.

    **Dependencies**: Python ast module (Python parser), tree-sitter-typescript (TypeScript parser), tree-sitter-rust (Rust parser, optional)

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format

    **Implementation**: AST-based class analysis with heuristic metrics and configurable thresholds

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thai-lint
thailint srp src/
```

**Example output:**
```
src/services.py:15 - Class 'UserManager' has too many responsibilities (12 methods, max 8)
  Suggestion: Consider splitting into focused classes like UserRepository, UserValidator
```

**Fix it:** Split large classes into smaller, single-purpose classes.

---

## Overview

The Single Responsibility Principle (SRP) linter detects classes that have too many responsibilities, making them harder to understand, test, and maintain. It analyzes Python, TypeScript, and Rust code using Abstract Syntax Tree (AST) parsing to measure class complexity through multiple heuristics.

### Why SRP Matters

Classes with too many responsibilities are:
- **Harder to understand**: Complex classes require understanding multiple concerns
- **Harder to test**: More responsibilities mean more test cases and mocking
- **Harder to maintain**: Changes affect multiple concerns, increasing risk
- **More coupled**: God classes often have many dependencies
- **Resistant to change**: Fear of breaking multiple features inhibits refactoring

### Benefits

- **Improved modularity**: Classes with single responsibilities are easier to compose
- **Better testability**: Focused classes are simpler to test in isolation
- **Easier maintenance**: Changes to one responsibility don't affect others
- **Reduced coupling**: Smaller classes have fewer dependencies
- **Team consistency**: Enforces shared architectural standards

## How It Works

### Heuristic-Based Analysis

The SRP linter uses multiple heuristics to detect potential SRP violations:

1. **Method Count**: Classes with many methods likely handle multiple responsibilities
   - Default threshold: 7 methods
   - Configurable per language

2. **Lines of Code (LOC)**: Large classes often violate SRP
   - Default threshold: 200 lines
   - Configurable per language

3. **Responsibility Keywords**: Generic names indicate poor design
   - Detects: Manager, Handler, Processor, Utility, Helper
   - Configurable keyword list

### AST-Based Analysis

The linter uses Abstract Syntax Tree (AST) parsing for accurate analysis:

1. **Parse source code** into AST using language-specific parsers:
   - Python: Built-in `ast` module
   - TypeScript: `tree-sitter-typescript` library
   - Rust: `tree-sitter-rust` library (optional dependency)

2. **Find all classes** in the file

3. **Calculate metrics** for each class:
   - Count public methods (excluding properties and private methods)
   - Count lines of code (excluding blank lines and comments)
   - Check for responsibility keywords in class name

4. **Report violations** when metrics exceed configured thresholds

### Metric Calculation

**Method Counting (Python):**
```python
class UserService:           # 8 methods
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def find_user(self): pass
    def send_email(self): pass      # ← Different responsibility
    def log_action(self): pass      # ← Different responsibility
    def validate_data(self): pass   # ← Different responsibility
    def generate_report(self): pass # ← Violation at method 8 (max: 7)
```

**Lines of Code (Python):**
```python
class DataProcessor:  # 250+ LOC - Violation (max: 200)
    # Complex initialization, validation, transformation,
    # serialization, persistence, caching, logging...
    # All in one class!
```

**Keyword Detection:**
```python
class UserManager:    # Violation - contains "Manager"
class DataHandler:    # Violation - contains "Handler"
class RequestProcessor:  # Violation - contains "Processor"
```

### Method Counting Rules

The SRP linter counts **public methods** to determine if a class has too many responsibilities.

**Counted as methods:**
- Regular public methods (`def process(self)`)
- Static methods and class methods (if public)

**NOT counted as methods:**
- Private methods (methods starting with `_` like `_helper()`)
- Dunder methods (`__init__`, `__str__`, `__eq__`, etc.)
- Properties decorated with `@property`
- TypeScript methods starting with `_`

**Rationale:** Classes with clean public interfaces but complex internal implementations
are considered legitimate. The SRP heuristic focuses on the complexity exposed to
consumers of the class, not internal implementation details. Large classes with many
private methods are still penalized via the lines of code (LOC) threshold.

**Example - Passes SRP check (2 public methods):**
```python
class DataProcessor:
    def process(self): pass          # Counted
    def validate(self): pass         # Counted
    def __init__(self): pass         # NOT counted (dunder)
    def __str__(self): return ""     # NOT counted (dunder)
    def _parse_json(self): pass      # NOT counted (private)
    def _validate_schema(self): pass # NOT counted (private)
    def _log_debug(self): pass       # NOT counted (private)
```

## Configuration

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
srp:
  enabled: true
  max_methods: 7    # Maximum methods per class
  max_loc: 200      # Maximum lines of code per class
```

### Language-Specific Configuration

Different languages have different verbosity levels. Configure thresholds per language:

```yaml
srp:
  enabled: true

  # Python-specific (more strict - Python is concise)
  python:
    max_methods: 8
    max_loc: 200

  # TypeScript-specific (more lenient - types add verbosity)
  typescript:
    max_methods: 10
    max_loc: 250

  # JavaScript-specific
  javascript:
    max_methods: 10
    max_loc: 225

  # Rust-specific (struct + impl block analysis)
  rust:
    max_methods: 8
    max_loc: 200

  # Default fallback for other languages
  max_methods: 8
  max_loc: 200
```

### Keyword Configuration

Customize responsibility keywords to detect:

```yaml
srp:
  enabled: true
  check_keywords: true
  keywords:
    - Manager
    - Handler
    - Processor
    - Utility
    - Helper
    - Controller   # Add custom keywords
    - Service      # Add custom keywords
```

Disable keyword checking:

```yaml
srp:
  enabled: true
  check_keywords: false  # Only check method count and LOC
```

### Complete Configuration Example

```yaml
srp:
  enabled: true

  # Language-specific thresholds
  python:
    max_methods: 8
    max_loc: 200

  typescript:
    max_methods: 10
    max_loc: 250

  javascript:
    max_methods: 10
    max_loc: 225

  rust:
    max_methods: 8
    max_loc: 200

  # Default for other languages
  max_methods: 8
  max_loc: 200

  # Keyword detection
  check_keywords: true
  keywords:
    - Manager
    - Handler
    - Processor
    - Utility
    - Helper
```

### Configuration Priority

Configuration is applied with the following priority (highest to lowest):

1. **Language-specific settings** (`python:`, `typescript:`, etc.)
2. **Top-level defaults** (`max_methods`, `max_loc`)
3. **Built-in defaults** (7 methods, 200 LOC)

## CLI Usage

### Basic Commands

```bash
# Check current directory
thailint srp .

# Check specific directory
thailint srp src/

# Check specific file
thailint srp src/services/user.py
```

### Command Options

```bash
# Use custom thresholds
thailint srp --max-methods 10 --max-loc 300 src/

# Use specific config file
thailint srp --config .thailint.custom.yaml src/

# Output JSON format (for CI/CD)
thailint srp --format json src/

# Non-recursive (current directory only)
thailint srp --no-recursive src/
```

### Complete Command Reference

```bash
thailint srp [OPTIONS] [PATH]

Arguments:
  PATH    File or directory to check (default: current directory)

Options:
  --config PATH         Configuration file path
  --format [text|json]  Output format (default: text)
  --max-methods INT     Override max methods threshold
  --max-loc INT         Override max LOC threshold
  --recursive           Scan directories recursively (default: true)
  --no-recursive        Scan only specified directory
  --help               Show help message
```

### Exit Codes

- **0**: No violations found
- **1**: Violations found
- **2**: Error occurred (invalid config, file not found, etc.)

```bash
thailint srp src/
if [ $? -eq 0 ]; then
    echo "SRP checks passed"
else
    echo "SRP violations found"
fi
```

## Library API

### Basic Usage

```python
from src import srp_lint

# Lint directory
violations = srp_lint("src/")

# Process violations
for violation in violations:
    print(f"{violation.file_path}:{violation.line} - {violation.message}")
```

### Advanced Usage

```python
from src import SRPRule
from src.core.base import BaseLintContext

# Create rule instance
rule = SRPRule()

# Create context
context = BaseLintContext(
    file_path="src/services/user.py",
    file_content=code,
    language="python",
    metadata={
        "srp": {
            "max_methods": 10,
            "max_loc": 250
        }
    }
)

# Check violations
violations = rule.check(context)
```

### Using the Orchestrator

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file=".thailint.yaml")

# Lint with specific rules
violations = linter.lint("src/", rules=["srp.violation"])

# Check results
if violations:
    print(f"Found {len(violations)} SRP violations")
    for v in violations:
        print(f"  {v.file_path}:{v.line} - {v.message}")
```

## Violation Examples

### Method Count Violation

**Code:**
```python
class UserManager:  # 8 methods - Violation (max: 7)
    def create(self): pass
    def update(self): pass
    def delete(self): pass
    def find(self): pass
    def validate(self): pass
    def notify(self): pass
    def log(self): pass
    def export(self): pass  # ← 8th method triggers violation
```

**Violation Message:**
```
src/user.py:1 - Class 'UserManager' may violate SRP: 8 methods (max: 7)
Suggestion: Consider extracting related methods into separate classes
```

### Lines of Code Violation

**Code:**
```python
class DataProcessor:  # 250 LOC - Violation (max: 200)
    # Handles data validation, transformation,
    # persistence, caching, logging, monitoring,
    # error handling, retry logic, etc.
    # ... 250+ lines ...
```

**Violation Message:**
```
src/processor.py:1 - Class 'DataProcessor' may violate SRP: 250 lines (max: 200)
Suggestion: Consider breaking the class into smaller, focused classes
```

### Keyword Violation

**Code:**
```python
class UserHandler:  # Contains "Handler" keyword
    def handle_request(self): pass
    def handle_response(self): pass
```

**Violation Message:**
```
src/handler.py:1 - Class 'UserHandler' may violate SRP: responsibility keyword in name
Suggestion: Avoid generic names like Manager, Handler, Processor
```

### Combined Violations

**Code:**
```python
class DataManager:  # 10 methods, 300 LOC, contains "Manager"
    # Multiple violations!
```

**Violation Message:**
```
src/manager.py:1 - Class 'DataManager' may violate SRP: 10 methods (max: 7), 300 lines (max: 200), responsibility keyword in name
Suggestion: Consider extracting related methods into separate classes. Consider breaking the class into smaller, focused classes. Avoid generic names like Manager, Handler, Processor
```

## Refactoring Patterns

### Pattern 1: Extract Class

**Problem**: Class with too many methods handling multiple concerns

**Before:**
```python
class UserManager:  # 12 methods - Violation
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def send_welcome_email(self): pass
    def send_reset_email(self): pass
    def send_notification(self): pass
    def validate_email(self): pass
    def validate_password(self): pass
    def hash_password(self): pass
    def log_creation(self): pass
    def log_update(self): pass
    def log_deletion(self): pass
```

**After:**
```python
class UserRepository:  # 3 methods ✓
    def create(self, user): pass
    def update(self, user): pass
    def delete(self, user): pass

class EmailService:  # 3 methods ✓
    def send_welcome(self, user): pass
    def send_reset(self, user): pass
    def send_notification(self, user): pass

class UserValidator:  # 3 methods ✓
    def validate_email(self, email): pass
    def validate_password(self, password): pass
    def hash_password(self, password): pass

class UserAuditLog:  # 3 methods ✓
    def log_creation(self, user): pass
    def log_update(self, user): pass
    def log_deletion(self, user): pass
```

### Pattern 2: Split Configuration and Logic

**Problem**: Class handling both config loading and business logic

**Before:**
```python
class FilePlacementLinter:  # 33 methods, 382 LOC - Violation
    def load_config(self): pass
    def validate_config(self): pass
    def check_pattern(self): pass
    def check_directory(self): pass
    def check_global(self): pass
    # ... 28 more methods
```

**After:**
```python
class ConfigLoader:  # 3 methods ✓
    def load(self, path): pass
    def validate(self, config): pass
    def merge_defaults(self, config): pass

class PatternMatcher:  # 4 methods ✓
    def matches(self, pattern, path): pass
    def compile_regex(self, pattern): pass
    def check_allow(self, path): pass
    def check_deny(self, path): pass

class FilePlacementLinter:  # 6 methods ✓
    def __init__(self, config_loader, matcher): pass
    def check(self, context): pass
    def check_file(self, path): pass
    def check_directory(self, path): pass
    def check_global(self, path): pass
    def create_violation(self, path, rule): pass
```

### Pattern 3: Extract Language-Specific Logic

**Problem**: Single class handling multiple languages

**Before:**
```python
class SRPRule:  # 16 methods - Violation
    def check_python(self): pass
    def check_typescript(self): pass
    def parse_python(self): pass
    def parse_typescript(self): pass
    def count_python_methods(self): pass
    def count_typescript_methods(self): pass
    # ... 10 more methods
```

**After:**
```python
class ClassAnalyzer:  # 4 methods ✓
    def analyze_python(self, code): pass
    def analyze_typescript(self, code): pass
    def extract_classes(self, ast): pass
    def calculate_metrics(self, cls): pass

class MetricsEvaluator:  # 3 methods ✓
    def evaluate(self, metrics, config): pass
    def exceeds_method_limit(self, count): pass
    def exceeds_loc_limit(self, lines): pass

class ViolationBuilder:  # 4 methods ✓
    def build(self, metrics, issues): pass
    def format_message(self, issues): pass
    def generate_suggestions(self, issues): pass
    def create_violation(self, data): pass

class SRPRule:  # 5 methods ✓
    def check(self, context): pass
    def load_config(self, context): pass
    def analyze_file(self, context, config): pass
    def filter_violations(self, violations): pass
    def apply_ignores(self, violations): pass
```

### Pattern 4: Utility Module Pattern

**Problem**: Helper methods cluttering main class

**Before:**
```python
class DataProcessor:  # 15 methods - Violation
    def process(self): pass
    def validate(self): pass
    def transform(self): pass
    def _parse_json(self): pass
    def _parse_xml(self): pass
    def _parse_csv(self): pass
    def _format_date(self): pass
    def _format_currency(self): pass
    def _sanitize_html(self): pass
    # ... 6 more helpers
```

**After:**
```python
# utils/parsers.py
class DataParser:  # 3 methods ✓
    def parse_json(self, data): pass
    def parse_xml(self, data): pass
    def parse_csv(self, data): pass

# utils/formatters.py
class DataFormatter:  # 3 methods ✓
    def format_date(self, date): pass
    def format_currency(self, amount): pass
    def sanitize_html(self, html): pass

# processor.py
class DataProcessor:  # 3 methods ✓
    def __init__(self, parser, formatter):
        self.parser = parser
        self.formatter = formatter

    def process(self, data): pass
    def validate(self, data): pass
    def transform(self, data): pass
```

## Real-World Refactoring Example

### Large Class Refactoring

**Problem**: A linter class handling multiple responsibilities

**Before:**
```python
class FilePlacementLinter:  # 33 methods, 382 LOC
    def load_config(self): pass
    def validate_config(self): pass
    def parse_patterns(self): pass
    def check_file(self): pass
    def check_directory(self): pass
    def check_global(self): pass
    def create_violation(self): pass
    # ... 26 more methods handling config, patterns, validation, etc.
```

**After - Extract Class Pattern:**
```python
class ConfigLoader:  # 3 methods, ~50 LOC
    def load(self, path): pass
    def validate(self, config): pass
    def merge_defaults(self, config): pass

class PatternValidator:  # 4 methods, ~60 LOC
    def compile_regex(self, pattern): pass
    def matches(self, pattern, path): pass
    def check_allow(self, path): pass
    def check_deny(self, path): pass

class RuleChecker:  # 5 methods, ~80 LOC
    def check_directory_rules(self, path): pass
    def check_global_rules(self, path): pass
    def evaluate_rule(self, rule, path): pass
    def should_ignore(self, path): pass
    def create_violation(self, path, rule): pass

class PathResolver:  # 3 methods, ~40 LOC
    def normalize(self, path): pass
    def resolve_relative(self, path): pass
    def get_parent_dir(self, path): pass

class FilePlacementLinter:  # 6 methods, ~80 LOC
    def __init__(self, loader, validator, checker, resolver):
        self.loader = loader
        self.validator = validator
        self.checker = checker
        self.resolver = resolver

    def check(self, context): pass
    def check_file(self, path): pass
    def check_directory(self, path): pass
    # Orchestrates the focused classes above
```

**Result**: Each class has a single, well-defined responsibility with ≤7 methods and ≤150 LOC

## Ignore Directives

### Line-Level Ignore (Python)

```python
class UserManager:  # thailint: ignore srp
    # Many methods, but explicitly allowed
    pass
```

### Line-Level Ignore (TypeScript)

```typescript
// thailint: ignore srp
class DataHandler {
    // Explicitly allowed
}
```

### Block-Level Ignore

```python
# thailint: ignore-start srp
class LegacyManager:
    # Legacy code - refactoring planned
    pass

class OldHandler:
    # Will be removed in v2
    pass
# thailint: ignore-end srp
```

### File-Level Ignore

```python
# thailint: ignore-file srp

# Entire file ignored for SRP violations
class Manager1: pass
class Manager2: pass
```

### Directory-Level Ignore

Add to `.thailint.yaml`:

```yaml
srp:
  enabled: true
  ignore:
    - "legacy/"
    - "third_party/"
    - "tests/"  # Don't enforce SRP in tests
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  srp-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install thailint
        run: pip install thailint

      - name: Run SRP linter
        run: thailint srp src/ --format json > srp-report.json

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: srp-report
          path: srp-report.json
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: srp-check
        name: Check SRP violations
        entry: thailint srp
        language: system
        types: [python, typescript]
        pass_filenames: false
```

### Make Target

Add to `Makefile`:

```makefile
.PHONY: lint-srp
lint-srp:
	@echo "=== Running SRP linter ==="
	@thailint srp src/ --config .thailint.yaml
	@echo "SRP checks complete"
```

## Troubleshooting

### Issue: False Positives on Data Classes

**Problem**: Data classes with many fields flagged for method count

**Solution**: Properties don't count as methods in Python

```python
class UserDTO:  # Not a violation
    @property
    def field1(self): return self._field1

    @property
    def field2(self): return self._field2
    # Properties are not counted as methods
```

### Issue: Abstract Base Classes Flagged

**Problem**: ABCs with many abstract methods flagged

**Solution**: Use ignore directive for legitimate cases

```python
# thailint: ignore srp
class BaseRepository(ABC):  # Interface definition - allowed
    @abstractmethod
    def create(self): pass
    @abstractmethod
    def read(self): pass
    # ... many abstract methods
```

### Issue: Inherited Methods Counted

**Problem**: Methods from parent class incorrectly counted

**Solution**: Only direct methods are counted, not inherited

```python
class Child(Parent):  # Only counts methods defined in Child
    def child_method(self): pass  # Only this counts
```

### Issue: Language-Specific Config Not Applied

**Problem**: TypeScript files using Python thresholds

**Solution**: Ensure language-specific config is properly nested

```yaml
# Wrong
srp:
  typescript:
    max_methods: 10

# Correct
srp:
  enabled: true
  typescript:
    max_methods: 10
    max_loc: 250
```

## Performance

The SRP linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file analysis | ~20-40ms | <100ms |
| 100 files | ~500ms | <2s |
| 1000 files | ~3-5s | <30s |
| AST parsing (cached) | ~5-10ms | <50ms |

*Performance benchmarks on standard hardware. Results may vary.*

## Best Practices

### 1. Start with Lenient Thresholds

Begin with higher thresholds, then gradually tighten:

```yaml
# Start here
srp:
  max_methods: 12
  max_loc: 300

# Gradually reduce
srp:
  max_methods: 10
  max_loc: 250

# Target
srp:
  max_methods: 7
  max_loc: 200
```

### 2. Use Language-Specific Settings

Account for language verbosity:

```yaml
srp:
  python:
    max_methods: 8    # Python is concise
  typescript:
    max_methods: 10   # TypeScript more verbose
```

### 3. Document Ignored Violations

Always explain why violations are ignored:

```python
# thailint: ignore srp
# Reason: Legacy adapter class, refactoring planned for v2.0
# Ticket: JIRA-123
class LegacyAdapter:
    pass
```

### 4. Combine with Other Linters

Use SRP linter alongside nesting and complexity linters:

```bash
just lint-full  # Includes SRP, nesting, complexity, security
```

### 5. Regular Refactoring

Don't let violations accumulate:

```bash
# Weekly SRP audit
thailint srp src/ --format json > srp-weekly.json
```

## Language Support

### Python Support

**Fully Supported** - Analyzes classes using the built-in `ast` module. Counts public methods, lines of code, and checks class names for responsibility keywords.

### TypeScript Support

**Fully Supported** - Analyzes classes using `tree-sitter-typescript`. Counts public methods (excluding `_`-prefixed), lines of code, and checks class names.

### JavaScript Support

**Supported** (via TypeScript parser) - JavaScript files are analyzed using the TypeScript parser, which handles JavaScript syntax.

### Rust Support

**Fully Supported** - Analyzes `struct` definitions and their `impl` blocks using `tree-sitter-rust`.

**How Rust SRP analysis works:**

- A Rust `struct` combined with its `impl` blocks is treated as a "class"
- Methods are counted across **all** `impl` blocks for the same struct
- Only public methods (not prefixed with `_`) are counted
- Lines of code include the struct definition and all associated impl blocks

**Example:**
```rust
struct UserService {
    db: Database,
    cache: Cache,
}

impl UserService {
    pub fn create_user(&self) {}   // Counted
    pub fn update_user(&self) {}   // Counted
    pub fn delete_user(&self) {}   // Counted
    fn _validate(&self) {}         // NOT counted (private)
}

impl UserService {
    pub fn send_email(&self) {}    // Counted (separate impl block, same struct)
    pub fn log_action(&self) {}    // Counted
}
// Total: 5 public methods for UserService
```

**Configuration:**
```yaml
srp:
  rust:
    max_methods: 8
    max_loc: 200
```

**Requires**: `tree-sitter-rust` (optional dependency). Install with `pip install thailint[rust]` or `pip install thailint[all]`.

## Further Reading

- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) - SRP principles
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID) - Object-oriented design
- [Refactoring by Martin Fowler](https://refactoring.com/) - Refactoring patterns
- [CLI Reference](cli-reference.md) - Complete CLI documentation
- [Configuration Guide](configuration.md) - Configuration format details

## Support

- **Issues**: https://github.com/be-wise-be-kind/thai-lint/issues
- **Documentation**: Complete docs at `docs/`
- **Examples**: Working examples in `examples/`

---

*SRP Linter - Part of thai-lint v0.3.0+*
