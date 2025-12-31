# Performance Linter - AI Context

**Purpose**: Comprehensive feature context for the Performance Linter

**Scope**: Architecture, design decisions, technical constraints, and implementation patterns for performance anti-pattern detection

**Overview**: This document provides deep context for AI agents working on the Performance Linter feature.
    Covers feature vision, architecture decisions, integration points, and common patterns to follow.
    Essential for understanding "why" decisions were made and how the linter fits into thai-lint's ecosystem.

**Dependencies**: tree-sitter, ast module, existing thai-lint infrastructure

**Exports**: Architecture decisions, design rationale, integration patterns

**Related**: PROGRESS_TRACKER.md for status, PR_BREAKDOWN.md for tasks

**Implementation**: AST-based static analysis with configurable rules

---

## Feature Vision

### Problem Statement

AI-generated code frequently contains performance anti-patterns that standard linters don't catch:

1. **String concatenation in loops** - O(n²) time complexity
   - `result += str(item)` in a loop creates new string objects each iteration
   - No open-source Python linter detects this
   - Only Amazon CodeGuru (commercial) has this rule

2. **Regex compilation in loops** - Unnecessary repeated compilation
   - `re.match(pattern, string)` compiles the pattern each call
   - Should use `re.compile(pattern)` outside loop
   - No Python linter detects this specifically

### Evidence from Real Codebases

Analysis of popular Python projects found real violations:

**FastAPI** (well-maintained, modern Python):
- `fastapi/exceptions.py:197` - String concat in loop building error messages
- `fastapi/openapi/docs.py:136` - String concat in loop building HTML
- `scripts/deploy_docs_status.py:83` - `re.match()` in loop

```python
# FastAPI exceptions.py - Real violation
message = f"{len(self._errors)} validation error{'s'...}:\n"
for err in self._errors:
    message += f"  {err}\n"  # O(n²) string concat
```

### Value Proposition

- **Unique**: No open-source alternative for these specific rules
- **Real Impact**: O(n²) → O(n) for string building
- **AI-Relevant**: Common patterns in AI-generated code
- **Educational**: Teaches developers about Python internals

---

## Architecture

### Component Overview

```
src/linters/performance/
├── __init__.py           # Public API exports
├── config.py             # PerformanceConfig dataclass
├── linter.py             # Main orchestrator
├── python_analyzer.py    # Python AST analysis
├── typescript_analyzer.py # TypeScript tree-sitter analysis
└── violation_builder.py  # Violation message construction
```

### Data Flow

```
Input File
    │
    ▼
┌─────────────────┐
│ Language Router │ ──► Detect .py or .ts/.tsx
└─────────────────┘
    │
    ▼
┌─────────────────┐     ┌─────────────────┐
│ Python Analyzer │ or  │ TS Analyzer     │
│ (ast module)    │     │ (tree-sitter)   │
└─────────────────┘     └─────────────────┘
    │                         │
    ▼                         ▼
┌─────────────────────────────────────────┐
│         Rule Engine                      │
│  - string_concat_in_loop()              │
│  - regex_in_loop()                      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────┐
│ Violation List  │
└─────────────────┘
```

### Integration with Existing Infrastructure

**Reuse from existing linters**:
- `Violation` dataclass from `src/core/violation.py`
- SARIF output from `src/output/sarif.py`
- Config loading from `src/cli/config.py`
- Orchestrator patterns from `src/orchestrator/`

**CLI integration**:
- Add `perf` subcommand to `src/cli_main.py`
- Follow pattern of `nesting`, `magic-numbers` commands

---

## Design Decisions

### Decision 1: Two Separate Rules

**Choice**: Implement `string-concat-loop` and `regex-in-loop` as separate rules

**Rationale**:
- Different detection logic
- Different fix suggestions
- Users may want to enable/disable independently
- Easier to test and maintain

**Alternative Considered**: Single "loop-inefficiency" rule
- Rejected: Too broad, harder to configure

### Decision 2: Heuristic String Detection

**Choice**: Use naming heuristics to detect string variables

**Rationale**:
- Python doesn't have static types
- Variable names often indicate type: `result`, `message`, `html`, `output`
- Combined with literal checks (f-strings, string literals)

**Heuristics**:
```python
STRING_INDICATIVE_NAMES = [
    'str', 'string', 'msg', 'message', 'text', 'html',
    'output', 'result', 'content', 'line', 'url', 'path',
    'query', 'sql', 'json', 'xml', 'csv', 'body', 'response'
]
```

**Alternative Considered**: Type inference
- Rejected: Too complex, would require full type analysis

### Decision 3: One Violation Per Loop (Default)

**Choice**: Report one violation per loop, not per `+=` statement

**Rationale**:
- Reduces noise
- One fix (use `join()`) addresses all `+=` in loop
- Configurable: `report_each_concat: true` for detailed view

### Decision 4: Python-Only for Regex Rule

**Choice**: Only implement `regex-in-loop` for Python

**Rationale**:
- TypeScript regex is typically literal (`/pattern/`)
- JavaScript regex compilation is handled differently
- Python's `re` module is the common case

**Future**: Could add TypeScript support if requested

### Decision 5: Ignore Compiled Patterns

