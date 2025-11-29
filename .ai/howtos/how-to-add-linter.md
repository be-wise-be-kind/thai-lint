# How to Add a New Linter to thai-lint

**Purpose**: Step-by-step guide for implementing new linters in thai-lint with full quality compliance

**Scope**: Complete linter development lifecycle from planning through documentation and testing

**Overview**: Comprehensive guide for developing new linters in thai-lint. Covers the complete
    development lifecycle including planning, TDD implementation, output format support (text, json,
    SARIF), CLI integration, testing requirements, and documentation. Ensures all new linters meet
    quality standards and support mandatory output formats including SARIF v2.1.0 for CI/CD integration.

**Dependencies**: Existing linter implementations in `src/linters/`, core violation types, CLI framework

**Exports**: Step-by-step implementation guide, code patterns, testing templates, checklist

**Related**: SARIF_STANDARDS.md for output format requirements, FILE_HEADER_STANDARDS.md for headers

**Implementation**: TDD-driven development with comprehensive testing and documentation requirements

---

## Overview

This guide walks through the complete process of adding a new linter to thai-lint. All new linters
must follow these guidelines to ensure consistency, quality, and proper integration with the CLI
and CI/CD pipelines.

## Prerequisites

Before starting, ensure you have:

- [ ] Understanding of the violation type you want to detect
- [ ] Read `.ai/docs/SARIF_STANDARDS.md` for output format requirements
- [ ] Read `.ai/docs/FILE_HEADER_STANDARDS.md` for code header requirements
- [ ] Reviewed existing linters in `src/linters/` for patterns

## Step-by-Step Implementation

### Step 1: Plan Your Linter

Before writing code, define:

1. **Violation Type**: What code smell or anti-pattern does this linter detect?
2. **Rule ID**: Short identifier (e.g., `magic-numbers`, `nesting-depth`)
3. **Severity Level**: ERROR (default), WARNING, or INFO
4. **Supported Languages**: Python, TypeScript, or both?
5. **Configuration Options**: Max values, exclude patterns, etc.

### Step 2: Create Test Directory Structure

Follow TDD - write tests FIRST:

```bash
mkdir -p tests/unit/linters/your_linter/
touch tests/unit/linters/your_linter/__init__.py
touch tests/unit/linters/your_linter/test_your_linter.py
```

### Step 3: Write Unit Tests (TDD Phase 1)

Create comprehensive tests BEFORE implementation:

```python
"""
Purpose: Unit tests for YourLinter violation detection

Scope: Test cases covering all detection scenarios and edge cases

Overview: Comprehensive test suite for YourLinter following TDD methodology.
    Tests cover basic detection, edge cases, configuration options, and all
    supported output formats including SARIF v2.1.0.
"""

import pytest
from src.linters.your_linter import YourLinter
from src.core.violation import Violation, Severity


class TestYourLinterBasicDetection:
    """Tests for basic violation detection."""

    def test_detects_violation_in_simple_case(self):
        """Should detect violation in straightforward example."""
        code = "your example code here"
        linter = YourLinter()
        violations = linter.analyze(code, "test.py")

        assert len(violations) == 1
        assert violations[0].rule_id == "your-rule-id"
        assert violations[0].severity == Severity.ERROR

    def test_no_false_positives_for_valid_code(self):
        """Should not flag valid code patterns."""
        code = "valid code here"
        linter = YourLinter()
        violations = linter.analyze(code, "test.py")

        assert len(violations) == 0


class TestYourLinterConfiguration:
    """Tests for linter configuration options."""

    def test_respects_max_threshold(self):
        """Should respect configured threshold values."""
        linter = YourLinter(max_value=5)
        # Test threshold behavior


class TestYourLinterEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_handles_empty_file(self):
        """Should handle empty files gracefully."""
        linter = YourLinter()
        violations = linter.analyze("", "test.py")
        assert len(violations) == 0

    def test_handles_unicode(self):
        """Should handle Unicode content correctly."""
        code = "# Thai comment: สวัสดี"
        linter = YourLinter()
        violations = linter.analyze(code, "test.py")
        # Verify correct handling
```

