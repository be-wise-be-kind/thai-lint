# SARIF Output Format Support - AI Context

**Purpose**: AI agent context document for implementing SARIF v2.1.0 output format support

**Scope**: Transform thai-lint output from text/json only to include SARIF (Static Analysis Results Interchange Format) v2.1.0 as a first-class output format, establishing SARIF as mandatory for all future linters

**Overview**: Comprehensive context document for AI agents working on the SARIF output format feature. SARIF is the OASIS standard format for static analysis tool output, enabling seamless integration with GitHub Code Scanning, Azure DevOps, VS Code SARIF Viewer, and other CI/CD platforms. This implementation uses strict TDD methodology, establishes SARIF as mandatory for future linters, and provides comprehensive testing and documentation. The feature adds `--format sarif` to all 5 existing linters (file-placement, nesting, srp, dry, magic-numbers) and creates standards documentation ensuring all future linters include SARIF support from day one.

**Dependencies**: Python 3.11+, pytest (TDD), Click (CLI), json stdlib module, existing formatters (src/core/cli_utils.py), package version metadata

**Exports**: SARIF v2.1.0 formatter, CLI integration (--format sarif), comprehensive tests (65+), standards documentation, user guides, SARIF badge

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Strict TDD approach (tests first, always), standards-driven development, comprehensive documentation, badge for discoverability

---

## Overview

**What We're Building**: Industry-standard SARIF v2.1.0 output format for all thai-lint linters

**Why It Matters**: SARIF is the universal interchange format for static analysis tools. Without SARIF support:
- ❌ No GitHub Code Scanning integration
- ❌ No Azure DevOps security tab integration
- ❌ No VS Code SARIF Viewer support
- ❌ Limited CI/CD platform integration

**Key Innovation**: Making SARIF mandatory for ALL future linters through `.ai/docs/SARIF_STANDARDS.md`, ensuring thai-lint remains a first-class citizen in modern development workflows.

---

## Project Background

### Current State (Starting Point)
- **Output Formats**: text (human-readable), json (machine-readable)
- **5 Working Linters**: file-placement, nesting, srp, dry, magic-numbers
- **CLI Integration**: `--format` option with `text` and `json` choices
- **Format Routing**: `src/core/cli_utils.py` handles format selection
- **Test Coverage**: 356/356 tests passing, 87% coverage

### Gap Analysis
**Missing Pieces**:
- ❌ SARIF output format (industry standard)
- ❌ SARIF standards documentation for future linters
- ❌ SARIF-specific tests (structure, compliance)
- ❌ SARIF badge in README
- ❌ GitHub Code Scanning integration examples
- ❌ VS Code SARIF Viewer usage guide

### What SARIF Enables
**GitHub Code Scanning Integration**:
```yaml
# .github/workflows/code-scanning.yml
- name: Run thailint
  run: thailint dry --format sarif src/ > results.sarif
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

**Azure DevOps Integration**:
```yaml
# azure-pipelines.yml
- script: thailint nesting --format sarif . > $(Build.ArtifactStagingDirectory)/results.sarif
- task: PublishBuildArtifacts@1
  inputs:
    artifactName: 'CodeAnalysisLogs'
```

**VS Code SARIF Viewer**:
```bash
# Generate SARIF, open in VS Code SARIF Viewer extension
thailint magic-numbers --format sarif src/ > results.sarif
code --install-extension MS-SarifVSCode.sarif-viewer
code results.sarif
```

---

## Feature Vision

### Three Output Formats (After Implementation)

#### 1. Text Format (Human-Readable)
```bash
thailint file-placement --format text .

# Output:
src/test_utils.py:1:0 - Test file in src/ directory
  Suggestion: Move to tests/ directory
```

#### 2. JSON Format (Machine-Readable)
```bash
thailint file-placement --format json .

# Output:
[
  {
    "rule_id": "file-placement.misplaced-file",
    "file_path": "src/test_utils.py",
    "line": 1,
    "column": 0,
    "message": "Test file in src/ directory",
    "severity": "error",
    "suggestion": "Move to tests/ directory"
  }
]
```

#### 3. SARIF Format (Industry Standard) **NEW**
```bash
thailint file-placement --format sarif .

