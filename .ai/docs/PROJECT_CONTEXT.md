# thai-lint - Project Context

**Purpose**: Comprehensive project context for AI agents working on thai-lint

**Scope**: Architecture, design decisions, development guidelines, and project vision

**Overview**: Context document for AI agents maintaining, extending, or using the thai-lint CLI application.
    Describes the purpose, architecture, design decisions, and patterns for a multi-language linter dedicated
    to identifying common mistakes made by AI agents when generating code. Essential for understanding the
    project's mission, technical approach, and development standards.

**Dependencies**: Click (CLI framework), Python 3.11+, Ruff (linting), pytest (testing), Poetry (dependency management)

**Exports**: Project context, architectural patterns, development guidelines, success criteria

**Related**: AGENTS.md for quick reference, `.ai/index.yaml` for navigation, `.roadmap/python-cli-install/AI_CONTEXT.md` for installation context

**Implementation**: Python CLI application with extensible linter architecture for multiple programming languages

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

1. **Multi-Language Support** - Lint Python, JavaScript/TypeScript, and additional languages (extensible architecture)
2. **AI-Specific Rules** - Detect patterns specific to AI-generated code (hardcoded paths, missing error handling, etc.)
3. **Configurable Severity** - Warning vs. error levels, customizable rule sets
4. **Auto-Fix Support** - Suggest and apply fixes for detected issues
5. **CLI Interface** - Professional command-line tool with subcommands, options, and configuration management

---

## AI-Specific Linting Rules

Traditional linters catch syntax errors and style violations. thai-lint catches **AI-specific anti-patterns**:

### Common AI Mistakes

1. **Hardcoded File Paths**
   - AI often generates absolute paths instead of relative
   - Example: `/home/user/project/file.txt` instead of `./file.txt`
   - Rule: Detect absolute paths in source code

2. **Missing Error Handling**
   - AI tends to generate "happy path" code without error cases
   - Example: File I/O without try/catch, API calls without timeout/retry
   - Rule: Detect unhandled exceptions, missing validation

3. **Over-Generic Variable Names**
   - AI sometimes uses `data`, `result`, `value` excessively
   - Example: Multiple `data` variables in same scope
   - Rule: Detect vague naming patterns

4. **Missing Type Hints** (Python-specific)
   - AI may omit type annotations for function parameters/returns
   - Example: `def process(data):` instead of `def process(data: dict[str, Any]) -> Result:`
   - Rule: Require type hints for public functions

5. **Incomplete Test Coverage**
   - AI generates tests for success cases, often skips edge cases
   - Example: Testing valid input but not invalid/boundary cases
   - Rule: Analyze test files for coverage patterns

6. **Security Vulnerabilities**
   - AI may introduce SQL injection, hardcoded secrets, weak crypto
   - Example: String concatenation for SQL queries, API keys in code
   - Rule: Detect security anti-patterns

7. **Inconsistent Code Style**
   - AI may mix formatting styles from different examples
   - Example: Mixing spaces and tabs, inconsistent naming conventions
   - Rule: Enforce consistent style per language

---

## Architecture Overview

### CLI Application Structure

```
src/
├── cli.py           # Main CLI entrypoint with Click commands
├── config.py        # YAML/JSON configuration file management
├── commands/        # Individual command implementations
│   ├── lint.py      # Linting command
│   ├── check.py     # Check command (alias for lint)
│   └── fix.py       # Auto-fix command
├── linters/         # Language-specific linters
│   ├── base.py      # Base linter interface
│   ├── python.py    # Python linter (AST-based)
│   ├── javascript.py # JavaScript/TypeScript linter
│   └── ...          # Additional languages
├── rules/           # Linting rules
│   ├── base.py      # Base rule interface
│   ├── hardcoded_paths.py
│   ├── missing_error_handling.py
│   └── ...          # Additional rules
└── utils/           # Shared utilities
    ├── logger.py    # Structured logging
    └── errors.py    # Custom exceptions

tests/
├── test_cli.py      # CLI invocation tests
├── test_config.py   # Configuration tests
├── test_linters/    # Linter-specific tests
└── test_rules/      # Rule-specific tests
```

### Extensible Linter Architecture

**Base Linter Interface** (`src/linters/base.py`):
```python
class BaseLinter(ABC):
    @abstractmethod
    def lint_file(self, file_path: Path) -> list[LintViolation]:
        """Lint a single file and return violations."""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """Return list of file extensions this linter handles."""
        pass
```

**Language-Specific Linters** implement the interface:
- **PythonLinter**: Uses AST (Abstract Syntax Tree) analysis
- **JavaScriptLinter**: Uses ESLint plugin architecture
- Additional linters added as needed

### Rule Engine

**Base Rule Interface** (`src/rules/base.py`):
```python
class BaseRule(ABC):
    severity: Severity  # WARNING or ERROR
    rule_id: str
    message: str

    @abstractmethod
    def check(self, node: ASTNode) -> bool:
        """Check if this node violates the rule."""
        pass

    @abstractmethod
    def suggest_fix(self, node: ASTNode) -> Optional[str]:
        """Suggest a fix for this violation."""
        pass
```

Rules are modular and can be enabled/disabled via configuration.

---

## Design Decisions

### Decision 1: Click Over Typer/Argparse

**Why**: Click is mature, widely adopted, decorator-based (clean syntax), extensive plugin ecosystem

**Impact**: Easier to add subcommands, nested command groups, configuration via decorators

**Example**:
```python
@cli.command()
@click.argument('path')
@click.option('--language', help='Programming language')
def lint(path: str, language: Optional[str]):
    """Lint files in the specified path."""
    ...
```

### Decision 2: AST-Based Analysis (Python)

**Why**: AST provides accurate code understanding vs. regex-based approaches

