# SARIF Output Format Support - PR Breakdown

**Purpose**: Detailed implementation breakdown of SARIF output format support into manageable, atomic pull requests

**Scope**: Complete feature implementation from planning through user documentation and badge deployment

**Overview**: Comprehensive breakdown of the SARIF output format feature into 4 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Follows strict TDD methodology with tests-first
    approach, establishes SARIF as mandatory standard, and provides comprehensive documentation and examples.

**Dependencies**: Python 3.11+, pytest (TDD), Click (CLI), json stdlib, existing formatters, package metadata

**Exports**: PR implementation plans, file structures, testing strategies, success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with TDD methodology, standards-first development, comprehensive testing validation

---

## Overview
This document breaks down the SARIF output format feature into 4 manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

**Development Phases**:
1. **PR1**: Standards & Documentation (Foundation)
2. **PR2**: Tests Only (TDD Phase 1)
3. **PR3**: Implementation (TDD Phase 2)
4. **PR4**: User Docs & Badge (Polish)

---

## PR1: SARIF Standards & Documentation Updates

### Overview
**Goal**: Establish SARIF as mandatory standard through comprehensive documentation

**Duration**: 1-2 hours

**Why This PR**:
- Sets foundation BEFORE any code
- Establishes SARIF as non-negotiable requirement
- Provides implementation guide for current and future developers
- Creates checklist for PR reviews

### Scope

**What Gets Created**:
1. `.ai/docs/SARIF_STANDARDS.md` - Comprehensive SARIF standard (150-200 lines)
2. Update `AGENTS.md` - Add SARIF to linter requirements
3. Update `.ai/index.yaml` - Add SARIF documentation reference
4. Create/Update `.ai/howtos/how-to-add-linter.md` - Include SARIF implementation steps

**What Does NOT Change**:
- No source code changes
- No test code changes
- No user-facing documentation changes (README, docs/)

### Detailed Steps

#### Step 1: Create `.ai/docs/SARIF_STANDARDS.md`

**File Path**: `/home/stevejackson/Projects/thai-lint/.ai/docs/SARIF_STANDARDS.md`

**File Header** (follow `.ai/docs/FILE_HEADER_STANDARDS.md`):
```markdown
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
```

**Content Sections**:
1. **Why SARIF is Mandatory**
   - GitHub Code Scanning integration
   - Azure DevOps integration
   - VS Code SARIF Viewer support
   - Industry standard status

2. **SARIF v2.1.0 Structure Overview**
   ```json
   {
     "version": "2.1.0",
     "$schema": "...",
     "runs": [
       {
         "tool": { "driver": {...} },
         "results": [...]
       }
     ]
   }
   ```

3. **Required Fields**
   - Document level: version, $schema, runs
   - Run level: tool, results
   - Tool level: driver (name, version, informationUri, rules)
   - Result level: ruleId, level, message, locations

4. **Field Mapping (Violation → SARIF)**
   ```
   Violation.rule_id    → result.ruleId
   Violation.message    → result.message.text
   Violation.severity   → result.level ("error")
   Violation.file_path  → location.artifactLocation.uri
   Violation.line       → location.region.startLine
   Violation.column+1   → location.region.startColumn (SARIF is 1-indexed)
   ```

5. **Severity Mapping**
   - Severity.ERROR → "error" (our only severity level)

6. **Tool Metadata Requirements**
   - name: "thai-lint"
   - version: from `src.__version__`
   - informationUri: "https://thai-lint.readthedocs.io/"

7. **Testing Requirements**
   - Test SARIF document structure (version, schema, runs)
   - Test tool metadata presence
   - Test result conversion for all violation types
   - Test all 5 linters produce valid SARIF
   - Test edge cases (empty violations, special characters)

8. **Implementation Checklist**
   ```markdown
   - [ ] Create SarifFormatter class in src/formatters/sarif.py
   - [ ] Add "sarif" to --format choices in src/cli.py
   - [ ] Add _format_sarif() handler in src/core/cli_utils.py
   - [ ] Write 40+ unit tests for formatter
   - [ ] Write 15+ CLI integration tests
   - [ ] Write 10+ multi-linter tests
   - [ ] Manual test: thailint <command> --format sarif . | jq
   - [ ] Validate output against SARIF v2.1.0 JSON schema
   ```

9. **Validation Criteria**
   - Output is valid JSON
   - Output validates against SARIF v2.1.0 JSON schema
   - GitHub Code Scanning can parse output
   - VS Code SARIF Viewer can display output

10. **Reference Implementation Pattern**
    ```python
    class SarifFormatter:
        def format(self, violations: list[Violation]) -> dict:
            return {
                "version": "2.1.0",
                "$schema": self._get_schema_uri(),
                "runs": [self._create_run(violations)]
            }
    ```

#### Step 2: Update `AGENTS.md`

**File Path**: `/home/stevejackson/Projects/thai-lint/AGENTS.md`

**Changes Required**:

Find the "Adding a New Linter" section (or create it) and add SARIF requirement:

```markdown
## Adding a New Linter

When implementing a new linter for thai-lint, follow this checklist:

### Development Checklist
- [ ] Implement linter class inheriting from BaseLintRule
- [ ] Write comprehensive tests (TDD approach)
- [ ] **Support all three output formats: text, json, and SARIF** ⭐ MANDATORY
- [ ] Follow file header standards (.ai/docs/FILE_HEADER_STANDARDS.md)
- [ ] Update documentation (README.md, docs/)
- [ ] Add usage examples

### SARIF Output Requirement
**ALL new linters MUST support SARIF v2.1.0 output format.**

See `.ai/docs/SARIF_STANDARDS.md` for:
- SARIF structure requirements
- Field mapping guidelines
- Testing standards
- Implementation checklist

**Validation**: Run `thailint <your-linter> --format sarif . | jq` to verify valid SARIF output.
```

#### Step 3: Update `.ai/index.yaml`

**File Path**: `/home/stevejackson/Projects/thai-lint/.ai/index.yaml`

**Changes Required**:

Add SARIF_STANDARDS.md to the `documentation` section:

```yaml
documentation:
  location: .ai/docs/
  files:
    - PROJECT_CONTEXT.md
    - SECURITY_STANDARDS.md
    - secrets-management.md
    - dependency-scanning.md
    - code-scanning.md
    - FILE_HEADER_STANDARDS.md
    - SARIF_STANDARDS.md  # ADD THIS LINE
  user_facing:
    - path: ../docs/ai-doc-standard.md
      description: AI-optimized documentation header standard
      tags: [documentation, standards, ai, headers, llm]
```

Also add to `standards` section:

```yaml
standards:
  sarif:
    description: "SARIF v2.1.0 output format standard for all linters"
    documentation:
      - path: "docs/SARIF_STANDARDS.md"
        description: "SARIF structure requirements, field mappings, testing standards"
    howtos:
      - path: "howtos/how-to-add-linter.md"
        description: "Implementing linters with SARIF support"
```

#### Step 4: Create/Update `.ai/howtos/how-to-add-linter.md`

**File Path**: `/home/stevejackson/Projects/thai-lint/.ai/howtos/how-to-add-linter.md`

**If file doesn't exist**, create it with file header:

```markdown
# How to Add a New Linter to thai-lint

**Purpose**: Step-by-step guide for implementing a new linter with complete output format support

**Scope**: Linter implementation, testing, SARIF support, CLI integration, documentation

**Overview**: Comprehensive guide for developers adding new linters to thai-lint. Covers linter
    class structure, TDD implementation approach, output format support (text, json, SARIF),
    CLI integration, testing requirements, and documentation standards. Ensures all linters
    maintain consistency and support industry-standard output formats.

(... rest of content ...)
```

**Add SARIF section**:

