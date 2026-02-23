# Dead Code Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of Dead Code Linter into 8 manageable, atomic pull requests

**Scope**: Complete feature implementation from core types and TDD infrastructure through documentation and self-dogfooding

**Overview**: Comprehensive breakdown of the Dead Code Linter feature into 8 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR. The linter uses a reference graph
    with BFS reachability from entry points to detect orphaned files, broken references, and refactor leftovers
    across Python, TypeScript/JavaScript, and infrastructure files.

**Dependencies**: ast module (Python parsing), tree-sitter (TypeScript/JavaScript parsing), PyYAML (state file), DRY linter two-phase pattern, src.core base classes

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: TDD approach with atomic PR structure, two-phase check()/finalize() pattern, and comprehensive testing validation

---

## Overview
This document breaks down the Dead Code Linter feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

**Total**: 40+ unit tests, 15+ CLI integration tests

---

## PR1: Core Types, Config, and Test Infrastructure (TDD Foundation)

**Priority**: P0
**Complexity**: Medium
**Tests**: All test files created (red phase -- all fail except config tests)

### Scope
Establish foundational types, configuration dataclass, and comprehensive failing test suite defining expected behavior. This is the TDD "red" phase -- all tests should fail with ImportError or NotImplementedError. Config tests should pass.

### Files to Create

```
src/linters/dead_code/
├── __init__.py                    # Empty with docstring, exports placeholder
└── config.py                     # DeadCodeConfig dataclass

tests/unit/linters/dead_code/
├── __init__.py
├── conftest.py                          # Shared fixtures (mock project trees via tmp_path)
├── test_config.py                       # DeadCodeConfig validation tests
├── test_reference_graph.py              # Graph construction, reachability tests
├── test_entry_point_detection.py        # Entry point auto-detection tests
├── test_python_import_parsing.py        # Python import extraction tests
├── test_typescript_import_parsing.py    # TS/JS import extraction tests
├── test_infrastructure_parsing.py       # Terraform/Docker/CI parsing tests
├── test_orphan_detection.py             # Orphaned file detection tests
├── test_broken_reference_detection.py   # Broken reference detection tests
├── test_triage_state_file.py            # State file load/save tests
└── test_violation_builder.py            # Violation message formatting tests
```

### Implementation Steps

1. **Create source directory structure**
   ```bash
   mkdir -p src/linters/dead_code
   ```

2. **Create `config.py`** with:
   - `DeadCodeConfig` dataclass with fields:
     - `enabled: bool = True`
     - `entry_points: list[str] = []` (configured entry points)
     - `entry_point_patterns: list[str] = []` (glob patterns like `**/conftest.py`)
     - `extensions: list[str] = [".py", ".ts", ".tsx", ".js", ".jsx"]`
     - `infrastructure: dict` (terraform, docker, ci, makefile booleans)
     - `ignore: list[str] = ["tests/", "__init__.py"]`
     - `state_file: str = ".thailint-dead-code.yaml"`
   - `from_dict()` class method for YAML loading
   - Validation for required fields

3. **Create `__init__.py`** with placeholder exports

4. **Create test directory structure**
   ```bash
   mkdir -p tests/unit/linters/dead_code
   ```

5. **Create `conftest.py`** with:
   - `create_project_tree(tmp_path, files: dict)` helper (creates files from dict of path->content)
   - `default_config` fixture
   - `mock_project` fixture (sample 5-file project with entry point)

6. **Create test files** (all marked `@pytest.mark.skip` except config tests):

### TDD Test Categories

**`test_config.py`** (pass in PR1):
- Config `from_dict()` with all fields
- Config defaults when fields omitted
- Config validation rejects invalid extensions
- Config `enabled` flag defaults to True
- Config loads ignore patterns as list
- Config infrastructure defaults (all True)

