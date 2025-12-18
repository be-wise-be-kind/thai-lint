# Collection Pipeline Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of the Collection Pipeline linter into manageable, atomic pull requests

**Scope**: Complete implementation from TDD tests through release and documentation

**Overview**: Comprehensive breakdown of the Collection Pipeline linter into 6 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application
    functionality while incrementally building toward the complete feature. Uses TDD approach
    where tests are written before implementation.

**Dependencies**: Existing linter patterns, AST analysis utilities

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria

**Related**: AI_CONTEXT.md for research findings, PROGRESS_TRACKER.md for status tracking

**Implementation**: TDD-first approach with comprehensive testing at each stage

---

## Overview

This document breaks down the Collection Pipeline linter into 6 atomic PRs:
- **PR1-PR3**: Core implementation (TDD, CLI, Config)
- **PR4**: Dogfooding and validation
- **PR5-PR6**: Documentation and release

Each PR is designed to be self-contained, testable, and revertible.

---

## PR1: Core Detection Engine (TDD)

### Goal
Implement pattern detection using Test-Driven Development. Write tests first, then implement.

### Scope
- Pattern detection for `for` loops with embedded filtering
- AST analysis for Python code
- Violation reporting with suggestions

### TDD Workflow

```
Step 1: Write test → RED (fails)
Step 2: Implement → GREEN (passes)
Step 3: Refactor → GREEN (still passes)
```

### Step 1: Write Tests First

#### Create `tests/unit/linters/collection_pipeline/__init__.py`
```python
"""Tests for collection-pipeline linter."""
```

#### Create `tests/unit/linters/collection_pipeline/test_patterns.py`
```python
"""
Purpose: Test detection of collection pipeline anti-patterns
Scope: Unit tests for pattern matching logic
"""
import pytest

class TestSingleContinuePattern:
    """Test detection of single if/continue pattern."""

    def test_detects_if_not_continue(self):
        """Detect: for x in iter: if not cond: continue; action(x)"""
        code = '''
for item in items:
    if not item.is_valid():
        continue
    process(item)
'''
        violations = analyze_code(code)
        assert len(violations) == 1
        assert "collection pipeline" in violations[0].message.lower()

    def test_detects_if_continue_with_negation(self):
        """Detect: for x in iter: if cond: continue; action(x)"""
        code = '''
for path in paths:
    if path.is_dir():
        continue
    lint_file(path)
'''
        violations = analyze_code(code)
        assert len(violations) == 1

    def test_ignores_if_with_else(self):
        """Don't flag if/continue when there's an else branch."""
        code = '''
for item in items:
    if not item.is_valid():
        continue
    else:
        special_process(item)
    process(item)
'''
        violations = analyze_code(code)
        assert len(violations) == 0  # Has else, not a simple filter

    def test_ignores_continue_with_side_effects(self):
        """Don't flag if condition has side effects."""
        code = '''
for item in items:
    if not (result := validate(item)):
        continue
    process(item, result)
'''
        violations = analyze_code(code)
        assert len(violations) == 0  # Walrus operator = side effect


class TestMultipleContinuePattern:
    """Test detection of multiple if/continue patterns."""

    def test_detects_multiple_continues(self):
        """Detect: for x: if not c1: continue; if not c2: continue; action(x)"""
        code = '''
for file_path in paths:
    if not file_path.is_file():
        continue
    if is_ignored(file_path):
        continue
    process(file_path)
'''
        violations = analyze_code(code)
        assert len(violations) == 1
        # Should suggest combining conditions

    def test_detects_three_continues(self):
        """Detect three sequential if/continue patterns."""
        code = '''
for item in items:
    if not cond1(item):
        continue
    if not cond2(item):
        continue
    if not cond3(item):
        continue
    process(item)
'''
        violations = analyze_code(code)
        assert len(violations) == 1


class TestNoViolationCases:
    """Test cases that should NOT trigger violations."""

    def test_no_violation_for_simple_loop(self):
        """Simple loop without filtering."""
        code = '''
for item in items:
    process(item)
'''
        violations = analyze_code(code)
        assert len(violations) == 0

    def test_no_violation_for_break(self):
        """Loop with break is not a filter pattern."""
        code = '''
for item in items:
    if item.is_target():
        break
    process(item)
'''
        violations = analyze_code(code)
        assert len(violations) == 0

    def test_no_violation_for_return(self):
        """Loop with return is handled by SIM110."""
        code = '''
for item in items:
    if item.matches():
        return item
'''
        violations = analyze_code(code)
        assert len(violations) == 0  # SIM110 handles this

    def test_no_violation_for_generator_expression(self):
        """Already using collection pipeline."""
        code = '''
for item in (x for x in items if x.is_valid()):
    process(item)
'''
        violations = analyze_code(code)
        assert len(violations) == 0

    def test_no_violation_for_filter(self):
        """Already using filter()."""
        code = '''
for item in filter(lambda x: x.is_valid(), items):
    process(item)
'''
        violations = analyze_code(code)
        assert len(violations) == 0
```

