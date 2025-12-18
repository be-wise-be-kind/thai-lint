# Collection Pipeline Linter - AI Context & Research Findings

**Purpose**: Architectural context and research documentation for AI agents implementing the Collection Pipeline linter

**Scope**: Research findings on existing linter gaps, pattern analysis, and Martin Fowler's refactoring principles

**Overview**: This document provides essential context for AI agents working on the Collection Pipeline linter.
    Contains verified research findings, competitor analysis, pattern documentation, and code examples
    from the thai-lint codebase. The research confirms a gap in the Python linting ecosystem that
    this feature will address.

**Dependencies**: None (standalone research document)

**Exports**: Research findings, pattern analysis, implementation guidance

**Related**: PROGRESS_TRACKER.md for current status, PR_BREAKDOWN.md for implementation details

**Implementation**: N/A - this is a research/context document

---

## Executive Summary

This linter addresses a **verified gap** in the Python linting ecosystem. No existing tool (Ruff, Pylint, Flake8, Sourcery) catches the `for x: if not cond: continue` anti-pattern. The closest rule (PERF401) only catches the `if cond: append` pattern, NOT the `continue` pattern.

---

## The Anti-Pattern

### Pattern 1: Single Continue Guard

```python
# Anti-pattern
for file_path in paths:
    if not file_path.is_file():
        continue
    process(file_path)

# Refactored
for file_path in (p for p in paths if p.is_file()):
    process(file_path)
```

### Pattern 2: Multiple Continue Guards (Most Common)

```python
# Anti-pattern (found in thai-lint codebase)
for file_path in dir_path.glob(pattern):
    if not file_path.is_file():
        continue
    if ignore_parser.is_ignored(file_path):
        continue
    violations.extend(self.lint_path(file_path))

# Refactored
valid_files = (
    f for f in dir_path.glob(pattern)
    if f.is_file() and not ignore_parser.is_ignored(f)
)
for file_path in valid_files:
    violations.extend(self.lint_path(file_path))
```

### Pattern 3: Simple First-Match Return

```python
# Anti-pattern
for path in [thailint_yaml, thailint_json]:
    if path.exists():
        return path

# Refactored
return next((p for p in [thailint_yaml, thailint_json] if p.exists()), None)
```

---

## Why This Matters

### Martin Fowler's "Replace Loop with Pipeline"

From Martin Fowler's refactoring catalog:

> "Loop code is complex to read because you have to track a lot of context as you're reading... collection pipelines allow you to read from top to bottom to see what operations are done to the collection."

**Key Benefits:**
1. **Separation of concerns**: Filtering logic separated from processing logic
2. **Readability**: Data flow is clear and linear
3. **Composability**: Pipeline stages can be reordered, added, or removed
4. **Testability**: Each pipeline stage can be tested independently

**Reference:** https://martinfowler.com/articles/refactoring-pipelines.html

### The Anti-Pattern Hierarchy

```
Contrived Complexity (General)
└── Imperative vs Declarative Styles
    └── Replace Loop with Pipeline (Fowler)
        └── Embedded Filtering Anti-Pattern (THIS LINTER)
            ├── if/continue pattern (NOT caught by PERF401)
            ├── if/break pattern (NOT caught by PERF401)
            └── if/append pattern (caught by PERF401)
```

---

## Competitor Analysis

### Verified Testing Results

| Tool | Rule | Catches `if/continue`? | Catches `if/append`? |
|------|------|------------------------|----------------------|
| Ruff | PERF401 | NO | YES |
| Ruff | SIM110/111 | NO (only any/all) | N/A |
| Pylint | R1702 | NO (only nesting) | N/A |
| Flake8 | - | NO | NO |
| Sourcery | - | NO | Partial |

### Ruff PERF401 Verification

**Test Code:**
```python
# test_perf401.py
def example():
    result = []
    for x in range(10):
        if x > 5:
            continue
        result.append(x)
    return result
```

**Test Result:**
```bash
$ ruff check test_perf401.py --select=PERF401
All checks passed!  # NO DETECTION
```

**Why PERF401 Misses This:**
- PERF401 looks for: `for x: if cond: list.append(x)`
- PERF401 suggests: `[x for x in iter if cond]`
- PERF401 does NOT look for: `for x: if not cond: continue`

### SIM110/SIM111 Limitations

These rules only catch patterns that should use `any()` or `all()`:

```python
# SIM110 catches this:
for x in items:
    if x > 5:
        return True
return False
# Suggests: return any(x > 5 for x in items)

# SIM110 does NOT catch:
for x in items:
    if x <= 5:
        continue
    process(x)  # <-- Has side effects, not a boolean return
```

---

## Thai-Lint Codebase Analysis

### Known Violations