**`test_reference_graph.py`** (skip -- green in PR2):
- Add nodes and edges
- Compute reachability from single entry point
- Compute reachability from multiple entry points
- Find orphans (nodes not reachable)
- Graph with cycles does not infinite loop
- Graph with diamond dependencies counts correctly
- Orphaned directory detection (all children are orphans)
- Empty project produces no orphans
- Single-file project with entry point produces no orphans
- Find broken references (edge target not in nodes)

**`test_entry_point_detection.py`** (skip -- green in PR2):
- Auto-detect `main.py`
- Auto-detect `__main__.py`
- Auto-detect `conftest.py`
- Auto-detect `index.ts` / `index.js`
- Auto-detect `package.json` "main" field
- Auto-detect `pyproject.toml` script entries
- Auto-detect infrastructure files (Dockerfile, workflows, Makefile, Justfile)
- Configured entry points override auto-detection
- `entry_point_patterns` glob matching
- Missing configured entry point logs warning

**`test_python_import_parsing.py`** (skip -- green in PR3):
- `import os` (stdlib, ignored)
- `from . import sibling` (relative import resolved)
- `from ..parent import thing` (parent-relative import)
- `import src.linters.dry` (dotted path resolution)
- `from typing import TYPE_CHECKING` guarded imports (tracked)
- `importlib.import_module("x")` dynamic import (warn, no edge)
- `try: import X except ImportError: import Y` (both tracked)
- Files with syntax errors handled gracefully (no crash)
- Empty file produces no imports
- `__all__` exports (informational, not blocking)

**`test_typescript_import_parsing.py`** (skip -- green in PR4):
- `import { X } from './module'` (ES6 named import)
- `import X from './module'` (default import)
- `import * as X from './module'` (namespace import)
- `require('./module')` (CommonJS)
- `import('./module')` (dynamic import)
- Relative path resolution with `index.ts`/`index.js` inference
- `.ts`, `.tsx`, `.js`, `.jsx` extension resolution
- `@scope/package` (third-party, ignored)

**`test_infrastructure_parsing.py`** (skip -- green in PR4):
- Dockerfile `COPY` and `ADD` referencing project files
- `docker-compose.yml` `build.context` and `volumes` referencing paths
- GitHub Actions `run: python scripts/deploy.py` referencing scripts
- GitHub Actions `uses: ./.github/actions/custom` referencing local actions
- Makefile targets referencing scripts (`python src/main.py`)
- Terraform `module "x" { source = "./modules/vpc" }` local module
- Terraform `source = "hashicorp/consul/aws"` (registry, ignored)

**`test_orphan_detection.py`** (skip -- green in PR5):
- Mock project with 5 files, 2 entry points, 1 orphan -- detects the orphan
- Mock project with circular references -- no false orphans
- Mock project with test file whose source was deleted -- detected as refactor leftover
- Disabled linter (`enabled: false`) returns no violations
- Respect ignore patterns (files in `tests/` not reported when ignored)

**`test_broken_reference_detection.py`** (skip -- green in PR5):
- Import pointing to nonexistent file detected as broken reference
- Mock project with broken import -- detected as broken reference

**`test_triage_state_file.py`** (skip -- green in PR6):
- Load existing state file with keep/remind-later/dead decisions
- Save decisions to YAML
- Roundtrip (load then save preserves format)
- Handle missing state file (first run)
- Handle corrupted YAML gracefully
- Expired remind-later entries detected
- Merge findings with existing decisions

**`test_violation_builder.py`** (skip -- green in PR5):
- Violation for orphaned file has rule_id `dead-code.orphaned-file`
- Violation for orphaned directory has `dead-code.orphaned-directory`
- Violation for broken reference has `dead-code.broken-reference`
- Violation for refactor leftover has `dead-code.refactor-leftover`
- Violations include file path, line 1, column 0
- Suggestions include remediation guidance