### Step 4: Create Linter Module Structure

Create the linter implementation files:

```bash
mkdir -p src/linters/your_linter/
touch src/linters/your_linter/__init__.py
touch src/linters/your_linter/analyzer.py
touch src/linters/your_linter/rules.py
```

### Step 5: Implement the Linter (TDD Phase 2)

Make your tests pass by implementing the linter:

```python
"""
Purpose: YourLinter implementation for detecting [violation type]

Scope: Analyzes Python and TypeScript code for [violation pattern]

Overview: Implements violation detection for [description]. Uses AST parsing
    to identify [pattern] in code. Supports configurable thresholds and
    exclude patterns. Integrates with thai-lint CLI and supports all three
    output formats: text, json, and SARIF v2.1.0.

Dependencies: tree-sitter for parsing, src.core.violation for violation types

Exports: YourLinter class, YourRule dataclass

Interfaces: analyze(code: str, filepath: str) -> list[Violation]

Implementation: AST-based pattern matching with configurable rules
"""

from dataclasses import dataclass
from src.core.violation import Violation, Severity


@dataclass
class YourLinterConfig:
    """Configuration options for YourLinter."""

    max_threshold: int = 10
    exclude_patterns: list[str] | None = None


class YourLinter:
    """Detects [violation type] in source code."""

    def __init__(self, config: YourLinterConfig | None = None):
        self.config = config or YourLinterConfig()

    def analyze(self, code: str, filepath: str) -> list[Violation]:
        """Analyze code and return list of violations."""
        violations: list[Violation] = []

        # Implementation here

        return violations

    def _create_violation(
        self,
        message: str,
        filepath: str,
        line: int,
        column: int
    ) -> Violation:
        """Create a violation object."""
        return Violation(
            rule_id="your-rule-id",
            message=message,
            severity=Severity.ERROR,
            file_path=filepath,
            line=line,
            column=column
        )
```

### Step 6: Register with CLI

Add your linter command to `src/cli.py`:

```python
@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@format_option
@click.option("--max-threshold", default=10, help="Maximum allowed threshold")
def your_linter(paths: tuple[str, ...], format: str, max_threshold: int):
    """Detect [violation type] in source code."""
    from src.linters.your_linter import YourLinter, YourLinterConfig

    config = YourLinterConfig(max_threshold=max_threshold)
    linter = YourLinter(config)

    all_violations = []
    for path in paths:
        violations = analyze_path(path, linter)
        all_violations.extend(violations)

    output = format_violations(all_violations, format)
    click.echo(output)
```

### Step 7: Ensure SARIF Support

Verify your linter works with all output formats:

```bash
# Text output (default)
thailint your-linter .

# JSON output
thailint your-linter --format json .

# SARIF output (MANDATORY)
thailint your-linter --format sarif . | jq
```

**SARIF is mandatory.** See `.ai/docs/SARIF_STANDARDS.md` for requirements.

### Step 8: Add CLI Integration Tests

Test the CLI integration:

```python
"""
Purpose: CLI integration tests for your-linter command

Scope: Tests CLI invocation, option handling, and output format support
"""

import subprocess
import json


class TestYourLinterCLI:
    """Tests for CLI integration."""

    def test_cli_text_output(self, tmp_path):
        """Should produce readable text output."""
        result = subprocess.run(
            ["thailint", "your-linter", str(tmp_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode in (0, 1)

    def test_cli_json_output(self, tmp_path):
        """Should produce valid JSON output."""
        result = subprocess.run(
            ["thailint", "your-linter", "--format", "json", str(tmp_path)],
            capture_output=True,
            text=True
        )
        output = json.loads(result.stdout)
        assert "violations" in output

    def test_cli_sarif_output(self, tmp_path):
        """Should produce valid SARIF output."""
        result = subprocess.run(
            ["thailint", "your-linter", "--format", "sarif", str(tmp_path)],
            capture_output=True,
            text=True
        )
        sarif = json.loads(result.stdout)
        assert sarif["version"] == "2.1.0"
        assert "runs" in sarif
```

