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

### Added

- **Stateless Class Linter** - Detect Python classes without state that should be module-level functions
  - AST-based detection of classes without `__init__`/`__new__` constructors
  - Detects classes without instance state (`self.attr` assignments)
  - Excludes ABC, Protocol, and decorated classes (legitimate patterns)
  - Excludes classes with class-level attributes
  - Minimum 2 methods required to flag (avoids false positives on simple wrappers)
  - CLI command: `thailint stateless-class src/`
  - JSON and SARIF output formats
  - Configuration via `.thailint.yaml` with `min_methods` and `ignore` options
  - Self-dogfooded: 23 violations in thai-lint codebase were fixed
  - 28 tests (15 detector + 13 CLI) with 100% pass rate
  - Documentation: `docs/stateless-class-linter.md`

- **Project Root Detection System** - Three-level precedence system for accurate configuration and ignore pattern resolution
  - `--project-root` CLI option for explicit project root specification (highest priority)
  - Automatic project root inference from `--config` path (config's parent directory becomes project root)
  - Auto-detection fallback that walks up from file location to find markers (`.git`, `.thailint.yaml`, `pyproject.toml`)
  - Priority order: `--project-root` > config inference > auto-detection
  - Click path validation (exists, is directory) with helpful error messages
  - All paths resolved to absolute paths immediately for consistency

- **Docker Sibling Directory Support** - Solves critical Docker use case where config and code are in separate directories
  - Explicit project root specification: `docker run -v $(pwd):/workspace thailint --project-root /workspace/root magic-numbers /workspace/backend/`
  - Automatic config path inference: `docker run -v $(pwd):/workspace thailint --config /workspace/root/.thailint.yaml magic-numbers /workspace/backend/`
  - Monorepo support with shared configuration across multiple projects
  - CI/CD-friendly with explicit paths preventing auto-detection issues

- **Enhanced Configuration System**
  - Config loading now respects project root context
  - Ignore patterns resolve relative to project root (not file location)
  - Config search paths: explicit `--config` > project-root/.thailint.yaml > auto-detected locations
  - Pyprojroot fallback for test environment compatibility

- **Test Suite**
  - 42 tests for project root detection (29 new + 13 updated, 100% passing)
  - `tests/unit/test_cli_project_root.py` - Explicit `--project-root` tests (15 tests)
  - `tests/unit/test_cli_config_inference.py` - Config path inference tests (14 tests)
  - Priority order tests verifying explicit > inferred > auto-detection
  - Error handling tests for invalid paths (doesn't exist, is file not directory)
  - Integration tests with real directory structures

### Changed

- **CLI Commands** - All linter commands now accept `--project-root` option
  - `thailint magic-numbers --project-root PATH [TARGET]`
  - `thailint nesting --project-root PATH [TARGET]`
  - `thailint srp --project-root PATH [TARGET]`
  - `thailint file-placement --project-root PATH [TARGET]`
  - All commands support combined usage: `--project-root` with `--config`

- **Orchestrator Initialization** - Now accepts explicit project root parameter
  - `Orchestrator(project_root=Path, config_path=Path)` signature
  - Project root passed from CLI to orchestrator for all linting operations
  - Config loading uses project root context for path resolution

- **Path Resolution** - All ignore patterns resolve relative to project root
  - Previous behavior: patterns resolved relative to file being linted
  - New behavior: patterns resolved relative to project root directory
  - More predictable and consistent ignore pattern matching
  - Better Docker compatibility with volume mounts

### Documentation

- **README.md** - Added comprehensive Docker sibling directory examples
  - "Docker with Sibling Directories" section (lines 171-207)
  - "Docker with Sibling Directories (Advanced)" section (lines 1071-1107)
  - Directory structure examples and use cases
  - Priority order explanation with multiple solution approaches

- **CLI Reference** (docs/cli-reference.md)
  - Complete `--project-root` option documentation (lines 120-170)
  - Enhanced `--config` section explaining automatic project root inference (lines 92-118)
  - Use case examples: Docker, monorepos, CI/CD, ignore patterns
  - Error handling examples and exit codes
  - Priority order documentation

- **Troubleshooting Guide** (docs/troubleshooting.md)
  - New "Docker sibling directory structure not working" section (lines 754-856)
  - Problem symptoms and root cause explanation
  - Three solution approaches ranked by recommendation
  - Debugging steps with test commands
  - Cross-references to related documentation

- **Technical Architecture** (.ai/docs/python-cli-architecture.md)
  - New "Project Root Detection" component documentation (section 2)
  - Architecture diagram updated with project root detection layer
  - Design decisions and implementation patterns
  - Testing strategy and related components
  - Docker use case examples and configuration integration

### Fixed

- **Docker Sibling Directory Issue** - Config and code can now be in separate, non-nested directories
  - Previous: Only worked when code was nested under config directory
  - Fixed: Works with any directory structure using `--project-root` or config inference
  - Ignore patterns now resolve correctly in Docker volume mount scenarios

- **Ignore Pattern Resolution** - Patterns now resolve consistently relative to project root
  - Previous: Resolved relative to file being linted (inconsistent behavior)
  - Fixed: Resolved relative to project root (predictable, consistent)
  - Especially important for Docker and monorepo scenarios

- **Test Environment Compatibility** - Added pyprojroot fallback for pytest environments
  - Tests can run in isolated temporary directories
  - Auto-detection gracefully handles test scenarios without project markers
  - No impact on production code behavior

### Infrastructure

- Test suite execution time: All tests pass in <120ms (optimized for fast feedback)
- TDD approach: RED tests → GREEN implementation → Documentation
- Pre-commit hooks validated for all changes
- Zero regressions in existing functionality (13 existing tests updated, all passing)

## [0.2.1] - 2025-10-09

**Docker Path Validation Fix** - Fixes critical Docker image bug where file-specific linting failed due to premature path validation.

### Fixed

- **Docker Path Validation** - Removed Click's `exists=True` parameter that validated paths before Docker volumes were mounted
  - All linter commands now work with file paths in Docker: `docker run -v $(pwd):/data thailint nesting /data/file.py`
  - Better error messages when paths don't exist, with Docker usage hints
  - Manual path validation happens after argument parsing, compatible with both CLI and Docker contexts

### Changed

- Path validation moved from Click argument parsing to execution functions
- Added `_validate_paths_exist()` helper function with user-friendly error messages

## [0.3.0] - TBD

**Single Responsibility Principle (SRP) Linter Release** - Adds comprehensive SRP violation detection for Python and TypeScript code. Uses heuristic-based analysis with configurable thresholds for method count, lines of code, and responsibility keywords. Includes language-specific configurations and extensive refactoring pattern documentation.

### Added

- **SRP Linter** - Complete Single Responsibility Principle violation detection
  - Heuristic-based analysis using method count, LOC, and keyword detection
  - Configurable thresholds: `max_methods` (default: 7), `max_loc` (default: 200)
  - Language-specific thresholds for Python, TypeScript, and JavaScript
  - Responsibility keyword detection (Manager, Handler, Processor, Utility, Helper)
  - AST-based analysis using Python `ast` module and `tree-sitter-typescript`
  - Helpful violation messages with refactoring suggestions

- **CLI Command: `thailint srp`**
  - `thailint srp [PATH]` - Check files for SRP violations
  - `--max-methods N` - Override method count threshold
  - `--max-loc N` - Override lines of code threshold
  - `--config PATH` - Use specific config file
  - `--format json/text` - Output format selection
  - `--help` - Comprehensive command documentation

- **Library API**
  - `srp_lint(path, config)` - Convenience function
  - `SRPRule` - Direct rule class for advanced usage
  - `from src import srp_lint, SRPRule` - Exported in package

- **Comprehensive Documentation**
  - `docs/srp-linter.md` - Complete SRP linter guide
  - Configuration examples and best practices
  - 4 refactoring patterns with before/after code examples
  - CI/CD integration examples (GitHub Actions, pre-commit hooks)
  - Troubleshooting guide and common issues
  - Real-world refactoring examples

- **Language-Specific Configuration**
  - Python: More strict thresholds (8 methods, 200 LOC)
  - TypeScript: More lenient thresholds (10 methods, 250 LOC) for type verbosity
  - JavaScript: Balanced thresholds (10 methods, 225 LOC)
  - Configurable keyword list for responsibility detection

- **Test Suite**
  - 91 tests for SRP linter (100% passing)
  - Python SRP tests (20 tests)
  - TypeScript SRP tests (20 tests)
  - Configuration tests (10 tests)
  - Integration tests (13 tests)
  - Edge case tests (10 tests)
  - Violation message tests (8 tests)
  - Ignore directive tests (10 tests)

- **Refactoring Patterns Documentation**
  - Extract Class pattern (split god classes into focused classes)
  - Split Configuration/Logic pattern (separate concerns)
  - Extract Language-Specific Logic pattern (per-language analyzers)
  - Utility Module pattern (group related helpers)

### Changed

- **Code Quality Improvements**
  - Refactored 6 classes with SRP violations
  - Applied Extract Class pattern to large classes
  - Improved modularity and maintainability
  - Zero SRP violations in codebase

- **README Updates**
  - Added comprehensive SRP linter section with examples
  - Updated feature list with SRP capabilities
  - Added refactoring patterns and examples

### Fixed

- Language-specific configuration loading for SRP thresholds
- Config priority: language-specific → top-level → built-in defaults

### Documentation

- Complete SRP linter guide (`docs/srp-linter.md`)
- Updated CLI reference with SRP command
- Configuration examples for SRP rules
- 4 refactoring patterns with code examples
- Real-world refactoring case studies

### Infrastructure

- Updated Makefile with `just lint-solid` target
- Integrated SRP checks into quality gates
- CI/CD ready (proper exit codes and JSON output)

## [0.2.0] - 2025-10-07

**Nesting Depth Linter Release** - Adds comprehensive nesting depth analysis for Python and TypeScript code. Includes AST-based analysis with tree-sitter, configurable depth limits, and extensive refactoring patterns. Validated on the thai-lint codebase (zero violations after refactoring 23 functions).

### Added

- **Nesting Depth Linter** - Complete nesting depth analysis for Python and TypeScript
  - AST-based depth calculation using Python `ast` module and `tree-sitter-typescript`
  - Configurable `max_nesting_depth` (default: 4, thai-lint uses: 3)
  - Detects excessive nesting in if/for/while/with/try/match (Python) and if/for/while/try/switch (TypeScript)
  - Helpful violation messages with refactoring suggestions
  - Depth calculation starts at 1 for function body (matches industry standards)

- **CLI Command: `thai-lint nesting`**
  - `thai-lint nesting [PATH]` - Check files for excessive nesting
  - `--max-depth N` - Override configured max depth
  - `--config PATH` - Use specific config file
  - `--format json/text` - Output format selection
  - `--help` - Comprehensive command documentation

- **Library API**
  - `nesting_lint(path, max_nesting_depth=4)` - Convenience function
  - `NestingDepthRule` - Direct rule class for advanced usage
  - `from src import nesting_lint, NestingDepthRule` - Exported in package

- **Comprehensive Documentation**
  - `docs/nesting-linter.md` - 400+ line comprehensive guide
  - Configuration examples and best practices
  - 5 refactoring patterns with before/after code examples
  - Case study results and time estimates
  - CI/CD integration examples (GitHub Actions, pre-commit hooks)
  - Troubleshooting guide and common issues

- **Example Code**
  - `examples/nesting_usage.py` - Library API usage example
  - Configuration templates in docs

- **Test Suite**
  - 76 tests for nesting linter (100% passing)
  - Python nesting tests (15 tests)
  - TypeScript nesting tests (15 tests)
  - Configuration tests (8 tests)
  - Integration tests (12 tests)
  - Edge case tests (8 tests)
  - Total project tests: 317 (100% passing, up from 221)

- **Refactoring Patterns Documentation**
  - Guard clauses (early returns) - Used in 7 functions
  - Extract method pattern - Used in 13 functions
  - Dispatch pattern (replace if-elif chains) - Used in 5 functions
  - Flatten error handling - Used in 6 functions
  - Invert conditions - Pattern documented

### Changed

- **Code Quality Improvements via Dogfooding**
  - Refactored 23 functions with excessive nesting (18 in src/, 5 in tests/examples)
  - Reduced max nesting depth from 4 to 3 project-wide
  - All functions now comply with strict depth limit
  - Improved readability and maintainability across codebase
  - Zero nesting violations in production code

- **Test Coverage**
  - Increased from 87% to 90% overall coverage
  - Added 96 new tests (221 → 317)
  - 100% coverage on nesting analyzer modules

- **README Updates**
  - Added comprehensive nesting linter section with examples
  - Updated feature list with nesting capabilities
  - Added refactoring patterns and real-world results
  - Updated test badges (317/317 passing, 90% coverage)

- **Dependencies**
  - Added `tree-sitter ^0.25.2` for AST parsing
  - Added `tree-sitter-typescript ^0.23.2` for TypeScript support
  - Pure Python solution (no Node.js required)

### Fixed

- Ignore directive parser now supports TypeScript comments (`//` and `/* */`)
- Block ignore directives (`thailint: ignore-start` / `ignore-end`) working correctly
- Rule matching supports prefix patterns (e.g., "nesting" matches "nesting.excessive-depth")

### Performance

- Single file analysis: ~10-30ms (well under 100ms target)
- 100 files: ~500ms (under 2s target)
- 1000 files: ~2-3s (under 10s target)
- AST parsing optimized with caching

### Documentation

- Complete nesting linter guide (`docs/nesting-linter.md`)
- Updated CLI reference with nesting command
- Configuration examples for nesting rules
- 5 refactoring patterns with code examples
- Codebase refactoring case study

### Validation: Codebase Refactoring

**Baseline Assessment:**
- 23 violations (depth 4, max configured: 3)
- Files: src/cli.py (6), src/config.py (5), orchestrator (3), others (9)

**Refactoring Applied:**
- Time: ~4 hours for 23 functions (~10 min/function average)
- Patterns: Extract method (13), Guard clauses (7), Dispatch (5), Flatten (6)
- Tests: 317/317 passing (100%)
- Quality: Pylint 10.00/10, all complexity A-grade

**Results:**
- Zero nesting violations
- Improved code readability
- No functionality broken
- All integration tests passing

### Infrastructure

- Updated Makefile with `just lint-nesting` target
- Integrated nesting checks into `just lint-full`
- CI/CD ready (proper exit codes and JSON output)

## [0.1.0] - 2025-10-06

**Initial Alpha Release**

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