**File: `src/linters/file_placement/linter.py`**
```python
# Lines ~120-130 (approximate)
for file_path in dir_path.glob(pattern):
    if not file_path.is_file():
        continue
    if ignore_parser.is_ignored(file_path):
        continue
    file_violations = self.lint_path(file_path)
    violations.extend(file_violations)
```

**Suggested Refactoring:**
```python
valid_files = (
    f for f in dir_path.glob(pattern)
    if f.is_file() and not ignore_parser.is_ignored(f)
)
for file_path in valid_files:
    violations.extend(self.lint_path(file_path))
```

### Potential Violation Locations

Files to scan during dogfooding:
- `src/linters/file_placement/linter.py` (verified)
- `src/orchestrator/orchestrator.py` (likely)
- `src/linters/dry/python_analyzer.py` (possible)
- Any file with `for` + `continue` pattern

### Search Command for Violations

```bash
# Find potential violations
grep -rn "continue" src/ | grep -B2 "if not\|if .*is_"
```

---

## Detection Algorithm

### AST Pattern Matching

```
For loop structure:
ast.For
├── target: ast.Name (loop variable)
├── iter: ast.* (iterable)
└── body: list[ast.stmt]
    ├── ast.If (guard 1)
    │   ├── test: condition (negated filter)
    │   └── body: [ast.Continue]
    ├── ast.If (guard 2) [optional]
    │   ├── test: condition (negated filter)
    │   └── body: [ast.Continue]
    └── ... (remaining body - actual processing)
```

### Detection Pseudocode

```python
def is_pipeline_candidate(for_node: ast.For) -> bool:
    """Detect if a for loop has embedded filtering via continue."""

    # 1. Find leading if/continue statements
    continue_guards = []
    remaining_body = []

    for i, stmt in enumerate(for_node.body):
        if is_continue_guard(stmt):
            continue_guards.append(stmt)
        else:
            remaining_body = for_node.body[i:]
            break

    # 2. Must have at least one continue guard
    if not continue_guards:
        return False

    # 3. Must have remaining body (something to do after filtering)
    if not remaining_body:
        return False

    # 4. Guards must be simple (no else clause, no side effects)
    for guard in continue_guards:
        if guard.orelse:
            return False
        if has_side_effects(guard.test):
            return False

    return True

def is_continue_guard(stmt: ast.stmt) -> bool:
    """Check if statement is `if cond: continue`."""
    return (
        isinstance(stmt, ast.If) and
        len(stmt.body) == 1 and
        isinstance(stmt.body[0], ast.Continue) and
        not stmt.orelse
    )
```

---

## Edge Cases and False Positives

### Should NOT Flag

1. **Continue with side effects in condition:**
```python
for item in items:
    if not validate_and_log(item):  # Side effect in condition
        continue
    process(item)
```

2. **Continue with else clause:**
```python
for item in items:
    if not is_valid(item):
        continue
    else:
        mark_as_checked(item)
    process(item)
```

3. **Loop variable modified before continue:**
```python
for item in items:
    item = transform(item)
    if not is_valid(item):
        continue
    process(item)
```

4. **Multiple exit points (break/return mixed with continue):**
```python
for item in items:
    if item is None:
        break  # Different semantics than filtering
    if not is_valid(item):
        continue
    process(item)
```

5. **Continue based on loop state (not item filtering):**
```python
count = 0
for item in items:
    if count > 10:  # External state, not item property
        continue
    process(item)
    count += 1
```

### Should Flag

1. **Simple continue guard:**
```python
for x in items:
    if not x:
        continue
    process(x)
```

2. **Multiple continue guards:**
```python
for x in items:
    if not x:
        continue
    if x.hidden:
        continue
    process(x)
```

3. **Method call conditions (if pure):**
```python
for path in paths:
    if not path.exists():
        continue
    read(path)
```

---

## Suggestion Generation

### Transformation Strategy

**Input Pattern:**
```python
for VAR in ITER:
    if not COND1:
        continue
    if not COND2:
        continue
    BODY
```

**Output Pattern:**
```python
filtered_VAR = (VAR for VAR in ITER if COND1 and COND2)
for VAR in filtered_VAR:
    BODY
```

### Naming Conventions for Generated Variable

| Original Iterator | Suggested Name |
|-------------------|----------------|
| `items` | `filtered_items` |
| `files` | `valid_files` |
| `paths` | `matching_paths` |
| `dir_path.glob(...)` | `valid_files` |
| `range(...)` | `filtered_values` |

### Condition Inversion

The conditions in `if not COND: continue` must be inverted for the generator:

- `if not x: continue` → `if x`
- `if not x.is_valid(): continue` → `if x.is_valid()`
- `if x is None: continue` → `if x is not None`
- `if not (a and b): continue` → `if a and b`

---

## Configuration Options

### Proposed Configuration Schema