**Impact**: More reliable detection, fewer false positives, enables complex rules

**Example**: Detect hardcoded paths by analyzing AST `Constant` nodes with string values containing `/`

### Decision 3: Configurable Rule Engine

**Why**: Different projects have different needs, allow customization

**Impact**: Users can enable/disable rules, set severity levels, configure thresholds

**Configuration** (`~/.config/thai-lint/config.yaml`):
```yaml
rules:
  hardcoded-paths:
    enabled: true
    severity: error
  missing-error-handling:
    enabled: true
    severity: warning
  generic-variable-names:
    enabled: false
```

### Decision 4: Multi-Language Support via Plugin Architecture

**Why**: Different languages require different analysis approaches

**Impact**: Each language linter is independent, easy to add new languages

**Benefit**: Users can lint projects with mixed languages (Python + JavaScript)

---

## Development Phases

### Phase 1: Infrastructure (Current - PR0-PR6)
- ✅ Create roadmap and planning (PR0)
- ⏳ Install foundation plugin (PR1 - in progress)
- ⏳ Install Python plugin (PR2)
- ⏳ Install Docker + CI/CD (PR3)
- ⏳ Install security, docs, pre-commit hooks (PR4)
- ⏳ Copy CLI starter code (PR5)
- ⏳ Validate setup (PR6)

### Phase 2: Core Linting Engine (Next)
- Implement AST-based analysis for Python
- Create base linter and rule interfaces
- Implement 3-5 core rules (hardcoded paths, missing error handling, etc.)
- Add CLI command: `thai-lint lint ./src --language python`

### Phase 3: Python-Specific Rules
- Missing type hints
- Incomplete test coverage patterns
- Security vulnerabilities (Bandit integration)

### Phase 4: JavaScript/TypeScript Support
- ESLint plugin architecture
- Language-specific AI rules
- Multi-language project support

### Phase 5: Auto-Fix Capabilities
- Suggest fixes for violations
- Apply fixes with `--fix` flag
- Preview mode before applying

### Phase 6: Integration & Distribution
- VSCode extension
- Pre-commit hook integration
- CI/CD GitHub Action
- PyPI distribution
- Docker Hub distribution

---

## Technology Stack

**Language**: Python 3.11+ (modern async support, better type hints)

**CLI Framework**: Click 8.x (decorator-based, widely adopted)

**Dependency Manager**: Poetry (isolated venvs, lockfiles, prevents system corruption)

**Linting**: Ruff (10-100x faster than traditional tools, handles linting + formatting)

**Type Checking**: MyPy (static type checking with strict mode)

**Testing**: pytest (fixtures, parametrization, async support, coverage)

**Security**: Bandit (code security), Safety (CVE database), Gitleaks (secret scanning)

**Containerization**: Docker + docker-compose (cross-platform distribution)

**CI/CD**: GitHub Actions (matrix testing, automated releases)

---

## Development Guidelines

### Code Standards

- Follow PEP 8 style guide (enforced by Ruff)
- Use type hints (checked by MyPy)
- Maximum cyclomatic complexity: B (enforced by Xenon)
- Docstrings required for all public functions (enforced by Flake8)

### Testing Requirements

- Minimum 80% code coverage
- All new features require tests
- Test both success and failure cases
- Use pytest fixtures for reusable components

### Documentation Standards

- All Python files require docstring headers
- Use Google-style docstrings
- Update `.ai/docs/` when making architectural changes
- Create how-to guides in `.ai/howtos/` for common tasks

---

## Success Criteria

### MVP Success (Core Engine)
- [ ] CLI runs and displays help
- [ ] Can lint Python files with 3-5 core rules
- [ ] Reports violations with file, line, rule ID
- [ ] Configurable via YAML config file
- [ ] Tests pass with >80% coverage

### Production Success
- [ ] Multi-language support (Python + JavaScript at minimum)
- [ ] 10+ AI-specific rules implemented
- [ ] Auto-fix capability for 50%+ of rules
- [ ] VSCode extension available
- [ ] Published to PyPI and Docker Hub
- [ ] Active usage in 5+ projects

---

## Future Enhancements

**Post-MVP Development**:

1. **Additional Language Support**:
   - Go (AST analysis via go/ast package)
   - Rust (AST analysis via syn crate)
   - Java (AST analysis via JavaParser)

2. **Advanced Rules**:
   - Code duplication detection
   - Performance anti-patterns
   - Accessibility issues (for web code)

3. **Machine Learning Integration**:
   - Learn from user fixes
   - Suggest project-specific rules
   - Adaptive severity levels

4. **Web Dashboard**:
   - Visualize violations over time
   - Track code quality trends
   - Team metrics and leaderboards

5. **IDE Integrations**:
   - VSCode extension
   - IntelliJ/PyCharm plugin
   - Real-time linting as you type

---

## Related Documents

### Essential Reading
- **AGENTS.md** - Primary entry point for AI agents
- **`.ai/index.yaml`** - Repository structure map
- **`.ai/layout.yaml`** - File placement rules

### Installation Context
- **`.roadmap/python-cli-install/PROGRESS_TRACKER.md`** - Current installation status
- **`.roadmap/python-cli-install/PR_BREAKDOWN.md`** - PR implementation details
- **`.roadmap/python-cli-install/AI_CONTEXT.md`** - Installation context

### How-To Guides (Will be added in PR5)
- `.ai/howtos/python-cli/how-to-add-cli-command.md`
- `.ai/howtos/python-cli/how-to-handle-config-files.md`
- `.ai/howtos/python-cli/how-to-package-cli-tool.md`

---

**Remember**: This project aims to improve AI-generated code quality. The irony of using AI to build a tool that lints AI code is not lost on us. We dogfood our own linter and fix violations it finds in our codebase.
