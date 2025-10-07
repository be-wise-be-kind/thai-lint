# Enterprise Multi-Language Linter - AI Context

**Purpose**: AI agent context document for implementing Enterprise Multi-Language Linter with TDD approach

**Scope**: Transform thai-lint from basic CLI to production-ready enterprise linter supporting 3 deployment modes, plugin framework, multi-level ignores, and file placement linting

**Overview**: Comprehensive context document for AI agents working on the Enterprise Linter feature. This feature
    transforms the basic Click-based CLI application into a powerful, extensible, multi-language linter framework.
    The implementation uses strict Test-Driven Development (TDD) methodology, leveraging reference implementation
    patterns from the durable-code-test project. The system provides three deployment modes (CLI, library, Docker),
    a plugin architecture for extensible rules, five levels of ignore directives, and begins with a file placement
    linter as the first concrete implementation.

**Dependencies**: Python 3.11+, Poetry, pytest (TDD), Click (CLI), PyYAML (config), pathlib (file ops), Docker (containerization)

**Exports**: Production-ready linter framework, file placement linter, PyPI package, Docker image, comprehensive API

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Strict TDD approach (tests first, always), plugin architecture with auto-discovery, configuration-driven rules, binary severity model (errors only)

---

## Overview

**What We're Building**: An enterprise-ready, multi-language linter that can be used three ways:

1. **CLI**: `thai lint file-placement src/`
2. **Library**: `from thailinter import file_placement_linter`
3. **Docker**: `docker run thailint/thailint lint file-placement /workspace`

**Why It Matters**: AI-generated code often has subtle placement and organizational issues that traditional linters miss. This linter provides extensible, configurable rules that can enforce project-specific conventions.

**Key Innovation**: Plugin architecture where rules are registered through configuration, not code changes. Add new rules by dropping them in a directory - no framework modifications needed.

---

## Project Background

### Current State (Starting Point)
- **Basic CLI**: Click-based CLI from python-cli-install roadmap (PR5 complete)
- **Testing Setup**: pytest installed and configured
- **Project Structure**: Professional Python project with Poetry, Ruff, MyPy
- **Documentation**: `.ai/` directory with standards and howtos

### Gap Analysis
**Missing Pieces**:
- ❌ Core linter framework (base classes, plugin system)
- ❌ Configuration system (YAML/JSON loading, validation)
- ❌ Multi-language orchestration (file routing, language detection)
- ❌ Concrete linters (file placement, etc.)
- ❌ Library API (currently only CLI)
- ❌ Docker containerization
- ❌ PyPI packaging and distribution

### Reference Implementation
**Available Resource**: `/home/stevejackson/Projects/durable-code-test/tools/design_linters/`

This reference implementation provides:
- ✅ Base interfaces (`framework/base_interfaces.py`)
- ✅ Rule registry with auto-discovery (`framework/rule_registry.py`)
- ✅ Ignore directive parsing (`framework/ignore_utils.py`)
- ✅ File placement linter (`rules/organization/file_placement_rules.py`)
- ✅ Multi-language orchestrator (`framework/multi_language_orchestrator.py`)

**Strategy**: Adapt these patterns to our architecture while following TDD methodology.

---

## Feature Vision

### Three Deployment Modes

#### 1. CLI Mode
```bash
# Simple usage
thai lint file-placement .

# With configuration
thai lint file-placement --config .ai/layout.yaml src/

# Inline rules (JSON object)
thai lint file-placement --rules '{"deny": ["^src/.*test.*"]}' .

# Multiple output formats
thai lint file-placement --format json .
thai lint file-placement --format sarif . > results.sarif
```

#### 2. Library Mode
```python
# High-level API
from thailinter import Linter

linter = Linter(config_file='.thailint.yaml')
violations = linter.lint('src/', rules=['file-placement'])
for v in violations:
    print(f"{v.file_path}:{v.line} - {v.message}")

# Direct linter import
from thailinter.linters import file_placement_linter as fpl

config = {
    'layout_file': '.ai/layout.yaml'
}
violations = fpl.lint('src/', config)
```