# Output: SARIF v2.1.0 JSON document
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "thai-lint",
          "version": "0.1.0",
          "informationUri": "https://thai-lint.readthedocs.io/",
          "rules": [...]
        }
      },
      "results": [...]
    }
  ]
}
```

### SARIF as Mandatory Standard

**`.ai/docs/SARIF_STANDARDS.md` will establish**:
1. All new linters MUST support SARIF output
2. SARIF v2.1.0 specification compliance required
3. Test patterns for SARIF validation
4. Implementation checklist for developers

**Impact on Future Development**:
- When adding a new linter (e.g., "import-linter")
- Developer must implement SARIF output
- Standards doc provides implementation guide
- Tests ensure compliance
- Cannot claim "feature complete" without SARIF

---

## Current Application Context

### Existing CLI Structure
```
src/
├── cli.py           # Main Click entrypoint
│   ├── @cli.command("file-placement")
│   ├── @cli.command("nesting")
│   ├── @cli.command("srp")
│   ├── @cli.command("dry")
│   └── @cli.command("magic-numbers")
│   # Each has @format_option decorator
│
├── core/
│   ├── cli_utils.py # Format routing
│   │   └── format_violations(violations, format)
│   │       ├── "text" → _format_text()
│   │       ├── "json" → _format_json()
│   │       └── "sarif" → _format_sarif() (NEW)
│   └── types.py     # Violation dataclass
│
└── formatters/      # NEW DIRECTORY
    ├── __init__.py
    └── sarif.py     # SarifFormatter class
```

### Existing Format Option Pattern
```python
# src/cli.py
def format_option(func):
    """Add --format option to a command."""
    return click.option(
        "--format", "-f",
        type=click.Choice(["text", "json"]),  # Will become ["text", "json", "sarif"]
        default="text",
        help="Output format"
    )(func)
```

### Existing Violation Structure
```python
# src/core/types.py
@dataclass
class Violation:
    rule_id: str           # "file-placement.misplaced-file"
    file_path: str         # "src/test_utils.py"
    line: int              # 1 (1-indexed)
    column: int            # 0 (0-indexed)
    message: str           # "Test file in src/ directory"
    severity: Severity     # Severity.ERROR (our only level)
    suggestion: str | None # "Move to tests/ directory"

    def to_dict(self) -> dict[str, str | int | None]:
        """Convert to dictionary for JSON serialization."""
        return {...}
```

---

## Target Architecture

### Core Components

#### 1. SARIF Formatter (`src/formatters/sarif.py`)

**Purpose**: Convert list of Violation objects to SARIF v2.1.0 JSON document

**Class Structure**:
```python
class SarifFormatter:
    """SARIF v2.1.0 formatter for thai-lint violations."""

    def __init__(self, tool_name: str = "thai-lint", tool_version: str | None = None):
        """Initialize formatter with tool metadata."""
        self.tool_name = tool_name
        self.tool_version = tool_version or self._get_package_version()

    def format(self, violations: list[Violation]) -> dict:
        """Convert violations to SARIF v2.1.0 document."""
        return {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [self._create_run(violations)]
        }

    def _create_run(self, violations: list[Violation]) -> dict:
        """Create SARIF run object."""
        return {
            "tool": self._create_tool(),
            "results": [self._create_result(v) for v in violations]
        }

    def _create_tool(self) -> dict:
        """Create SARIF tool object with driver metadata."""
        return {
            "driver": {
                "name": self.tool_name,
                "version": self.tool_version,
                "informationUri": "https://thai-lint.readthedocs.io/",
                "rules": self._extract_rules(violations)
            }
        }

    def _create_result(self, violation: Violation) -> dict:
        """Convert Violation to SARIF result object."""
        return {
            "ruleId": violation.rule_id,
            "level": self._map_severity(violation.severity),
            "message": {"text": violation.message},
            "locations": [self._create_location(violation)]
        }

    def _create_location(self, violation: Violation) -> dict:
        """Create SARIF location object."""
        return {
            "physicalLocation": {
                "artifactLocation": {
                    "uri": violation.file_path,
                    "uriBaseId": "%SRCROOT%"
                },
                "region": {
                    "startLine": violation.line,
                    "startColumn": violation.column + 1  # SARIF uses 1-indexed columns
                }
            }
        }

    def _map_severity(self, severity: Severity) -> str:
        """Map Severity enum to SARIF level string."""
        return "error"  # We only have ERROR severity

    def _get_package_version(self) -> str:
        """Get package version from __version__."""
        from src import __version__
        return __version__
