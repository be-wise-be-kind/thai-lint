# SARIF Standards for thai-lint

**Purpose**: Establish SARIF v2.1.0 as mandatory output format standard for all thai-lint linters

**Scope**: SARIF structure requirements, field mappings, testing standards, implementation checklist

**Overview**: Comprehensive standards document defining SARIF (Static Analysis Results Interchange Format)
    v2.1.0 requirements for all thai-lint linters. Establishes SARIF as mandatory output format alongside
    text and json, provides detailed structure specifications, field mapping guidelines, testing requirements,
    and implementation checklists. Essential reference for developers implementing new linters or modifying
    existing formatters. Ensures thai-lint maintains compatibility with GitHub Code Scanning, Azure DevOps,
    and other industry-standard CI/CD platforms.

**Dependencies**: SARIF v2.1.0 OASIS specification, thai-lint Violation dataclass structure

**Exports**: SARIF structure requirements, field mappings, testing standards, implementation checklists

**Related**: how-to-add-linter.md for implementation guidance, AGENTS.md for linter requirements

**Implementation**: Standards documentation with code examples, structure diagrams, and validation checklists

---

## Overview

This document defines the SARIF (Static Analysis Results Interchange Format) v2.1.0 standards for thai-lint. It covers why SARIF is mandatory, the required document structure, field mappings from thai-lint Violation objects to SARIF results, testing requirements, and implementation checklists. All linter developers must follow these standards to ensure compatibility with GitHub Code Scanning, Azure DevOps, VS Code SARIF Viewer, and other industry-standard tools.

---

## Why SARIF is Mandatory

SARIF (Static Analysis Results Interchange Format) is the industry-standard format for static analysis tool output. All thai-lint linters MUST support SARIF v2.1.0 output for the following reasons:

### Industry Integration

1. **GitHub Code Scanning**
   - Accepts SARIF as native input format
   - Displays results directly in PR security tab
   - Enables code scanning alerts and notifications
   - Supports SARIF for custom security tools

2. **Azure DevOps**
   - Native SARIF support in pipeline security features
   - Integrates with security dashboards and alerts
   - Supports SARIF-based policy enforcement

3. **VS Code SARIF Viewer**
   - Microsoft's official SARIF visualization extension
   - Enables clicking violations to navigate to source
   - Provides filtering and grouping capabilities

4. **Universal Tool Interoperability**
   - Standard format across security and linting ecosystems
   - Enables aggregation of results from multiple tools
   - Supports rich metadata and code snippets

---

## SARIF v2.1.0 Structure Overview

SARIF documents follow a hierarchical structure with three main levels:

```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "thai-lint",
          "version": "0.5.0",
          "informationUri": "https://github.com/be-wise-be-kind/thai-lint",
          "rules": []
        }
      },
      "results": []
    }
  ]
}
```

### Document Level
- `version`: Must be "2.1.0"
- `$schema`: URL to official SARIF JSON schema
- `runs`: Array of analysis runs (thai-lint produces one run)

### Run Level
- `tool`: Contains driver information
- `results`: Array of violation results

### Tool Driver Level
- `name`: "thai-lint"
- `version`: Package version from `src.__version__`
- `informationUri`: Documentation URL
- `rules`: Array of rule definitions (optional but recommended)

### Result Level (Per Violation)
- `ruleId`: Rule identifier (e.g., "file-placement", "nesting-depth")
- `level`: Severity level ("error", "warning", "note")
- `message`: Violation description
- `locations`: Array of affected code locations

---

## Required Fields

### Document Level (Mandatory)

| Field | Value | Description |
|-------|-------|-------------|
| `version` | "2.1.0" | SARIF specification version |
| `$schema` | Schema URL | JSON schema for validation |
| `runs` | Array | One or more analysis runs |

### Run Level (Mandatory)

| Field | Value | Description |
|-------|-------|-------------|
| `tool.driver.name` | "thai-lint" | Tool identifier |
| `tool.driver.version` | Package version | Semantic version |
| `results` | Array | Violation results |

### Result Level (Per Violation)

| Field | Source | Description |
|-------|--------|-------------|
| `ruleId` | `Violation.rule_id` | Rule identifier |
| `level` | Mapped from severity | "error", "warning", or "note" |
| `message.text` | `Violation.message` | Human-readable description |
| `locations[0].physicalLocation.artifactLocation.uri` | `Violation.file_path` | Relative file path |
| `locations[0].physicalLocation.region.startLine` | `Violation.line` | 1-indexed line number |
| `locations[0].physicalLocation.region.startColumn` | `Violation.column + 1` | 1-indexed column |

---

## Field Mapping: Violation to SARIF

The following mapping converts thai-lint Violation objects to SARIF results:

```python
# thai-lint Violation structure
@dataclass
class Violation:
    rule_id: str
    message: str
    severity: Severity
    file_path: str
    line: int
    column: int

# SARIF result structure
result = {
    "ruleId": violation.rule_id,
    "level": _map_severity(violation.severity),
    "message": {"text": violation.message},
    "locations": [{
        "physicalLocation": {
            "artifactLocation": {"uri": violation.file_path},
            "region": {
                "startLine": violation.line,
                "startColumn": violation.column + 1  # SARIF is 1-indexed
            }
        }
    }]
}
```

### Severity Mapping

| thai-lint Severity | SARIF Level |
|-------------------|-------------|
| `Severity.ERROR` | "error" |
| `Severity.WARNING` | "warning" |
| `Severity.INFO` | "note" |

Note: thai-lint linters use `Severity.ERROR` as the default severity level.