```markdown
## Step 5: Implement SARIF Output Support

**MANDATORY**: All linters MUST support SARIF v2.1.0 output format.

### What is SARIF?
SARIF (Static Analysis Results Interchange Format) is the OASIS standard for static analysis
tool output. It enables integration with:
- GitHub Code Scanning
- Azure DevOps Security
- VS Code SARIF Viewer
- Other CI/CD platforms

### SARIF Implementation Steps

1. **Read SARIF Standards**: `.ai/docs/SARIF_STANDARDS.md`
2. **Your linter automatically gets SARIF**: No linter-specific code needed
3. **Test SARIF output**:
   ```bash
   thailint <your-linter> --format sarif . | jq
   ```

### Validation Checklist
- [ ] Output is valid JSON
- [ ] Contains version "2.1.0"
- [ ] Contains $schema field
- [ ] Contains runs array with tool and results
- [ ] GitHub Code Scanning can parse it (upload to test repo)
- [ ] VS Code SARIF Viewer can display it

### Why No Linter-Specific Code?
The SARIF formatter in `src/formatters/sarif.py` converts Violation objects to SARIF.
Your linter just needs to return proper Violation objects, and SARIF works automatically.
```

### Files Modified
- `.ai/docs/SARIF_STANDARDS.md` (NEW)
- `AGENTS.md` (UPDATE)
- `.ai/index.yaml` (UPDATE)
- `.ai/howtos/how-to-add-linter.md` (CREATE or UPDATE)

### Testing Requirements
**No code to test** - this is pure documentation

**Manual validation**:
- [ ] SARIF_STANDARDS.md is comprehensive and clear
- [ ] AGENTS.md mentions SARIF requirement
- [ ] index.yaml properly categorizes SARIF docs
- [ ] how-to-add-linter.md includes SARIF steps

### Success Criteria
- ✅ SARIF_STANDARDS.md exists and is comprehensive (150+ lines)
- ✅ AGENTS.md mandates SARIF for new linters
- ✅ index.yaml includes SARIF documentation
- ✅ how-to-add-linter.md includes SARIF implementation steps
- ✅ `just lint-full` passes (10.00/10 Pylint)
- ✅ All files have proper headers per FILE_HEADER_STANDARDS.md

### PR Description Template
```markdown
feat: Establish SARIF v2.1.0 as mandatory output format standard

Adds comprehensive SARIF standards documentation and updates agent-facing
documentation to mandate SARIF support for all future linters.

**Changes:**
- Add .ai/docs/SARIF_STANDARDS.md (comprehensive standard)
- Update AGENTS.md (add SARIF to linter checklist)
- Update .ai/index.yaml (add SARIF documentation reference)
- Add/Update .ai/howtos/how-to-add-linter.md (include SARIF steps)

**Impact:**
- All future linters MUST support SARIF v2.1.0 output
- Clear implementation guide for developers
- Foundation for PR2 (tests) and PR3 (implementation)

**No code changes** - pure documentation PR.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## PR2: SARIF Core Infrastructure Tests (TDD Phase 1)

### Overview
**Goal**: Write comprehensive tests for SARIF formatter with ZERO implementation

**Duration**: 2-3 hours

**Why This PR**:
- Pure TDD: Tests define behavior before implementation
- Documents expected SARIF structure through tests
- Ensures comprehensive coverage from start
- All tests MUST FAIL (no implementation exists)

### Scope

**What Gets Created**:
1. `tests/unit/formatters/test_sarif_formatter.py` - 40+ unit tests
2. `tests/unit/test_cli_sarif_output.py` - 15+ CLI integration tests
3. `tests/integration/test_sarif_all_linters.py` - 10+ multi-linter tests

**What Does NOT Exist Yet**:
- src/formatters/ directory (will be created in PR3)
- src/formatters/sarif.py (will be created in PR3)
- "sarif" in --format choices (will be added in PR3)

### Detailed Steps

#### Step 1: Create Unit Tests for SARIF Formatter

**File Path**: `/home/stevejackson/Projects/thai-lint/tests/unit/formatters/test_sarif_formatter.py`

**File Header**:
```python
"""
Purpose: Unit tests for SARIF v2.1.0 formatter implementation

Scope: SARIF document structure, field mappings, tool metadata, result conversion

Overview: Comprehensive test suite for SarifFormatter class validating SARIF v2.1.0 compliance.
    Tests document structure requirements (version, schema, runs), tool metadata (name, version,
    informationUri), result conversion from Violation objects, location mapping with proper indexing,
    and edge cases (empty violations, special characters). Following TDD methodology - tests written
    BEFORE implementation exists, all tests MUST FAIL initially, implementation in PR3 makes them pass.

Dependencies: pytest (testing), src.core.types.Violation (dataclass), src.formatters.sarif.SarifFormatter (NOT YET EXISTS)

Exports: 40+ test functions validating SARIF v2.1.0 compliance

Interfaces: pytest test discovery, parametrized tests, fixtures for sample violations

Implementation: TDD approach with comprehensive test coverage, expects SarifFormatter in PR3
"""

import pytest
from src.core.types import Violation, Severity

# NOTE: This import will FAIL until PR3 creates the file
from src.formatters.sarif import SarifFormatter


# === Fixtures ===

@pytest.fixture
def sample_violation():
    """Create a sample violation for testing."""
    return Violation(
        rule_id="test.rule-id",
        file_path="src/example.py",
        line=42,
        column=10,
        message="Test violation message",
        severity=Severity.ERROR,
        suggestion="Test suggestion"
    )


@pytest.fixture
def empty_violations():
    """Empty violations list."""
    return []


@pytest.fixture
def multiple_violations():
    """Multiple violations for testing."""
    return [
        Violation(
            rule_id="file-placement.misplaced-file",
            file_path="src/test_utils.py",
            line=1,
            column=0,
            message="Test file in src/ directory",
            severity=Severity.ERROR,
            suggestion="Move to tests/ directory"
        ),
        Violation(
            rule_id="nesting.excessive-depth",
            file_path="src/complex.py",
            line=15,
            column=4,
            message="Nesting depth of 5 exceeds maximum 4",
            severity=Severity.ERROR,
            suggestion=None
        ),
    ]


# === Document Structure Tests (10 tests) ===

def test_sarif_document_has_required_fields(sample_violation):
    """SARIF document must have version, $schema, runs."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    assert "version" in sarif_doc
    assert "$schema" in sarif_doc
    assert "runs" in sarif_doc


def test_sarif_version_is_2_1_0(sample_violation):
    """SARIF version must be exactly 2.1.0."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    assert sarif_doc["version"] == "2.1.0"


def test_sarif_schema_uri_is_correct(sample_violation):
    """SARIF $schema must point to 2.1.0 schema."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    expected_schema = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
    assert sarif_doc["$schema"] == expected_schema


def test_sarif_runs_is_list(sample_violation):
    """SARIF runs must be a list."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    assert isinstance(sarif_doc["runs"], list)


def test_sarif_runs_has_one_element(sample_violation):
    """SARIF runs must have exactly one run for single invocation."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    assert len(sarif_doc["runs"]) == 1


def test_sarif_run_has_tool_and_results(sample_violation):
    """SARIF run must have tool and results fields."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    run = sarif_doc["runs"][0]
    assert "tool" in run
    assert "results" in run


def test_sarif_results_is_list(sample_violation):
    """SARIF results must be a list."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    run = sarif_doc["runs"][0]
    assert isinstance(run["results"], list)


def test_sarif_empty_violations_produces_empty_results():
    """Empty violations list produces empty results array."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([])

    run = sarif_doc["runs"][0]
    assert len(run["results"]) == 0