```

#### 2. CLI Integration (`src/cli.py`)

**Change**: Update format_option decorator
```python
def format_option(func):
    """Add --format option to a command."""
    return click.option(
        "--format", "-f",
        type=click.Choice(["text", "json", "sarif"]),  # ADDED "sarif"
        default="text",
        help="Output format"
    )(func)
```

**Impact**: All 5 commands automatically get SARIF support

#### 3. Format Routing (`src/core/cli_utils.py`)

**Change**: Add SARIF handling to format_violations
```python
def format_violations(violations: list[Violation], output_format: str) -> None:
    """Format and output violations."""
    if output_format == "json":
        _format_json(violations)
    elif output_format == "sarif":
        _format_sarif(violations)  # NEW
    else:
        _format_text(violations)

def _format_sarif(violations: list[Violation]) -> None:
    """Format violations as SARIF v2.1.0 JSON."""
    from src.formatters.sarif import SarifFormatter
    formatter = SarifFormatter()
    sarif_doc = formatter.format(violations)
    click.echo(json.dumps(sarif_doc, indent=2))
```

### Data Flow

```
User Command:
  thailint dry --format sarif src/

         ↓

CLI (src/cli.py):
  @cli.command("dry")
  @format_option  # Accepts "sarif"
  def dry(format, ...):
      violations = orchestrator.lint(...)
      format_violations(violations, format)

         ↓

Format Router (src/core/cli_utils.py):
  def format_violations(violations, "sarif"):
      _format_sarif(violations)

         ↓

SARIF Formatter (src/formatters/sarif.py):
  SarifFormatter.format(violations)
    → SARIF v2.1.0 JSON document

         ↓

Output:
  {
    "version": "2.1.0",
    "$schema": "...",
    "runs": [...]
  }
```

---

## Key Decisions Made

### Decision 1: SARIF v2.1.0 (Not 2.0)
**Rationale**:
- 2.1.0 is the latest OASIS standard (approved)
- GitHub Code Scanning uses 2.1.0
- Better tool metadata support
- Errata fixes from 2.0

**Impact**:
- Use 2.1.0 specification only
- Schema URL points to 2.1.0
- Documentation references 2.1.0

### Decision 2: TDD Mandatory
**Rationale**:
- Ensures SARIF compliance from start
- Tests document expected SARIF structure
- Prevents regressions

**Impact**:
- PR2: Write ALL tests (65+) with zero implementation
- PR3: Implement to pass PR2 tests
- No new tests in PR3

**Example**:
```python
# Step 1: Write test (PR2)
def test_sarif_document_has_required_fields():
    """SARIF document must have version, $schema, runs."""
    violations = [...]
    formatter = SarifFormatter()
    sarif_doc = formatter.format(violations)

    assert sarif_doc["version"] == "2.1.0"
    assert "$schema" in sarif_doc
    assert "runs" in sarif_doc
    # Test FAILS (formatter doesn't exist yet)