**Choice**: Don't flag `pattern.match()` when pattern is from `re.compile()`

**Rationale**:
- This is the correct pattern
- Would require tracking variable assignments
- Worth the complexity to avoid false positives

**Implementation**:
```python
# Track variables assigned from re.compile()
compiled_patterns = set()
for node in ast.walk(tree):
    if is_assign_from_re_compile(node):
        compiled_patterns.add(get_target_name(node))

# When checking loop calls
if is_method_call_on(node, compiled_patterns):
    continue  # Not a violation
```

---

## Technical Constraints

### AST Limitations

**Python `ast` module**:
- No type information
- Comments not preserved
- Line numbers may be approximate for multi-line statements

**tree-sitter-typescript**:
- Requires correct installation
- Different node types than Python AST
- Need to handle both `.ts` and `.tsx`

### Performance Constraints

**Target**: <100ms per file

**Approach**:
- Single-pass AST walk
- Early exit on non-applicable files
- No caching needed (analysis is fast)

### Compatibility

**Python versions**: 3.9+
**TypeScript**: All versions (via tree-sitter)
**Platforms**: Linux, macOS, Windows

---

## Common Patterns

### Pattern: Loop Detection

```python
def find_loops(tree: ast.AST) -> list[ast.For | ast.While]:
    """Find all loop nodes in AST."""
    loops = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            loops.append(node)
    return loops
```

### Pattern: Check Within Loop

```python
def check_within_loop(loop: ast.For | ast.While, checker: Callable) -> list[Violation]:
    """Run checker on all nodes within a loop body."""
    violations = []
    for node in ast.walk(loop):
        if node is loop:
            continue  # Skip the loop itself
        violation = checker(node)
        if violation:
            violations.append(violation)
    return violations
```

### Pattern: Violation Building

```python
def build_violation(
    file_path: str,
    line: int,
    rule_id: str,
    message: str,
    suggestion: str
) -> Violation:
    """Build a Violation object with consistent format."""
    return Violation(
        file_path=file_path,
        line_number=line,
        rule_id=f"performance.{rule_id}",
        message=message,
        suggestion=suggestion,
        severity="warning"
    )
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Flagging All +=

**Wrong**:
```python
# Don't do this - flags numeric counters
if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
    return violation  # Too broad!
```

**Correct**:
```python
# Check if target is likely a string
if is_likely_string_variable(node.target):
    return violation
```

### Anti-Pattern 2: Ignoring Nested Loops

**Wrong**:
```python
# Only checks top-level for loops
for node in tree.body:
    if isinstance(node, ast.For):
        check_loop(node)
```

**Correct**:
```python
# Walk entire tree to find nested loops
for node in ast.walk(tree):
    if isinstance(node, (ast.For, ast.While)):
        check_loop(node)
```

### Anti-Pattern 3: Missing Context in Messages

**Wrong**:
```python
message = "String concatenation in loop"
```

**Correct**:
```python
message = f"String concatenation in loop (variable '{var_name}' at line {line}). Consider using ''.join() instead."
```

---

## Testing Strategy

### Unit Test Structure

```
tests/unit/linters/performance/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_string_concat_loop.py     # String concat tests
├── test_regex_in_loop.py          # Regex tests
└── test_edge_cases.py             # Edge cases
```

### Test Categories

1. **Detection Tests**: Verify violations are found
2. **Non-Detection Tests**: Verify no false positives
3. **Edge Cases**: Empty files, syntax errors, nested structures
4. **Message Tests**: Verify messages are helpful
5. **Config Tests**: Verify config options work

### Validation on Real Codebases

After implementation, run on:
1. **FastAPI** - Should find known violations
2. **thai-lint itself** - Should have zero violations
3. **Flask** - Baseline comparison
4. **Pydantic** - Baseline comparison

---

## Future Considerations

### Potential Additional Rules

1. **`json-in-loop`** - `json.loads()`/`json.dumps()` in loop
2. **`dict-items-discard`** - `.items()` when only key or value needed (already in perflint)
3. **`list-append-vs-extend`** - Multiple appends vs extend
4. **`repeated-attr-access`** - Same attribute accessed multiple times

### Potential Enhancements

1. **Auto-fix**: Generate `join()` replacement code
2. **Severity Levels**: Based on loop size estimation
3. **TypeScript Regex**: If users request it
4. **JavaScript Support**: Via TypeScript parser

---

## Resources

### Internal References
- Existing linter: `src/linters/nesting/` (similar structure)
- Tests: `tests/unit/linters/nesting/` (similar patterns)
- Config: `src/templates/thailint_config_template.yaml`
- Docs: `docs/nesting-linter.md` (template for docs)

### External References
- [Python AST documentation](https://docs.python.org/3/library/ast.html)
- [tree-sitter-typescript](https://github.com/tree-sitter/tree-sitter-typescript)
- [Amazon CodeGuru string-concatenation rule](https://docs.aws.amazon.com/codeguru/detector-library/python/string-concatenation/)
- [Real Python: String Concatenation](https://realpython.com/python-string-concatenation/)

### Test Data
- FastAPI clone: `~/popular-repos/fastapi/`
- Known violations documented in PROGRESS_TRACKER.md