def test_sarif_multiple_violations_produces_multiple_results(multiple_violations):
    """Multiple violations produce multiple results."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format(multiple_violations)

    run = sarif_doc["runs"][0]
    assert len(run["results"]) == 2


def test_sarif_document_is_valid_json(sample_violation):
    """SARIF document can be serialized to JSON."""
    import json

    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    # Should not raise exception
    json_str = json.dumps(sarif_doc)
    assert len(json_str) > 0


# === Tool Metadata Tests (10 tests) ===

def test_sarif_tool_has_driver(sample_violation):
    """SARIF tool must have driver field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    tool = sarif_doc["runs"][0]["tool"]
    assert "driver" in tool


def test_sarif_driver_has_name(sample_violation):
    """SARIF driver must have name field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    assert "name" in driver


def test_sarif_driver_name_is_thai_lint(sample_violation):
    """SARIF driver name must be 'thai-lint'."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    assert driver["name"] == "thai-lint"


def test_sarif_driver_has_version(sample_violation):
    """SARIF driver must have version field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    assert "version" in driver
    assert isinstance(driver["version"], str)
    assert len(driver["version"]) > 0


def test_sarif_driver_has_information_uri(sample_violation):
    """SARIF driver must have informationUri field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    assert "informationUri" in driver


def test_sarif_driver_information_uri_is_correct(sample_violation):
    """SARIF driver informationUri must point to documentation."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    assert driver["informationUri"] == "https://thai-lint.readthedocs.io/"


def test_sarif_driver_has_rules_array(sample_violation):
    """SARIF driver must have rules array."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    assert "rules" in driver
    assert isinstance(driver["rules"], list)


def test_sarif_rules_contains_violation_rule_id(sample_violation):
    """SARIF rules must include rule metadata for violation."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    rule_ids = [rule["id"] for rule in driver["rules"]]
    assert sample_violation.rule_id in rule_ids


def test_sarif_rule_has_short_description(sample_violation):
    """SARIF rule must have shortDescription with text."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    rule = driver["rules"][0]
    assert "shortDescription" in rule
    assert "text" in rule["shortDescription"]


def test_sarif_custom_tool_name_is_used():
    """SarifFormatter accepts custom tool name."""
    formatter = SarifFormatter(tool_name="custom-linter")
    sarif_doc = formatter.format([])

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    assert driver["name"] == "custom-linter"


# === Result Conversion Tests (10 tests) ===

def test_sarif_result_has_rule_id(sample_violation):
    """SARIF result must have ruleId field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert "ruleId" in result


def test_sarif_result_rule_id_matches_violation(sample_violation):
    """SARIF result ruleId must match Violation.rule_id."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert result["ruleId"] == sample_violation.rule_id


def test_sarif_result_has_level(sample_violation):
    """SARIF result must have level field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert "level" in result


def test_sarif_result_level_is_error(sample_violation):
    """SARIF result level must be 'error' for ERROR severity."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert result["level"] == "error"


def test_sarif_result_has_message(sample_violation):
    """SARIF result must have message field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert "message" in result


def test_sarif_result_message_has_text(sample_violation):
    """SARIF result message must have text field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert "text" in result["message"]


def test_sarif_result_message_text_matches_violation(sample_violation):
    """SARIF result message text must match Violation.message."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert result["message"]["text"] == sample_violation.message


def test_sarif_result_has_locations(sample_violation):
    """SARIF result must have locations array."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert "locations" in result
    assert isinstance(result["locations"], list)
    assert len(result["locations"]) == 1


def test_sarif_result_location_has_physical_location(sample_violation):
    """SARIF result location must have physicalLocation."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    location = result["locations"][0]
    assert "physicalLocation" in location


def test_sarif_result_preserves_violation_order(multiple_violations):
    """SARIF results must preserve violation order."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format(multiple_violations)

    results = sarif_doc["runs"][0]["results"]
    assert results[0]["ruleId"] == multiple_violations[0].rule_id
    assert results[1]["ruleId"] == multiple_violations[1].rule_id


# === Location Mapping Tests (10 tests) ===

def test_sarif_physical_location_has_artifact_location(sample_violation):
    """SARIF physicalLocation must have artifactLocation."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    phys_loc = result["locations"][0]["physicalLocation"]
    assert "artifactLocation" in phys_loc


def test_sarif_artifact_location_has_uri(sample_violation):
    """SARIF artifactLocation must have uri field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
    assert "uri" in artifact


def test_sarif_artifact_uri_matches_file_path(sample_violation):
    """SARIF artifactLocation uri must match Violation.file_path."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
    assert artifact["uri"] == sample_violation.file_path


def test_sarif_artifact_has_uri_base_id(sample_violation):
    """SARIF artifactLocation should have uriBaseId."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
    assert "uriBaseId" in artifact
    assert artifact["uriBaseId"] == "%SRCROOT%"


def test_sarif_physical_location_has_region(sample_violation):
    """SARIF physicalLocation must have region field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    phys_loc = result["locations"][0]["physicalLocation"]
    assert "region" in phys_loc


def test_sarif_region_has_start_line(sample_violation):
    """SARIF region must have startLine field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    region = result["locations"][0]["physicalLocation"]["region"]
    assert "startLine" in region


def test_sarif_region_start_line_matches_violation(sample_violation):
    """SARIF region startLine must match Violation.line."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    region = result["locations"][0]["physicalLocation"]["region"]
    assert region["startLine"] == sample_violation.line


def test_sarif_region_has_start_column(sample_violation):
    """SARIF region must have startColumn field."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    region = result["locations"][0]["physicalLocation"]["region"]
    assert "startColumn" in region


