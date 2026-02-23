# Dead Code Linter - AI Context

**Purpose**: AI agent context document for implementing the Dead Code Linter

**Scope**: Cross-language, cross-file-type orphan detection via reference graph + BFS reachability from entry points, with interactive triage system and persistent state file

**Overview**: Comprehensive context document for AI agents working on the Dead Code Linter feature.
    This linter implements the first cross-language, project-level orphan detection tool, identifying files
    not reachable from any entry point by building a directed reference graph and performing BFS traversal.
    Supports Python, TypeScript/JavaScript, and infrastructure files (Terraform, Docker, CI, Makefile).
    Includes an interactive triage system for managing findings and a persistent state file for team-shared
    decisions. Uses the two-phase check()/finalize() pattern established by the DRY linter.

**Dependencies**: ast module (Python), tree-sitter (TypeScript/JavaScript), PyYAML (state file), src.core base classes

**Exports**: DeadCodeRule, DeadCodeConfig, ReferenceGraph, EntryPointDetector, TriageStateFile

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Two-phase check()/finalize() with in-memory reference graph, BFS reachability, and TDD methodology

---

## Overview

The Dead Code Linter detects project-level orphaned code by building a **directed reference graph** where:

- **Nodes** = every file in the project
- **Edges** = "file A references file B" (imports, COPY commands, module sources, etc.)

It then identifies **entry points** (files "alive" by definition) and performs **BFS traversal** from those entry points. Every reached file is "alive." Everything unreached is an orphan.

This is fundamentally different from existing tools that analyze dead code within files (unused variables, unreachable branches). This linter operates at the **project level**, finding entire files that nothing references.

## Project Background

### The Gap in Existing Tools

- **Python**: Vulture/deadcode handle in-file dead code; findimports builds import graphs but does not detect orphans
- **JavaScript/TypeScript**: Knip handles unused files/exports but is Node.js-only and cannot embed in thai-lint
- **Terraform**: TFLint finds unused declarations within modules but NOT orphaned module directories
- **Cross-language**: No tool performs holistic orphan detection across Python, TypeScript, and infrastructure files

### Validation Against Real Codebase

Testing against the `pizza-party` repository found real findings:
- 2 orphaned Terraform modules (`vpc-peering/`, `github-runner/`)
- Broken workflow references (`.github/workflows/service-deploy.yaml` referencing nonexistent paths)
- Orphaned test code (`tests/load/locustfile.py`, `tests/integration/whisper-api-test/`)
- Stale artifacts (4 committed `tfplan` binary files)

## Feature Vision

1. **Project-Level Detection**: Find entire orphaned files, not just unused variables
2. **Cross-Language**: Unified analysis across Python, TypeScript/JavaScript, and infrastructure
3. **Interactive Triage**: Walk users through findings with keep/remind-later/dead decisions
4. **CI Gate**: Audit mode fails on untriaged orphans (remediation = run triage mode)
5. **Team Collaboration**: State file committed to version control for shared decisions
6. **Zero New Dependencies**: Uses ast (stdlib), tree-sitter (existing), and regex

## Current Application Context

### Reference Implementation: DRY Linter

The DRY linter at `src/linters/dry/linter.py` establishes the two-phase pattern:

```
src/linters/dry/
├── __init__.py
├── config.py            # DRYConfig with from_dict()
├── linter.py            # DRYRule(BaseLintRule) - check() + finalize()
├── ...
```

Key pattern: `check()` collects per-file data, `finalize()` runs cross-file analysis after all files are processed.

### Key Base Classes

- `BaseLintRule` (`src/core/base.py`): Abstract base for all linters
- `Violation` (`src/core/types.py`): Standard violation dataclass
- `load_linter_config` (`src/core/linter_utils.py`): Config loading helper
- `BaseLintContext` (`src/core/base.py`): Context passed to check()

### Config Loading Pattern

