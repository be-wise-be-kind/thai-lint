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
- Supports multiple languages: Python, TypeScript, JavaScript
- Outputs in multiple formats: text, JSON, SARIF (for CI/CD)
- Detects: nesting depth, magic numbers, SRP violations, DRY violations, stringly-typed code

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

---

## The thailint CLI

```bash
thailint <command> [options] <paths>

# Commands
thailint lint <paths>           # Run all linters
thailint nesting <paths>        # Check nesting depth
thailint magic-numbers <paths>  # Check for magic numbers
thailint srp <paths>            # Check single responsibility
thailint dry <paths>            # Check for duplicate code
thailint stringly-typed <paths> # Check for string-based typing
```

---

## Architecture

### Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| CLI Framework | Click |
| AST Parsing | tree-sitter (multi-language) |
| Testing | pytest |
| Packaging | Poetry |

### Key Directories

```
src/
├── cli.py              # Main CLI entry point
├── linters/            # Individual linter implementations
│   ├── nesting/        # Nesting depth linter
│   ├── magic_numbers/  # Magic numbers linter
│   ├── srp/            # Single responsibility linter
│   ├── dry/            # DRY violations linter
│   ├── stringly_typed/ # Stringly-typed code linter
│   └── ...
├── parsers/            # Language-specific parsers
└── models/             # Shared data models

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

All linters follow a common interface:

```python
from src.models import LintResult

class MyLinter:
    def lint(self, file_path: str, content: str) -> list[LintResult]:
        """Analyze file and return list of violations."""
        ...
```

### Output Formats

All linters **must** support three output formats:
- `text` - Human-readable console output
- `json` - Machine-readable JSON
- `sarif` - SARIF v2.1.0 for CI/CD integration (see `.ai/docs/SARIF_STANDARDS.md`)

---

## Adding a New Linter

1. Create directory: `src/linters/<linter_name>/`
2. Add `__init__.py` with public API exports
3. Implement linter class following common interface
4. Implement all 3 output formats (text, json, sarif)
5. Register in CLI (`src/cli.py`)
6. Add tests in `tests/unit/linters/<linter_name>/`
7. Update AGENTS.md with new command

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