#### 3. Docker Mode
```bash
# Pull image
docker pull thailint/thailint:latest

# Run on mounted volume
docker run -v $(pwd):/workspace thailint/thailint \
    lint file-placement /workspace

# With configuration
docker run -v $(pwd):/workspace \
    -v $(pwd)/.ai:/config \
    thailint/thailint \
    lint file-placement --config /config/layout.yaml /workspace

# Docker Compose
services:
  linter:
    image: thailint/thailint:latest
    volumes:
      - .:/workspace
    command: lint file-placement /workspace
```

### Five-Level Ignore System

#### 1. Repository Level (`.thailintignore` file)
```gitignore
# .thailintignore (gitignore syntax)
*.pyc
__pycache__/
.git/
node_modules/
build/
dist/
```

#### 2. Directory Level
```yaml
# .lint-config.yaml in directory
ignore:
  - file-placement  # Ignore this rule for this directory
```

#### 3. File Level (first 10 lines)
```python
#!/usr/bin/env python3
# thailint: ignore-file[file-placement]
# This file is exempt from file placement rules

def some_function():
    pass
```

#### 4. Method Level
```python
# thailint: ignore-next-line[file-placement]
def debug_function():  # Ignored
    pass

# Or decorator style (future enhancement)
@thailint.ignore("file-placement")
def another_function():
    pass
```

#### 5. Line Level
```python
bad_placement = True  # thailint: ignore[file-placement]
```

### Plugin Framework

**Auto-Discovery**: Drop rules in `src/linters/` directory, they're automatically registered.

```python
# src/linters/my_custom_linter/linter.py
from thailinter.core.base import BaseLintRule
from thailinter.core.types import Violation, Severity

class MyCustomRule(BaseLintRule):
    @property
    def rule_id(self) -> str:
        return "custom.my-rule"

    @property
    def rule_name(self) -> str:
        return "My Custom Rule"

    @property
    def description(self) -> str:
        return "Checks for custom conditions"

    def check(self, context) -> list[Violation]:
        # Implementation
        return []
```

**Registration**: Automatically discovered and available as `thai lint custom.my-rule`

### File Placement Linter Spec

**Configuration Format** (`.ai/layout.yaml` or `.ai/layout.json`):

```yaml
file_placement:
  directories:
    src/:
      allow:
        - "^src/.*\\.py$"        # Only .py files in src/
      deny:
        - pattern: "^src/.*test.*\\.py$"
          reason: "Tests belong in tests/ directory"
        - pattern: "^src/.*debug.*"
          reason: "Debug files should be in debug/ or removed"

    tests/:
      allow:
        - "^tests/test_.*\\.py$"  # Only test_*.py files

  global_deny:
    - pattern: ".*\\.tmp$"
      reason: "No temporary files in repository"
    - pattern: ".*\\.log$"
      reason: "Log files belong in logs/ or .gitignore"
    - pattern: "^/.*"  # Absolute paths
      reason: "No absolute paths in source code"
```

**JSON Equivalent**:
```json
{
  "file_placement": {
    "directories": {
      "src/": {
        "allow": ["^src/.*\\.py$"],
        "deny": [
          {"pattern": "^src/.*test.*\\.py$", "reason": "Tests in tests/"}
        ]
      }
    },
    "global_deny": [
      {"pattern": ".*\\.tmp$", "reason": "No temp files"}
    ]
  }
}
```

---

## Current Application Context

### Existing Structure (from python-cli-install)
```
thai-lint/
├── src/
│   ├── __init__.py
│   ├── cli.py          # Click CLI (hello, config commands)
│   └── config.py       # Basic config loading
├── tests/
│   ├── __init__.py
│   └── test_cli.py     # Existing CLI tests
├── pyproject.toml      # Poetry configuration
├── README.md
└── .ai/                # AI agent documentation
    ├── docs/
    ├── howtos/
    └── templates/
```