### Success Criteria
- [ ] Config tests pass
- [ ] All other tests fail with ImportError (not SyntaxError)
- [ ] `just lint-full` passes on all new files
- [ ] Proper file headers on all files
- [ ] Pylint 10.00/10 on new files

---

## PR2: Reference Graph and Entry Point Detection

**Priority**: P0
**Complexity**: Medium
**Tests**: `test_reference_graph.py` and `test_entry_point_detection.py` pass

### Scope
Implement the core graph data structure for tracking file references and the entry point auto-detection system. The reference graph is the heart of dead-code detection.

### Files to Create

```
src/linters/dead_code/
├── reference_graph.py             # ReferenceGraph class
└── entry_point_detector.py        # EntryPointDetector class
```

### Implementation Steps

1. **Create `reference_graph.py`**:
   - Class `ReferenceGraph` with:
     - `_nodes: set[Path]` -- all known files
     - `_edges: dict[Path, set[Path]]` -- source -> set of targets
     - `add_file(file_path: Path) -> None`
     - `add_reference(source: Path, target: Path) -> None`
     - `compute_reachable(entry_points: set[Path]) -> set[Path]` (BFS)
     - `find_orphans(entry_points: set[Path]) -> set[Path]`
     - `find_orphaned_directories(orphans: set[Path]) -> set[Path]`
     - `find_broken_references() -> list[tuple[Path, Path]]`
   - BFS implementation in `compute_reachable()` using `collections.deque`
   - Cycle-safe: visited set prevents infinite loops

2. **Create `entry_point_detector.py`**:
   - Class `EntryPointDetector` with:
     - `detect(project_root: Path, config: DeadCodeConfig) -> set[Path]`
     - `_detect_python_entry_points(root: Path) -> set[Path]`
     - `_detect_typescript_entry_points(root: Path) -> set[Path]`
     - `_detect_infrastructure_entry_points(root: Path) -> set[Path]`
     - `_resolve_configured_entry_points(root: Path, config: DeadCodeConfig) -> set[Path]`
   - Python entry points: `__main__.py`, `main.py`, `setup.py`, `manage.py`, `wsgi.py`, `asgi.py`, `app.py`, `conftest.py`, `pyproject.toml` scripts
   - TypeScript entry points: `index.ts/js/tsx/jsx`, `main.ts/js`, `server.ts/js`, `app.ts/js`, `package.json` main/bin fields
   - Infrastructure: `Dockerfile`, `docker-compose.yml`, `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Makefile`, `Justfile`, `*.tf`, `.pre-commit-config.yaml`
   - Config files: `pyproject.toml`, `package.json`, `Cargo.toml`, `tox.ini`, `.flake8`, `.eslintrc.*`

3. **Remove skip markers** from `test_reference_graph.py` and `test_entry_point_detection.py`

### Success Criteria
- [ ] `test_reference_graph.py` passes (cycles, diamonds, empty projects handled)
- [ ] `test_entry_point_detection.py` passes (auto-detect + configured overrides)
- [ ] `just lint-full` passes
- [ ] Pylint 10.00/10

---

## PR3: Python Import Parser

**Priority**: P0
**Complexity**: Medium
**Tests**: `test_python_import_parsing.py` passes

### Scope
Python import parsing to extract file-level dependencies. Uses `ast` module to parse `import` and `from...import` statements and resolve them to file paths.

### Files to Create

```
src/linters/dead_code/import_parsers/
├── __init__.py
└── python_parser.py               # PythonImportParser class
```

### Implementation Steps

1. **Create `import_parsers/` package**