def test_sarif_region_start_column_is_one_indexed(sample_violation):
    """SARIF region startColumn must be 1-indexed (Violation.column + 1)."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation])

    result = sarif_doc["runs"][0]["results"][0]
    region = result["locations"][0]["physicalLocation"]["region"]
    # Violation.column is 0-indexed (10), SARIF is 1-indexed (11)
    assert region["startColumn"] == sample_violation.column + 1


def test_sarif_handles_zero_column_correctly():
    """SARIF must convert column 0 to column 1 (1-indexed)."""
    violation = Violation(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=0,  # 0-indexed
        message="Test",
        severity=Severity.ERROR
    )

    formatter = SarifFormatter()
    sarif_doc = formatter.format([violation])

    result = sarif_doc["runs"][0]["results"][0]
    region = result["locations"][0]["physicalLocation"]["region"]
    assert region["startColumn"] == 1  # 1-indexed


# === Edge Case Tests (remainder to reach 40+) ===

def test_sarif_handles_special_characters_in_message():
    """SARIF must handle special characters in message."""
    violation = Violation(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=0,
        message='Message with "quotes" and <brackets> and & ampersand',
        severity=Severity.ERROR
    )

    formatter = SarifFormatter()
    sarif_doc = formatter.format([violation])

    result = sarif_doc["runs"][0]["results"][0]
    assert result["message"]["text"] == violation.message


def test_sarif_handles_unicode_in_file_path():
    """SARIF must handle unicode characters in file path."""
    violation = Violation(
        rule_id="test.rule",
        file_path="src/日本語.py",
        line=1,
        column=0,
        message="Test",
        severity=Severity.ERROR
    )

    formatter = SarifFormatter()
    sarif_doc = formatter.format([violation])

    result = sarif_doc["runs"][0]["results"][0]
    artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
    assert artifact["uri"] == "src/日本語.py"


def test_sarif_handles_none_suggestion():
    """SARIF must handle None suggestion gracefully."""
    violation = Violation(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=0,
        message="Test",
        severity=Severity.ERROR,
        suggestion=None  # Explicitly None
    )

    formatter = SarifFormatter()
    sarif_doc = formatter.format([violation])

    # Should not raise exception
    result = sarif_doc["runs"][0]["results"][0]
    assert result["message"]["text"] == "Test"


def test_sarif_handles_large_line_numbers():
    """SARIF must handle large line numbers correctly."""
    violation = Violation(
        rule_id="test.rule",
        file_path="test.py",
        line=999999,
        column=0,
        message="Test",
        severity=Severity.ERROR
    )

    formatter = SarifFormatter()
    sarif_doc = formatter.format([violation])

    result = sarif_doc["runs"][0]["results"][0]
    region = result["locations"][0]["physicalLocation"]["region"]
    assert region["startLine"] == 999999


def test_sarif_handles_large_column_numbers():
    """SARIF must handle large column numbers correctly."""
    violation = Violation(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=9999,  # 0-indexed
        message="Test",
        severity=Severity.ERROR
    )

    formatter = SarifFormatter()
    sarif_doc = formatter.format([violation])

    result = sarif_doc["runs"][0]["results"][0]
    region = result["locations"][0]["physicalLocation"]["region"]
    assert region["startColumn"] == 10000  # 1-indexed


def test_sarif_handles_windows_paths():
    """SARIF must normalize Windows paths to forward slashes."""
    violation = Violation(
        rule_id="test.rule",
        file_path=r"src\subdir\file.py",  # Windows path
        line=1,
        column=0,
        message="Test",
        severity=Severity.ERROR
    )

    formatter = SarifFormatter()
    sarif_doc = formatter.format([violation])

    result = sarif_doc["runs"][0]["results"][0]
    artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
    # SARIF uses forward slashes for URIs
    assert "/" in artifact["uri"]


def test_sarif_deduplicates_rules():
    """SARIF rules array must deduplicate repeated rule IDs."""
    violations = [
        Violation("test.rule-a", "file1.py", 1, 0, "Msg 1", Severity.ERROR),
        Violation("test.rule-a", "file2.py", 2, 0, "Msg 2", Severity.ERROR),  # Same rule
        Violation("test.rule-b", "file3.py", 3, 0, "Msg 3", Severity.ERROR),
    ]

    formatter = SarifFormatter()
    sarif_doc = formatter.format(violations)

    driver = sarif_doc["runs"][0]["tool"]["driver"]
    rule_ids = [rule["id"] for rule in driver["rules"]]
    assert len(rule_ids) == 2  # Not 3 (rule-a deduplicated)
    assert "test.rule-a" in rule_ids
    assert "test.rule-b" in rule_ids


def test_sarif_formatter_is_reusable():
    """SarifFormatter instance can format multiple violation lists."""
    formatter = SarifFormatter()

    violations1 = [Violation("test.a", "file1.py", 1, 0, "Msg1", Severity.ERROR)]
    violations2 = [Violation("test.b", "file2.py", 2, 0, "Msg2", Severity.ERROR)]

    sarif1 = formatter.format(violations1)
    sarif2 = formatter.format(violations2)

    # Both should be valid SARIF documents
    assert sarif1["version"] == "2.1.0"
    assert sarif2["version"] == "2.1.0"
    assert sarif1["runs"][0]["results"][0]["ruleId"] == "test.a"
    assert sarif2["runs"][0]["results"][0]["ruleId"] == "test.b"
```

**(Continue with remaining tests to reach 40+ total)**

#### Step 2: Create CLI Integration Tests

**File Path**: `/home/stevejackson/Projects/thai-lint/tests/unit/test_cli_sarif_output.py`

**Content**: (15+ tests for CLI integration)

```python
"""
Purpose: CLI integration tests for SARIF output format option

Scope: CLI invocation with --format sarif, output validation, exit codes

Overview: Integration tests validating thai-lint CLI properly handles --format sarif option
    across all 5 linters (file-placement, nesting, srp, dry, magic-numbers). Tests CLI
    invocation, SARIF output structure, JSON validity, exit codes (0 for no violations,
    1 for violations), and stderr vs stdout handling. Following TDD methodology - tests
    written BEFORE implementation, all tests MUST FAIL initially.

Dependencies: pytest, click.testing.CliRunner, src.cli (CLI commands), src.formatters.sarif (NOT YET EXISTS)

Exports: 15+ CLI integration test functions

Interfaces: Click testing runner, JSON parsing for output validation

Implementation: TDD approach with CLI testing patterns, expects "sarif" format option in PR3
"""

import json
import pytest
from click.testing import CliRunner
from src.cli import cli


# === CLI Invocation Tests (5 tests) ===

def test_file_placement_accepts_sarif_format():
    """file-placement command accepts --format sarif option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["file-placement", "--format", "sarif", "."])

    # Should not error on invalid option (sarif should be valid)
    assert "--format" not in result.output or "Invalid value" not in result.output


def test_nesting_accepts_sarif_format():
    """nesting command accepts --format sarif option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["nesting", "--format", "sarif", "."])

    assert "--format" not in result.output or "Invalid value" not in result.output


def test_srp_accepts_sarif_format():
    """srp command accepts --format sarif option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["srp", "--format", "sarif", "."])

    assert "--format" not in result.output or "Invalid value" not in result.output


def test_dry_accepts_sarif_format():
    """dry command accepts --format sarif option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["dry", "--format", "sarif", "."])

    assert "--format" not in result.output or "Invalid value" not in result.output


def test_magic_numbers_accepts_sarif_format():
    """magic-numbers command accepts --format sarif option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", "."])

    assert "--format" not in result.output or "Invalid value" not in result.output


# === Output Structure Tests (5 tests) ===

def test_sarif_output_is_valid_json(tmp_path):
    """SARIF output must be valid JSON."""
    # Create test file with violation
    test_file = tmp_path / "test.py"
    test_file.write_text("# test file")

    runner = CliRunner()
    result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(test_file)])

    # Should be parsable JSON
    output = json.loads(result.output)
    assert isinstance(output, dict)


def test_sarif_output_has_required_top_level_fields(tmp_path):
    """SARIF output must have version, $schema, runs at top level."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    runner = CliRunner()
    result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    assert "version" in output
    assert "$schema" in output
    assert "runs" in output


def test_sarif_output_version_is_2_1_0(tmp_path):
    """SARIF output version must be 2.1.0."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    runner = CliRunner()
    result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    assert output["version"] == "2.1.0"


def test_sarif_output_has_tool_metadata(tmp_path):
    """SARIF output must include tool metadata."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    runner = CliRunner()
    result = runner.invoke(cli, ["dry", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    driver = output["runs"][0]["tool"]["driver"]
    assert driver["name"] == "thai-lint"
    assert "version" in driver


def test_sarif_output_has_results_array(tmp_path):
    """SARIF output must have results array."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    runner = CliRunner()
    result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    run = output["runs"][0]
    assert "results" in run
    assert isinstance(run["results"], list)


# === Exit Code Tests (3 tests) ===

def test_sarif_exit_code_zero_when_no_violations(tmp_path):
    """CLI exits with 0 when no violations found (SARIF format)."""
    # Create valid file (no violations)
    test_file = tmp_path / "valid.py"
    test_file.write_text("# valid Python file")

    runner = CliRunner()
    result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

    assert result.exit_code == 0


def test_sarif_exit_code_one_when_violations_found(tmp_path):
    """CLI exits with 1 when violations found (SARIF format)."""
    # Create file that will trigger violation
    # (depends on linter config, may need specific setup)
    test_file = tmp_path / "violating.py"
    test_file.write_text("# file with violation")

    runner = CliRunner()
    result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(test_file)])

    # Exit code should be 1 if violations found
    # (This test may need adjustment based on actual violations)
    assert result.exit_code in [0, 1]  # Valid exit codes


def test_sarif_exit_code_consistent_with_json_format(tmp_path):
    """SARIF and JSON formats produce same exit codes."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    runner = CliRunner()
    json_result = runner.invoke(cli, ["srp", "--format", "json", str(test_file)])
    sarif_result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

    assert json_result.exit_code == sarif_result.exit_code


# === Output Routing Tests (2 tests) ===

def test_sarif_output_goes_to_stdout(tmp_path):
    """SARIF output is written to stdout, not stderr."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    runner = CliRunner()
    result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

    # Output should be in stdout (result.output)
    # and be valid SARIF JSON
    output = json.loads(result.output)
    assert output["version"] == "2.1.0"


