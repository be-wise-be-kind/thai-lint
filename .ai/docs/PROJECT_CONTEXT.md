# thai-lint - Project Context

**Purpose**: Comprehensive project context for AI agents working on thai-lint

**Scope**: Architecture, design decisions, development guidelines, and project vision

**Overview**: Context document for AI agents maintaining, extending, or using the thai-lint CLI application.
    Describes the purpose, architecture, design decisions, and patterns for a multi-language linter dedicated
    to identifying common mistakes made by AI agents when generating code. Essential for understanding the
    project's mission, technical approach, and development standards.

**Dependencies**: Click (CLI framework), Python 3.11+, tree-sitter (multi-language AST parsing), Ruff (linting),
    pytest (testing), Poetry (dependency management)

**Exports**: Project context, architectural patterns, development guidelines

**Related**: AGENTS.md for quick reference, `.ai/index.yaml` for navigation, `.ai/ai-context.md` for concise overview

**Implementation**: Python CLI application with extensible plugin-based linter architecture for multiple programming languages

---

## What thai-lint Does

**thai-lint** (The AI Linter) is a specialized linter dedicated to identifying and preventing common mistakes made by AI agents when generating code.

### Mission

Provide governance and quality control for AI-generated code across multiple programming languages, catching AI-specific anti-patterns, security issues, and quality problems that traditional linters miss.

### Target Users

- **Development teams** using AI coding assistants (Claude, Copilot, etc.)
- **DevOps engineers** implementing AI-assisted automation
- **Organizations** establishing AI code quality standards
- **Individual developers** wanting to validate AI-generated code

### Core Capabilities

1. **Multi-Language Support** - Lint Python, TypeScript/JavaScript, and Rust (extensible architecture)
2. **AI-Specific Rules** - Detect patterns specific to AI-generated code (duplicate code, deep nesting, magic numbers, SRP violations, etc.)
3. **Configurable Severity** - Warning vs. error levels, customizable rule sets via `.thailint.yaml`
4. **Multiple Output Formats** - Text (human-readable), JSON (machine-readable), SARIF v2.1.0 (CI/CD integration)
5. **CLI Interface** - Professional command-line tool with subcommands, options, and configuration management
6. **Library API** - Programmatic access via `src.api.Linter` class for embedding in editors, CI/CD, and automation
7. **Parallel Linting** - Orchestrator supports parallel file processing via `--parallel` flag
8. **Docker Support** - Containerized distribution via Docker and docker-compose

---

## Linters

thai-lint includes 18 specialized linters organized by category:

### Structure Quality
| Linter | Rule Class | Languages | Description |
|--------|-----------|-----------|-------------|
| `nesting` | `NestingDepthRule` | Python, TypeScript, JS, Rust | Excessive control flow nesting depth |
| `srp` | `SRPRule` | Python, TypeScript, JS | Single Responsibility Principle violations |

### Code Smells
| Linter | Rule Class | Languages | Description |
|--------|-----------|-----------|-------------|
| `dry` | `DRYRule` | Python, TypeScript, JS | Duplicate code detection via token hashing |
| `magic-numbers` | `MagicNumberRule` | Python, TypeScript, JS | Unexplained numeric literals |

### Code Patterns
| Linter | Rule Class | Languages | Description |
|--------|-----------|-----------|-------------|
| `improper-logging` | `PrintStatementRule` | Python, TypeScript, JS | Print statements and conditional verbose guards |
| `method-property` | `MethodPropertyRule` | Python, TypeScript, JS | Methods that should be properties |
| `stateless-class` | `StatelessClassRule` | Python | Classes with no instance state |
| `lazy-ignores` | `LazyIgnoresRule` | Python | Unjustified linter suppression comments |
| `lbyl` | `LBYLRule` | Python | Look Before You Leap vs EAFP patterns |
| `stringly-typed` | `StringlyTypedRule` | Python, TypeScript, JS | String enums instead of proper types |
| `cqs` | `CQSRule` | Python, TypeScript, JS | Command-Query Separation violations |