#### Create `tests/unit/linters/collection_pipeline/test_suggestions.py`
```python
"""
Purpose: Test that suggestions are accurate and helpful
Scope: Unit tests for suggestion generation
"""
import pytest

class TestSuggestions:
    """Test suggestion quality."""

    def test_suggests_generator_expression(self):
        """Suggestion should show generator expression syntax."""
        code = '''
for item in items:
    if not item.is_valid():
        continue
    process(item)
'''
        violations = analyze_code(code)
        assert "for item in (x for x in items if x.is_valid())" in violations[0].suggestion

    def test_suggests_combined_conditions(self):
        """Multiple conditions should be combined with 'and'."""
        code = '''
for path in paths:
    if not path.is_file():
        continue
    if is_ignored(path):
        continue
    process(path)
'''
        violations = analyze_code(code)
        suggestion = violations[0].suggestion
        assert "path.is_file()" in suggestion
        assert "not is_ignored(path)" in suggestion
        assert " and " in suggestion
```

### Step 2: Implement Detection Engine

#### Create `src/linters/collection_pipeline/__init__.py`
```python
"""
Purpose: Export CollectionPipelineRule for automatic discovery by the rule registry
Scope: Module initialization and public API exposure
Overview: Provides the CollectionPipelineRule class which detects imperative loop patterns
    with embedded filtering that could be refactored to collection pipelines.
Dependencies: src.core.base, src.core.types
Exports: CollectionPipelineRule
Interfaces: BaseLintRule interface
Implementation: Plugin architecture with automatic discovery via rule registry
"""
from .linter import CollectionPipelineRule

__all__ = ["CollectionPipelineRule"]
```

#### Create `src/linters/collection_pipeline/config.py`
```python
"""
Purpose: Configuration dataclass for collection-pipeline linter
Scope: Define configurable options and thresholds
Overview: Provides CollectionPipelineConfig for customizing linter behavior including
    minimum pattern complexity to report, whether to suggest filter() vs generators,
    and ignore patterns.
Dependencies: dataclasses
Exports: CollectionPipelineConfig
Interfaces: from_dict class method for configuration loading
Implementation: Dataclass with sensible defaults and validation
"""
from dataclasses import dataclass, field

@dataclass
class CollectionPipelineConfig:
    """Configuration for collection-pipeline linter."""

    enabled: bool = True
    min_continues: int = 1  # Minimum if/continue patterns to flag
    suggest_filter: bool = False  # Suggest filter() instead of generator
    suggest_comprehension: bool = False  # Suggest list comp for .append patterns
    ignore: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config: dict, language: str | None = None) -> "CollectionPipelineConfig":
        """Load configuration from dictionary."""
        return cls(
            enabled=config.get("enabled", True),
            min_continues=config.get("min_continues", 1),
            suggest_filter=config.get("suggest_filter", False),
            suggest_comprehension=config.get("suggest_comprehension", False),
            ignore=config.get("ignore", []),
        )
```

