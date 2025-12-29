# Lazy Ignores Linter - AI Context & Architecture

**Purpose**: Comprehensive feature context and design decisions for the lazy-ignores linter

**Scope**: Architecture, design rationale, integration points, patterns to follow

**Overview**: This document provides deep architectural context for the lazy-ignores linter feature. It explains the header-based suppression model, detection strategies, and how this linter differs from simple pattern matching. Essential for understanding design decisions and maintaining consistency across implementation.

**Dependencies**: File-header linter infrastructure, CLI patterns, core types

**Exports**: Architecture documentation, design decisions, integration patterns

**Related**: PROGRESS_TRACKER.md for status, PR_BREAKDOWN.md for implementation steps

**Implementation**: Reference architecture for consistent implementation

---

## Feature Vision

### The Problem

AI agents (Claude, GPT, etc.) often take shortcuts when encountering linting errors:

```python
# AI agent encounters: "PLR0912: Too many branches (15 > 12)"
# Instead of refactoring, adds:
def complex_function():  # noqa: PLR0912
    ...  # Still complex, now hidden from linters
```

This creates **hidden technical debt**:
- The code remains complex
- Future developers don't see the warning
- The ignore has no justification
- No human approved the shortcut

### The Solution

Require **explicit justification** in file headers with **human approval**:

```python
"""
Purpose: State machine for WebSocket lifecycle

Suppressions:
    PLR0912: State machine inherently requires branching for 6 states
             Approved by @steve in PR #123
"""

def handle_state():  # noqa: PLR0912
    # Now justified and approved
```

---

## Architecture

### High-Level Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Parse Header   │────▶│ Find Ignores in  │────▶│ Match Against   │
│  Suppressions   │     │ Code Body        │     │ Header Entries  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                              ┌────────────────────────────┤
                              ▼                            ▼
                    ┌─────────────────┐          ┌─────────────────┐
                    │ Unjustified     │          │ Orphaned Header │
                    │ Violation       │          │ Violation       │
                    └─────────────────┘          └─────────────────┘
```

### Component Diagram

```
src/linters/lazy_ignores/
├── __init__.py
├── types.py                 # Data structures
│   ├── IgnoreType (enum)
│   ├── IgnoreDirective (dataclass)
│   └── SuppressionEntry (dataclass)
│
├── config.py                # Configuration
│   └── LazyIgnoresConfig
│
├── ignore_detector.py       # Base interface
│   └── BaseIgnoreDetector (ABC)
│
├── python_analyzer.py       # Python detection
│   └── PythonIgnoreDetector
│       ├── find_ignores() -> list[IgnoreDirective]
│       └── PATTERNS dict
│
├── typescript_analyzer.py   # TS/JS detection
│   └── TypeScriptIgnoreDetector
│
├── header_parser.py         # Suppressions parsing
│   └── SuppressionsParser
│       ├── parse() -> dict[str, str]
│       ├── normalize_rule_id()
│       └── extract_header()
│
├── test_skip_detector.py    # Test skip detection
│   └── TestSkipDetector
│
├── violation_builder.py     # Message formatting
│   └── build_unjustified_violation()
│   └── build_orphaned_violation()
│
└── linter.py                # Main orchestrator
    └── LazyIgnoresRule
        ├── check() -> list[Violation]
        ├── _check_file()
        ├── _find_unjustified()
        └── _find_orphaned()
```

---

## Design Decisions

### Decision 1: Header-Based Declarations

**Why headers instead of inline comments?**

| Approach | Pros | Cons |
|----------|------|------|
| Inline: `# noqa: PLR0912 - justification` | Easy to add | Scattered, hard to audit |
| Header: `Suppressions: PLR0912: ...` | Centralized, auditable | Requires header format |

**Choice**: Header-based for auditability and explicit human approval workflow.

### Decision 2: Rule-Based (Not Line-Based)

**Why one entry per rule, not per line?**

```python
# Option A: Line-based (rejected)
Suppressions:
    Line 45 PLR0912: reason
    Line 67 PLR0912: reason  # Tedious, brittle

# Option B: Rule-based (chosen)
Suppressions:
    PLR0912: reason  # Covers all PLR0912 in file
```