### What We're Adding
```
src/
├── core/               # NEW: Core framework
│   ├── base.py         # Abstract base classes
│   ├── registry.py     # Plugin registry
│   └── types.py        # Violation, Severity
├── config/             # NEW: Configuration system
│   ├── loader.py       # YAML/JSON loading
│   ├── ignore.py       # 5-level ignore parsing
│   └── schema.py       # Validation
├── orchestrator/       # NEW: Multi-language orchestration
│   ├── core.py         # Main orchestrator
│   ├── file_router.py  # Route files to analyzers
│   └── language_detector.py
├── linters/            # NEW: Concrete linters
│   └── file_placement/
│       ├── linter.py
│       ├── pattern_matcher.py
│       └── config_loader.py
└── cli/                # MODIFY: Enhanced CLI
    ├── commands/
    │   └── lint.py     # New lint command
    └── formatters/
        ├── text.py
        ├── json.py
        └── sarif.py

tests/
├── core/               # NEW: Core framework tests
├── config/             # NEW: Config system tests
├── orchestrator/       # NEW: Orchestrator tests
├── linters/            # NEW: Linter tests
│   └── file_placement/
└── integration/        # NEW: E2E tests
```

---

## Target Architecture

### Core Components

#### 1. Base Interfaces (`src/core/base.py`)
**Purpose**: Abstract base classes for plugin architecture

```python
class BaseLintContext(ABC):
    """Context for a linting operation."""
    @property
    @abstractmethod
    def file_path(self) -> Path | None: ...

    @property
    @abstractmethod
    def file_content(self) -> str | None: ...

    @property
    @abstractmethod
    def language(self) -> str: ...

class BaseLintRule(ABC):
    """Base class for all linting rules."""
    @property
    @abstractmethod
    def rule_id(self) -> str: ...

    @abstractmethod
    def check(self, context: BaseLintContext) -> list[Violation]: ...
```

#### 2. Rule Registry (`src/core/registry.py`)
**Purpose**: Auto-discover and register rules

**Features**:
- Plugin discovery in `src/linters/`
- Skip abstract base classes
- Cache discovered rules
- Provide by-id and by-category lookups

#### 3. Configuration System (`src/config/`)
**Purpose**: Multi-format config loading with validation

**Features**:
- Load YAML and JSON
- Schema validation
- Default values
- Environment variable interpolation

#### 4. Orchestrator (`src/orchestrator/core.py`)
**Purpose**: Route files to appropriate analyzers

**Workflow**:
```
1. Receive file path or directory
2. Detect language (extension, shebang)
3. Check ignore patterns (all 5 levels)
4. Get applicable rules for language
5. Create context
6. Execute rules
7. Collect and return violations
```

#### 5. File Placement Linter (`src/linters/file_placement/`)
**Purpose**: First concrete linter implementation

**Components**:
- `linter.py`: Main FilePlacementLinter class
- `pattern_matcher.py`: Regex matching engine
- `config_loader.py`: Load layout rules
- `violation_factory.py`: Create consistent violations

### User Journey

#### As CLI User
```bash
# 1. Install
pip install thailint

# 2. Create config
cat > .ai/layout.yaml <<EOF
file_placement:
  directories:
    src/:
      allow: ["^src/.*\\.py$"]
EOF

# 3. Run linter
thai lint file-placement .

# 4. See output
src/test_utils.py:1:0 - Test file in src/ directory
  Suggestion: Move to tests/ directory

# 5. Fix issues or add ignores
echo "src/test_utils.py" >> .thailintignore

# 6. Re-run (no violations)
thai lint file-placement .
✓ No violations found
```

#### As Library User
```python
# 1. Install
# pip install thailint

# 2. Import and use
from thailinter import Linter

linter = Linter(config_file='.thailint.yaml')
violations = linter.lint('src/')

# 3. Process results
for v in violations:
    print(f"{v.file_path}:{v.line} - {v.message}")
    if v.suggestion:
        print(f"  → {v.suggestion}")
```

#### As Docker User
```bash
# 1. Pull image
docker pull thailint/thailint:latest

# 2. Run on project
docker run -v $(pwd):/workspace \
    thailint/thailint lint file-placement /workspace

# 3. Integrate with CI/CD
# .github/workflows/lint.yml
- name: Lint file placement
  run: |
    docker run -v ${{ github.workspace }}:/workspace \
      thailint/thailint lint file-placement /workspace
```

### Data Flow

```
┌─────────────────┐
│   User Input    │
│ (path/config)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │◄──── Config System
│                 │
│  • Load config  │
│  • Check ignore │
│  • Route files  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Rule Registry  │
│                 │
│  • Get rules    │
│  • Filter by    │
│    language     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lint Rules     │
│                 │
│  • Check file   │
│  • Return       │
│    violations   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Formatter     │
│                 │
│  • Text/JSON    │
│  • SARIF        │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Output │
    └────────┘
```