Config is loaded via `context.metadata` (same pattern as DRY and method-property linters):
```python
def check(self, context: BaseLintContext) -> list[Violation]:
    if not self._initialized:
        config_dict = context.metadata.get("dead-code", {})
        self._config = DeadCodeConfig.from_dict(config_dict)
        self._initialized = True
```

## Target Architecture

### Core Components

```
src/linters/dead_code/
├── __init__.py                    # Exports DeadCodeRule, DeadCodeConfig
├── config.py                      # DeadCodeConfig dataclass with from_dict()
├── linter.py                      # DeadCodeRule(BaseLintRule) - check() + finalize()
├── reference_graph.py             # ReferenceGraph: nodes, edges, BFS reachability
├── entry_point_detector.py        # Auto-detect + configured entry points
├── import_parsers/
│   ├── __init__.py
│   ├── python_parser.py           # Python import extraction (ast module)
│   ├── typescript_parser.py       # TS/JS import extraction (tree-sitter)
│   └── infrastructure_parser.py   # Terraform/Docker/CI/Makefile (regex)
├── triage/
│   ├── __init__.py
│   ├── state_file.py              # Load/save .thailint-dead-code.yaml
│   ├── triage_runner.py           # Interactive triage session
│   └── decision.py                # Decision dataclass, DecisionStatus enum
├── violation_builder.py           # Build violations for orphans/broken refs
└── violation_filter.py            # Filter by triage decisions + ignore patterns
```

### Data Flow

```
File Content
    ↓
DeadCodeRule.check(context)     [called once per file]
    ↓
Add file as node in graph
    ↓
Dispatch to parser by file type:
    PythonImportParser.parse_imports()
    TypeScriptImportParser.parse_imports()
    InfrastructureParser.parse_references()
    ↓
Add edges from file to resolved imports
    ↓
Return []  (no violations yet)

========== After all files processed ==========

DeadCodeRule.finalize()          [called once]
    ↓
EntryPointDetector.detect()
    ↓
ReferenceGraph.compute_reachable(entry_points)   [BFS]
    ↓
ReferenceGraph.find_orphans()
ReferenceGraph.find_orphaned_directories()
ReferenceGraph.find_broken_references()
    ↓
ViolationFilter: apply ignore patterns + triage decisions
    ↓
ViolationBuilder: create Violation objects
    ↓
List[Violation]
```

### User Journey

1. User runs `thailint dead-code .` (standard mode)
2. CLI discovers all project files
3. `DeadCodeRule.check()` parses each file, building reference graph
4. `DeadCodeRule.finalize()` computes reachability, reports orphans
5. User sees orphaned files with remediation suggestions
6. User runs `thailint dead-code --triage .` for interactive walkthrough
7. Decisions saved to `.thailint-dead-code.yaml`
8. CI runs `thailint dead-code --audit .` to enforce triage completion

### Reference Graph Walkthrough

```
main.py --> src/app.py --> src/utils/helpers.py
   |                  \--> src/models/user.py
   \--> src/config.py

Dockerfile --> src/ (directory)
.github/workflows/deploy.yml --> scripts/deploy.sh

src/old_handler.py          (no incoming edges)
tests/test_old_handler.py --> src/old_handler.py
```

Starting BFS from `{main.py, Dockerfile, deploy.yml}`:
- Step 1: Follow main.py edges -> `src/app.py`, `src/config.py` (alive)
- Step 2: Follow src/app.py edges -> `src/utils/helpers.py`, `src/models/user.py` (alive)
- Step 3: Follow Dockerfile edges -> `src/` directory (alive)
- Step 4: Follow deploy.yml edges -> `scripts/deploy.sh` (alive)
- Orphans: `{src/old_handler.py, tests/test_old_handler.py}`

## Key Decisions Made

### Two-Phase check()/finalize() Pattern