**Choice**: Rule-based because:
- Less verbose
- Survives line number changes
- Forces holistic justification

### Decision 3: Orphaned Detection

**Why detect orphaned header entries?**

```python
"""
Suppressions:
    PLR0912: Old justification  # But no PLR0912 ignore in code!
"""
```

**Choice**: Error on orphaned because:
- Keeps headers synchronized with code
- Prevents stale documentation
- Indicates code was refactored but header wasn't updated

### Decision 4: Test Skips as Violations

**Why flag test skips?**

AI agents often skip failing tests rather than fixing them:

```python
@pytest.mark.skip  # "I'll fix this later" - never happens
def test_critical_feature():
    ...
```

**Choice**: Require `reason=` parameter for all skips:

```python
@pytest.mark.skip(reason="Depends on external service - see #456")
```

### Decision 5: Agent-Friendly Error Messages

**Why special error message format?**

AI agents read error messages to decide next actions. Clear guidance prevents:
- Adding inline justifications (wrong approach)
- Adding ignores without asking human
- Misunderstanding the approval requirement

**Choice**: Error messages explicitly state:
1. What to add (Suppressions section format)
2. Where to add it (file header)
3. Approval requirement (human must approve)

---

## Integration Points

### Existing Infrastructure to Reuse

| Component | Location | Usage |
|-----------|----------|-------|
| File header parsing | `src/linters/file_header/python_parser.py` | Extract header from Python files |
| TypeScript parsing | `src/linters/file_header/typescript_parser.py` | Extract header from TS files |
| Violation type | `src/core/types.py` | Standard violation dataclass |
| CLI patterns | `src/cli/linters/code_patterns.py` | Command registration |
| Output formatting | `src/core/cli_utils.py` | text/json/sarif |

### New File Header Field

Add `Suppressions:` as optional field to FILE_HEADER_STANDARDS.md:

```python
"""
Purpose: ...
Scope: ...
Overview: ...
Dependencies: ...
Exports: ...
Interfaces: ...
Implementation: ...

Suppressions:                    # NEW - Optional section
    RULE_ID: Justification text
"""
```

---

## Pattern Detection Details

### Python Patterns

| Pattern | Regex | Captures |
|---------|-------|----------|
| noqa | `#\s*noqa(?::\s*([A-Z0-9,\s]+))?` | Rule IDs (optional) |
| type:ignore | `#\s*type:\s*ignore(?:\[([^\]]+)\])?` | Error code (optional) |
| pylint:disable | `#\s*pylint:\s*disable=([a-z0-9\-,]+)` | Rule names |
| nosec | `#\s*nosec(?:\s+([A-Z0-9]+))?` | Bandit rule ID |

### TypeScript/JavaScript Patterns

| Pattern | Regex | Notes |
|---------|-------|-------|
| @ts-ignore | `//\s*@ts-ignore` | Single-line |
| @ts-nocheck | `//\s*@ts-nocheck` | File-level |
| @ts-expect-error | `//\s*@ts-expect-error` | Expected error |
| eslint-disable | `//\s*eslint-disable(?:-next-line)?` | Line/block |
| eslint-disable block | `/\*\s*eslint-disable` | Block comment |

### Rule ID Normalization

```python
# These should all match the same suppression entry:
"PLR0912" -> "plr0912"
"plr0912" -> "plr0912"

# These are distinct:
"type:ignore[arg-type]" -> "type:ignore[arg-type]"
"type:ignore[return-value]" -> "type:ignore[return-value]"

# Multi-rule noqa:
"# noqa: PLR0912, PLR0915" -> ["plr0912", "plr0915"]
```

---

## Error Message Templates

### Unjustified Ignore

```
lazy-ignores.unjustified  {file_path}:{line}:{column}  ERROR

  Unjustified suppression found:
    {raw_text}

  Rule: {rule_id}

  To fix, add an entry to the file header Suppressions section:

      Suppressions:
          {rule_id}: [Your justification here]

  IMPORTANT: Adding suppressions requires human approval.
  Do not add this entry without explicit permission from
  a human reviewer. Ask first, then add if approved.
```

### Orphaned Suppression