---

## Key Decisions Made

### Decision 1: TDD Mandatory
**Rationale**:
- Ensures correctness from start
- Documentation through tests
- Prevents regressions
- Enables confident refactoring

**Impact**:
- Write ALL tests before implementation
- PR4 is pure tests (40+ tests, zero implementation)
- PR5 implements to pass PR4 tests

**Example**:
```python
# Step 1: Write test
def test_deny_pattern_overrides_allow():
    """Deny patterns take precedence over allow."""
    config = {
        'allow': [r'.*\.py$'],
        'deny': [{'pattern': r'.*debug.*'}]
    }
    linter = FilePlacementLinter(config_obj=config)
    violations = linter.lint_path(Path("src/debug_utils.py"))
    assert len(violations) > 0  # Denied despite matching allow

# Step 2: Implement (later)
# Make the test pass
```

### Decision 2: Reference Implementation as Guide
**Rationale**:
- Don't reinvent the wheel
- Proven patterns available
- Adapt, don't copy blindly

**Impact**:
- Study `/home/stevejackson/Projects/durable-code-test/tools/design_linters/`
- Understand patterns
- Adapt to our architecture
- Maintain TDD discipline

**Key Patterns to Adapt**:
- Plugin discovery from `rule_registry.py`
- Ignore parsing from `ignore_utils.py`
- File placement logic from `file_placement_rules.py`
- Orchestration from `multi_language_orchestrator.py`

### Decision 3: Binary Severity Model
**Rationale**:
- Simplicity: Either it's wrong or it's not
- User requirement: "no levels, it is either an error or not"
- Reduces configuration complexity

**Impact**:
- Only one severity: `Severity.ERROR`
- No warning vs error distinction
- Clearer decision making (fix it or ignore it)

```python
class Severity(Enum):
    """Binary severity model."""
    ERROR = "error"
    # No WARNING, INFO, etc.
```

### Decision 4: Configuration-Driven Plugin Registration
**Rationale**:
- User requirement: "extensible plugin framework where rules can be registered through configuration"
- Reduces code changes for new rules
- Enables user-defined rules

**Impact**:
- Auto-discovery in `src/linters/`
- Rules self-register via `rule_id`
- Configuration enables/disables rules

```yaml
# .thailint.yaml
rules:
  file-placement:
    enabled: true
    config:
      layout_file: .ai/layout.yaml

  custom.my-rule:
    enabled: false
```

### Decision 5: File-Based Initially (No AST)
**Rationale**:
- File placement linter doesn't need AST parsing
- Simpler implementation
- Faster execution
- AST can be added later for other linters

**Impact**:
- File placement works on paths and regex
- Future linters (e.g., naming conventions) can add AST
- Architecture supports both approaches

### Decision 6: Three Deployment Modes from Day One
**Rationale**:
- User requirement: "work it three ways: CLI, library, Docker"
- Enables different use cases
- Library mode for CI/CD integration
- Docker for isolation

**Impact**:
- PR7: CLI mode
- PR8: Library API
- PR9: Docker containerization
- All must be tested and working

---

## Integration Points

### With Existing Features

#### 1. Click CLI (`src/cli.py`)
**Integration**: Add new `lint` command group

**Before**:
```python
@cli.group()
def config():
    """Configuration management commands."""
    pass
```

**After**:
```python
@cli.group()
def lint():
    """Linting commands."""
    pass

@lint.command('file-placement')
@click.argument('path')
@click.option('--config', help='Config file')
def lint_file_placement(path, config):
    """Lint file placement."""
    # Implementation
    pass
```

#### 2. Configuration System (`src/config.py`)
**Integration**: Extend existing config loading

**Before** (simple):
```python
def load_config(path=None):
    # Basic YAML loading
    pass
```

**After** (enhanced):
```python
from src.config.loader import ConfigLoader

def load_config(path=None):
    loader = ConfigLoader()
    return loader.load(path)
```

#### 3. Testing Framework (`tests/test_cli.py`)
**Integration**: Add linter tests alongside CLI tests