Dead code detection is inherently cross-file analysis. A single file cannot be determined orphaned in isolation -- the entire project graph must be built first. The DRY linter established this pattern, and the orchestrator already supports calling `finalize()` after all files are processed.

### In-Memory Graph (dict-based, NOT SQLite)

The reference graph uses `set[Path]` for nodes and `dict[Path, set[Path]]` for edges. Graph traversal is BFS using `collections.deque`. No persistent storage needed -- the graph is rebuilt on each run. This keeps the implementation simple and avoids new dependencies.

### No New Dependencies

- **Python parsing**: `ast` module (stdlib)
- **TypeScript parsing**: tree-sitter (already in thai-lint)
- **Infrastructure parsing**: regex (stdlib)
- **State file**: PyYAML (already in thai-lint)
- **Interactive prompts**: Click (already in thai-lint)

### State File Committed to Repo

The `.thailint-dead-code.yaml` file is committed to version control so that:
- Triage decisions are shared across the team
- CI can enforce audit mode (fail on untriaged orphans)
- Decisions persist across branches and environments

### Pre-Commit Configuration

Uses `pass_filenames: false` (same as DRY linter) because dead code detection requires whole-project context. Individual file names are meaningless for orphan detection.

## Detection Mechanism Details

### Entry Point Detection by Language

**Python**:
- `__main__.py`, `main.py` files
- `setup.py`, `setup.cfg` (setuptools entry points)
- `pyproject.toml` containing `[tool.poetry.scripts]` or `[project.scripts]`
- `conftest.py` (pytest infrastructure)
- `manage.py` (Django), `wsgi.py`, `asgi.py`, `app.py` (web frameworks)

**TypeScript/JavaScript**:
- `index.ts`, `index.js`, `index.tsx`, `index.jsx`
- `main.ts`, `main.js`, `server.ts`, `server.js`, `app.ts`, `app.js`
- `package.json` `"main"` and `"bin"` fields

**Infrastructure (always entry points)**:
- `Dockerfile`, `docker-compose.yml`
- `.github/workflows/*.yml`, `.gitlab-ci.yml`
- `Makefile`, `Justfile`
- `*.tf` (Terraform root modules)

**Config files (always entry points)**:
- `pyproject.toml`, `package.json`, `Cargo.toml`
- `.pre-commit-config.yaml`
- `tox.ini`, `.flake8`, `.eslintrc.*`

### Import/Reference Parsing by File Type

**Python** (via `ast` module):
- `import X` -> resolves to `X.py` or `X/__init__.py`
- `from X import Y` -> resolves to `X/Y.py` or `X.py`
- `from . import sibling` -> relative to current file
- `from ..parent import thing` -> parent-relative
- Dynamic imports (`importlib.import_module()`) -> warn only, no edge

**TypeScript/JavaScript** (via tree-sitter):
- `import { foo } from './utils'` -> `./utils.ts` or `./utils/index.ts`
- `const bar = require('./config')` -> `./config.js`
- `import('./lazy-module')` -> `./lazy-module.ts`
- Bare specifiers (no `./` or `../`) = third-party, ignored

**Terraform** (regex):
- `module "x" { source = "./modules/vpc" }` -> edge to `modules/vpc/`
- Registry modules (`hashicorp/consul`) -> ignored

**Dockerfile** (regex):
- `COPY src/ /app/src/` -> edge to `src/`
- `ADD scripts/setup.sh /setup.sh` -> edge to `scripts/setup.sh`

**GitHub Actions** (regex):
- `run: python scripts/deploy.py` -> edge to `scripts/deploy.py`
- `uses: ./.github/actions/custom` -> edge to `.github/actions/custom/`

**Makefile/Justfile** (regex, conservative):
- `python scripts/deploy.py` -> edge to `scripts/deploy.py`
- `./scripts/migrate.sh` -> edge to `scripts/migrate.sh`

### Special Node Handling