2. **Create `python_parser.py`**:
   - Class `PythonImportParser` with:
     - `parse_imports(file_path: Path, content: str, project_root: Path) -> list[Path]`
     - `_parse_ast_imports(content: str) -> list[ast.Import | ast.ImportFrom]`
     - `_resolve_import_to_path(import_name: str, file_path: Path, project_root: Path) -> Path | None`
     - `_resolve_relative_import(node: ast.ImportFrom, file_path: Path) -> Path | None`
     - `_is_project_import(module_path: Path, project_root: Path) -> bool`
   - Resolution strategy: Convert dotted path to file path, check `path.py` then `path/__init__.py`
   - Ignore anything resolving outside the project (stdlib, third-party)
   - Dynamic imports (`importlib.import_module()`) log warning, do not create edges
   - `try/except ImportError` blocks: track both branches
   - Handle syntax errors gracefully (return empty list, no crash)

3. **Remove skip markers** from `test_python_import_parsing.py`

### Python Import Patterns

```python
# Absolute imports -> resolve to project files
import src.linters.dry          # -> src/linters/dry/__init__.py
from src.core import base       # -> src/core/base.py

# Relative imports -> resolve relative to current file
from . import sibling           # -> ./sibling.py or ./sibling/__init__.py
from ..parent import thing      # -> ../parent/thing.py

# Stdlib/third-party -> ignored (not project files)
import os
from typing import Optional
import pytest

# Dynamic imports -> warn only, no edge
importlib.import_module("plugins.auth")

# Conditional imports -> both branches tracked
try:
    import ujson as json
except ImportError:
    import json
```

### Success Criteria
- [ ] Resolves absolute and relative imports to file paths
- [ ] Ignores stdlib and third-party imports
- [ ] Dynamic imports warn but do not create edges
- [ ] Handles syntax errors gracefully
- [ ] `test_python_import_parsing.py` passes
- [ ] `just lint-full` passes
- [ ] Pylint 10.00/10

---

## PR4: TypeScript/JS Import Parser and Infrastructure Parsing

**Priority**: P0
**Complexity**: Medium
**Tests**: `test_typescript_import_parsing.py` and `test_infrastructure_parsing.py` pass

### Scope
TypeScript/JavaScript import extraction using tree-sitter (already in thai-lint) and lightweight regex-based parsing for Terraform, Docker, CI configs, and Makefiles.

### Files to Create

```
src/linters/dead_code/import_parsers/
├── typescript_parser.py           # TypeScriptImportParser class
└── infrastructure_parser.py       # InfrastructureParser class
```

### Implementation Steps

1. **Create `typescript_parser.py`**:
   - Class `TypeScriptImportParser` with:
     - `parse_imports(file_path: Path, content: str, project_root: Path) -> list[Path]`
   - Use tree-sitter for parsing (follow existing TS analyzer patterns in `src/analyzers/typescript_base.py`)
   - Handle ES6 imports: `import { X } from './module'`, `import X from './module'`, `import * as X from './module'`
   - Handle CommonJS: `require('./module')`
   - Handle dynamic: `import('./module')`
   - Extension resolution: try `.ts`, `.tsx`, `.js`, `.jsx`, then `index.*` in directory
   - Bare specifiers (no `./` or `../`) = third-party, ignored
   - v1 limitation: tsconfig.json path aliases not supported (document as known limitation)

2. **Create `infrastructure_parser.py`**:
   - Class `InfrastructureParser` with:
     - `parse_references(file_path: Path, content: str, project_root: Path) -> list[Path]`
   - Regex-based parsing for:
     - **Dockerfile**: `COPY src/ /app/src/` -> edge to `src/`; `ADD scripts/setup.sh` -> edge to file
     - **docker-compose.yml**: `build.context` and `volumes` paths
     - **GitHub Actions**: `run: python scripts/deploy.py` -> edge to script; `uses: ./.github/actions/custom` -> edge to local action
     - **Makefile/Justfile**: `python scripts/deploy.py` -> edge to script; `./scripts/migrate.sh` -> edge to script
     - **Terraform**: `module "x" { source = "./modules/vpc" }` -> edge to directory; registry modules ignored

3. **Remove skip markers** from `test_typescript_import_parsing.py` and `test_infrastructure_parsing.py`

### TypeScript Import Patterns