# Step 2: Implement (PR3)
# Make the test pass by creating SarifFormatter
```

### Decision 3: SARIF as Mandatory Standard
**Rationale**:
- Industry expects SARIF from modern linters
- GitHub Code Scanning requires SARIF
- Without standards, future linters will skip SARIF

**Impact**:
- `.ai/docs/SARIF_STANDARDS.md` establishes requirement
- AGENTS.md references standard
- Future linter PRs cannot merge without SARIF

### Decision 4: Badge for Discoverability
**Rationale**:
- Users need to know SARIF is supported
- Shields.io provides standard SARIF badge
- Orange color is SARIF convention

**Impact**:
- README badge: `![SARIF Support](https://img.shields.io/badge/SARIF-2.1.0-orange.svg)`
- Links to OASIS specification
- Placed after Documentation Status badge

### Decision 5: Minimal Dependencies
**Rationale**:
- SARIF is JSON - use stdlib json module
- No need for sarif-tools or pysarif libraries
- Keeps dependency tree small

**Impact**:
- Zero new dependencies
- Uses Python stdlib only
- Faster installation, fewer conflicts

---

## Integration Points

### With Existing Features

#### 1. Violation Data Structure (`src/core/types.py`)
**Integration**: SARIF formatter consumes Violation objects

**Mapping**:
```python
Violation.rule_id    → result.ruleId
Violation.message    → result.message.text
Violation.severity   → result.level ("error")
Violation.file_path  → location.artifactLocation.uri
Violation.line       → location.region.startLine
Violation.column     → location.region.startColumn (add 1 for SARIF)
Violation.suggestion → NOT INCLUDED (future: result.fixes)
```

#### 2. CLI Commands (`src/cli.py`)
**Integration**: All 5 commands get SARIF automatically

**Pattern**:
```python
@cli.command("nesting")
@format_option  # Provides --format with "sarif" choice
def nesting(format, ...):
    violations = orchestrator.lint(...)
    format_violations(violations, format)  # Routes to SARIF if format="sarif"
```

**No per-command changes needed** - format_option decorator handles it

#### 3. Testing Framework (`tests/`)
**Integration**: Add SARIF tests alongside existing tests

**Structure**:
```
tests/
├── unit/
│   ├── formatters/              # NEW
│   │   ├── __init__.py
│   │   └── test_sarif_formatter.py  # 40+ tests
│   └── test_cli_sarif_output.py     # 15+ tests
└── integration/
    └── test_sarif_all_linters.py    # 10+ tests
```

### With External Systems

#### 1. GitHub Code Scanning
**Integration**: Upload SARIF to GitHub Security tab

**Workflow**:
```yaml
# .github/workflows/code-scanning.yml
name: Code Scanning
on: [push, pull_request]

jobs:
  thailint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install thailint
        run: pip install thailint
      - name: Run thailint
        run: thailint dry --format sarif src/ > results.sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
          category: thailint-dry
```

**Result**: Violations appear in GitHub Security tab

#### 2. Azure DevOps
**Integration**: Publish SARIF to Azure Pipelines

**Pipeline**:
```yaml
# azure-pipelines.yml
steps:
  - script: |
      pip install thailint
      thailint nesting --format sarif . > $(Build.ArtifactStagingDirectory)/results.sarif
    displayName: 'Run thailint'

  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: '$(Build.ArtifactStagingDirectory)'
      artifactName: 'CodeAnalysisLogs'
```

#### 3. VS Code SARIF Viewer
**Integration**: Open SARIF files in VS Code extension

**Usage**:
```bash
# Generate SARIF
thailint magic-numbers --format sarif src/ > results.sarif

# Install extension
code --install-extension MS-SarifVSCode.sarif-viewer

# Open in VS Code
code results.sarif
```

**Result**: Interactive violation viewer with file navigation

---

## Success Metrics

### Technical Success
- ✅ 65+ tests covering SARIF v2.1.0 compliance
- ✅ All tests pass (100% pass rate)
- ✅ `just lint-full` passes (10.00/10 Pylint)
- ✅ Type checking passes (`mypy --strict`)
- ✅ A-grade complexity maintained (Xenon)
- ✅ Zero new dependencies added

### Feature Success
- ✅ All 5 linters support `--format sarif`
- ✅ SARIF output validates against v2.1.0 JSON schema
- ✅ GitHub Code Scanning can parse and display violations
- ✅ Azure DevOps can consume SARIF artifacts
- ✅ VS Code SARIF Viewer can display results interactively

### Documentation Success
- ✅ `.ai/docs/SARIF_STANDARDS.md` establishes mandatory standard
- ✅ AGENTS.md mandates SARIF for new linters
- ✅ User guide complete with CI/CD examples
- ✅ Python API example functional
- ✅ SARIF badge visible in README header

### Adoption Success
- ✅ SARIF feature is discoverable (badge + docs)
- ✅ GitHub Actions example workflow provided
- ✅ Azure DevOps example pipeline provided
- ✅ Used in project's own CI/CD (dogfooding)

---

## Technical Constraints

### SARIF Specification Compliance
- **Version**: SARIF v2.1.0 (OASIS Standard)
- **Schema**: Must validate against official JSON schema
- **Required Fields**: version, $schema, runs (non-empty)
- **Tool Metadata**: name, version, informationUri
- **Results**: ruleId, level, message, locations

### Performance
- **SARIF Generation**: <100ms for 100 violations
- **Memory**: No memory leaks when formatting large violation lists
- **JSON Size**: Reasonable output size (no unnecessary fields)

### Compatibility
- **JSON Output**: Valid JSON (parsable by jq, json.loads)
- **UTF-8 Encoding**: Proper handling of non-ASCII characters
- **Path Handling**: Use forward slashes (/) for cross-platform URIs
- **Line/Column Indexing**: SARIF uses 1-indexed columns (convert from 0-indexed)

### Backward Compatibility
- **Existing Formats**: text and json formats unchanged
- **Default Format**: Remains "text" (no breaking changes)
- **CLI Options**: --format option adds "sarif" choice (non-breaking)

---

## AI Agent Guidance

### When Writing Tests (PR2 - TDD Phase 1)
1. **Follow SARIF_STANDARDS.md**: Tests validate standard compliance
2. **Test Structure**: Validate SARIF document structure (version, schema, runs)
3. **Test Mappings**: Verify Violation → SARIF result mappings
4. **Test Edge Cases**: Empty violations, multiple violations, special characters
5. **Test All Linters**: Each of 5 linters must produce valid SARIF
6. **Zero Implementation**: Do not create src/formatters/sarif.py yet

**Example Test**:
```python
def test_sarif_tool_metadata():
    """SARIF tool must include name, version, informationUri."""
    violations = [sample_violation()]
    formatter = SarifFormatter()  # Will not exist yet
    sarif_doc = formatter.format(violations)

    tool = sarif_doc["runs"][0]["tool"]["driver"]
    assert tool["name"] == "thai-lint"
    assert "version" in tool
    assert tool["informationUri"] == "https://thai-lint.readthedocs.io/"
```

### When Implementing (PR3 - TDD Phase 2)
1. **Make Tests Pass**: Minimal implementation to pass ALL PR2 tests
2. **Follow Pattern**: Study existing formatters (_format_text, _format_json)
3. **Use Violation.to_dict()**: Leverage existing serialization where possible
4. **Map Severity**: Severity.ERROR → "error" (only mapping needed)
5. **Handle Empty**: Empty violations list should produce valid SARIF with empty results array
6. **No New Tests**: Use ONLY PR2 tests to validate

**Implementation Checklist**:
- [ ] Create src/formatters/__init__.py
- [ ] Create src/formatters/sarif.py with SarifFormatter class
- [ ] Update src/cli.py format_option decorator
- [ ] Update src/core/cli_utils.py with _format_sarif()
- [ ] Run PR2 tests → ALL pass
- [ ] Manual test: `thailint file-placement --format sarif . | jq`

### When Documenting (PR4 - Polish)
1. **User-Focused**: Write for users, not implementers
2. **Working Examples**: Every example must be copy-paste runnable
3. **CI/CD Templates**: Provide complete GitHub Actions and Azure Pipelines examples
4. **Badge Placement**: After Documentation Status badge in README
5. **Link to Specification**: Reference OASIS SARIF v2.1.0 spec

**Documentation Checklist**:
- [ ] Create docs/sarif-output.md (comprehensive user guide)
- [ ] Update README.md (add badge, add examples)
- [ ] Update docs/configuration.md (add SARIF to format options)
- [ ] Update docs/cli-reference.md (document --format sarif)
- [ ] Create examples/sarif_usage.py (working Python example)
- [ ] Create .github/workflows/sarif-example.yml (CI/CD template)

### Common Patterns

#### Pattern 1: SARIF Document Builder
```python
class SarifFormatter:
    def format(self, violations: list[Violation]) -> dict:
        """Build SARIF v2.1.0 document."""
        return {
            "version": "2.1.0",
            "$schema": self._get_schema_uri(),
            "runs": [self._create_run(violations)]
        }
```

#### Pattern 2: Violation to Result Mapping
```python
def _create_result(self, violation: Violation) -> dict:
    """Map Violation to SARIF result."""
    return {
        "ruleId": violation.rule_id,
        "level": "error",  # Our only severity
        "message": {"text": violation.message},
        "locations": [self._create_location(violation)]
    }
```

#### Pattern 3: Testing SARIF Structure
```python
def test_sarif_document_structure():
    """Validate SARIF v2.1.0 structure."""
    formatter = SarifFormatter()
    sarif_doc = formatter.format([sample_violation()])

    # Required fields
    assert sarif_doc["version"] == "2.1.0"
    assert "$schema" in sarif_doc
    assert len(sarif_doc["runs"]) == 1

    # Run structure
    run = sarif_doc["runs"][0]
    assert "tool" in run
    assert "results" in run
```

---

## Risk Mitigation

### Risk: SARIF Spec Misinterpretation
**Mitigation**:
- Reference official OASIS specification
- Test against GitHub Code Scanning (real-world validation)
- Use VS Code SARIF Viewer for visual validation

### Risk: Breaking Existing Formats
**Mitigation**:
- Do not modify existing format handlers
- Add SARIF as new choice only
- Maintain default="text" (no breaking changes)
- Test that text and json still work

### Risk: Large Violation Lists
**Mitigation**:
- Use generator patterns if needed
- Test with 1000+ violations
- Monitor memory usage

### Risk: Future Linters Missing SARIF
**Mitigation**:
- `.ai/docs/SARIF_STANDARDS.md` establishes requirement
- AGENTS.md checklist includes SARIF
- PR reviews verify SARIF support

---

## Future Enhancements

### Post-MVP (After PR4)

#### 1. SARIF Fixes
- Add result.fixes array with suggested fixes
- Map Violation.suggestion to SARIF fix objects
- Enable auto-fix via SARIF tools

#### 2. Rule Metadata Enrichment
- Add rule.fullDescription with detailed explanations
- Add rule.help with markdown-formatted guidance
- Add rule.properties for custom metadata

#### 3. SARIF Validation Tool
```bash
# Validate SARIF output against schema
thailint validate-sarif results.sarif
```

#### 4. SARIF Diff Tool
```bash
# Compare SARIF outputs across commits
thailint sarif-diff baseline.sarif current.sarif
```

#### 5. SARIF Metrics
- Track violation trends over time
- Generate SARIF reports with statistics
- Integration with code quality dashboards

---

## Related Documents

### Essential Reading (Read in Order)
1. **PROGRESS_TRACKER.md** - START HERE for current status
2. **This Document (AI_CONTEXT.md)** - Comprehensive context
3. **PR_BREAKDOWN.md** - Detailed implementation steps

### SARIF Specification
- **Official Spec**: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- **JSON Schema**: https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json
- **Microsoft Tutorials**: https://github.com/microsoft/sarif-tutorials

### Existing Project Docs
- **`.ai/docs/FILE_HEADER_STANDARDS.md`** - File header templates
- **`.ai/howtos/how-to-write-tests.md`** - Testing guidance
- **`src/core/types.py`** - Violation dataclass structure
- **`src/core/cli_utils.py`** - Existing format routing

---

## Development Philosophy

### TDD is Non-Negotiable
Tests are written before implementation, always. PR2 writes ALL tests, PR3 implements to pass them.

### Standards First, Code Second
`.ai/docs/SARIF_STANDARDS.md` establishes requirements before any code is written. This ensures consistency.

### User Experience Matters
SARIF should be as easy to use as text/json formats. Badge makes it discoverable, docs make it usable.

### Future-Proof the Codebase
All future linters MUST support SARIF. Standards doc and AGENTS.md checklist enforce this.

---

**Remember**: SARIF is not just another output format - it's the industry standard that enables thai-lint to integrate with modern CI/CD platforms. This implementation establishes SARIF as a first-class citizen and mandatory requirement for all future linters.
