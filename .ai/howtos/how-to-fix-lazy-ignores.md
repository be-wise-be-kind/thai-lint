# How to: Fix Lazy Ignores Violations

**Purpose**: Step-by-step guide for AI agents to properly handle linting suppressions with justification

**Scope**: Adding justified suppression entries to file headers, understanding suppression requirements, human approval process

**Overview**: This guide covers systematic fixing of lazy-ignores violations - unjustified linting suppressions
    that AI agents added without proper documentation. Uses a header-based declaration model where all
    suppressions must be documented in the file's `Suppressions:` section with human-approved justifications.
    Includes the critical requirement that AI agents MUST obtain human approval before adding any suppression.
    Also covers orphaned entry cleanup and test skip violations.

**Dependencies**: lazy-ignores linter, FILE_HEADER_STANDARDS.md, file header linter infrastructure

**Exports**: Clean code with all suppressions justified, AI agent governance compliance

**Related**: how-to-fix-linting-errors.md, FILE_HEADER_STANDARDS.md, AGENTS.md (Quality Gates section)

**Implementation**: Header-based suppression declaration with human approval workflow

---

## Overview

Lazy-ignores violations occur when AI agents add linting suppression comments (`# noqa`, `# type: ignore`, `# pylint: disable`, etc.) without documenting them in the file header. This guide explains how to properly fix these violations while maintaining the human approval requirement.

**The Process**:
1. Run `thailint lazy-ignores src/` to find violations
2. For each violation, decide: fix the underlying issue OR justify the suppression
3. If suppression is needed, ASK the human for approval
4. Add the suppression entry to the file header's `Suppressions:` section
5. Run `thailint lazy-ignores src/` again to verify
6. Repeat until clean

**Critical Rule**: **NEVER add a suppression entry without explicit human approval.**

---

## The Iterative Cycle

### Step 1: Assess Current State

```bash
# Run lazy-ignores linter
thailint lazy-ignores src/

# Check exit code
echo $?
# 0 = success, 1 = violations found
```

### Step 2: Categorize Each Violation

For each violation, determine the type:

| Type | Description | Action |
|------|-------------|--------|
| **Unjustified** | Suppression in code without header entry | Add header entry OR fix the issue |
| **Orphaned** | Header entry without matching suppression | Remove stale entry |
| **Test Skip** | Test skip without reason | Add reason OR remove skip |

### Step 3: Handle Each Violation

For unjustified suppressions:
1. First, try to **fix the underlying issue** (preferred)
2. If suppression is truly needed, **ask human for approval**
3. Only after approval, **add header entry**

### Step 4: Validate

```bash
# After fixes, validate
thailint lazy-ignores src/
echo $?  # Must be 0
```

---

## Understanding Violations

### Unjustified Suppression

**What it means**: A suppression comment exists in code but no matching entry in the file header.

**Example violation:**
```
src/utils.py:45:20 - Unjustified suppression: # noqa: PLR0912
```

**The code:**
```python
"""
Purpose: Utility functions
"""

def complex_function():  # noqa: PLR0912
    # complex logic...
```

**Problem**: The `# noqa: PLR0912` has no justification in the header.

### Orphaned Entry

**What it means**: A `Suppressions:` section entry exists in the header but no matching suppression in the code.

**Example violation:**
```
src/utils.py:5:4 - Orphaned suppression entry: PLR0912
```

**The code:**
```python
"""
Purpose: Utility functions

Suppressions:
    - PLR0912: Complex branching required
"""

def simple_function():  # No PLR0912 suppression in code!
    return 1
```

**Problem**: Header declares PLR0912 but no such ignore exists in the code.

### Test Skip Without Reason

**What it means**: A test is skipped without explaining why.

**Example violation:**
```
tests/test_api.py:15:0 - Test skip without reason: @pytest.mark.skip
```

**The code:**
```python
@pytest.mark.skip  # No reason!
def test_flaky_integration():
    pass
```

---

## Fixing Unjustified Suppressions

### Option 1: Fix the Underlying Issue (Preferred)

Before adding a suppression, try to fix the root cause:

**Example - Too Many Branches (PLR0912):**

```python
# Before (violation)
def process_state(state):  # noqa: PLR0912
    if state == 'A':
        do_a()
    elif state == 'B':
        do_b()
    elif state == 'C':
        do_c()
    # ... many more branches

# After (fixed with dispatch pattern)
STATE_HANDLERS = {
    'A': do_a,
    'B': do_b,
    'C': do_c,
}

def process_state(state):
    handler = STATE_HANDLERS.get(state)
    if handler:
        handler()
```

**Example - Type Ignore:**

```python
# Before (violation)
result = api.process(data)  # type: ignore[arg-type]

# After (fixed with proper typing)
from typing import cast
result = api.process(cast(ApiData, data))
```