**Pattern** (from existing tests):
```python
from click.testing import CliRunner

def test_lint_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['lint', 'file-placement', '.'])
    assert result.exit_code in [0, 1]
```

### With External Systems

#### 1. CI/CD Integration
```yaml
# .github/workflows/lint.yml
name: Lint Code
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run thailint
        run: |
          pip install thailint
          thai lint file-placement .
```

#### 2. Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: thailint-file-placement
        name: Thai Lint - File Placement
        entry: thai lint file-placement
        language: python
        pass_filenames: false
```

#### 3. VSCode Extension (Future)
```json
{
  "thailint.enable": true,
  "thailint.rules": ["file-placement"],
  "thailint.configFile": ".ai/layout.yaml"
}
```

---

## Success Metrics

### Technical Success
- ✅ Test coverage >95%
- ✅ All tests pass (pytest)
- ✅ Type checking passes (mypy --strict)
- ✅ Linting passes (ruff check)
- ✅ Performance: <100ms single file, <5s for 1000 files

### Feature Success
- ✅ CLI: `thai lint file-placement .` works
- ✅ Library: `from thailinter import ...` works
- ✅ Docker: `docker run thailint/thailint ...` works
- ✅ All three modes have equivalent functionality
- ✅ Published to PyPI as `thailint`
- ✅ Docker image on Docker Hub

### Adoption Success
- ✅ Dogfooded on own codebase (no violations)
- ✅ Documentation complete with working examples
- ✅ Used in CI/CD pipeline
- ✅ Pre-commit hook template available

---

## Technical Constraints

### Language Version
- **Python 3.11+**: Required for modern type hints (`|` union operator, `Self` type)

### Dependencies
- **Minimal**: Keep dependency tree small
- **Poetry-managed**: All deps in `pyproject.toml`
- **No heavy libraries**: Avoid pandas, numpy, etc. for core functionality

### Performance
- **Fast startup**: <500ms to first lint result
- **Memory efficient**: <100MB for typical projects
- **Parallelizable**: Support concurrent file processing (future)

### Compatibility
- **Cross-platform**: Windows, macOS, Linux
- **Path handling**: Use `pathlib.Path` everywhere
- **Line endings**: Handle CRLF and LF

### Security
- **No arbitrary code execution**: Validate all user input
- **Regex safety**: Limit regex complexity to prevent ReDoS
- **Path traversal prevention**: Validate file paths
- **No secrets in config**: Warn if sensitive data detected

---

## AI Agent Guidance

### When Writing Tests (TDD)
1. **Start with the test**: Never write implementation first
2. **Test one thing**: Each test function tests one behavior
3. **Use descriptive names**: `test_deny_pattern_overrides_allow_pattern()`
4. **Arrange-Act-Assert**: Structure tests clearly
5. **Use fixtures**: Share setup code with pytest fixtures

**Example**:
```python
def test_loads_yaml_configuration(tmp_path):
    # Arrange
    config_file = tmp_path / "config.yaml"
    config_file.write_text("rules:\n  file-placement:\n    enabled: true")

    # Act
    from src.config.loader import ConfigLoader
    loader = ConfigLoader()
    config = loader.load(config_file)

    # Assert
    assert config['rules']['file-placement']['enabled'] is True
```

### When Implementing (After Tests)
1. **Make tests pass**: Minimal implementation to pass tests
2. **Refactor**: Clean up once tests pass
3. **No premature optimization**: Make it work, then make it fast
4. **Follow patterns**: Use reference implementation as guide
5. **Type hints always**: Every function fully typed

**Example**:
```python
# src/config/loader.py
from pathlib import Path
import yaml

class ConfigLoader:
    """Load configuration from YAML or JSON."""

    def load(self, config_path: Path) -> dict[str, Any]:
        """Load config from file."""
        if not config_path.exists():
            return {}  # Default to empty config

        with open(config_path) as f:
            if config_path.suffix == '.yaml':
                return yaml.safe_load(f)
            # Add JSON support later
```

### When Stuck
1. **Check reference implementation**: Study the pattern in durable-code-test
2. **Read the test**: The test shows exactly what's needed
3. **Simplify**: Start with minimal implementation
4. **Ask for help**: Update PROGRESS_TRACKER.md with blocker

### Common Patterns

#### Pattern 1: BaseLintRule Subclass
```python
from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation, Severity

