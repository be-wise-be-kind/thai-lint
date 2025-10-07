# Changelog

**Purpose**: Version history and release notes for all thailint package versions

**Scope**: All public releases, API changes, features, bug fixes, and breaking changes

**Overview**: Maintains comprehensive version history following Keep a Changelog format. Documents
    all notable changes in each release including new features, bug fixes, breaking changes,
    deprecations, and security updates. Organized by version with release dates. Supports
    automated changelog extraction for GitHub releases and user upgrade planning.

**Dependencies**: Semantic versioning (semver.org), Keep a Changelog format (keepachangelog.com)

**Exports**: Release history, upgrade guides, breaking change documentation

**Related**: pyproject.toml (version configuration), GitHub releases, docs/releasing.md

**Implementation**: Keep a Changelog 1.1.0 format with semantic versioning and organized change categories

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes

**Configuration Format Update**: Multi-Linter Top-Level Sections

The configuration format has been restructured to support multiple linters with separate top-level sections. This prepares the project for future linters while maintaining a clean separation of concerns.

**Old Format** (v0.1.0 and earlier):
```yaml
# .thailint.yaml
directories:
  src/:
    allow:
      - "^src/.*\\.py$"
global_patterns:
  deny:
    - pattern: ".*\\.tmp$"
      reason: "No temp files"
```

**New Format** (v0.2.0+):
```yaml
# .thailint.yaml
file-placement:
  directories:
    src/:
      allow:
        - "^src/.*\\.py$"
  global_patterns:
    deny:
      - pattern: ".*\\.tmp$"
        reason: "No temp files"
```

**Migration Steps**:
1. Wrap your entire file-placement configuration under a `file-placement:` top-level key
2. Use hyphens (`file-placement`) not underscores (`file_placement`)
3. Indent all existing configuration one level
4. Update any `.thailint.json` files similarly

**Rationale**: This change allows multiple linters to coexist cleanly. Future linters like `code-quality:` and `security:` will have their own top-level sections, following the pattern of tools like `pyproject.toml`.

### Added
- Example configuration files (`.thailint.yaml.example`, `.thailint.json.example`)
- Documentation for multi-linter configuration format

### Changed
- Configuration schema now uses top-level linter sections
- File placement linter looks for config under `file-placement` key (hyphen, not underscore)

### Deprecated
- Old flat configuration format (still works in v0.1.x but will be removed in v1.0.0)

## [0.1.0] - 2025-10-06

**Initial Alpha Release** - This release represents early development status. Core features are functional but the API and configuration formats may change in future releases. Suitable for testing and evaluation.

### Added
- **Core Framework**: Pluggable linter architecture with base interfaces and rule registry
  - `BaseLintRule` and `BaseLintContext` abstractions
  - Automatic plugin discovery via `RuleRegistry`
  - Binary severity model (ERROR only)
  - Violation dataclass with file, line, rule_id, message, severity

- **Configuration System**: Multi-format config loading with 5-level ignore system
  - YAML and JSON config file support
  - 5-level ignore directives (repo, directory, file, method, line)
  - Wildcard rule matching for flexible ignore patterns
  - Config validation and error reporting

- **Multi-Language Orchestrator**: File routing and language detection engine
  - Extension-based language detection with shebang fallback
  - Per-language linter routing and execution
  - Context creation and violation aggregation
  - Recursive directory scanning

- **File Placement Linter**: Complete file organization linter
  - Pattern-based allow/deny rules with regex support
  - Directory scoping for targeted enforcement
  - Configurable via YAML/JSON with validation
  - Helpful violation suggestions based on file type
  - 81% test coverage, 42/50 tests passing

- **CLI Interface**: Professional command-line interface
  - `thailint lint file-placement [PATH]` command
  - Inline JSON rules via `--rules` flag
  - External config via `--config` flag
  - Text and JSON output formats (`--format`)
  - Recursive and non-recursive scanning modes
  - Proper exit codes (0=pass, 1=violations, 2=error)

- **Library API**: High-level programmatic interface
  - `Linter` class with config_file and project_root parameters
  - `lint(path, rules=[...])` method for filtered linting
  - Autodiscovery of config files in project root
  - Direct linter imports for backwards compatibility
  - Usage examples (basic, advanced, CI integration)

- **Docker Support**: Production-ready containerization
  - Multi-stage Dockerfile with optimized layers
  - Non-root user execution (UID 1000)
  - Volume mounting at `/workspace`
  - 270MB image size (Python 3.11-slim)
  - docker-compose.yml for development workflows

- **PyPI Distribution**: Complete packaging and publishing setup
  - PyPI-ready package metadata with classifiers
  - GitHub Actions workflow for automated publishing
  - PyPI Trusted Publishing (OIDC) configuration
  - Automated GitHub releases with changelog extraction
  - MANIFEST.in for clean source distributions

- **Comprehensive Testing**: TDD-driven test suite
  - 181+ unit and integration tests
  - 87% overall test coverage
  - pytest with coverage reporting
  - Docker integration tests

- **Development Tooling**: Complete quality assurance stack
  - Ruff (linting and formatting)
  - MyPy (strict type checking)
  - Pylint (comprehensive linting)
  - Bandit (security scanning)
  - Xenon (complexity analysis)
  - Pre-commit hooks for quality gates

### Changed
- Package name: `thai-lint` → `thailint` (PyPI-friendly)
- CLI command: `thai-lint` → `thailint` (both supported for compatibility)

### Documentation
- Comprehensive README with installation and usage guides
- API examples for library usage
- Docker usage documentation
- Release process documentation (docs/releasing.md)
- AI agent guides (.ai/ directory)

### Infrastructure
- GitHub Actions CI/CD pipelines (test, lint, security)
- Pre-commit hooks for automated quality checks
- Poetry-based dependency management
- Docker multi-stage builds

## [0.0.1] - Initial Development

### Added
- Basic project structure
- Poetry configuration
- Initial CLI scaffold

---

## Version History

- **0.1.0** (2025-10-06): Initial alpha release with core feature set
- **0.0.1**: Initial development version

## Upgrade Guide

### Using Version 0.1.0 (Alpha Release)

This is an early alpha release for testing and feedback. Key notes:

1. **CLI Command**: Use `thailint` instead of `thai-lint` (both work)
2. **Package Name**: Install as `pip install thailint`
3. **Library Import**: Use `from thailint import Linter`

## Contributing

When adding entries to this changelog:

1. Add changes to `[Unreleased]` section during development
2. Move to versioned section when releasing
3. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
4. Include user-facing changes only (not internal refactors)
5. Link to issues/PRs when relevant
6. Follow Keep a Changelog format

## Links

- [PyPI Package](https://pypi.org/project/thailint/)
- [GitHub Repository](https://github.com/steve-e-jackson/thai-lint)
- [Issue Tracker](https://github.com/steve-e-jackson/thai-lint/issues)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
