# Contributing to thai-lint

**Purpose**: Guide for contributing to thai-lint, covering development setup, workflow, quality standards, and the roadmap-driven development process

**Scope**: All contributors (human and AI-assisted), covering code contributions, new linter proposals, bug fixes, and documentation changes

**Overview**: This document defines the contribution workflow for thai-lint, a multi-language linter for AI-generated code.
    Contributions follow a roadmap-driven process where non-trivial features require a committed roadmap before implementation begins.
    The guide covers development environment setup, branching conventions, quality gates, linter acceptance criteria,
    and the pull request lifecycle. AI-assisted development is a first-class workflow, with dedicated tooling in `AGENTS.md`
    and the `.ai/` directory to support agent-driven roadmap creation and implementation.

**Dependencies**: `AGENTS.md`, `.ai/howtos/how-to-roadmap.md`, `.ai/templates/roadmap-*.md.template`, `.ai/docs/FILE_HEADER_STANDARDS.md`

**Exports**: Contribution guidelines, quality gate definitions, linter acceptance criteria, roadmap workflow documentation

**Related**: [README.md](README.md), [AGENTS.md](AGENTS.md), [PROJECT_CONTEXT.md](.ai/docs/PROJECT_CONTEXT.md)

**Implementation**: Structured as a progressive guide from setup through advanced contribution patterns, with the roadmap-first rule as the central organizing principle

---

## Code of Conduct

Be an adult. Be decent. That's the policy.

## Development Setup

### Prerequisites

- **Python 3.11+**
- **Poetry** (dependency management)
- **just** (command runner, see [justfile](justfile))

### Getting Started

```bash
# Clone and install
git clone https://github.com/be-wise-be-kind/thai-lint.git
cd thai-lint
just init

# Verify your setup
just test
just lint-full
just format
```

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit and enforce formatting, linting, and secret detection. They are installed as part of `just init`. If hooks fail, fix the reported issues before committing.

## Branching and Commits

### Branch Naming

- `feature/*` - New features and linters
- `fix/*` - Bug fixes
- `docs/*` - Documentation changes

Never commit directly to `main`. All changes go through pull requests.

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): Brief description