- **`__init__.py`**: Reachable if any file in their directory is reachable. Flagged as part of orphaned directory if all directory files are orphans.
- **Test files**: Alive if their source is alive (via natural graph traversal). Orphaned test whose source was deleted is classified as `refactor-leftover`.

### Orphan Classification

| Type | Rule ID | Detection Logic |
|------|---------|----------------|
| Orphaned file | `dead-code.orphaned-file` | File not reachable from any entry point |
| Orphaned directory | `dead-code.orphaned-directory` | All files in directory are orphans |
| Broken reference | `dead-code.broken-reference` | Import/reference target does not exist |
| Refactor leftover | `dead-code.refactor-leftover` | `test_foo.py` exists but `foo.py` does not |

## Triage System Design

### Interactive Triage Session

1. First run: Scans entire project, prompts through all findings, saves decisions
2. Subsequent runs: Only prompts for new orphans + expired reminders
3. Uses `click.prompt()` and `click.confirm()` for interaction
4. Presents orphans one at a time with context (file path)
5. Options: keep (permanently), remind-later (re-ask after N days), dead (safe to remove), skip

### Example Triage Output

```
$ thailint dead-code --triage .

Scanning project...
Found 847 files, 12 potential orphans.

[1/12] src/utils/old_crypto.py
  -> Not imported by any file in the project

  (k)eep  (r)emind me later  (d)ead - safe to remove  (s)kip  ?  d
```

### How Triage Interacts with Detection

- Files marked "keep" in state file -> not reported as violations
- Files marked "remind-later" with future date -> not reported yet
- Files marked "remind-later" past their date -> reported again
- Files marked "dead" that still exist -> reported as "marked dead but not yet removed"
- Orphans not in state file -> reported (and prompted in `--triage` mode)

### The Novel Insight

"Remediation is to run the tool" -- a CI failure (`--audit` mode) turns into a conversation with the developer (`--triage` mode) rather than a wall of errors. The audit gate ensures findings are triaged, not necessarily fixed.

## Three Modes

### Standard Mode (`thailint dead-code .`)
- Full project scan, reports orphans
- Used in CI/pre-commit
- Respects triage decisions
- Exit code 0 = clean, 1 = violations found

### Triage Mode (`thailint dead-code --triage .`)
- Interactive walkthrough
- Saves decisions to `.thailint-dead-code.yaml`
- Skips already-decided files
- Only prompts for new orphans + expired reminders

### Audit Mode (`thailint dead-code --audit .`)
- CI gate mode, non-interactive
- Fails (exit 1) if untriaged orphans exist, expired reminders exist, or files marked "dead" still exist
- Passes (exit 0) when all orphans have been triaged

### Workflow Integration

```
PR workflow:          thailint dead-code .          (standard - CI/pre-commit)
Weekly schedule:      thailint dead-code --audit .  (full audit gate)
When audit fails:     thailint dead-code --triage . (interactive remediation)
```

## Configuration Schema

```yaml
dead-code:
  enabled: true

  # Entry points (auto-detected if not specified)
  entry_points:
    - "src/cli/main.py"
    - "src/main.py"

  # Additional entry point patterns (glob)
  entry_point_patterns:
    - "**/conftest.py"
    - "**/setup.py"

  # File extensions to include in analysis
  extensions:
    - ".py"
    - ".ts"
    - ".tsx"
    - ".js"
    - ".jsx"
    - ".tf"
    - ".rs"

  # Infrastructure file patterns to analyze
  infrastructure:
    terraform: true
    docker: true
    ci: true
    makefile: true

  # Ignore patterns
  ignore:
    - "tests/"
    - "scripts/"
    - "__init__.py"
    - "*.d.ts"

  # State file path (relative to project root)
  state_file: ".thailint-dead-code.yaml"
```

## Core Type Definitions

### ReferenceGraph