---

## Tool Metadata Requirements

### Required Metadata

```python
TOOL_METADATA = {
    "name": "thai-lint",
    "version": __version__,  # From src/__init__.py
    "informationUri": "https://github.com/be-wise-be-kind/thai-lint"
}
```

### Optional but Recommended

- `rules`: Array of rule definitions with `id`, `name`, and `shortDescription`
- `semanticVersion`: Semantic version for compatibility checking

---

## Testing Requirements

All SARIF implementations MUST include comprehensive tests:

### Unit Tests (40+ tests)

1. **Document Structure Tests**
   - `version` is exactly "2.1.0"
   - `$schema` contains valid schema URL
   - `runs` is non-empty array
   - Single run per output

2. **Tool Metadata Tests**
   - `tool.driver.name` is "thai-lint"
   - `tool.driver.version` matches package version
   - `tool.driver.informationUri` is valid URL

3. **Result Conversion Tests**
   - Each violation produces one result
   - `ruleId` matches violation rule_id
   - `level` correctly maps severity
   - `message.text` contains violation message
   - Location contains valid file path
   - Line numbers are correct (1-indexed)
   - Column numbers are correct (1-indexed)

4. **Edge Case Tests**
   - Empty violations produces empty results array
   - Special characters in messages are handled
   - Very long messages are preserved
   - Unicode in file paths is handled

### CLI Integration Tests (15+ tests)

1. **Format Option Tests**
   - `--format sarif` option works
   - Output is valid JSON
   - Output matches SARIF structure

2. **Multi-Linter Tests**
   - Each of 5 linters supports `--format sarif`
   - Output structure is consistent across linters

### Schema Validation Tests (10+ tests)

1. **JSON Schema Validation**
   - Output validates against SARIF v2.1.0 JSON schema
   - Required fields are present
   - Field types are correct

---

## Implementation Checklist

When implementing SARIF support, verify each item:

### Code Implementation
- [ ] Create `src/formatters/__init__.py` (if not exists)
- [ ] Create `src/formatters/sarif.py` with `SarifFormatter` class
- [ ] Add "sarif" to `--format` choices in `src/cli.py`
- [ ] Add `_format_sarif()` handler in `src/core/cli_utils.py`
- [ ] Import version from `src/__init__.py`

### Test Implementation
- [ ] Create `tests/unit/formatters/__init__.py`
- [ ] Create `tests/unit/formatters/test_sarif_formatter.py` (40+ tests)
- [ ] Create `tests/unit/test_cli_sarif_output.py` (15+ tests)
- [ ] Create `tests/integration/test_sarif_all_linters.py` (10+ tests)

### Validation
- [ ] All tests pass (`just test`)
- [ ] Quality checks pass (`just lint-full`)
- [ ] Manual test: `thailint file-placement --format sarif . | jq`
- [ ] Output validates against SARIF v2.1.0 JSON schema

---

## Validation Criteria

SARIF output is considered valid when:

1. **Valid JSON**: Output can be parsed by any JSON parser
2. **Schema Compliance**: Validates against SARIF v2.1.0 JSON schema
3. **GitHub Compatible**: GitHub Code Scanning accepts and displays results
4. **VS Code Compatible**: VS Code SARIF Viewer can open and display results
5. **Complete Data**: All violation information is present and accurate

---

## Reference Implementation Pattern

```python
"""SARIF v2.1.0 formatter for thai-lint violations."""

from dataclasses import dataclass
from src import __version__
from src.core.violation import Violation, Severity


SARIF_SCHEMA_URL = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
    "main/sarif-2.1/schema/sarif-schema-2.1.0.json"
)


class SarifFormatter:
    """Formats violations as SARIF v2.1.0 JSON."""

    def format(self, violations: list[Violation]) -> dict:
        """Convert violations to SARIF document."""
        return {
            "version": "2.1.0",
            "$schema": SARIF_SCHEMA_URL,
            "runs": [self._create_run(violations)]
        }

    def _create_run(self, violations: list[Violation]) -> dict:
        """Create a SARIF run object."""
        return {
            "tool": self._create_tool(),
            "results": [self._create_result(v) for v in violations]
        }

    def _create_tool(self) -> dict:
        """Create SARIF tool object with driver info."""
        return {
            "driver": {
                "name": "thai-lint",
                "version": __version__,
                "informationUri": "https://github.com/be-wise-be-kind/thai-lint"
            }
        }

    def _create_result(self, violation: Violation) -> dict:
        """Convert a single violation to SARIF result."""
        return {
            "ruleId": violation.rule_id,
            "level": self._map_severity(violation.severity),
            "message": {"text": violation.message},
            "locations": [self._create_location(violation)]
        }

    def _create_location(self, violation: Violation) -> dict:
        """Create SARIF location from violation."""
        return {
            "physicalLocation": {
                "artifactLocation": {"uri": violation.file_path},
                "region": {
                    "startLine": violation.line,
                    "startColumn": violation.column + 1  # SARIF is 1-indexed
                }
            }
        }

    def _map_severity(self, severity: Severity) -> str:
        """Map thai-lint severity to SARIF level."""
        mapping = {
            Severity.ERROR: "error",
            Severity.WARNING: "warning",
            Severity.INFO: "note"
        }
        return mapping.get(severity, "error")
```

---

## Resources

- **SARIF Specification**: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- **SARIF JSON Schema**: https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json
- **GitHub SARIF Support**: https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning
- **VS Code SARIF Viewer**: https://marketplace.visualstudio.com/items?itemName=MS-SarifVSCode.sarif-viewer