```typescript
// ES6 imports -> resolve relative to file
import { foo } from './utils'        // -> ./utils.ts or ./utils/index.ts
import Bar from '../components/Bar'  // -> ../components/Bar.tsx

// CommonJS -> resolve same as ES6
const config = require('./config')   // -> ./config.js

// Dynamic -> still tracked
import('./lazy-module')              // -> ./lazy-module.ts

// Third-party -> ignored
import React from 'react'
import { useState } from 'react'
```

### Success Criteria
- [ ] TypeScript ES6, CommonJS, and dynamic imports parsed correctly
- [ ] Infrastructure references parsed from Dockerfile, docker-compose, Actions, Makefile, Terraform
- [ ] Third-party imports ignored
- [ ] Tree-sitter gracefully degrades if unavailable
- [ ] `test_typescript_import_parsing.py` and `test_infrastructure_parsing.py` pass
- [ ] `just lint-full` passes
- [ ] Pylint 10.00/10

---

## PR5: DeadCodeRule Implementation (check + finalize)

**Priority**: P0
**Complexity**: High
**Tests**: `test_orphan_detection.py`, `test_broken_reference_detection.py`, `test_violation_builder.py` pass

### Scope
The core linter rule that integrates all previous components. `check()` builds graph incrementally, `finalize()` computes reachability and generates violations.

### Files to Create

```
src/linters/dead_code/
├── linter.py                      # DeadCodeRule(BaseLintRule)
├── violation_builder.py           # DeadCodeViolationBuilder
└── violation_filter.py            # Filter by ignore patterns
```

### Implementation Steps

1. **Create `linter.py`**:
   - Class `DeadCodeRule(BaseLintRule)` with:
     - `_graph: ReferenceGraph` (in-memory)
     - `_config: DeadCodeConfig | None`
     - `_project_root: Path | None`
     - `_initialized: bool`
     - `_file_contents: dict[str, str]`
     - `rule_id = "dead-code.orphaned-file"`
     - `check(context: BaseLintContext) -> list[Violation]`: Collection phase
       - Add file as node
       - Parse imports based on file type (dispatch to correct parser)
       - Add edges from file to each resolved import
       - Return empty list (all violations deferred to `finalize()`)
     - `finalize() -> list[Violation]`: Analysis phase
       - Detect entry points
       - BFS from entry points
       - Compute orphans
       - Classify orphan type
       - Filter by triage decisions and ignore patterns
       - Build violations

2. **Create `violation_builder.py`**:
   - Function to build violations with correct rule IDs:
     - `dead-code.orphaned-file` -- file not reachable from any entry point
     - `dead-code.orphaned-directory` -- all files in directory are orphans
     - `dead-code.broken-reference` -- import to nonexistent file
     - `dead-code.refactor-leftover` -- test file whose source was deleted
   - All violations at line 1, column 0 (project-level, not line-specific)
   - Include remediation suggestions in violation message

3. **Create `violation_filter.py`**:
   - Filter by ignore patterns from config
   - Filter by triage decisions from state file (files marked "keep" not reported)

4. **Refactor leftover detection logic**:
   - Test file `test_foo.py` exists but `foo.py` does not (heuristic: `test_` prefix / `_test` suffix)
   - Config file `foo.config.ts` exists but `foo.ts` does not
   - `conftest.py` in an otherwise-empty directory

5. **Update `__init__.py`** with `DeadCodeRule` export

6. **Remove skip markers** from `test_orphan_detection.py`, `test_broken_reference_detection.py`, `test_violation_builder.py`

### Rule IDs

| Rule ID | Description |
|---------|-------------|
| `dead-code.orphaned-file` | File not reachable from any entry point |
| `dead-code.orphaned-directory` | All files in directory are orphans |
| `dead-code.broken-reference` | Import/reference to nonexistent file |
| `dead-code.refactor-leftover` | Test file whose source was deleted |