```python
class ReferenceGraph:
    """Directed graph tracking file references for orphan detection."""

    def __init__(self) -> None:
        self._nodes: set[Path] = set()
        self._edges: dict[Path, set[Path]] = {}

    def add_file(self, file_path: Path) -> None: ...
    def add_reference(self, source: Path, target: Path) -> None: ...
    def compute_reachable(self, entry_points: set[Path]) -> set[Path]: ...
    def find_orphans(self, entry_points: set[Path]) -> set[Path]: ...
    def find_orphaned_directories(self, orphans: set[Path]) -> set[Path]: ...
    def find_broken_references(self) -> list[tuple[Path, Path]]: ...
```

### EntryPointDetector

```python
class EntryPointDetector:
    """Auto-detect and validate entry points for reachability analysis."""

    def detect(self, project_root: Path, config: DeadCodeConfig) -> set[Path]: ...
    def _detect_python_entry_points(self, root: Path) -> set[Path]: ...
    def _detect_typescript_entry_points(self, root: Path) -> set[Path]: ...
    def _detect_infrastructure_entry_points(self, root: Path) -> set[Path]: ...
    def _resolve_configured_entry_points(self, root: Path, config: DeadCodeConfig) -> set[Path]: ...
```

### PythonImportParser

```python
class PythonImportParser:
    """Extract import references from Python files using ast module."""

    def parse_imports(self, file_path: Path, content: str, project_root: Path) -> list[Path]: ...
    def _resolve_import_to_path(self, import_name: str, file_path: Path, project_root: Path) -> Path | None: ...
    def _resolve_relative_import(self, node: ast.ImportFrom, file_path: Path) -> Path | None: ...
    def _is_project_import(self, module_path: Path, project_root: Path) -> bool: ...
```

### DeadCodeRule

```python
class DeadCodeRule(BaseLintRule):
    """Detects orphaned files and broken references at project level."""

    def __init__(self) -> None:
        self._graph = ReferenceGraph()
        self._config: DeadCodeConfig | None = None
        self._project_root: Path | None = None
        self._initialized = False

    @property
    def rule_id(self) -> str:
        return "dead-code.orphaned-file"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Collection phase: parse imports and build reference graph."""
        return []  # All violations deferred to finalize()

    def finalize(self) -> list[Violation]:
        """Analysis phase: compute reachability and report orphans."""
```

### TriageDecision

```python
class DecisionStatus(str, Enum):
    KEEP = "keep"
    REMIND_LATER = "remind-later"
    DEAD = "dead"

@dataclass
class TriageDecision:
    status: DecisionStatus
    reason: str
    decided_by: str
    decided_at: str           # ISO 8601
    remind_after: str | None = None  # ISO 8601 date
```

## Integration Points

### With Existing Features

1. **CLI Framework** (`src/cli/linters/code_smells.py`):
   - Register `dead-code` command with custom options (`--triage`, `--audit`)
   - Follow DRY linter CLI pattern (custom options, NOT `create_linter_command()`)

2. **Orchestrator** (`src/orchestrator/core.py`):
   - `DeadCodeRule` auto-discovered via rule registry
   - Orchestrator calls `finalize()` after all files processed

3. **Config System** (`src/templates/thailint_config_template.yaml`):
   - Add dead-code section with all options
   - `thailint init-config` generates dead-code config

4. **Output Formatters** (`src/core/cli_utils.py`):
   - Use `format_violations()` for text/json/sarif output
   - SARIF must comply with v2.1.0

### Critical Reference Files

| File | Purpose |
|------|---------|
| `src/linters/dry/linter.py` | Two-phase check()/finalize() pattern |
| `src/core/base.py` | BaseLintRule interface |
| `src/core/types.py` | Violation dataclass |
| `src/orchestrator/core.py` | How finalize() is called |
| `src/cli/linters/code_smells.py` | CLI registration for custom-option linters |
| `src/analyzers/typescript_base.py` | Tree-sitter patterns for TypeScript |

## Success Metrics