#### Create `src/linters/collection_pipeline/detector.py`
```python
"""
Purpose: AST-based detection of collection pipeline anti-patterns
Scope: Pattern matching for for loops with embedded filtering
Overview: Implements the core detection logic for identifying imperative loop patterns
    that use if/continue for filtering instead of collection pipelines. Uses Python's
    AST module to analyze code structure and identify refactoring opportunities.
Dependencies: ast, src.core.types
Exports: PipelinePatternDetector, PatternMatch
Interfaces: detect_patterns(ast_tree) -> list[PatternMatch]
Implementation: AST visitor pattern with pattern matching heuristics
"""
import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PatternMatch:
    """Represents a detected anti-pattern."""

    line_number: int
    loop_var: str
    iterable: str
    conditions: list[str]
    has_side_effects: bool
    suggestion: str


class PipelinePatternDetector(ast.NodeVisitor):
    """Detects for loops with embedded filtering."""

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.matches: list[PatternMatch] = []

    def detect_patterns(self) -> list[PatternMatch]:
        """Analyze source code and return detected patterns."""
        try:
            tree = ast.parse(self.source_code)
            self.visit(tree)
        except SyntaxError:
            pass  # Invalid Python, skip
        return self.matches

    def visit_For(self, node: ast.For) -> None:
        """Visit for loop and check for filtering patterns."""
        # Check if loop body starts with if/continue patterns
        continues = self._extract_continue_patterns(node.body)

        if continues and not self._has_side_effects(continues):
            match = self._create_match(node, continues)
            self.matches.append(match)

        self.generic_visit(node)

    def _extract_continue_patterns(self, body: list[ast.stmt]) -> list[ast.If]:
        """Extract if statements that only contain continue."""
        continues = []
        for stmt in body:
            if isinstance(stmt, ast.If):
                if self._is_continue_only(stmt):
                    continues.append(stmt)
                else:
                    break  # Non-continue if, stop
            else:
                break  # Non-if statement, stop
        return continues

    def _is_continue_only(self, if_node: ast.If) -> bool:
        """Check if an if statement only contains continue."""
        if len(if_node.body) != 1:
            return False
        if not isinstance(if_node.body[0], ast.Continue):
            return False
        if if_node.orelse:  # Has else branch
            return False
        return True

    def _has_side_effects(self, continues: list[ast.If]) -> bool:
        """Check if any condition has side effects (walrus, function calls that mutate)."""
        for if_node in continues:
            if self._condition_has_side_effects(if_node.test):
                return True
        return False

    def _condition_has_side_effects(self, node: ast.expr) -> bool:
        """Check if expression has side effects."""
        # Walrus operator
        if isinstance(node, ast.NamedExpr):
            return True
        # Recursively check children
        for child in ast.walk(node):
            if isinstance(child, ast.NamedExpr):
                return True
        return False

    def _create_match(self, for_node: ast.For, continues: list[ast.If]) -> PatternMatch:
        """Create a PatternMatch from detected pattern."""
        loop_var = self._get_target_name(for_node.target)
        iterable = self._get_source_segment(for_node.iter)
        conditions = [self._invert_condition(c.test) for c in continues]

        suggestion = self._generate_suggestion(loop_var, iterable, conditions)

        return PatternMatch(
            line_number=for_node.lineno,
            loop_var=loop_var,
            iterable=iterable,
            conditions=conditions,
            has_side_effects=False,
            suggestion=suggestion,
        )

    def _get_target_name(self, target: ast.expr) -> str:
        """Get the loop variable name."""
        if isinstance(target, ast.Name):
            return target.id
        return ast.unparse(target)

    def _get_source_segment(self, node: ast.expr) -> str:
        """Get source code for an AST node."""
        return ast.unparse(node)

    def _invert_condition(self, condition: ast.expr) -> str:
        """Invert a condition (for if not x: continue -> if x)."""
        if isinstance(condition, ast.UnaryOp) and isinstance(condition.op, ast.Not):
            return ast.unparse(condition.operand)
        else:
            return f"not ({ast.unparse(condition)})"

    def _generate_suggestion(self, loop_var: str, iterable: str, conditions: list[str]) -> str:
        """Generate refactoring suggestion."""
        combined = " and ".join(conditions)
        return f"for {loop_var} in ({loop_var} for {loop_var} in {iterable} if {combined}):"
```