```yaml
# .thailint.yaml
collection-pipeline:
  enabled: true

  # Minimum continue guards to trigger (default: 1)
  min_guards: 1

  # Maximum loop body complexity to suggest refactoring
  max_body_statements: 10

  # Ignore patterns (file paths)
  ignore:
    - "tests/**"
    - "**/migrations/**"

  # Methods considered pure (no side effects)
  pure_methods:
    - "is_file"
    - "is_dir"
    - "exists"
    - "startswith"
    - "endswith"
```

### Inline Ignore Directives

```python
# Ignore single violation
for item in items:  # thailint: ignore[collection-pipeline]
    if not valid(item):
        continue
    process(item)

# Ignore with reason
for item in items:  # thailint: ignore[collection-pipeline] - intentional for readability
    if not valid(item):
        continue
    process(item)
```

---

## Output Format Examples

### Text Output

```
src/linters/file_placement/linter.py:125: [collection-pipeline] Loop with embedded filtering could use collection pipeline
  Consider extracting filter conditions to a generator expression:

  valid_files = (f for f in dir_path.glob(pattern) if f.is_file() and not ignore_parser.is_ignored(f))
  for file_path in valid_files:
      ...
```

### JSON Output

```json
{
  "violations": [
    {
      "rule_id": "collection-pipeline",
      "message": "Loop with embedded filtering could use collection pipeline",
      "file_path": "src/linters/file_placement/linter.py",
      "line_number": 125,
      "severity": "suggestion",
      "suggestion": "Extract filter conditions to generator expression",
      "details": {
        "guard_count": 2,
        "conditions": ["is_file()", "not is_ignored()"]
      }
    }
  ]
}
```

### SARIF Output

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "thailint",
          "rules": [
            {
              "id": "collection-pipeline",
              "name": "CollectionPipeline",
              "shortDescription": {
                "text": "Loop with embedded filtering"
              },
              "fullDescription": {
                "text": "Detects for loops with if/continue patterns that could be refactored to use collection pipelines (generator expressions, filter())."
              },
              "helpUri": "https://thai-lint.readthedocs.io/en/latest/linters/collection-pipeline/",
              "defaultConfiguration": {
                "level": "note"
              }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "collection-pipeline",
          "level": "note",
          "message": {
            "text": "Loop with 2 embedded filter guards could use collection pipeline"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/linters/file_placement/linter.py"
                },
                "region": {
                  "startLine": 125
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Related Patterns and Future Extensions

### Potential Future Enhancements

1. **Break patterns**: `if cond: break` followed by processing
2. **Nested loops**: Multiple levels of embedded filtering
3. **Mixed patterns**: `continue` + `break` in same loop
4. **Auto-fix support**: Automatic refactoring (higher complexity)

### Related Refactoring Patterns

- **Replace Loop with Pipeline** (Fowler)
- **Extract Method** (for complex filter conditions)
- **Replace Conditional with Polymorphism** (for type-based filtering)

---

## Testing Strategy

### Unit Test Categories

1. **Pattern Detection**
   - Single continue guard
   - Multiple continue guards
   - Nested if statements
   - Mixed control flow

2. **False Positive Prevention**
   - Side effects in conditions
   - Else clauses
   - Modified loop variables
   - External state dependencies

3. **Suggestion Quality**
   - Condition inversion correctness
   - Variable naming
   - Generator expression syntax

4. **Configuration**
   - Enable/disable
   - Threshold settings
   - Ignore patterns

### Integration Test Categories

1. **CLI Integration**
   - Command works end-to-end
   - All output formats work
   - Configuration loading works

2. **Dogfooding**
   - Detects violations in thai-lint codebase
   - No false positives in thai-lint codebase

---

## References

1. **Martin Fowler - Replace Loop with Pipeline**
   https://martinfowler.com/articles/refactoring-pipelines.html

2. **Ruff PERF401 Documentation**
   https://docs.astral.sh/ruff/rules/manual-list-comprehension/

3. **Python itertools Documentation**
   https://docs.python.org/3/library/itertools.html

4. **Generator Expressions (PEP 289)**
   https://peps.python.org/pep-0289/

---

## Appendix: Full Verification Script

```python
#!/usr/bin/env python3
"""Verify that existing linters don't catch the continue pattern."""

import subprocess
import tempfile
from pathlib import Path

TEST_CODE = '''
def example():
    result = []
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Pattern 1: continue guard (NOT caught by PERF401)
    for x in items:
        if x <= 5:
            continue
        result.append(x)

    return result
'''

def test_ruff():
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(TEST_CODE)
        f.flush()

        result = subprocess.run(
            ['ruff', 'check', f.name, '--select=PERF401'],
            capture_output=True,
            text=True
        )

        print("=== Ruff PERF401 ===")
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout or 'No output (pattern not detected)'}")

        Path(f.name).unlink()

if __name__ == "__main__":
    test_ruff()
```

**Expected Output:**
```
=== Ruff PERF401 ===
Exit code: 0
Output: No output (pattern not detected)
```

This confirms the gap that this linter addresses.