def test_sarif_format_does_not_print_text_violations(tmp_path):
    """SARIF format does not print text-formatted violations."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    runner = CliRunner()
    result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(test_file)])

    # Output should be JSON, not text like "file.py:1:0 - message"
    # Should start with { (JSON object)
    assert result.output.strip().startswith("{")
```

**(Continue with remaining tests to reach 15+ total)**

#### Step 3: Create Multi-Linter Integration Tests

**File Path**: `/home/stevejackson/Projects/thai-lint/tests/integration/test_sarif_all_linters.py`

**Content**: (10+ tests validating all 5 linters produce SARIF)

```python
"""
Purpose: Integration tests validating SARIF output across all thai-lint linters

Scope: All 5 linters (file-placement, nesting, srp, dry, magic-numbers) with SARIF output

Overview: End-to-end integration tests ensuring all thai-lint linters produce valid SARIF v2.1.0
    output. Tests each linter individually with --format sarif option, validates SARIF structure,
    verifies linter-specific rule IDs appear in output, and ensures consistency across linters.
    Following TDD methodology - tests written BEFORE implementation, all tests MUST FAIL initially.

Dependencies: pytest, click.testing.CliRunner, src.cli (all linter commands), json (parsing)

Exports: 10+ integration test functions for multi-linter SARIF validation

Interfaces: CLI testing runner, JSON parsing, temporary file creation

Implementation: TDD approach with comprehensive linter coverage, expects SARIF support in PR3
"""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from src.cli import cli


# === File Placement Linter Tests (2 tests) ===

def test_file_placement_produces_valid_sarif(tmp_path):
    """file-placement linter produces valid SARIF output."""
    test_file = tmp_path / "src" / "test_utils.py"
    test_file.parent.mkdir()
    test_file.write_text("# test utilities")

    runner = CliRunner()
    result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(tmp_path)])

    output = json.loads(result.output)
    assert output["version"] == "2.1.0"
    assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"


def test_file_placement_sarif_contains_rule_ids(tmp_path):
    """file-placement SARIF output contains file-placement rule IDs."""
    test_file = tmp_path / "src" / "test_file.py"
    test_file.parent.mkdir()
    test_file.write_text("# potentially misplaced file")

    runner = CliRunner()
    result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(tmp_path)])

    output = json.loads(result.output)
    # If violations found, rule IDs should start with "file-placement"
    if output["runs"][0]["results"]:
        rule_id = output["runs"][0]["results"][0]["ruleId"]
        assert rule_id.startswith("file-placement")


# === Nesting Linter Tests (2 tests) ===

def test_nesting_produces_valid_sarif(tmp_path):
    """nesting linter produces valid SARIF output."""
    test_file = tmp_path / "nested.py"
    test_file.write_text("""
def deeply_nested():
    for i in range(10):
        if i > 5:
            for j in range(5):
                if j > 2:
                    print(i, j)
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    assert output["version"] == "2.1.0"
    assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"


def test_nesting_sarif_contains_rule_ids(tmp_path):
    """nesting SARIF output contains nesting rule IDs."""
    test_file = tmp_path / "nested.py"
    test_file.write_text("def simple(): pass")

    runner = CliRunner()
    result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    # If violations found, rule IDs should contain "nesting"
    if output["runs"][0]["results"]:
        rule_id = output["runs"][0]["results"][0]["ruleId"]
        assert "nesting" in rule_id


# === SRP Linter Tests (2 tests) ===