#### Create `src/linters/collection_pipeline/linter.py`
```python
"""
Purpose: CollectionPipelineRule implementation for detecting loop filtering anti-patterns
Scope: Multi-language analysis and violation reporting
Overview: Implements the BaseLintRule interface to detect for loops with embedded
    filtering logic that could be refactored to collection pipelines. Currently
    supports Python; TypeScript support planned for future.
Dependencies: src.core.base, src.core.types, .detector, .config
Exports: CollectionPipelineRule
Interfaces: BaseLintRule.check(), BaseLintRule.rule_id
Implementation: Uses PipelinePatternDetector for AST analysis
"""
from pathlib import Path

from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation, Severity
from src.core.linter_utils import load_linter_config

from .config import CollectionPipelineConfig
from .detector import PipelinePatternDetector


class CollectionPipelineRule(BaseLintRule):
    """Detects for loops with embedded filtering that could use collection pipelines."""

    @property
    def rule_id(self) -> str:
        return "collection-pipeline.embedded-filter"

    @property
    def description(self) -> str:
        return "For loop contains embedded filtering that could be a collection pipeline"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file for collection pipeline anti-patterns."""
        if context.language != "python":
            return []  # Only Python for now

        config = load_linter_config(
            context, "collection-pipeline", CollectionPipelineConfig
        )

        if not config.enabled:
            return []

        content = context.file_content
        if not content:
            return []

        detector = PipelinePatternDetector(content)
        matches = detector.detect_patterns()

        violations = []
        for match in matches:
            if len(match.conditions) >= config.min_continues:
                violation = Violation(
                    rule_id=self.rule_id,
                    message=self._build_message(match),
                    file_path=context.file_path,
                    line_number=match.line_number,
                    column=0,
                    severity=Severity.WARNING,
                    suggestion=match.suggestion,
                )
                violations.append(violation)

        return violations

    def _build_message(self, match) -> str:
        """Build violation message."""
        num_conditions = len(match.conditions)
        if num_conditions == 1:
            return (
                f"For loop over '{match.iterable}' has embedded filtering. "
                f"Consider using a generator expression: {match.suggestion}"
            )
        else:
            return (
                f"For loop over '{match.iterable}' has {num_conditions} filter conditions. "
                f"Consider combining into a collection pipeline: {match.suggestion}"
            )
```

### Success Criteria
- [ ] All tests in `test_patterns.py` pass
- [ ] All tests in `test_suggestions.py` pass
- [ ] Coverage > 90% for new code
- [ ] Pylint 10.00/10
- [ ] Xenon A-grade complexity

---

## PR2: CLI Integration

### Goal
Add `thailint pipeline` command to the CLI.

### Files to Create/Modify

#### Create `tests/unit/linters/collection_pipeline/test_cli_interface.py`
```python
"""Test CLI interface for collection-pipeline linter."""
import pytest
from click.testing import CliRunner

class TestCLIInterface:
    """Test the pipeline CLI command."""

    def test_command_exists(self):
        """The pipeline command should exist."""
        from src.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", "--help"])
        assert result.exit_code == 0
        assert "embedded filtering" in result.output.lower()

    def test_detects_violation(self, tmp_path):
        """Should detect violations in files."""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
for item in items:
    if not item.valid:
        continue
    process(item)
''')
        from src.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", str(test_file)])
        assert result.exit_code == 1
        assert "collection-pipeline" in result.output

    def test_json_output(self, tmp_path):
        """Should support JSON output format."""
        # ...

    def test_sarif_output(self, tmp_path):
        """Should support SARIF output format."""
        # ...
```

#### Modify `src/cli.py`
Add new command:
```python
@cli.command("pipeline")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--min-continues", default=1, help="Minimum if/continue patterns to flag")
@common_options
def pipeline_command(paths, min_continues, format, verbose, project_root):
    """Check for loop filtering that could use collection pipelines.

    Detects for loops with embedded if/continue patterns that could be
    refactored to use generator expressions or filter().

    Based on Martin Fowler's 'Replace Loop with Pipeline' refactoring.
    """
    # Implementation
```

#### Modify `justfile`
```just
# Lint collection pipeline patterns
lint-pipeline *ARGS:
    poetry run python -m src.cli pipeline {{ARGS}}
```

### Success Criteria
- [ ] `thailint pipeline --help` works
- [ ] `thailint pipeline src/` detects violations
- [ ] All 3 output formats work (text, JSON, SARIF)
- [ ] `just lint-pipeline` recipe works

---

## PR3: Configuration & Ignore Support

### Goal
Add configuration in `.thailint.yaml` and inline ignore support.

### Configuration Schema

```yaml
collection-pipeline:
  enabled: true
  min_continues: 1
  suggest_filter: false
  ignore:
    - "tests/**"
    - "**/legacy/**"
```

### Inline Ignore

```python
# thailint: ignore[collection-pipeline]
for item in items:
    if not item.valid:
        continue
    process(item)
```

### Success Criteria
- [ ] Configuration loads from `.thailint.yaml`
- [ ] Inline ignores work
- [ ] File-level ignores work
- [ ] `min_continues` threshold respected

---

## PR4: Dogfooding & Fixes

### Goal
Run linter on thai-lint's own codebase and fix any violations.

### Process

1. Run `thailint pipeline src/`
2. Review each violation
3. Fix violations OR add justified ignores
4. Document any edge cases discovered
5. Update tests if needed

### Expected Violations