class MyRule(BaseLintRule):
    @property
    def rule_id(self) -> str:
        return "category.rule-name"

    @property
    def rule_name(self) -> str:
        return "Human Readable Name"

    @property
    def description(self) -> str:
        return "What this rule checks"

    def check(self, context: BaseLintContext) -> list[Violation]:
        violations = []
        # Check logic here
        if condition:
            violations.append(Violation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=1,
                column=0,
                message="Problem detected",
                severity=Severity.ERROR,
                suggestion="How to fix"
            ))
        return violations
```

#### Pattern 2: Using CliRunner for Tests
```python
from click.testing import CliRunner
from src.cli import cli

def test_cli_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['command', 'arg'])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

#### Pattern 3: Temporary Files in Tests
```python
def test_with_temp_file(tmp_path):
    """tmp_path is a pytest fixture."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# content")

    # Test with test_file
    assert test_file.exists()
```

---

## Risk Mitigation

### Risk: Regex Performance (ReDoS)
**Mitigation**:
- Limit regex complexity
- Timeout regex execution
- Validate patterns on load
- Test with pathological inputs

### Risk: Large File Memory Usage
**Mitigation**:
- Stream large files
- Limit file size for full read
- Process line-by-line where possible

### Risk: Plugin Security
**Mitigation**:
- Only load from known directories
- No eval() or exec()
- Validate rule classes before instantiation

### Risk: Breaking Changes to API
**Mitigation**:
- Semantic versioning
- Deprecation warnings
- Comprehensive tests
- API stability promise

---

## Future Enhancements

### Post-MVP (After PR12)

#### 1. Additional Linters
- **Naming conventions**: Check class, function, variable names
- **Import organization**: Detect circular imports, unused imports
- **Security patterns**: Hardcoded secrets, SQL injection patterns
- **Code complexity**: Cyclomatic complexity, nesting depth

#### 2. Auto-Fix Capabilities
```bash
# Suggest fixes
thai lint file-placement --fix-dry-run .

# Apply fixes
thai lint file-placement --fix .
```

#### 3. Language Support
- **JavaScript/TypeScript**: ESLint integration
- **Go**: AST-based linting
- **Rust**: Clippy integration
- **Java**: PMD/Checkstyle integration

#### 4. IDE Integration
- **VSCode Extension**: Real-time linting
- **IntelliJ Plugin**: Inline violations
- **Emacs/Vim**: Editor integration

#### 5. Web Dashboard
- **Metrics Over Time**: Track violation trends
- **Team Leaderboards**: Gamify code quality
- **Rule Analytics**: Which rules catch most issues

#### 6. Machine Learning
- **Custom Rule Suggestions**: Learn from fixes
- **Project-Specific Patterns**: Adapt to codebase style
- **False Positive Reduction**: Learn from ignores

---

## Related Documents

### Essential Reading
- **PROGRESS_TRACKER.md** - Start here for current status and next PR
- **PR_BREAKDOWN.md** - Detailed implementation steps for all PRs
- **`.ai/docs/PROJECT_CONTEXT.md`** - Overall project vision
- **`.roadmap/how-to-roadmap.md`** - How to use this roadmap system

### Reference Implementation
- **`/home/stevejackson/Projects/durable-code-test/tools/design_linters/`** - Pattern library

### Existing Project Docs
- **`.ai/docs/python-cli-architecture.md`** - CLI architecture patterns
- **`.ai/docs/PRE_COMMIT_STANDARDS.md`** - Pre-commit hook patterns
- **`.ai/howtos/python-cli/`** - CLI development howtos

---

## Development Philosophy

### TDD is Non-Negotiable
Tests are written before implementation, always. This is not optional.

### Reference, Don't Copy
Study the reference implementation to understand patterns, then write tests and implementation from scratch. Don't copy-paste.

### Simple First, Optimize Later
Make it work, make it right, make it fast - in that order.

### Document as You Go
Update PROGRESS_TRACKER.md after each PR. Keep documentation synchronized with code.

### Dogfood Early
Use the linter on its own codebase as soon as possible. Find issues early.

---

**Remember**: The goal is a production-ready linter that developers actually want to use. Make it fast, make it clear, make it helpful.