### Structure
| Linter | Rule Class | Languages | Description |
|--------|-----------|-----------|-------------|
| `file-placement` | `FilePlacementRule` | Any | Files in wrong directories per project conventions |
| `pipeline` | `CollectionPipelineRule` | Python, TypeScript, JS | Imperative loops instead of collection pipelines |

### Documentation
| Linter | Rule Class | Languages | Description |
|--------|-----------|-----------|-------------|
| `file-header` | `FileHeaderRule` | Python | Missing or incomplete file headers |

### Performance
| Linter | Rule Class | Languages | Description |
|--------|-----------|-----------|-------------|
| `perf` | (aggregated) | Python, TypeScript | Performance anti-patterns (aggregates sub-rules) |
| `string-concat-loop` | `StringConcatLoopRule` | Python, TypeScript | O(n²) string concatenation in loops |
| `regex-in-loop` | (via perf) | Python | Uncompiled regex in loops |

### Rust
| Linter | Rule Class | Languages | Description |
|--------|-----------|-----------|-------------|
| `unwrap-abuse` | `UnwrapAbuseRule` | Rust | Excessive `.unwrap()` instead of proper error handling |
| `clone-abuse` | `CloneAbuseRule` | Rust | Unnecessary `.clone()` calls |
| `blocking-async` | `BlockingAsyncRule` | Rust | Blocking operations in async functions |

---

## Architecture Overview

### Source Code Structure

```
src/
├── cli_main.py          # CLI entrypoint, imports and registers all commands
├── api.py               # Library API (Linter class for programmatic usage)
├── __init__.py           # Package init, exports Linter
├── cli/                  # CLI package
│   ├── main.py           # Click CLI group definition
│   ├── __main__.py       # python -m src.cli entrypoint
│   ├── config.py         # Config commands (show, get, set, reset, init-config)
│   ├── config_merge.py   # Config merge utilities
│   ├── utils.py          # Shared CLI utilities
│   └── linters/          # Linter command registrations
│       ├── __init__.py   # Imports all linter modules to register commands
│       ├── structure_quality.py  # nesting, srp commands
│       ├── code_smells.py        # dry, magic-numbers commands
│       ├── code_patterns.py      # improper-logging, method-property, stateless-class, etc.
│       ├── structure.py          # file-placement, pipeline commands
│       ├── documentation.py      # file-header command
│       ├── performance.py        # perf, string-concat-loop, regex-in-loop commands
│       ├── rust.py               # unwrap-abuse, clone-abuse, blocking-async commands
│       └── shared.py             # Shared command utilities
├── core/                 # Core framework
│   ├── base.py           # BaseLintRule, BaseLintContext, MultiLanguageLintRule
│   ├── types.py          # Violation, Severity, and other data types
│   ├── constants.py      # Language enum and other constants
│   ├── registry.py       # Rule discovery and registration
│   ├── rule_discovery.py # Dynamic rule loading
│   ├── rule_aliases.py   # Backward-compatible rule ID aliases
│   ├── config_parser.py  # Configuration parsing
│   ├── cli_utils.py      # CLI utility functions
│   ├── linter_utils.py   # Linter helper functions
│   ├── python_lint_rule.py # PythonOnlyLintRule base class
│   ├── violation_builder.py # Builder pattern for violations
│   └── violation_utils.py   # Violation processing utilities
├── linters/              # Linter implementations (one directory per linter)
│   ├── blocking_async/   # Rust blocking-in-async detection
│   ├── clone_abuse/      # Rust clone abuse detection
│   ├── collection_pipeline/ # Collection pipeline patterns
│   ├── cqs/              # Command-Query Separation
│   ├── dry/              # Don't Repeat Yourself
│   ├── file_header/      # File header validation
│   ├── file_placement/   # File placement rules
│   ├── lazy_ignores/     # Unjustified suppression comments
│   ├── lbyl/             # Look Before You Leap
│   ├── magic_numbers/    # Magic number detection
│   ├── method_property/  # Method-to-property suggestions
│   ├── nesting/          # Nesting depth analysis
│   ├── performance/      # Performance anti-patterns
│   ├── print_statements/ # Improper logging (print/console detection)
│   ├── srp/              # Single Responsibility Principle
│   ├── stateless_class/  # Stateless class detection
│   ├── stringly_typed/   # Stringly-typed code detection
│   └── unwrap_abuse/     # Rust unwrap abuse detection
├── orchestrator/         # Linting orchestration engine
│   ├── core.py           # Orchestrator class (file collection, rule execution, output)
│   └── language_detector.py # File language detection
├── formatters/           # Output format implementations
│   └── sarif.py          # SARIF v2.1.0 formatter
├── analyzers/            # Language-specific AST analysis utilities
│   ├── typescript_base.py # TypeScript/JS tree-sitter base analyzer
│   ├── rust_base.py      # Rust tree-sitter base analyzer
│   ├── rust_context.py   # Rust lint context
│   └── ast_utils.py      # AST utility functions (parent map building)
├── linter_config/        # Configuration loading and management
│   └── loader.py         # LinterConfigLoader
├── templates/            # init-config template files
└── utils/                # Shared utilities
    └── project_root.py   # Project root detection
```