Known files with potential patterns:
- `src/linters/file_placement/linter.py` (verified)
- `src/orchestrator/orchestrator.py`
- `src/linters/dry/python_analyzer.py`

### Success Criteria
- [ ] `thailint pipeline src/` exits with code 0
- [ ] All fixes maintain test coverage
- [ ] Any ignores have justification comments
- [ ] Edge cases documented

---

## PR5: Documentation

### Goal
Comprehensive documentation for PyPI, ReadTheDocs, and DockerHub.

### Files to Create/Modify

#### Create `docs/collection-pipeline-linter.md`

```markdown
# Collection Pipeline Linter

Detects for loops with embedded filtering that could be refactored to
collection pipelines.

## The Anti-Pattern

```python
# Before: Embedded filtering
for file_path in paths:
    if not file_path.is_file():
        continue
    if is_ignored(file_path):
        continue
    process(file_path)
```

## The Solution

```python
# After: Collection pipeline
valid_files = (
    f for f in paths
    if f.is_file() and not is_ignored(f)
)
for file_path in valid_files:
    process(file_path)
```

## Why This Matters

- **Separation of concerns**: Filtering is separate from processing
- **Readability**: Intent is clearer
- **Based on**: Martin Fowler's "Replace Loop with Pipeline"

## Quick Start

```bash
# Check a directory
thailint pipeline src/

# With minimum threshold
thailint pipeline src/ --min-continues 2

# JSON output
thailint pipeline src/ --format json
```

## Configuration

```yaml
# .thailint.yaml
collection-pipeline:
  enabled: true
  min_continues: 1
  ignore:
    - "tests/**"
```

## Ignoring Violations

```python
# Inline ignore
# thailint: ignore[collection-pipeline]
for item in items:
    if not item.valid:
        continue
    process(item)
```

## Rule Details

| Property | Value |
|----------|-------|
| Rule ID | `collection-pipeline.embedded-filter` |
| Severity | Warning |
| Fixable | Manual |
| Languages | Python |

## Related

- [Martin Fowler: Refactoring with Loops and Collection Pipelines](https://martinfowler.com/articles/refactoring-pipelines.html)
- [Ruff PERF401](https://docs.astral.sh/ruff/rules/manual-list-comprehension/) (related but different pattern)
```

#### Update `README.md`

Add to linter list:
```markdown
| Collection Pipeline | Embedded filtering in loops | `thailint pipeline` |
```

#### DockerHub README

Add usage example:
```markdown
## Collection Pipeline Linter

```bash
docker run --rm -v $(pwd):/code thailint pipeline /code/src
```
```

### Success Criteria
- [ ] `docs/collection-pipeline-linter.md` created
- [ ] README updated with new linter
- [ ] CLI reference updated
- [ ] Configuration docs updated
- [ ] Docker examples added

---

## PR6: Release

### Goal
Publish new version with collection-pipeline linter.

### Steps

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Run full lint suite
5. Create release commit
6. Tag version
7. Publish to PyPI
8. Push Docker image

### Changelog Entry

```markdown
## [0.10.0] - YYYY-MM-DD

### Added
- **Collection Pipeline Linter**: New linter that detects for loops with
  embedded filtering (if/continue patterns) that could be refactored to
  collection pipelines. Based on Martin Fowler's "Replace Loop with Pipeline"
  refactoring pattern.
  - Rule ID: `collection-pipeline.embedded-filter`
  - CLI command: `thailint pipeline`
  - Configuration: `.thailint.yaml` under `collection-pipeline:`
```

### Success Criteria
- [ ] Version bumped
- [ ] Changelog updated
- [ ] All tests pass
- [ ] All lints pass
- [ ] Published to PyPI
- [ ] Docker image pushed
- [ ] GitHub release created

---

## Implementation Guidelines

### Code Standards
- All new code: Pylint 10.00/10
- All new code: Xenon A-grade complexity
- All new code: MyPy strict mode compliant
- File headers per `.ai/docs/FILE_HEADER_STANDARDS.md`
- Google-style docstrings on all public functions

### Testing Requirements
- TDD: Write tests BEFORE implementation
- Unit tests for all new code
- Integration tests for CLI
- Coverage > 90% for new code

### Documentation Standards
- Comprehensive docstrings
- Usage examples
- Configuration examples
- Error message examples

### Performance Targets
- Single file analysis: < 100ms
- Full codebase: < 5s
- Memory: < 100MB for typical usage