### Success Criteria
- [ ] Two-phase check()/finalize() pattern works correctly
- [ ] Detects orphaned files in mock projects
- [ ] Circular references do not produce false orphans
- [ ] Refactor leftovers detected (orphaned test files)
- [ ] Broken references detected
- [ ] Disabled linter returns no violations
- [ ] Ignore patterns respected
- [ ] Correct rule_id on all violation types
- [ ] `test_orphan_detection.py`, `test_broken_reference_detection.py`, `test_violation_builder.py` pass
- [ ] `just lint-full` passes
- [ ] Pylint 10.00/10

---

## PR6: Triage Mode and State File

**Priority**: P0
**Complexity**: Medium
**Tests**: `test_triage_state_file.py` and `test_triage_mode.py` pass

### Scope
`--triage` interactive mode walks users through findings; `--audit` CI mode fails on untriaged orphans. Decisions stored in `.thailint-dead-code.yaml` committed to version control.

### Files to Create

```
src/linters/dead_code/triage/
├── __init__.py
├── state_file.py                  # TriageStateFile: load/save .thailint-dead-code.yaml
├── triage_runner.py               # TriageRunner: interactive session
└── decision.py                    # Decision dataclass, DecisionStatus enum
```

### Implementation Steps

1. **Create `decision.py`**:
   - `DecisionStatus(str, Enum)`: `KEEP`, `REMIND_LATER`, `DEAD`
   - `TriageDecision` dataclass: `status`, `reason`, `decided_by`, `decided_at` (ISO 8601), `remind_after` (optional ISO 8601 date)

2. **Create `state_file.py`**:
   - Class `TriageStateFile` with:
     - `load(path: Path) -> dict[str, TriageDecision]`
     - `save(path: Path, decisions: dict[str, TriageDecision]) -> None`
     - `merge(existing: dict, new_orphans: set[Path]) -> dict`
     - `expired_reminders(decisions: dict) -> list[str]`
   - YAML format with `version`, `last_triage`, and `decisions` sections
   - Handle missing file (first run -- return empty dict)
   - Handle corrupted YAML (log warning, return empty dict)

3. **Create `triage_runner.py`**:
   - Class `TriageRunner` with:
     - Interactive walkthrough using `click.prompt()`
     - Present each orphan with context (file path)
     - Options: **(k)eep**, **(r)emind me later**, **(d)ead - safe to remove**, **(s)kip**
     - Save decisions to state file after session
     - Skip already-decided files on subsequent runs

4. **Create test file** `tests/unit/linters/dead_code/test_triage_mode.py`:
   - Triage mode presents each orphan to user
   - User can choose "keep" with reason
   - User can choose "remind-later" with date
   - User can choose "dead"
   - Triage mode skips already-decided files
   - Audit mode fails when untriaged orphans exist
   - Audit mode fails when remind-later entries expired
   - Audit mode passes when all orphans decided
   - Standard mode respects "keep" decisions
   - Standard mode re-reports "remind-later" files after expiry

5. **Remove skip markers** from `test_triage_state_file.py`

### State File Schema

```yaml
# Purpose: Dead code triage decisions for project
# Generated by: thailint dead-code --triage
# Committed to version control for team-shared decisions

version: "1.0"
last_triage: "2026-02-23T10:30:00Z"

decisions:
  "src/legacy/old_handler.py":
    status: "keep"
    reason: "Used via dynamic import in plugin system"
    decided_by: "steve"
    decided_at: "2026-02-23T10:30:00Z"

  "src/utils/deprecated_helper.py":
    status: "remind-later"
    reason: "Migration planned"
    decided_by: "alice"
    decided_at: "2026-02-20T14:00:00Z"
    remind_after: "2026-05-01"

  "src/old_api/v1_routes.py":
    status: "dead"
    reason: "API v1 fully decommissioned"
    decided_by: "steve"
    decided_at: "2026-02-22T09:00:00Z"
```