### Plugin Architecture

**Base Rule Interface** (`src/core/base.py`):

```python
class BaseLintContext(ABC):
    """Provides file information to rules during analysis."""
    file_path: Path | None      # Path to file being analyzed
    file_content: str | None    # File content as string
    language: str               # Language identifier

class BaseLintRule(ABC):
    """Base class for all linting rules."""
    rule_id: str        # Unique ID (e.g., 'nesting.depth')
    rule_name: str      # Human-readable name
    description: str    # Rule description

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for violations in the given context."""

    def finalize(self) -> list[Violation]:
        """Optional: cross-file analysis after all files processed."""
```

**Multi-Language Support** (`src/core/base.py`):

```python
class MultiLanguageLintRule(BaseLintRule):
    """Template method pattern for language dispatch."""

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Dispatches to _check_python(), _check_typescript(), or _check_rust()."""

    def _load_config(self, context: BaseLintContext) -> Any: ...
    def _check_python(self, context, config) -> list[Violation]: ...
    def _check_typescript(self, context, config) -> list[Violation]: ...
    def _check_rust(self, context, config) -> list[Violation]: ...
```

**Python-Only Rules** (`src/core/python_lint_rule.py`):

```python
class PythonOnlyLintRule(BaseLintRule, Generic[T]):
    """Base for rules that only apply to Python files."""
```

### Orchestrator

The `Orchestrator` class (`src/orchestrator/core.py`) coordinates the linting pipeline:

1. Collects files from specified paths
2. Detects file languages via `LanguageDetector`
3. Creates `BaseLintContext` instances for each file
4. Executes applicable rules against each context
5. Calls `finalize()` on rules that need cross-file analysis (e.g., DRY)
6. Collects and formats violations for output

### Library API

The `Linter` class (`src/api.py`) provides a clean programmatic interface:

```python
from src import Linter

linter = Linter(config_file='.thailint.yaml')
violations = linter.lint('src/', rules=['file-placement'])
```

---

## Design Decisions

### Decision 1: Click Over Typer/Argparse

**Why**: Click is mature, widely adopted, decorator-based (clean syntax), extensive plugin ecosystem

**Impact**: Easier to add subcommands, nested command groups, configuration via decorators

### Decision 2: Plugin-Based Linter Architecture

**Why**: Each linter is independent with its own directory, configuration, and tests. Rules are discovered dynamically via the registry system.

**Impact**: Adding a linter requires only creating the linter module, implementing the `BaseLintRule` interface, and registering a CLI command. No changes to core framework needed.

### Decision 3: tree-sitter for Multi-Language Parsing

**Why**: tree-sitter provides fast, incremental, multi-language AST parsing. Supports TypeScript, JavaScript, Rust, and other languages with a consistent API.

**Impact**: Enables accurate analysis of non-Python languages without language-specific parser dependencies. Used in `src/analyzers/` base classes.

### Decision 4: Context-Based Rule Execution

**Why**: The `BaseLintContext` pattern decouples rules from file I/O. Rules receive parsed context objects rather than raw file paths.

**Impact**: Rules are testable in isolation, language detection is centralized, and the orchestrator controls the execution pipeline.