| Metric | Target |
|--------|--------|
| Unit tests | 40+ passing |
| CLI integration tests | 15+ passing |
| Pylint score | 10.00/10 |
| MyPy errors | 0 |
| Xenon complexity | A-grade |
| False positive rate | < 5% on self-dogfooding |

## Technical Constraints

1. **No New Dependencies**: Only use ast (stdlib), tree-sitter (existing), regex, PyYAML (existing), Click (existing)
2. **In-Memory Graph**: No persistent storage, graph rebuilt on each run
3. **Error Handling**: Syntax errors, missing files, corrupted YAML all handled gracefully
4. **Performance**: Target < 30 seconds for 1000-file project
5. **Compatibility**: Python 3.10+, TypeScript via tree-sitter

## Documented Limitations

1. **Dynamic imports**: `importlib.import_module(f"plugins.{name}")` -- logged as warnings, no edges
2. **String-based references**: Config files naming modules by string (Django `INSTALLED_APPS`) -- not detected
3. **TypeScript path aliases**: `@/utils` with tsconfig `paths` mapping -- v1 limitation
4. **Conditional exports**: Files only used in certain build configurations -- may produce false positives

## AI Agent Guidance

### When Implementing Parsers

1. Use `ast.NodeVisitor` for Python (see existing linter patterns)
2. Use tree-sitter for TypeScript (see `src/analyzers/typescript_base.py`)
3. Use compiled regex for infrastructure files (conservative patterns)
4. Resolution: Convert import path to file path, check existence on disk
5. Ignore anything resolving outside the project (stdlib, third-party, registry modules)

### When Building the Graph

1. `check()` is called once per file -- add the file as a node and its imports as edges
2. `finalize()` is called once -- compute BFS reachability and generate violations
3. Use `collections.deque` for BFS traversal
4. Track visited set to prevent infinite loops on circular references

### Common Patterns

**Checking file type for parser dispatch**:
```python
if file_path.suffix == ".py":
    imports = python_parser.parse_imports(file_path, content, root)
elif file_path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
    imports = ts_parser.parse_imports(file_path, content, root)
elif file_path.name in {"Dockerfile", "docker-compose.yml", "Makefile"}:
    imports = infra_parser.parse_references(file_path, content, root)
```

**BFS reachability**:
```python
def compute_reachable(self, entry_points: set[Path]) -> set[Path]:
    visited: set[Path] = set()
    queue = deque(entry_points & self._nodes)
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for neighbor in self._edges.get(current, set()):
            if neighbor not in visited and neighbor in self._nodes:
                queue.append(neighbor)
    return visited
```

**Config loading via context.metadata**:
```python
def check(self, context: BaseLintContext) -> list[Violation]:
    if not self._initialized:
        config_dict = context.metadata.get("dead-code", {})
        self._config = DeadCodeConfig.from_dict(config_dict)
        self._initialized = True
    # ... build graph
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| False positives from dynamic imports | Warn-only for dynamic imports, configurable ignore patterns |
| Performance on large codebases | In-memory graph, BFS is O(V+E), no I/O during analysis |
| Circular dependencies cause infinite loop | Visited set in BFS prevents cycles |
| Infrastructure regex misses patterns | Conservative matching, document limitations |
| State file corruption | Graceful degradation (treat as empty), YAML validation |
| Tree-sitter unavailable | Graceful fallback (skip TypeScript files, log warning) |

## Potential Enhancements

1. **Auto-remove dead code**: `--fix` flag that deletes files marked "dead"
2. **TypeScript path aliases**: Parse `tsconfig.json` paths configuration
3. **Django/Flask integration**: Parse `INSTALLED_APPS`, URL patterns, template references
4. **IDE integration**: VS Code extension highlighting orphaned files
5. **Dependency graph visualization**: Generate DOT/Mermaid diagrams of the reference graph
6. **In-file dead code**: Wrap Vulture/deadcode for unused function/variable detection within files