Detailed description if needed.
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(linters): Add collection pipeline linter for Python
fix(cli): Correct SARIF output schema version
docs: Update linter acceptance criteria
```

## Contributing Features and Linters

### The Roadmap-First Rule

All non-trivial features and linters require a **committed roadmap before implementation begins**. This ensures alignment on scope, approach, and acceptance criteria before any code is written.

### When a Roadmap Is Required

- Adding a new linter
- Adding a major feature or capability
- Multi-PR implementation efforts
- Architectural changes

### When a Roadmap Is NOT Required

- Single-PR bug fixes
- Documentation updates
- Minor configuration changes
- Typo corrections

### Roadmap Process

1. **Open an issue** describing the feature or linter you want to build
2. **Get concept approval** from a maintainer before investing in a roadmap
3. **Create a roadmap** in `.roadmap/planning/[feature-name]/` using the templates in `.ai/templates/`:

```bash
# Copy the templates
cp .ai/templates/roadmap-progress-tracker.md.template .roadmap/planning/your-feature/PROGRESS_TRACKER.md
cp .ai/templates/roadmap-pr-breakdown.md.template .roadmap/planning/your-feature/PR_BREAKDOWN.md
cp .ai/templates/roadmap-ai-context.md.template .roadmap/planning/your-feature/AI_CONTEXT.md  # optional
```

4. **Fill in the placeholders** in each template with your feature's specifics
5. **Submit the roadmap as the first PR** for review
6. **Implement PRs sequentially** as defined in `PR_BREAKDOWN.md`
7. **Update `PROGRESS_TRACKER.md`** after each PR merges
8. **Move the roadmap** through the lifecycle: `planning/` -> `in-progress/` -> `complete/`

### Three-Document Structure

| Document | Required | Purpose |
|---|---|---|
| `PROGRESS_TRACKER.md` | Yes | Primary handoff document, tracks status of each PR |
| `PR_BREAKDOWN.md` | Yes (multi-PR) | Defines each PR's scope, files, and acceptance criteria |
| `AI_CONTEXT.md` | No | Architectural context and design decisions |

See `.roadmap/complete/` for real examples of finished roadmaps (e.g., `rust-linter-support/` with 7 PRs).

### Using AI Agents to Create Roadmaps

This project is designed for AI-assisted development. `AGENTS.md` and the `.ai/` directory serve as the AI agent entrypoints, providing howtos, templates, and standards that agents use automatically.

**To create a roadmap with an AI agent** (e.g., Claude Code), use prompts like:

- "I want to plan out a new linter for X"
- "Create a roadmap for adding Y support"
- "Plan the implementation of Z feature"
- "Break down the feature for W"

These prompts trigger the agent to read `.ai/howtos/how-to-roadmap.md` and use the roadmap templates. The agent helps break features into atomic PRs, fill in templates, and define success criteria.

**To continue or resume roadmap work**, use prompts like:

- "Continue the roadmap for X"
- "What's next in the Y roadmap?"
- "Resume work on Z"

The agent reads `PROGRESS_TRACKER.md` first and picks up where the previous session left off.

The agent reads `AGENTS.md` as its first action, which directs it to all relevant howtos, templates, and standards automatically. No manual setup is needed.

## Linter Acceptance Criteria

New linters must meet all six criteria to be accepted:

### 1. Complements Existing Tools

The linter must NOT duplicate functionality provided by established tools:
- **Python**: Pylint, Ruff, Flake8, Bandit, MyPy
- **JavaScript/TypeScript**: ESLint, Biome
- **Rust**: Clippy

Your proposal must cite which existing tools you evaluated and explain what gap your linter fills.

### 2. Targets AI-Generated Code Anti-Patterns

The linter must target patterns that are specifically prevalent in AI-generated code, supported by evidence. Include links, examples, or research demonstrating the anti-pattern's prevalence in AI output.

### 3. Validated Against Real Projects

Run validation trials against real open-source repositories. The false positive rate must be **below 5%**. Document the repositories tested, the number of findings, and the confirmed true/false positive breakdown.

### 4. Multi-Language Support Preferred

Linters that support multiple languages are preferred. If proposing a single-language linter, provide justification for why the pattern is language-specific.

### 5. All Three Output Formats

Every linter must support all three output formats:
- **text** - Human-readable console output
- **json** - Machine-readable JSON
- **sarif** - SARIF v2.1.0 for CI/CD integration

See `.ai/docs/SARIF_STANDARDS.md` for SARIF implementation requirements.

### 6. Follow Existing Patterns

- Place linter modules in `src/linters/`
- Register the linter in `src/cli.py`
- Include proper file headers per `.ai/docs/FILE_HEADER_STANDARDS.md`
- Follow the structure of existing linters as reference

## Quality Gates

All contributions must pass these quality gates before merging:

| Gate | Requirement | Command |
|---|---|---|
| Full lint suite | Exit code 0 | `just lint-full` |
| Pylint score | Exactly 10.00/10 | `poetry run pylint src/` |
| Complexity | A-grade (every block) | `just lint-complexity` |
| Tests | Zero failures | `just test` |
| File headers | Per FILE_HEADER_STANDARDS.md | Checked by header linter |

### Pre-PR Checklist

Run these commands before opening a pull request:

```bash
just lint-full        # Must exit with code 0
just test             # Must exit with code 0
```

Verify in the output:
- Pylint reports `Your code has been rated at 10.00/10`
- Xenon shows no `ERROR:xenon:` lines
- All tests pass

### Linter Suppressions

Any linter suppression (`# type: ignore`, `# pylint: disable`, `# noqa`, `# nosec`) requires a justification comment explaining why the suppression is necessary and what alternatives were considered.

## Pull Request Process

1. **Keep your branch current** with `main`
2. **Pass all quality gates locally** before pushing
3. **Use a conventional commit title** for the PR (e.g., `feat(linters): Add collection pipeline linter`)
4. **Reference the roadmap PR number** in the description if this is part of a roadmap
5. **Update `PROGRESS_TRACKER.md`** after your PR merges
6. **One logical change per PR** - avoid combining unrelated changes

## Getting Help

- **[PROJECT_CONTEXT.md](.ai/docs/PROJECT_CONTEXT.md)** - Architecture and design decisions
- **[.ai/howtos/](.ai/howtos/)** - Step-by-step guides for common tasks
- **[src/linters/](src/linters/)** - Reference implementations for existing linters
- **[.roadmap/complete/](.roadmap/complete/)** - Examples of finished roadmaps
- **[GitHub Issues](https://github.com/be-wise-be-kind/thai-lint/issues)** - Report bugs or propose features