### Step 9: Write Documentation

Create user-facing documentation:

1. **Update README.md** - Add linter to feature list
2. **Create docs/your-linter.md** - Detailed usage guide
3. **Add examples** - Sample code with violations

### Step 10: Final Quality Checks

Before submitting your PR, verify:

```bash
# All tests pass
just test

# Full quality checks pass
just lint-full

# Manual verification
thailint your-linter --format sarif examples/ | jq

# Type checking
poetry run mypy src/linters/your_linter/
```

## Complete Implementation Checklist

### Development
- [ ] Define violation type and rule ID
- [ ] Write unit tests (40+ tests recommended)
- [ ] Implement linter class with proper file headers
- [ ] Add CLI command registration
- [ ] Write CLI integration tests (15+ tests)

### Output Format Support (MANDATORY)
- [ ] Text format works (`--format text` or default)
- [ ] JSON format works (`--format json`)
- [ ] SARIF format works (`--format sarif`)
- [ ] SARIF output validates against v2.1.0 schema

### Quality
- [ ] All tests pass (`just test`)
- [ ] Pylint score is 10.00/10
- [ ] Xenon complexity is A-grade
- [ ] MyPy passes with no errors
- [ ] `just lint-full` passes

### Documentation
- [ ] File headers on all new files
- [ ] README.md updated with new linter
- [ ] User documentation in docs/
- [ ] Usage examples provided

## Common Patterns

### Violation Creation Pattern

```python
def _create_violation(
    self,
    message: str,
    filepath: str,
    node: Any
) -> Violation:
    """Create violation from AST node."""
    return Violation(
        rule_id=self.RULE_ID,
        message=message,
        severity=Severity.ERROR,
        file_path=filepath,
        line=node.start_point[0] + 1,  # tree-sitter is 0-indexed
        column=node.start_point[1]
    )
```

### Configuration Pattern

```python
@dataclass
class LinterConfig:
    """Configuration with sensible defaults."""

    max_value: int = 10
    exclude_patterns: list[str] = field(default_factory=list)

    @classmethod
    def from_cli_options(cls, **kwargs) -> "LinterConfig":
        """Create config from CLI options."""
        return cls(**{k: v for k, v in kwargs.items() if v is not None})
```

### Multi-Language Support Pattern

```python
class MultiLanguageLinter:
    """Linter supporting multiple languages."""

    ANALYZERS = {
        ".py": PythonAnalyzer,
        ".ts": TypeScriptAnalyzer,
        ".tsx": TypeScriptAnalyzer,
    }

    def analyze(self, code: str, filepath: str) -> list[Violation]:
        """Route to appropriate language analyzer."""
        ext = Path(filepath).suffix
        analyzer_class = self.ANALYZERS.get(ext)
        if analyzer_class:
            return analyzer_class().analyze(code, filepath)
        return []
```

## Resources

- **SARIF Standards**: `.ai/docs/SARIF_STANDARDS.md`
- **File Headers**: `.ai/docs/FILE_HEADER_STANDARDS.md`
- **Existing Linters**: `src/linters/` (reference implementations)
- **Core Types**: `src/core/violation.py`
- **CLI Framework**: `src/cli.py`

## Troubleshooting

### Tests Fail with Import Errors

Ensure `__init__.py` files exist in all directories and exports are correct.

### SARIF Output Invalid

Check that your violations include all required fields:
- `rule_id`
- `message`
- `severity`
- `file_path`
- `line` (1-indexed)
- `column` (0-indexed, SARIF will add 1)

### Pylint Score Below 10.00

Common issues:
- Missing docstrings
- Line too long (max 100 characters)
- Missing type hints
- Unused imports

### Complexity Too High

Break down large functions:
- Extract helper methods
- Use early returns
- Simplify conditionals

See `.ai/howtos/how-to-refactor-for-quality.md` for guidance.