### Decision 5: SARIF Output for CI/CD

**Why**: SARIF (Static Analysis Results Interchange Format) is the standard for GitHub Code Scanning and other CI/CD tools.

**Impact**: All linters must support text, JSON, and SARIF output formats. The SARIF formatter in `src/formatters/sarif.py` handles the conversion.

### Decision 6: Configuration via `.thailint.yaml`

**Why**: Project-level configuration in the project root. Supports YAML and JSON formats.

**Impact**: Each linter reads its configuration section from the loaded config. `LinterConfigLoader` handles discovery and parsing.

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Modern type hints, async support |
| CLI Framework | Click 8.x | Decorator-based CLI |
| Multi-Language Parsing | tree-sitter | TypeScript, JavaScript, Rust AST analysis |
| Python Parsing | ast module | Python AST analysis |
| Dependency Manager | Poetry | Isolated venvs, lockfiles |
| Linting | Ruff | Fast linting + formatting |
| Type Checking | MyPy (strict mode) | Static type checking |
| Testing | pytest | Fixtures, parametrization, coverage |
| Complexity | Xenon + Radon | Cyclomatic complexity (A-grade required) |
| Security | Bandit, pip-audit, Gitleaks | Code security, CVE scanning, secret detection |
| Containerization | Docker + docker-compose | Cross-platform distribution |
| CI/CD | GitHub Actions | Matrix testing, automated releases |
| Task Runner | just (justfile) | Build, test, lint, format commands |

---

## Development Guidelines

### Code Standards

- Follow PEP 8 style guide (enforced by Ruff)
- Use type hints everywhere (checked by MyPy strict mode)
- Maximum cyclomatic complexity: **A** (enforced by Xenon with `--max-absolute A`)
- Docstrings required for all public functions (Google-style)
- Atemporal language in documentation (no "currently", "now", "new", "old", dates)
- No print statements (use logging or Click output)

### Quality Gates

All code must pass before commit:

| Tool | Requirement | Command |
|------|-------------|---------|
| Ruff | All checks pass | `just lint` |
| Pylint | Score 10.00/10 | `poetry run pylint src/` |
| MyPy | Zero errors | `poetry run mypy src/` |
| Xenon | ALL blocks A-grade | `just lint-complexity` |
| Bandit | All security checks | `just lint-security` |
| Tests | All passing | `just test` |

**Run all checks**: `just lint-full`

### Testing Requirements

- All new features require tests in `tests/`
- Test both success and failure cases
- Use pytest fixtures for reusable components
- Linter tests organized in `tests/unit/linters/<linter_name>/`

### Configuration

Project configuration lives in `.thailint.yaml` at the project root. Supports:

- Per-linter enable/disable and thresholds
- File ignore patterns (glob syntax)
- Language-specific overrides
- Presets (strict, standard, lenient) via `init-config`

---

## Related Documents

### Essential Reading
- **AGENTS.md** - Primary entry point for AI agents
- **`.ai/index.yaml`** - Repository structure map
- **`.ai/ai-context.md`** - Concise development context
- **`.ai/ai-rules.md`** - Quality gates and mandatory rules

### Architecture
- **`.ai/docs/python-cli-architecture.md`** - CLI architecture patterns
- **`.ai/docs/SARIF_STANDARDS.md`** - SARIF output format requirements
- **`.ai/docs/FILE_HEADER_STANDARDS.md`** - File header standards

### How-To Guides
- **`.ai/howtos/how-to-add-linter.md`** - Implementing new linters
- **`.ai/howtos/how-to-fix-linting-errors.md`** - Fixing quality violations
- **`.ai/howtos/how-to-refactor-for-quality.md`** - Architectural refactoring

### User-Facing Documentation
- **`docs/cli-reference.md`** - Complete CLI command reference
- **`docs/configuration.md`** - Configuration file reference
- **`docs/api-reference.md`** - Library API documentation
- **`docs/getting-started.md`** - Installation and quick start

---

**Remember**: This project aims to improve AI-generated code quality. The irony of using AI to build a tool that lints AI code is not lost on us. We dogfood our own linter and fix violations it finds in our codebase.