### Three Modes Interaction

| Mode | Flag | Behavior | Exit Code |
|------|------|----------|-----------|
| Standard | (none) | Report orphans, respect triage decisions | 0=clean, 1=violations |
| Triage | `--triage` | Interactive walkthrough, save decisions | 0 always |
| Audit | `--audit` | Fail on untriaged orphans or expired reminders | 0=clean, 1=violations |

### Success Criteria
- [ ] State file roundtrip (load/save) preserves data
- [ ] Missing state file handled (first run)
- [ ] Corrupted YAML handled gracefully
- [ ] Expired reminders detected correctly
- [ ] Merge combines existing decisions with new orphans
- [ ] Interactive triage flow works with click prompts
- [ ] Audit mode exits non-zero on untriaged/expired
- [ ] Standard mode respects "keep" decisions
- [ ] `test_triage_state_file.py` and `test_triage_mode.py` pass
- [ ] `just lint-full` passes
- [ ] Pylint 10.00/10

---

## PR7: CLI Integration and Output Formats

**Priority**: P0
**Complexity**: Medium
**Tests**: `test_cli_integration.py` passes

### Scope
Register the `dead-code` CLI command with Click, implement all three modes, and ensure text/json/sarif output formats work.

### Files to Create/Modify

```
src/cli/linters/
  dead_code.py                   # NEW: CLI command module

src/cli/linters/__init__.py      # MODIFY: Import dead_code module
```

### Implementation Steps

1. **Create `dead_code.py`** CLI command:
   ```python
   @cli.command("dead-code")
   @click.argument("paths", nargs=-1, type=click.Path())
   @click.option("--config", "-c", "config_file", type=click.Path())
   @format_option
   @click.option("--triage", is_flag=True, help="Interactive triage mode")
   @click.option("--audit", is_flag=True, help="CI audit mode")
   @click.option("--recursive/--no-recursive", default=True)
   @parallel_option
   @click.pass_context
   def dead_code(ctx, paths, config_file, format, triage, audit, recursive, parallel):
       ...
   ```
   - Follow DRY linter CLI pattern in `code_smells.py` (custom options, NOT `create_linter_command()`)
   - `--triage` and `--audit` are mutually exclusive (validate, raise click.UsageError)

2. **Update `__init__.py`** to import the dead_code command

3. **Key behaviors by mode**:
   - **Standard mode** (no flags): Scan project, report orphans, respect triage state, exit 0/1
   - **Triage mode** (`--triage`): Interactive walkthrough, save decisions, exit 0
   - **Audit mode** (`--audit`): Check state file, exit 1 if untriaged/expired, exit 0 otherwise

4. **Create test file** `tests/unit/linters/dead_code/test_cli_integration.py`:
   - `thailint dead-code .` runs without error on clean project
   - `thailint dead-code --format json .` produces valid JSON
   - `thailint dead-code --format sarif .` produces valid SARIF v2.1.0
   - `thailint dead-code --triage .` enters interactive mode (mock stdin)
   - `thailint dead-code --audit .` checks state file and exits 0/1
   - `--triage` and `--audit` are mutually exclusive
   - Config file override via `--config`
   - Exit code 0 when no orphans, exit code 1 when orphans found
   - Verbose mode (`-v`) shows debug output

### Success Criteria
- [ ] CLI command registered and discoverable via `thailint --help`
- [ ] All three modes work correctly
- [ ] All three output formats produce valid output
- [ ] SARIF v2.1.0 compliant
- [ ] `--triage` and `--audit` mutually exclusive
- [ ] Proper exit codes (0=clean, 1=violations, 2=error)
- [ ] `test_cli_integration.py` passes
- [ ] `just lint-full` passes
- [ ] Pylint 10.00/10

---

## PR8: Documentation, Config Template, and Dogfooding

**Priority**: P1
**Complexity**: Low
**Tests**: Dogfooding validation (zero false positives)