### Option 2: Request Human Approval for Suppression

If the suppression is truly necessary, you MUST ask the human for approval.

**Required Process:**

1. **STOP** - Do not add the suppression yet
2. **EXPLAIN** the issue clearly:
   - What linter rule is being violated?
   - What code is triggering it?
   - What alternatives have you tried?
3. **JUSTIFY** why suppression is needed:
   - Why can't the issue be fixed properly?
   - What makes this a false positive or acceptable exception?
4. **ASK** for explicit permission
5. **WAIT** for approval before proceeding

**Example Request to User:**

```
"I'm encountering a Pylint PLR0912 violation (too many branches) in
`src/state_machine.py:45` in the `handle_event` function. The function
has 15 branches because it's a state machine handling all possible
state transitions.

I've considered:
- Using a dispatch dictionary (but transitions have complex logic)
- Splitting into separate functions (but they share state context)
- Using a state pattern (but this is a simple script, not a class)

The complexity is inherent to the state machine design. May I add a
suppression with the justification 'State machine requires branch
for each state transition'?"
```

### Option 3: Add the Suppression Entry (After Approval)

**ONLY after receiving explicit human approval**, add the entry to the file header:

**Python Format:**
```python
"""
Purpose: State machine event handler

Scope: Event processing and state transitions

Overview: Handles all event types and transitions between states.

Suppressions:
    - PLR0912: State machine requires branch for each state transition
"""

def handle_event(event):  # noqa: PLR0912
    # state machine logic
```

**TypeScript Format:**
```typescript
/**
 * Purpose: Legacy API adapter
 *
 * Suppressions:
 *   - ts-ignore: Legacy API returns untyped data, validated at runtime
 */

// @ts-ignore
const data = await legacyApi.fetch();
```

---

## Suppression Entry Format

### Correct Format

```python
"""
Suppressions:
    - rule-id: Justification explaining WHY the ignore is legitimate
"""
```

**Format Rules:**
- Start with `Suppressions:` on its own line
- Each entry: `- rule-id: justification`
- Indent entries with 4 spaces
- Rule ID should match the code exactly (case-insensitive matching)
- Justification explains WHY, not WHAT

### Rule ID Extraction

| Code Pattern | Header Entry |
|--------------|--------------|
| `# noqa: PLR0912` | `PLR0912` |
| `# noqa: PLR0912, PLR0915` | `PLR0912` and `PLR0915` (separate entries) |
| `# type: ignore[arg-type]` | `arg-type` |
| `# type: ignore` | `type-ignore` (no specific code) |
| `# pylint: disable=no-member` | `no-member` |
| `# nosec B602` | `B602` |
| `// @ts-ignore` | `ts-ignore` |
| `// eslint-disable-line no-console` | `no-console` |

### Good vs Bad Justifications

| Rule ID | Good Justification | Bad Justification |
|---------|-------------------|-------------------|
| `PLR0912` | "State machine requires branch per state" | "Too many branches" |
| `arg-type` | "Pydantic v2 coerces at validation time" | "Type mismatch" |
| `B602` | "Command from trusted config, input sanitized" | "Need shell" |
| `no-member` | "Attribute added dynamically by decorator" | "Pylint bug" |
| `ts-ignore` | "Legacy API untyped, validated at runtime" | "TypeScript error" |

---

## Fixing Orphaned Entries

Orphaned entries indicate stale documentation. The suppression was removed from code but the header wasn't updated.

### Step 1: Identify the Orphan

```
src/utils.py:5:4 - Orphaned suppression entry: PLR0912
```

### Step 2: Verify It's Truly Orphaned

Check if the rule ID mismatch is causing the issue:

```python
# Header says:
Suppressions:
    - plr0912: Some reason

# Code has:
# noqa: PLR0912  # Case mismatch!
```

If case mismatch, fix the header to match the code.

### Step 3: Remove or Update

**If suppression was removed from code:** Remove the header entry.

**Before:**
```python
"""
Purpose: Simple utilities

Suppressions:
    - PLR0912: Complex logic (no longer needed)
"""

def simple_function():
    return 1  # No suppression here anymore
```

**After:**
```python
"""
Purpose: Simple utilities
"""

def simple_function():
    return 1
```

---

## Fixing Test Skip Violations

### Test Skips Without Reason

**Violation:**
```
tests/test_api.py:15:0 - Test skip without reason: @pytest.mark.skip
```

**Fix by adding a reason:**

```python
# Before
@pytest.mark.skip
def test_flaky_integration():
    pass

# After
@pytest.mark.skip(reason="Flaky on CI, investigating timeout issue #123")
def test_flaky_integration():
    pass
```

### Allowed Skip Patterns

These patterns are allowed because they have reasons:

```python
@pytest.mark.skip(reason="Waiting for dependency update")  # OK
@pytest.mark.skipif(sys.platform == 'win32', reason="Linux-only feature")  # OK
pytest.skip("Database not available in this environment")  # OK
```

### JavaScript/TypeScript Test Skips

For Jest/Mocha, `it.skip()` and `describe.skip()` are always violations because the reason cannot be provided inline. Use `it.todo()` instead for pending tests:

```typescript
// Before (violation)
it.skip('should process data', () => {
    // test code
});

// After (use todo for pending tests)
it.todo('should process data');  // OK - clearly indicates pending work

// Or fix/remove the test entirely
it('should process data', () => {
    // actually test it
});
```

---

## Common Mistakes to Avoid

### Mistake 1: Adding Suppressions Without Permission

**NEVER do this:**
```python
# Agent just adds the entry without asking
"""
Suppressions:
    - PLR0912: Complex function
"""
```

**ALWAYS do this:**
```
"I found a PLR0912 violation. May I add a suppression with justification?"
```

### Mistake 2: Weak Justifications

**Bad:**
```python
Suppressions:
    - PLR0912: Disable check
    - arg-type: Type error
    - B602: Security warning
```

**Good:**
```python
Suppressions:
    - PLR0912: State machine requires one branch per transition state
    - arg-type: Pydantic handles coercion during model validation
    - B602: Command built from sanitized config values, no user input
```

### Mistake 3: Wrong Rule ID Format

**Bad:**
```python
Suppressions:
    - noqa: PLR0912  # Wrong - includes 'noqa'
    - type:ignore[arg-type]: reason  # Wrong - includes full pattern
    - pylint: disable=no-member  # Wrong - includes 'pylint: disable='
```

**Good:**
```python
Suppressions:
    - PLR0912: reason
    - arg-type: reason
    - no-member: reason
```

### Mistake 4: Assuming Permission Transfers

Permission for one suppression does NOT grant permission for others:

- MyPy permission ≠ Pylint permission
- Permission for file A ≠ permission for file B
- Permission for one rule ≠ permission for another rule

**Always ask separately for each new suppression.**

---

## Configuration Options

### Disable Specific Checks

```yaml
lazy-ignores:
  check_noqa: true           # Detect # noqa
  check_type_ignore: true    # Detect # type: ignore
  check_pylint_disable: true # Detect # pylint: disable
  check_nosec: true          # Detect # nosec
  check_ts_ignore: true      # Detect @ts-ignore
  check_eslint_disable: true # Detect eslint-disable
  check_thailint_ignore: true # Detect # thailint: ignore
  check_test_skips: true     # Detect test skips without reason
  check_orphaned: true       # Detect orphaned entries
```

### Ignore Specific Paths

```yaml
lazy-ignores:
  ignore_patterns:
    - "tests/**"           # Skip test files
    - "**/migrations/**"   # Skip database migrations
    - "**/generated/**"    # Skip generated code
    - "**/vendor/**"       # Skip vendored code
```

---

## The Complete Workflow

### Initial Assessment

```bash
# See all violations
thailint lazy-ignores src/

# Count violations
thailint lazy-ignores --format json src/ | jq '.violations | length'
```

### Process Each Violation

For each unjustified suppression:

1. **Can you fix it?**
   - Try refactoring, proper typing, or design changes
   - If fixed, remove the suppression comment

2. **Is suppression truly necessary?**
   - External API constraints?
   - Framework limitations?
   - Legitimate false positive?

3. **Request approval:**
   ```
   "I need to suppress [rule] in [file:line] because [reason].
    I tried [alternatives]. May I add the suppression?"
   ```

4. **After approval, add entry:**
   ```python
   Suppressions:
       - rule-id: Approved justification from discussion
   ```

### Final Validation

```bash
# Verify all fixed
thailint lazy-ignores src/
echo $?  # Must be 0

# Also run full linting
just lint-full
echo $?  # Must be 0
```

---

## Success Checklist

Before considering lazy-ignores violations fixed:

- [ ] `thailint lazy-ignores src/` exits with code 0
- [ ] All unjustified suppressions have header entries
- [ ] All header entries have meaningful justifications
- [ ] All orphaned entries removed
- [ ] All test skips have reasons
- [ ] Human approved each new suppression entry
- [ ] `just lint-full` still passes

---

## See Also

- **Linting errors**: `.ai/howtos/how-to-fix-linting-errors.md`
- **Refactoring**: `.ai/howtos/how-to-refactor-for-quality.md`
- **Quality standards**: `AGENTS.md` (Quality Gates section)
- **Header standards**: `.ai/docs/FILE_HEADER_STANDARDS.md` (Suppressions section)
- **User documentation**: `docs/lazy-ignores-linter.md`
