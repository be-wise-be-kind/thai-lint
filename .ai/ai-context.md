"""
File: .ai/ai-context.md

Purpose: Development context and patterns for AI agents working on thai-lint

Exports: Project overview, architecture, key patterns, conventions

Depends: index.yaml, ai-rules.md

Overview: Comprehensive development context document that provides AI agents with
    everything needed to understand this project. Includes project purpose, CLI
    architecture, code patterns, and development conventions.
"""

# AI Development Context

**Purpose**: Everything an agent needs to understand this project for development

**Deep Dive**: For comprehensive architecture details, see `.ai/docs/PROJECT_CONTEXT.md`

---

## Mission & Vision

**thai-lint** (The AI Linter) provides governance and quality control for AI-generated code. It catches AI-specific anti-patterns, security issues, and quality problems that traditional linters miss.

### Target Users

- Development teams using AI coding assistants (Claude, Copilot, etc.)
- DevOps engineers implementing AI-assisted automation
- Organizations establishing AI code quality standards
- Individual developers validating AI-generated code

### What This Repo Does

- Lints AI-generated code for common AI-specific patterns
- Supports multiple languages: **Python, TypeScript, JavaScript, Rust**
- Outputs in multiple formats: text, JSON, SARIF (for CI/CD)
- Detects: nesting depth, magic numbers, SRP violations, DRY violations, stringly-typed code, improper logging, CQS violations, performance anti-patterns, Rust-specific issues, and more (18 linters total)

### What This Repo Does NOT Do

- Replace standard linters (Ruff, ESLint) - it complements them
- Provide auto-fix capabilities (detection only)
- Generate or refactor code

---

## AI-Specific Detection

Traditional linters catch syntax and style. Thai-lint catches **AI patterns**:

| Pattern | Description | Example |
|---------|-------------|---------|
| Magic Numbers | Unexplained numeric literals | `if count > 42:` |
| Deep Nesting | Excessive control flow depth | 5+ levels of if/for/try |
| SRP Violations | Classes doing too much | 15+ methods per class |
| DRY Violations | Duplicate code blocks | Same 5+ lines repeated |
| Stringly-Typed | String enums instead of proper types | `if status == "active":` |
| Improper Logging | print()/console.log() instead of logging | `print("debug info")` |
| Blocking Async | Sync calls in async Rust functions | `std::fs::read` in async fn |
| Unwrap Abuse | Excessive .unwrap() in Rust | `result.unwrap()` everywhere |

---

## The thailint CLI

```bash
thailint <command> [options] <paths>

# Linting commands
thailint nesting <paths>           # Check nesting depth
thailint magic-numbers <paths>     # Check for magic numbers
thailint srp <paths>               # Check single responsibility
thailint dry <paths>               # Check for duplicate code
thailint stringly-typed <paths>    # Check for string-based typing
thailint improper-logging <paths>  # Check for print/console statements
thailint method-property <paths>   # Check methods that should be properties
thailint stateless-class <paths>   # Check for stateless classes
thailint file-placement <paths>    # Check file placement conventions
thailint file-header <paths>       # Check file headers
thailint pipeline <paths>          # Check for collection pipeline patterns
thailint lazy-ignores <paths>      # Check for unjustified suppressions
thailint lbyl <paths>              # Check LBYL vs EAFP patterns
thailint perf <paths>              # Check performance anti-patterns
thailint string-concat-loop <paths> # Check string concat in loops
thailint regex-in-loop <paths>     # Check regex compilation in loops
thailint unwrap-abuse <paths>      # Check Rust unwrap abuse
thailint clone-abuse <paths>       # Check Rust clone abuse
thailint blocking-async <paths>    # Check Rust blocking in async

# Configuration commands
thailint init-config               # Generate .thailint.yaml
thailint config show               # Show configuration
thailint config get <key>          # Get config value
thailint config set <key> <value>  # Set config value
thailint config reset              # Reset to defaults

# Global options
thailint --version                 # Show version
thailint --verbose                 # Enable verbose output
thailint --config <path>           # Use specific config file
thailint --parallel                # Enable parallel linting
thailint --format [text|json|sarif] # Output format
```

---

## Architecture

### Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| CLI Framework | Click |
| AST Parsing | tree-sitter (TypeScript, JS, Rust), ast (Python) |
| Testing | pytest |
| Packaging | Poetry |

### Key Directories

```
src/
├── cli_main.py         # CLI entrypoint (registers all commands)
├── api.py              # Library API (Linter class)
├── cli/                # CLI package
│   ├── main.py         # Click CLI group definition
│   ├── config.py       # Configuration commands
│   └── linters/        # Linter command registrations
├── core/               # Framework (BaseLintRule, BaseLintContext, types)
│   ├── base.py         # Abstract base classes
│   └── types.py        # Violation, Severity types
├── linters/            # Linter implementations (18 directories)
├── orchestrator/       # Linting pipeline (file collection, execution)
├── formatters/         # Output formatters (SARIF)
├── analyzers/          # Language-specific AST utilities (tree-sitter)
├── linter_config/      # Configuration loading
└── utils/              # Shared utilities

tests/
├── unit/               # Unit tests
│   └── linters/        # Linter-specific tests
└── integration/        # Integration tests
```

---

## Key Patterns

### CLI Commands (Click)

```python
import click

@click.command()
@click.argument("paths", nargs=-1)
@click.option("--format", type=click.Choice(["text", "json", "sarif"]))
def my_command(paths: tuple[str, ...], format: str) -> None:
    """Command description."""
    ...
```

### Linter Interface

All linters implement `BaseLintRule` from `src/core/base.py`:

```python
from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation

class MyRule(BaseLintRule):
    @property
    def rule_id(self) -> str: return "my-rule.check"
    @property
    def rule_name(self) -> str: return "My Rule"
    @property
    def description(self) -> str: return "Checks for X"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Analyze file and return violations."""
        ...
```

For multi-language linters, extend `MultiLanguageLintRule` which provides
language dispatch via `_check_python()`, `_check_typescript()`, `_check_rust()`.

### Output Formats

All linters **must** support three output formats:
- `text` - Human-readable console output
- `json` - Machine-readable JSON
- `sarif` - SARIF v2.1.0 for CI/CD integration (see `.ai/docs/SARIF_STANDARDS.md`)

---

## Adding a New Linter

1. Create directory: `src/linters/<linter_name>/`
2. Add `__init__.py` with public API exports
3. Implement rule class extending `BaseLintRule` or `MultiLanguageLintRule`
4. Implement all 3 output formats (text, json, sarif)
5. Register CLI command in `src/cli/linters/` (appropriate module)
6. Add tests in `tests/unit/linters/<linter_name>/`
7. Update documentation in `docs/`

**Detailed guide**: `.ai/howtos/how-to-add-linter.md`

---

## File Headers

All Python files require standardized headers. See `.ai/docs/FILE_HEADER_STANDARDS.md`.

---

## DO NOT

- Use print() statements (use logging or Click output)
- Skip type hints (MyPy strict mode)
- Commit without running quality gates (`just lint-full`)
- Add suppressions (noqa, type: ignore) without asking
- Skip reading `.ai/index.yaml` before starting work
- Commit directly to main branch