### Scope
User-facing documentation, config template update, README update, and run the linter on thai-lint itself to validate zero false positives.

### Files to Create/Modify

```
docs/dead-code-linter.md                      # NEW: User documentation
.ai/howtos/how-to-fix-dead-code.md            # NEW: Fix guide
src/templates/thailint_config_template.yaml    # MODIFY: Add dead-code section
README.md                                      # MODIFY: Add to linter list
.thailint.yaml                                 # MODIFY: Add dead-code config
```

### Implementation Steps

1. **Create `docs/dead-code-linter.md`**:
   - What dead-code detection does
   - Three modes explained (standard, triage, audit)
   - Configuration reference (all config fields)
   - Triage workflow walkthrough
   - CI integration guide (pre-commit hook, audit mode)
   - State file format reference
   - Examples and common patterns
   - Limitations and known issues

2. **Create `.ai/howtos/how-to-fix-dead-code.md`**:
   - How to interpret dead-code violations
   - Decision framework: keep vs remove vs remind-later
   - How to run triage mode
   - How to set up audit mode in CI
   - How to configure ignore patterns

3. **Update config template** with dead-code section:
   ```yaml
   # ============================================================================
   # DEAD CODE LINTER
   # ============================================================================
   dead-code:
     enabled: true
     # entry_points:
     #   - "src/main.py"
     extensions: [".py", ".ts", ".tsx", ".js", ".jsx"]
     infrastructure:
       terraform: true
       docker: true
       ci: true
       makefile: true
     ignore:
       - "tests/"
       - "__init__.py"
   ```

4. **Update README.md** with dead-code linter entry in feature list

5. **Update `.thailint.yaml`** with dead-code configuration

6. **Dogfooding**: Run `thailint dead-code .` on thai-lint itself
   - Verify zero false positives
   - Document any findings and resolutions

### Success Criteria
- [ ] User documentation complete (300+ lines)
- [ ] Fix guide howto created
- [ ] Config template valid YAML with dead-code section
- [ ] README mentions dead-code linter
- [ ] Zero false positives on thai-lint codebase
- [ ] `just lint-full` passes

---

## Implementation Guidelines

### Code Standards
- Follow DRY linter pattern for two-phase check()/finalize()
- All files must have proper file headers (see `.ai/docs/FILE_HEADER_STANDARDS.md`)
- Pylint 10.00/10 required
- MyPy zero errors required
- Xenon A-grade on every function/block
- Use atemporal language in all documentation

### Testing Requirements
- TDD: Write tests before implementation (PR1 is red phase)
- Unit tests for all detection logic
- Integration tests for CLI
- SARIF compliance tests
- Use `tmp_path` fixtures for mock project trees

### Documentation Standards
- File headers on all files
- Google-style docstrings on all public functions/classes
- User documentation in `docs/`

### Security Considerations
- No code execution, AST/tree-sitter analysis only
- Handle malformed input gracefully (syntax errors, corrupted YAML)
- State file is human-readable YAML

### Performance Targets
- Single file import parsing < 50ms
- Full project scan (1000 files) < 30 seconds
- In-memory graph (no disk I/O during analysis)

## Rollout Strategy

1. **PR1-PR2**: Foundation (types, graph, entry points)
2. **PR3-PR4**: Parsers (Python, TypeScript, infrastructure)
3. **PR5**: Core rule integration (feature internally functional)
4. **PR6**: Triage system (unique differentiator)
5. **PR7**: CLI integration (feature externally usable)
6. **PR8**: Documentation and dogfooding (feature complete)

## Success Metrics

### Launch Metrics
- 40+ unit tests passing
- 15+ CLI integration tests passing
- `thailint dead-code` command functional
- Three modes operational

### Ongoing Metrics
- False positive rate < 5% on self-dogfooding
- `just lint-full` passing
- User documentation complete
- State file workflow validated