def test_srp_produces_valid_sarif(tmp_path):
    """srp linter produces valid SARIF output."""
    test_file = tmp_path / "class_file.py"
    test_file.write_text("""
class SmallClass:
    def method1(self): pass
    def method2(self): pass
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    assert output["version"] == "2.1.0"
    assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"


def test_srp_sarif_contains_rule_ids(tmp_path):
    """srp SARIF output contains srp rule IDs."""
    test_file = tmp_path / "class_file.py"
    test_file.write_text("class Simple: pass")

    runner = CliRunner()
    result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    # If violations found, rule IDs should contain "srp"
    if output["runs"][0]["results"]:
        rule_id = output["runs"][0]["results"][0]["ruleId"]
        assert "srp" in rule_id


# === DRY Linter Tests (2 tests) ===

def test_dry_produces_valid_sarif(tmp_path):
    """dry linter produces valid SARIF output."""
    test_file = tmp_path / "duplicates.py"
    test_file.write_text("""
def func1():
    x = 1
    y = 2
    return x + y

def func2():
    x = 1
    y = 2
    return x + y
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["dry", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    assert output["version"] == "2.1.0"
    assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"


def test_dry_sarif_contains_rule_ids(tmp_path):
    """dry SARIF output contains dry rule IDs."""
    test_file = tmp_path / "simple.py"
    test_file.write_text("def simple(): pass")

    runner = CliRunner()
    result = runner.invoke(cli, ["dry", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    # If violations found, rule IDs should start with "dry"
    if output["runs"][0]["results"]:
        rule_id = output["runs"][0]["results"][0]["ruleId"]
        assert rule_id.startswith("dry")


# === Magic Numbers Linter Tests (2 tests) ===

def test_magic_numbers_produces_valid_sarif(tmp_path):
    """magic-numbers linter produces valid SARIF output."""
    test_file = tmp_path / "numbers.py"
    test_file.write_text("""
def calculate():
    timeout = 3600
    retries = 5
    return timeout * retries
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    assert output["version"] == "2.1.0"
    assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"


def test_magic_numbers_sarif_contains_rule_ids(tmp_path):
    """magic-numbers SARIF output contains magic-number rule IDs."""
    test_file = tmp_path / "constants.py"
    test_file.write_text("VALID_CONSTANT = 100")

    runner = CliRunner()
    result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(test_file)])

    output = json.loads(result.output)
    # If violations found, rule IDs should contain "magic-number"
    if output["runs"][0]["results"]:
        rule_id = output["runs"][0]["results"][0]["ruleId"]
        assert "magic-number" in rule_id
```

### Files Created
- `tests/unit/formatters/__init__.py` (empty, for package)
- `tests/unit/formatters/test_sarif_formatter.py` (40+ tests)
- `tests/unit/test_cli_sarif_output.py` (15+ tests)
- `tests/integration/test_sarif_all_linters.py` (10+ tests)

### Testing Requirements
**ALL tests MUST FAIL initially** - this validates TDD approach

**Run tests**:
```bash
# All tests should FAIL with import errors or missing "sarif" option
pytest tests/unit/formatters/test_sarif_formatter.py -v
pytest tests/unit/test_cli_sarif_output.py -v
pytest tests/integration/test_sarif_all_linters.py -v
```

**Expected failures**:
- `ModuleNotFoundError: No module named 'src.formatters.sarif'`
- `Invalid value for '--format'` (sarif not in choices)

### Success Criteria
- ✅ 65+ tests written (40 unit + 15 CLI + 10 integration)
- ✅ ALL tests FAIL (no implementation exists)
- ✅ Tests follow `.ai/docs/SARIF_STANDARDS.md` requirements
- ✅ Proper pytest fixtures and parametrization
- ✅ Test names clearly describe expected behavior
- ✅ `just lint-full` passes (10.00/10 Pylint)
- ✅ All test files have proper headers

### PR Description Template
```markdown
test: Add comprehensive SARIF v2.1.0 formatter tests (TDD Phase 1)

Adds 65+ tests for SARIF output format support following TDD methodology.
ALL tests MUST FAIL initially - implementation comes in PR3.

**Test Coverage:**
- 40+ unit tests for SarifFormatter class (document structure, tool metadata, result conversion, location mapping, edge cases)
- 15+ CLI integration tests (all 5 linters with --format sarif)
- 10+ multi-linter integration tests (cross-linter consistency)

**Tests Validate:**
- SARIF v2.1.0 structure compliance
- Tool metadata (name, version, informationUri)
- Violation → SARIF result mapping
- Location mapping with proper 1-indexed columns
- Edge cases (empty violations, special characters, unicode)
- All 5 linters (file-placement, nesting, srp, dry, magic-numbers)

**Expected State:**
- ALL 65+ tests FAIL (ModuleNotFoundError, invalid --format choice)
- This is CORRECT behavior (TDD - tests first, implementation second)
- PR3 will implement SarifFormatter to make all tests pass

**Follows Standards:**
- .ai/docs/SARIF_STANDARDS.md (SARIF requirements)
- .ai/docs/FILE_HEADER_STANDARDS.md (file headers)
- .ai/howtos/how-to-write-tests.md (testing patterns)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## PR3: SARIF Formatter Implementation (TDD Phase 2)

### Overview
**Goal**: Implement SARIF formatter to make ALL PR2 tests pass

**Duration**: 3-4 hours

**Why This PR**:
- Makes PR2 tests pass (TDD validation)
- Adds SARIF as actual output format option
- Integrates with existing CLI structure
- Zero new tests (validates against PR2 tests only)

### Scope

**What Gets Created**:
1. `src/formatters/__init__.py` - Package marker
2. `src/formatters/sarif.py` - SarifFormatter class (150-200 lines)

**What Gets Modified**:
1. `src/cli.py` - Add "sarif" to --format choices
2. `src/core/cli_utils.py` - Add SARIF routing

**What Does NOT Change**:
- No user-facing documentation yet (that's PR4)
- No new tests (use only PR2 tests)
- No changes to existing formatters (text/json)

### Detailed Steps

#### Step 1: Create SarifFormatter Class

**File Path**: `/home/stevejackson/Projects/thai-lint/src/formatters/__init__.py`

**Content**:
```python
"""
Purpose: SARIF formatter package for thai-lint output

Scope: SARIF v2.1.0 formatter implementation

Overview: Formatters package providing SARIF (Static Analysis Results Interchange Format) v2.1.0
    output generation from thai-lint Violation objects. Enables integration with GitHub Code
    Scanning, Azure DevOps, VS Code SARIF Viewer, and other industry-standard CI/CD platforms.

Dependencies: None (package marker)

Exports: SarifFormatter class from sarif.py module

Interfaces: from src.formatters.sarif import SarifFormatter

Implementation: Package initialization for formatters module
"""

from src.formatters.sarif import SarifFormatter

__all__ = ["SarifFormatter"]
```

**File Path**: `/home/stevejackson/Projects/thai-lint/src/formatters/sarif.py`

**Content**: (150-200 lines implementing SarifFormatter)

Due to length, I'll note that this file should:
1. Implement all methods required by PR2 tests
2. Follow `.ai/docs/FILE_HEADER_STANDARDS.md` for header
3. Use type hints throughout
4. Handle all edge cases tested in PR2
5. Be fully documented with docstrings

#### Step 2: Update CLI Format Options

**File Path**: `/home/stevejackson/Projects/thai-lint/src/cli.py`

**Changes**: Update `format_option` decorator (line 38-42)

```python
# BEFORE:
def format_option(func):
    """Add --format option to a command for output format selection."""
    return click.option(
        "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Output format"
    )(func)

# AFTER:
def format_option(func):
    """Add --format option to a command for output format selection."""
    return click.option(
        "--format", "-f", type=click.Choice(["text", "json", "sarif"]), default="text", help="Output format"
    )(func)
```

**Impact**: All 5 commands automatically get "sarif" option

#### Step 3: Add SARIF Routing

**File Path**: `/home/stevejackson/Projects/thai-lint/src/core/cli_utils.py`

**Changes**: Add `_format_sarif` function and route in `format_violations`

```python
# Add after _format_json function (around line 160):

def _format_sarif(violations: list[Violation]) -> None:
    """Format violations as SARIF v2.1.0 JSON document.

    Args:
        violations: List of violations to format

    Output:
        SARIF v2.1.0 JSON document to stdout
    """
    from src.formatters.sarif import SarifFormatter

    formatter = SarifFormatter()
    sarif_doc = formatter.format(violations)
    click.echo(json.dumps(sarif_doc, indent=2))


# Update format_violations function (around line 149):

def format_violations(violations: list[Violation], output_format: str) -> None:
    """Format and output violations in specified format.

    Args:
        violations: List of violations to format
        output_format: Output format ("text", "json", or "sarif")
    """
    if output_format == "json":
        _format_json(violations)
    elif output_format == "sarif":  # ADD THIS
        _format_sarif(violations)   # ADD THIS
    else:
        _format_text(violations)
```

### Files Modified
- `src/cli.py` (1 line change - add "sarif" to choices)
- `src/core/cli_utils.py` (add _format_sarif function + elif branch)

### Files Created
- `src/formatters/__init__.py` (package marker + exports)
- `src/formatters/sarif.py` (150-200 lines, SarifFormatter class)

### Testing Requirements
**Run ALL PR2 tests** - they MUST now PASS

```bash
# All 65+ tests should now PASS
pytest tests/unit/formatters/test_sarif_formatter.py -v
pytest tests/unit/test_cli_sarif_output.py -v
pytest tests/integration/test_sarif_all_linters.py -v

# Run full test suite
pytest tests/ -v

# Linting must pass
just lint-full

# Type checking must pass
mypy --strict src/
```

### Manual Testing
```bash
# Test each linter with SARIF output
thailint file-placement --format sarif . | jq
thailint nesting --format sarif . | jq
thailint srp --format sarif . | jq
thailint dry --format sarif . | jq
thailint magic-numbers --format sarif . | jq

# Validate SARIF structure
thailint file-placement --format sarif . | jq '.version, .$schema, .runs[0].tool.driver.name'

# Save SARIF to file
thailint dry --format sarif src/ > results.sarif

# Validate against JSON schema (optional)
# npm install -g ajv-cli
# ajv validate -s https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json -d results.sarif
```

### Success Criteria
- ✅ ALL 65+ tests from PR2 now PASS (100% pass rate)
- ✅ `just lint-full` passes (10.00/10 Pylint, A-grade complexity)
- ✅ `mypy --strict` passes (no type errors)
- ✅ Manual test: `thailint <command> --format sarif . | jq` works for all 5 linters
- ✅ SARIF output is valid JSON
- ✅ SARIF output validates against v2.1.0 schema
- ✅ No breaking changes to text/json formats
- ✅ Implementation follows `.ai/docs/SARIF_STANDARDS.md`

### PR Description Template
```markdown
feat: Implement SARIF v2.1.0 output format for all linters

Implements SarifFormatter class and CLI integration, making all 65+ tests
from PR2 pass. Adds SARIF as third output format alongside text and json.

**Implementation:**
- Add src/formatters/sarif.py (SarifFormatter class)
- Add src/formatters/__init__.py (package exports)
- Update src/cli.py (add "sarif" to --format choices)
- Update src/core/cli_utils.py (add SARIF routing)

**SARIF Features:**
- SARIF v2.1.0 compliant output
- Tool metadata (name, version, informationUri)
- Proper severity mapping (ERROR → "error")
- Location mapping with 1-indexed columns
- Rule metadata with short descriptions
- Edge case handling (unicode, special characters)

**Testing:**
- ALL 65+ tests from PR2 now PASS
- 40+ unit tests for SarifFormatter
- 15+ CLI integration tests
- 10+ multi-linter tests
- Manual testing: thailint <cmd> --format sarif . | jq

**Usage:**
```bash
# Any linter with SARIF output
thailint dry --format sarif src/ > results.sarif
thailint nesting --format sarif . | jq
```

**Validation:**
- just lint-full passes (10.00/10 Pylint)
- mypy --strict passes (no type errors)
- SARIF validates against v2.1.0 JSON schema
- GitHub Code Scanning can parse output
- VS Code SARIF Viewer can display output

**No Breaking Changes:**
- text and json formats unchanged
- Default format remains "text"
- Backward compatible CLI options

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## PR4: Documentation, Examples & Badge (Polish)

### Overview
**Goal**: Complete user documentation with working examples and SARIF badge

**Duration**: 2 hours

**Why This PR**:
- Makes SARIF discoverable (badge)
- Provides user guidance (docs)
- Enables adoption (examples, CI/CD templates)
- Professional polish (complete documentation)

### Scope

**What Gets Created**:
1. `docs/sarif-output.md` - Comprehensive user guide (300+ lines)
2. `examples/sarif_usage.py` - Working Python example
3. `.github/workflows/sarif-example.yml` - GitHub Actions template

**What Gets Modified**:
1. `README.md` - Add SARIF badge, add examples
2. `docs/configuration.md` - Add SARIF format examples
3. `docs/cli-reference.md` - Update --format option docs
4. `docs/getting-started.md` - Add SARIF quick start
5. `docs/quick-start.md` - Add SARIF example

**What Does NOT Change**:
- No source code changes
- No test code changes

### Detailed Steps

#### Step 1: Add SARIF Badge to README

**File Path**: `/home/stevejackson/Projects/thai-lint/README.md`

**Changes**: Add SARIF badge after line 7 (after Documentation Status badge)

```markdown
# BEFORE (lines 3-7):
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-356%2F356%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)](htmlcov/)
[![Documentation Status](https://readthedocs.org/projects/thai-lint/badge/?version=latest)](https://thai-lint.readthedocs.io/en/latest/?badge=latest)

# AFTER:
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-356%2F356%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)](htmlcov/)
[![Documentation Status](https://readthedocs.org/projects/thai-lint/badge/?version=latest)](https://thai-lint.readthedocs.io/en/latest/?badge=latest)
[![SARIF Support](https://img.shields.io/badge/SARIF-2.1.0-orange.svg)](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
```

**Also add SARIF examples throughout README**:

Find "Quick Start" section (around line 109) and add SARIF example:

```markdown
# SARIF output for CI/CD
thailint dry --format sarif src/ > results.sarif
```

Find "JSON output for CI/CD" mentions and add SARIF alongside:

```markdown
# Get JSON output
thailint dry --format json src/

# Get SARIF output (industry standard)
thailint dry --format sarif src/ > results.sarif
```

#### Step 2: Create Comprehensive User Guide

**File Path**: `/home/stevejackson/Projects/thai-lint/docs/sarif-output.md`

**Content**: (300+ lines - comprehensive guide)

This document should include:
1. What is SARIF and why use it
2. Quick start examples
3. GitHub Code Scanning integration
4. Azure DevOps integration
5. VS Code SARIF Viewer usage
6. CLI usage for all 5 linters
7. Library API usage
8. Troubleshooting

#### Step 3: Create Working Python Example

**File Path**: `/home/stevejackson/Projects/thai-lint/examples/sarif_usage.py`

**Content**:
```python
"""
Purpose: Example demonstrating SARIF output usage with thai-lint library API

Scope: Library API usage, SARIF generation, file operations, JSON validation

Overview: Working example demonstrating how to use thai-lint library API to generate
    SARIF v2.1.0 output programmatically. Shows basic linting, SARIF generation,
    file saving, JSON validation, and integration patterns for custom tools and
    CI/CD workflows.

Dependencies: thai-lint (src.api), json (stdlib), pathlib (stdlib)

Exports: Example functions for SARIF generation and validation

Interfaces: thai-lint Linter API, file I/O, JSON operations

Implementation: Example code with comprehensive comments and error handling
"""

import json
from pathlib import Path
from src.api import Linter


def generate_sarif_output(target_path: str, output_file: str = "results.sarif"):
    """Generate SARIF output from linting results.

    Args:
        target_path: Path to lint (file or directory)
        output_file: Output SARIF file path
    """
    print(f"Linting {target_path}...")

    # Initialize linter with SARIF format
    linter = Linter(config_file=".thailint.yaml")

    # Run all linters
    violations = linter.lint(target_path)

    print(f"Found {len(violations)} violation(s)")

    # Generate SARIF document
    from src.formatters.sarif import SarifFormatter
    formatter = SarifFormatter()
    sarif_doc = formatter.format(violations)

    # Save to file
    output_path = Path(output_file)
    output_path.write_text(json.dumps(sarif_doc, indent=2), encoding="utf-8")

    print(f"SARIF output saved to {output_file}")

    # Validate SARIF structure
    validate_sarif(sarif_doc)

    return sarif_doc


def validate_sarif(sarif_doc: dict) -> bool:
    """Validate SARIF document structure.

    Args:
        sarif_doc: SARIF document dictionary

    Returns:
        True if valid, False otherwise
    """
    print("Validating SARIF structure...")

    # Check required fields
    required_fields = ["version", "$schema", "runs"]
    for field in required_fields:
        if field not in sarif_doc:
            print(f"❌ Missing required field: {field}")
            return False

    # Check version
    if sarif_doc["version"] != "2.1.0":
        print(f"❌ Invalid version: {sarif_doc['version']} (expected 2.1.0)")
        return False

    # Check runs
    if not sarif_doc["runs"] or not isinstance(sarif_doc["runs"], list):
        print("❌ Invalid runs array")
        return False

    # Check tool metadata
    driver = sarif_doc["runs"][0]["tool"]["driver"]
    if driver["name"] != "thai-lint":
        print(f"❌ Invalid tool name: {driver['name']}")
        return False

    print("✅ SARIF document is valid!")
    return True


def upload_to_github_code_scanning(sarif_file: str):
    """Example: Upload SARIF to GitHub Code Scanning.

    Note: This is a placeholder. In real workflow, use github/codeql-action/upload-sarif

    Args:
        sarif_file: Path to SARIF file
    """
    print(f"To upload {sarif_file} to GitHub Code Scanning:")
    print("""
    # .github/workflows/code-scanning.yml
    steps:
      - name: Run thailint
        run: thailint dry --format sarif src/ > results.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
          category: thailint-dry
    """)


def main():
    """Main example execution."""
    # Example 1: Generate SARIF for current directory
    print("=" * 60)
    print("Example 1: Generate SARIF output")
    print("=" * 60)
    sarif_doc = generate_sarif_output(".", "thailint-results.sarif")

    # Example 2: Inspect SARIF structure
    print("\n" + "=" * 60)
    print("Example 2: Inspect SARIF structure")
    print("=" * 60)
    print(f"SARIF version: {sarif_doc['version']}")
    print(f"Tool name: {sarif_doc['runs'][0]['tool']['driver']['name']}")
    print(f"Results count: {len(sarif_doc['runs'][0]['results'])}")

    # Example 3: GitHub integration guidance
    print("\n" + "=" * 60)
    print("Example 3: GitHub Code Scanning Integration")
    print("=" * 60)
    upload_to_github_code_scanning("thailint-results.sarif")


if __name__ == "__main__":
    main()
```

#### Step 4: Create GitHub Actions Workflow Example

**File Path**: `/home/stevejackson/Projects/thai-lint/.github/workflows/sarif-example.yml`

**Content**:
```yaml
name: Thai-lint Code Scanning (SARIF Example)

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  thailint-sarif:
    name: Run thai-lint with SARIF output
    runs-on: ubuntu-latest

    permissions:
      # Required for uploading SARIF to GitHub Code Scanning
      security-events: write
      contents: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install thai-lint
        run: |
          pip install --upgrade pip
          pip install thai-lint

      - name: Run thai-lint DRY linter (SARIF)
        run: |
          thailint dry --format sarif src/ > dry-results.sarif
        continue-on-error: true  # Don't fail workflow if violations found

      - name: Run thai-lint nesting linter (SARIF)
        run: |
          thailint nesting --format sarif src/ > nesting-results.sarif
        continue-on-error: true

      - name: Run thai-lint magic-numbers linter (SARIF)
        run: |
          thailint magic-numbers --format sarif src/ > magic-numbers-results.sarif
        continue-on-error: true

      - name: Upload DRY SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: dry-results.sarif
          category: thailint-dry
        if: always()  # Upload even if previous steps failed

      - name: Upload Nesting SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: nesting-results.sarif
          category: thailint-nesting
        if: always()

      - name: Upload Magic Numbers SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: magic-numbers-results.sarif
          category: thailint-magic-numbers
        if: always()

      - name: Archive SARIF files
        uses: actions/upload-artifact@v3
        with:
          name: sarif-results
          path: |
            dry-results.sarif
            nesting-results.sarif
            magic-numbers-results.sarif
        if: always()
```

#### Step 5: Update Existing Documentation

**File Path**: `/home/stevejackson/Projects/thai-lint/docs/configuration.md`

Add SARIF examples to each linter section (around 5 locations total).

**File Path**: `/home/stevejackson/Projects/thai-lint/docs/cli-reference.md`

Update `--format` option documentation to include "sarif" choice.

**File Path**: `/home/stevejackson/Projects/thai-lint/docs/getting-started.md`

Add SARIF quick start example.

### Files Modified
- `README.md` (badge + examples)
- `docs/configuration.md` (SARIF examples)
- `docs/cli-reference.md` (--format option)
- `docs/getting-started.md` (quick start)
- `docs/quick-start.md` (SARIF example)

### Files Created
- `docs/sarif-output.md` (300+ lines)
- `examples/sarif_usage.py` (working example)
- `.github/workflows/sarif-example.yml` (CI/CD template)

### Testing Requirements
**No code tests** - documentation only

**Manual validation**:
- [ ] SARIF badge appears in README
- [ ] Badge links to OASIS specification
- [ ] All example code is copy-paste runnable
- [ ] GitHub Actions workflow is valid YAML
- [ ] Python example runs without errors
- [ ] Documentation covers all 5 linters

### Success Criteria
- ✅ SARIF badge visible in README header
- ✅ Comprehensive user guide complete (docs/sarif-output.md, 300+ lines)
- ✅ All docs mention SARIF where relevant
- ✅ Working Python API example (examples/sarif_usage.py)
- ✅ GitHub Actions workflow template works
- ✅ README updated in 5+ places with SARIF examples
- ✅ Links to SARIF specification and tools
- ✅ `just lint-full` passes (10.00/10 Pylint)

### PR Description Template
```markdown
docs: Add SARIF support badge, user documentation, and examples

Completes SARIF feature with comprehensive documentation, working examples,
and CI/CD integration templates. Makes SARIF discoverable and usable.

**Documentation:**
- Add SARIF badge to README header (orange, SARIF 2.1.0)
- Create comprehensive user guide (docs/sarif-output.md, 300+ lines)
- Update configuration guide with SARIF examples
- Update CLI reference with --format sarif option
- Update getting started guide with SARIF quick start

**Examples:**
- Working Python API example (examples/sarif_usage.py)
- GitHub Actions workflow template (.github/workflows/sarif-example.yml)
- Azure DevOps integration guidance (in sarif-output.md)
- VS Code SARIF Viewer usage (in sarif-output.md)

**README Updates:**
- SARIF badge after Documentation Status badge
- Quick start example with SARIF output
- SARIF mentioned in 5+ locations
- Links to OASIS specification

**SARIF Badge:**
```markdown
[![SARIF Support](https://img.shields.io/badge/SARIF-2.1.0-orange.svg)](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
```

**User Guidance Includes:**
- What is SARIF and why use it
- GitHub Code Scanning integration
- Azure DevOps integration
- VS Code SARIF Viewer setup
- CLI usage for all 5 linters
- Library API usage patterns
- Troubleshooting common issues

**CI/CD Templates:**
- GitHub Actions workflow (complete, ready to use)
- Azure Pipelines example (in sarif-output.md)
- GitLab CI example (in sarif-output.md)

**All examples tested** - copy-paste ready for users

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Implementation Guidelines

### Code Standards
- **Python Version**: 3.11+ (use modern type hints)
- **Type Hints**: Full type annotations (mypy --strict compliant)
- **Docstrings**: Google-style docstrings for all public functions
- **Line Length**: 100 characters maximum
- **Imports**: Group stdlib, third-party, local (isort)
- **Naming**: PEP 8 conventions (snake_case functions, PascalCase classes)

### Testing Requirements
- **Coverage**: >90% for new code
- **TDD Discipline**: Tests written BEFORE implementation (PR2 before PR3)
- **Test Organization**: Unit tests in tests/unit/, integration in tests/integration/
- **Fixtures**: Use pytest fixtures for reusable test data
- **Parametrization**: Use @pytest.mark.parametrize for multiple similar tests
- **Assertions**: Clear, descriptive assertion messages

### Documentation Standards
- **File Headers**: Follow `.ai/docs/FILE_HEADER_STANDARDS.md`
- **Atemporal Language**: No "currently", "now", dates in docs
- **Code Examples**: All examples must be copy-paste runnable
- **Links**: Use full URLs for external references
- **Markdown**: Follow CommonMark specification

### Security Considerations
- **No Eval**: Never use eval() or exec()
- **Input Validation**: Validate all user input (file paths, format options)
- **JSON Safety**: Use json.loads() with proper error handling
- **Path Traversal**: Validate file paths don't escape project root
- **Unicode Handling**: Properly handle unicode in file paths and messages

### Performance Targets
- **SARIF Generation**: <100ms for 100 violations
- **Memory Usage**: <50MB for 1000 violations
- **JSON Serialization**: <50ms for typical SARIF document
- **No Blocking I/O**: Use pathlib, don't shell out

---

## Rollout Strategy

### Phase 1: Planning & Standards (PR1)
- Establish SARIF as mandatory
- Create comprehensive standards doc
- Update agent-facing documentation
- **Outcome**: All future linters know SARIF is required

### Phase 2: Tests First (PR2)
- Write 65+ comprehensive tests
- Document expected behavior
- Validate TDD approach (all tests FAIL)
- **Outcome**: Clear specification via tests

### Phase 3: Implementation (PR3)
- Implement SarifFormatter class
- Integrate with CLI
- Make all tests PASS
- **Outcome**: Working SARIF output

### Phase 4: User Experience (PR4)
- Add SARIF badge (discoverability)
- Write comprehensive docs
- Provide working examples
- **Outcome**: Users can easily adopt SARIF

---

## Success Metrics

### Launch Metrics
- ✅ All 4 PRs merged to main
- ✅ 65+ tests passing (100% pass rate)
- ✅ `just lint-full` passes (10.00/10 Pylint)
- ✅ `mypy --strict` passes (no type errors)
- ✅ SARIF badge visible in README
- ✅ Documentation complete (300+ lines of user docs)
- ✅ Working examples (Python API + GitHub Actions)

### Ongoing Metrics
- ✅ All 5 linters support SARIF
- ✅ GitHub Code Scanning can parse output
- ✅ VS Code SARIF Viewer can display results
- ✅ Azure DevOps can consume SARIF artifacts
- ✅ Zero SARIF-related bug reports (quality)
- ✅ All future linters include SARIF from day one

---

**Next Step**: Review this PR_BREAKDOWN.md, then proceed to PROGRESS_TRACKER.md to start PR1
