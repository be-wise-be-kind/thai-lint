# Contributing to thai-lint

**Purpose**: Guidelines for contributing to the thai-lint project

**Scope**: Development setup, code standards, testing, and PR workflows

**Overview**: Comprehensive guide for contributors covering environment setup, code quality requirements,
    testing procedures, and the pull request workflow. This document ensures consistent development
    practices across all contributors and maintains the high quality standards required for thai-lint.

**Dependencies**: Poetry, Python 3.11+, just (command runner)

**Exports**: Development workflows, quality standards, and contribution procedures

**Related**: README.md, AGENTS.md, .ai/docs/FILE_HEADER_STANDARDS.md

**Implementation**: Follows the established project conventions with strict quality gates

---

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- [just](https://github.com/casey/just) for running commands

### Installation

```bash
# Clone the repository
git clone https://github.com/be-wise-be-kind/thai-lint.git
cd thai-lint

# Install dependencies with Poetry
poetry install

# Verify installation
poetry run thai-lint --help
```

### IDE Setup

For VS Code, recommended extensions:
- Python (Microsoft)
- Pylint
- MyPy Type Checker

## Running Tests

```bash
# Run all tests
just test

# Run tests with coverage
just test-coverage

# Run specific test file
poetry run pytest tests/unit/linters/test_dry.py -v

# Run tests matching pattern
poetry run pytest -k "test_dry" -v
```

All tests must pass before submitting a PR.

## Code Quality

### Linting Commands

```bash
# Quick lint (Ruff only)
just lint

# Full lint suite (all linters + type checking)
just lint-full

# Auto-fix formatting issues
just format

# Individual linting steps
just lint-security      # Security scanning (Bandit)
just lint-complexity    # Complexity analysis (Xenon)
just lint-solid         # SOLID principles (thai-lint srp)
just lint-lazy-ignores  # Check for unjustified suppressions
```

### Quality Requirements

All code must meet these standards before merge:

| Check | Requirement | Command |
|-------|-------------|---------|
| Tests | All pass | `just test` |
| Pylint | Score 10.00/10 | `poetry run pylint src/` |
| Xenon | All A-grade complexity | `just lint-complexity` |
| MyPy | No type errors | `poetry run mypy src/` |
| Ruff | No violations | `just lint` |
| Full suite | Exit code 0 | `just lint-full` |

### Code Style

- Follow PEP 8 (enforced by Ruff)
- Use type hints for all function signatures
- Google-style docstrings for public functions
- Maximum cyclomatic complexity: A-grade (Xenon)

### File Headers

All new files must include proper headers. See `.ai/docs/FILE_HEADER_STANDARDS.md` for templates.

Python files require:
```python
"""
Purpose: Brief description
Scope: What this module covers
Overview: Detailed explanation of functionality
Dependencies: Key imports and related modules
Exports: Main classes/functions provided
Interfaces: Key APIs exposed
Implementation: Notable patterns used
"""
```

## Git Workflow

### Branches

- `main` - Production-ready code (protected)
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): Brief description

Detailed description if needed.

Co-Authored-By: Your Name <email@example.com>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(lbyl): add hasattr pattern detector
fix(dry): handle empty files gracefully
docs(readme): add LBYL linter to table
test(srp): add edge case for nested classes
```

## Pull Request Process

### Before Submitting

1. **Tests pass**: `just test`
2. **Linting clean**: `just lint-full`
3. **Quality gates met**: Pylint 10.00/10, Xenon A-grade
4. **Documentation updated** (if applicable)
5. **Commit messages follow conventions**

### PR Requirements

- Clear title following commit message format
- Description of changes and motivation
- Link to related issue (if applicable)
- All CI checks passing

### Review Process

1. Submit PR against `main`
2. Automated CI runs tests and linting
3. Maintainer reviews code
4. Address feedback
5. Merge when approved

## Adding a New Linter

For detailed guidance on implementing new linters, see:
- `.ai/howtos/how-to-add-linter.md`
- `.ai/docs/SARIF_STANDARDS.md`

Quick checklist:
1. Create linter module in `src/linters/`
2. Write tests first (TDD approach)
3. Implement all 3 output formats (text, json, sarif)
4. Register CLI command in `src/cli.py`
5. Add documentation in `docs/`
6. Update README.md

## Roadmap-Driven Development

Major features follow a roadmap workflow:

1. Plan in `.roadmap/planning/[feature-name]/`
2. Move to `.roadmap/in-progress/` when starting
3. Create PRs following the PR_BREAKDOWN.md
4. Track progress in PROGRESS_TRACKER.md
5. Move to `.roadmap/complete/` when finished

See `.ai/howtos/how-to-roadmap.md` for detailed workflow.

## Getting Help

- **Documentation**: Check `.ai/docs/` for architecture and standards
- **How-to guides**: See `.ai/howtos/` for common tasks
- **Issues**: [github.com/be-wise-be-kind/thai-lint/issues](https://github.com/be-wise-be-kind/thai-lint/issues)

## Code of Conduct

Be respectful and constructive. We welcome contributions from everyone.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