```
lazy-ignores.orphaned  {file_path}:{header_line}  ERROR

  Orphaned suppression in header:
    {rule_id}: {justification}

  This rule is declared in the Suppressions section but
  no matching ignore directive was found in the code.

  Either:
  1. Remove the entry if the ignore was removed from code
  2. Add the ignore directive if it's missing
```

### Test Skip Without Reason

```
lazy-ignores.test-skip  {file_path}:{line}:{column}  ERROR

  Test skip without reason:
    {raw_text}

  All test skips must have a reason explaining why the test
  is skipped and when it will be re-enabled.

  Fix by adding a reason:
    @pytest.mark.skip(reason="Description - see issue #XXX")
```

---

## Configuration Schema

```yaml
# .thailint.yaml
lazy-ignores:
  # Pattern detection toggles
  check_noqa: true
  check_type_ignore: true
  check_pylint_disable: true
  check_nosec: true
  check_ts_ignore: true
  check_eslint_disable: true
  check_test_skips: true

  # Orphaned detection
  check_orphaned: true

  # File patterns to ignore
  ignore_patterns:
    - "tests/**"  # Don't enforce in test files
    - "**/migrations/**"
    - "**/__pycache__/**"
```

---

## Testing Strategy

### Unit Tests

| Test File | Coverage |
|-----------|----------|
| test_python_ignore_detection.py | noqa, type:ignore, pylint, nosec |
| test_typescript_detection.py | @ts-ignore, eslint-disable |
| test_header_parser.py | Suppressions extraction |
| test_orphaned_detection.py | Orphaned entry detection |
| test_violation_messages.py | Agent-friendly formatting |
| test_test_skip_detection.py | pytest.skip, it.skip |

### Integration Tests

| Test | Scenario |
|------|----------|
| test_full_python_file.py | Complete Python file with mixed patterns |
| test_full_typescript_file.py | Complete TS file with mixed patterns |
| test_cli_integration.py | CLI command with all options |
| test_output_formats.py | text, json, sarif output |

### Edge Cases

- Empty files
- Files without headers
- Malformed Suppressions sections
- Mixed ignore types on same line
- Unicode in justifications
- Very long files (performance)

---

## Relationship to Existing Linters

| Linter | Focus | Relationship |
|--------|-------|--------------|
| file-header | Header field presence | lazy-ignores adds Suppressions field |
| nesting | Code complexity | lazy-ignores checks noqa for nesting rules |
| srp | Class responsibility | lazy-ignores checks noqa for srp rules |
| magic-numbers | Numeric literals | lazy-ignores checks noqa for magic rules |

The lazy-ignores linter is **meta** - it lints the linting suppressions themselves.

---

## Success Criteria

### Must Have (P0)
- [ ] Detects all Python ignore patterns
- [ ] Detects all TypeScript/JavaScript patterns
- [ ] Header Suppressions parsing works
- [ ] Orphaned detection works
- [ ] Error messages guide AI agents correctly
- [ ] CLI command with all output formats

### Should Have (P1)
- [ ] Test skip detection
- [ ] Configuration via .thailint.yaml
- [ ] Dogfooding on thai-lint itself

### Nice to Have (P2)
- [ ] Auto-fix suggestions
- [ ] IDE integration hints
- [ ] Metrics/statistics output

---

## References

### Survey Findings

The design is based on surveying real projects:

| Project | Findings |
|---------|----------|
| safeshell | Excellent - all 13 ignores justified |
| durable-code-test | Good - mostly justified, few issues |
| tubebuddy | Mixed - 8+ complexity ignores without justification |
| tb-automation-py | Mixed - TODOs acknowledging risky type ignores |

Key patterns that informed design:
1. Complexity ignores (PLR0912/PLR0915) often unjustified
2. TODOs like "may cause runtime exceptions" indicate lazy ignores
3. Repeated identical ignores suggest systemic issues
4. Well-documented projects have inline justification comments

### Similar Tools

| Tool | Approach | Difference |
|------|----------|------------|
| flake8-noqa | Validates noqa has correct codes | Doesn't require justification |
| pylint-ignore | Manages ignore files | External file, not header-based |

Our approach is unique in requiring **human-approved header declarations**.
