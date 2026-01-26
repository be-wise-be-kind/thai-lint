# Lazy Ignores Linter

**Purpose**: Complete guide to using the lazy-ignores linter for detecting and fixing unjustified linting suppressions

**Scope**: Configuration, usage, suppression declaration, and best practices for AI-generated code governance

**Overview**: Comprehensive documentation for the lazy-ignores linter that detects when AI agents add linting suppressions (`# noqa`, `# type: ignore`, `# pylint: disable`, `@ts-ignore`, etc.) without proper justification. Uses a header-based declaration model where all suppressions must be documented in the file header's `Suppressions:` section with human-approved justifications. This enforces that AI assistants cannot silently bypass quality gates. The linter also detects orphaned entries (declared but not used) and test skips without reasons.

**Dependencies**: tree-sitter (TypeScript parser), Python AST module, file header linter infrastructure

**Exports**: Usage documentation, configuration examples, suppression declaration patterns

**Related**: cli-reference.md for CLI commands, configuration.md for config format, FILE_HEADER_STANDARDS.md for Suppressions section format

**Implementation**: Header-based suppression declaration model with AST-based detection and orphaned entry validation

---

## Try It Now

```bash
pip install thai-lint
thailint lazy-ignores src/
```

**Example output:**
```
src/utils.py:45:20 - Unjustified suppression: # noqa: PLR0912
  To fix, add entry to file header Suppressions section:

      Suppressions:
          - PLR0912: [Your justification here]

  IMPORTANT: Suppression requires human approval. Do not add
  without explicit permission from a human reviewer.
```

**Fix it:** Add a `Suppressions:` section to the file header with a justification for each ignore.

---

## Overview

The lazy-ignores linter enforces that all linting suppressions in code are justified and documented. It catches a common AI assistant anti-pattern: adding `# noqa`, `# type: ignore`, or `# pylint: disable` comments to make linting errors disappear without addressing the underlying issue.

### The Problem

AI coding assistants frequently add suppression comments to bypass linting errors:

```python
# BAD - AI added these to silence linters without explanation
result = complex_function()  # noqa: PLR0912
data = api_call()  # type: ignore[arg-type]
subprocess.run(cmd, shell=True)  # nosec B602
```

This behavior:
- **Hides real issues**: The suppression may mask a genuine bug or security vulnerability
- **Bypasses quality gates**: Linting rules exist for good reasons
- **Creates technical debt**: No one knows why the ignore was added
- **Reduces code quality**: AI assistants take shortcuts without human oversight

### The Solution

The lazy-ignores linter requires all suppressions to be:
1. **Documented** in the file header's `Suppressions:` section
2. **Justified** with an explanation of why the ignore is legitimate
3. **Human-approved** before being added

```python
"""
Purpose: Complex data processing utilities

Suppressions:
    - PLR0912: State machine implementation requires complex branching (reviewed 2024-01)
    - arg-type: Pydantic model coercion handles type conversion
    - B602: Subprocess call uses trusted, sanitized input from config
"""

result = complex_function()  # noqa: PLR0912
data = api_call()  # type: ignore[arg-type]
subprocess.run(cmd, shell=True)  # nosec B602
```

### Benefits

- **AI Governance**: AI assistants cannot silently bypass quality gates
- **Documentation**: Every suppression has a recorded justification
- **Auditability**: Easy to review and reconsider suppressions later
- **Code Quality**: Encourages fixing issues rather than ignoring them
- **Human Oversight**: Ensures human approval for all exceptions

## How It Works

### Detection Process

1. **Scan source files** for ignore directive patterns:
   - Python: `# noqa`, `# type: ignore`, `# pylint: disable`, `# nosec`
   - TypeScript/JavaScript: `@ts-ignore`, `@ts-nocheck`, `@ts-expect-error`, `eslint-disable`
   - thai-lint: `# thailint: ignore`
   - Test skips: `@pytest.mark.skip` without reason, `it.skip()`, `describe.skip()`

2. **Parse file headers** to find `Suppressions:` section entries

3. **Match ignores to declarations** by normalizing rule IDs:
   - `PLR0912` matches `plr0912` (case-insensitive)
   - `type:ignore[arg-type]` matches `arg-type`
   - `nosec B602` matches `B602`

4. **Report violations** for:
   - **Unjustified ignores**: Suppression in code without matching header entry
   - **Orphaned entries**: Header entry without matching suppression in code

### Supported Patterns

#### Python Patterns

| Pattern | Example | Rule ID Extracted |
|---------|---------|-------------------|
| `# noqa` | `# noqa: PLR0912, PLR0915` | `PLR0912`, `PLR0915` |
| `# type: ignore` | `# type: ignore[arg-type]` | `arg-type` |
| `# pyright: ignore` | `# pyright: ignore[reportPrivateImportUsage]` | `reportPrivateImportUsage` |
| `# pylint: disable` | `# pylint: disable=no-member` | `no-member` |
| `# nosec` | `# nosec B602` | `B602` |
| `# thailint: ignore` | `# thailint: ignore[nesting]` | `nesting` |

#### TypeScript/JavaScript Patterns

| Pattern | Example | Rule ID Extracted |
|---------|---------|-------------------|
| `@ts-ignore` | `// @ts-ignore` | (no rule ID) |
| `@ts-nocheck` | `// @ts-nocheck` | (no rule ID) |
| `@ts-expect-error` | `// @ts-expect-error` | (no rule ID) |
| `eslint-disable` | `// eslint-disable-next-line no-console` | `no-console` |
| `eslint-disable` (block) | `/* eslint-disable react/prop-types */` | `react/prop-types` |

#### Test Skip Patterns

| Pattern | Example | Violation Trigger |
|---------|---------|-------------------|
| `@pytest.mark.skip` | `@pytest.mark.skip` | Skip without reason |
| `@pytest.mark.skip()` | `@pytest.mark.skip()` | Skip without reason |
| `pytest.skip()` | `pytest.skip()` | Skip without reason |
| `it.skip()` | `it.skip('test name', ...)` | Always (use `it.todo()` instead) |
| `describe.skip()` | `describe.skip('suite', ...)` | Always |
| `test.skip()` | `test.skip('test', ...)` | Always |

**Allowed Test Skip Patterns:**
```python
@pytest.mark.skip(reason="Flaky on CI, investigating #123")  # OK - has reason
@pytest.mark.skipif(sys.platform == 'win32', reason="Windows-specific")  # OK
pytest.skip("Database not available")  # OK - has reason string
```

## Configuration

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
lazy-ignores:
  enabled: true
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable lazy-ignores linter |
| `check_noqa` | boolean | `true` | Detect `# noqa` patterns |
| `check_type_ignore` | boolean | `true` | Detect `# type: ignore` patterns |
| `check_pylint_disable` | boolean | `true` | Detect `# pylint: disable` patterns |
| `check_nosec` | boolean | `true` | Detect `# nosec` patterns |
| `check_ts_ignore` | boolean | `true` | Detect `@ts-ignore`, `@ts-nocheck`, `@ts-expect-error` |
| `check_eslint_disable` | boolean | `true` | Detect `eslint-disable` patterns |
| `check_thailint_ignore` | boolean | `true` | Detect `# thailint: ignore` patterns |
| `check_test_skips` | boolean | `true` | Detect test skips without reasons |
| `check_orphaned` | boolean | `true` | Detect header entries without matching ignores |
| `ignore_patterns` | list[str] | `["tests/**"]` | File patterns to exclude |

### Full Configuration Example

```yaml
lazy-ignores:
  enabled: true

  # Pattern detection toggles
  check_noqa: true
  check_type_ignore: true
  check_pylint_disable: true
  check_nosec: true
  check_ts_ignore: true
  check_eslint_disable: true
  check_thailint_ignore: true
  check_test_skips: true

  # Orphaned detection
  check_orphaned: true

  # Files/directories to ignore
  ignore_patterns:
    - "tests/**"
    - "**/migrations/**"
    - "**/generated/**"
```

### Recommended Configurations

#### Strict (For New Projects)

```yaml
lazy-ignores:
  enabled: true
  check_orphaned: true
  ignore_patterns: []  # Enforce everywhere, including tests
```

#### Standard (For Most Projects)

```yaml
lazy-ignores:
  enabled: true
  check_orphaned: true
  ignore_patterns:
    - "tests/**"  # Don't enforce in test files
```

#### Lenient (For Legacy Code)

```yaml
lazy-ignores:
  enabled: true
  check_orphaned: false  # Don't flag stale entries
  check_test_skips: false  # Allow lazy test skips
  ignore_patterns:
    - "tests/**"
    - "legacy/**"
```

### JSON Configuration

```json
{
  "lazy-ignores": {
    "enabled": true,
    "check_noqa": true,
    "check_type_ignore": true,
    "check_pylint_disable": true,
    "check_nosec": true,
    "check_ts_ignore": true,
    "check_eslint_disable": true,
    "check_test_skips": true,
    "check_orphaned": true,
    "ignore_patterns": ["tests/**"]
  }
}
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thailint lazy-ignores

# Check specific directory
thailint lazy-ignores src/

# Check specific file
thailint lazy-ignores src/main.py
```

#### With Options

```bash
# Disable orphaned detection
thailint lazy-ignores --no-check-orphaned src/

# Skip test skip detection
thailint lazy-ignores --no-check-test-skips src/

# Check a specific minimum number of unjustified ignores
thailint lazy-ignores src/
```

#### With Config File

```bash
# Use config file
thailint lazy-ignores --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint lazy-ignores src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint lazy-ignores src/

# JSON output for CI/CD
thailint lazy-ignores --format json src/

# SARIF for GitHub Code Scanning
thailint lazy-ignores --format sarif src/ > results.sarif
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint lazy-ignores /workspace/src/

# With config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint lazy-ignores --config /config/.thailint.yaml /workspace/src/
```

## Suppression Declaration Format

### Python Files

Add a `Suppressions:` section to your file header docstring:

```python
"""
Purpose: Complex data processing utilities

Scope: Data transformation and validation

Overview: Provides utilities for processing complex data structures
    with type coercion and validation.

Suppressions:
    - PLR0912: State machine implementation requires complex branching
    - arg-type: Pydantic model coercion handles type conversion
    - B602: Subprocess call uses trusted, sanitized input from config
"""

def complex_state_machine():  # noqa: PLR0912
    # ... complex logic ...
    pass

def call_api(data):
    result = api.process(data)  # type: ignore[arg-type]
    return result

def run_trusted_command():
    subprocess.run(cmd, shell=True)  # nosec B602
```

### TypeScript/JavaScript Files

Add a `Suppressions:` section to your JSDoc header:

```typescript
/**
 * Purpose: Legacy API integration module
 *
 * Scope: Third-party API communication
 *
 * Overview: Handles communication with legacy API that uses
 *   dynamic typing and untyped responses.
 *
 * Suppressions:
 *   - ts-ignore: Legacy API returns untyped data, types added at runtime
 *   - no-console: Debug logging required for API tracing
 */

// @ts-ignore - Legacy API response
const data = await legacyApi.fetch();

console.log('API trace:', data);  // eslint-disable-line no-console
```

### Format Rules

1. **Each suppression on its own line** with `- rule-id: justification`
2. **Rule IDs should match** what appears in the code:
   - Use `PLR0912` not `plr0912` (convention is uppercase)
   - Use `arg-type` not `type:ignore[arg-type]` (just the error code)
   - Use `B602` not `nosec B602` (just the rule ID)
3. **Justifications explain WHY**, not WHAT:
   - Good: "State machine implementation requires complex branching"
   - Bad: "Disables too-many-branches check"

### Example Justifications

| Rule ID | Good Justification | Bad Justification |
|---------|-------------------|-------------------|
| `PLR0912` | "State machine requires complex branching for all states" | "Too many branches" |
| `arg-type` | "Pydantic model handles coercion at validation time" | "Type mismatch" |
| `B602` | "Command from trusted config, user input sanitized" | "Shell is needed" |
| `no-member` | "Dynamic attribute added by metaclass decorator" | "Pylint doesn't understand" |
| `ts-ignore` | "Legacy API returns untyped data, runtime validation applied" | "TypeScript error" |

## Violation Examples

### Example 1: Unjustified Python Suppression

**Code with violation:**
```python
"""
Purpose: User validation utilities
"""

def validate_user(user):
    result = check_complex_rules(user)  # noqa: PLR0912
    return result
```

**Violation message:**
```
src/validators.py:7:40 - Unjustified suppression: # noqa: PLR0912

  To fix, add entry to file header Suppressions section:

      Suppressions:
          - PLR0912: [Your justification here]

  IMPORTANT: Suppression requires human approval. Do not add
  without explicit permission from a human reviewer.
```

**Fixed code:**
```python
"""
Purpose: User validation utilities

Suppressions:
    - PLR0912: Multi-factor validation requires checking all auth methods
"""

def validate_user(user):
    result = check_complex_rules(user)  # noqa: PLR0912
    return result
```

### Example 2: Orphaned Header Entry

**Code with violation:**
```python
"""
Purpose: Simple utility functions

Suppressions:
    - PLR0912: Complex branching required
"""

def simple_add(a, b):
    return a + b  # No PLR0912 ignore in code!
```

**Violation message:**
```
src/utils.py:5:4 - Orphaned suppression entry: PLR0912

  The header declares a suppression for 'PLR0912' but no matching
  ignore directive exists in the code.

  Either:
  1. Remove the orphaned entry from the Suppressions section
  2. Verify the rule ID matches exactly (case-sensitive)
```

### Example 3: TypeScript Violation

**Code with violation:**
```typescript
/**
 * Purpose: API client module
 */

// @ts-ignore
const response = await fetchData();
```

**Violation message:**
```
src/api.ts:6:0 - Unjustified suppression: // @ts-ignore

  To fix, add entry to file header Suppressions section:

      Suppressions:
        - ts-ignore: [Your justification here]

  IMPORTANT: Suppression requires human approval.
```

### Example 4: Test Skip Without Reason

**Code with violation:**
```python
import pytest

@pytest.mark.skip
def test_flaky_integration():
    # Test that sometimes fails
    pass
```

**Violation message:**
```
tests/test_integration.py:3:0 - Test skip without reason: @pytest.mark.skip

  Test skips should include a reason explaining why the test is skipped.

  Fix by adding a reason:
      @pytest.mark.skip(reason="Flaky on CI, tracking issue #123")
```

**Fixed code:**
```python
import pytest

@pytest.mark.skip(reason="Flaky on CI, investigating intermittent timeout #123")
def test_flaky_integration():
    # Test that sometimes fails
    pass
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lazy-ignores-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install thailint
        run: pip install thai-lint

      - name: Check for unjustified suppressions
        run: thailint lazy-ignores src/

      - name: Upload SARIF (optional)
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: lazy-ignores.sarif
        continue-on-error: true
```

### GitHub Actions with SARIF

```yaml
name: Code Scanning

on: [push, pull_request]

jobs:
  lazy-ignores:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install thailint
        run: pip install thai-lint

      - name: Run lazy-ignores check
        run: thailint lazy-ignores --format sarif src/ > lazy-ignores.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: lazy-ignores.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: lazy-ignores
        name: Check unjustified suppressions
        entry: thailint lazy-ignores
        language: python
        types: [python]
        pass_filenames: false
```

### Makefile Integration

```makefile
lint-lazy-ignores:
	@echo "=== Checking for unjustified suppressions ==="
	@poetry run thailint lazy-ignores src/ || exit 1

lint-all: lint-lazy-ignores
	@echo "All checks passed"
```

### Justfile Integration

```just
# Check for unjustified suppressions
lint-lazy-ignores:
    @echo "=== Checking for unjustified suppressions ==="
    poetry run thailint lazy-ignores src/

# Full linting including lazy-ignores
lint-full: lint lint-lazy-ignores lint-complexity lint-solid
```

## Language Support

### Python Support

**Fully Supported**

**Patterns detected:**
- `# noqa` with optional rule IDs (e.g., `# noqa: PLR0912, PLR0915`)
- `# type: ignore` with optional error codes (e.g., `# type: ignore[arg-type]`)
- `# pylint: disable=rule-name` (e.g., `# pylint: disable=no-member`)
- `# nosec` with optional rule IDs (e.g., `# nosec B602`)
- `# thailint: ignore[rule]` (thai-lint's own ignore directive)
- `@pytest.mark.skip` without reason
- `pytest.skip()` without reason string

**Header format:** Python docstrings (triple-quoted strings)

### TypeScript/JavaScript Support

**Fully Supported**

**Patterns detected:**
- `// @ts-ignore`
- `// @ts-nocheck`
- `// @ts-expect-error`
- `// eslint-disable-next-line rule-name`
- `// eslint-disable-line rule-name`
- `/* eslint-disable rule-name */` (block)
- `it.skip()`, `describe.skip()`, `test.skip()` (Jest/Mocha)

**Header format:** JSDoc comments (`/** ... */`)

## Best Practices

### 1. Fix Rather Than Suppress

Before adding a suppression, try to fix the underlying issue:

```python
# Instead of this:
def complex_function():  # noqa: PLR0912
    if a:
        if b:
            if c:
                # deeply nested logic

# Do this:
def complex_function():
    if not a:
        return
    if not b:
        return
    if not c:
        return
    # flattened logic
```

### 2. Be Specific with Rule IDs

```python
# BAD - Suppresses all checks
result = foo()  # noqa

# GOOD - Suppresses only the specific rule
result = foo()  # noqa: PLR0912
```

### 3. Group Related Suppressions

```python
"""
Suppressions:
    - PLR0912: State machine complexity (all methods in this module)
    - PLR0915: Related to PLR0912, same state machine logic
"""
```

### 4. Include Context in Justifications

```python
"""
Suppressions:
    - B602: Shell command from trusted config file, input sanitized by ConfigValidator
    - arg-type: Pydantic v2 handles coercion, type error is false positive
"""
```

### 5. Review Suppressions Periodically

Set up a periodic review to check if suppressions are still needed:
- Remove orphaned entries
- Reconsider if fixes are now possible
- Update justifications if context has changed

### 6. Never Auto-Add Suppressions

AI assistants should **never** add suppression comments without human approval:

```
"I'm encountering a MyPy error on line 45. I've tried several approaches
but cannot resolve it without a type: ignore. May I add a suppression
with the justification 'Dynamic attribute from decorator'?"
```

## Troubleshooting

### Issue: False Positives on Legitimate Patterns

Some patterns may be flagged incorrectly. Check:

1. **Rule ID normalization**: Ensure the header entry matches the code
   - Code: `# noqa: PLR0912` → Header: `PLR0912`
   - Code: `# type: ignore[arg-type]` → Header: `arg-type`

2. **File exclusion**: Add to `ignore_patterns` if file should be excluded

```yaml
lazy-ignores:
  ignore_patterns:
    - "src/legacy/**"
    - "**/vendor/**"
```

### Issue: Orphaned Entries Not Detected

Orphaned detection requires exact rule ID matching:

```python
# Header says:
#   - plr0912: justification

# Code has:
#   # noqa: PLR0912

# These DON'T match! Use consistent casing.
```

### Issue: TypeScript Files Not Scanned

Ensure files have `.ts` or `.tsx` extension:

```bash
# Verify TypeScript parsing
thailint lazy-ignores --verbose src/file.ts
```

## API Reference

### Configuration Class

```python
@dataclass
class LazyIgnoresConfig:
    check_noqa: bool = True
    check_type_ignore: bool = True
    check_pylint_disable: bool = True
    check_nosec: bool = True
    check_ts_ignore: bool = True
    check_eslint_disable: bool = True
    check_thailint_ignore: bool = True
    check_test_skips: bool = True
    check_orphaned: bool = True
    ignore_patterns: list[str] = field(default_factory=list)
```

### Rule Class

```python
class LazyIgnoresRule(BaseLintRule):
    rule_id: str = "lazy-ignores.unjustified"
    rule_name: str = "Unjustified Suppression"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file for unjustified suppressions."""
```

### Violation Types

| Rule ID | Description |
|---------|-------------|
| `lazy-ignores.unjustified` | Suppression in code without header entry |
| `lazy-ignores.orphaned` | Header entry without matching code suppression |
| `lazy-ignores.test-skip-no-reason` | Test skip without reason parameter |

## Resources

- **CLI Reference**: `docs/cli-reference.md` - Complete CLI documentation
- **Configuration Guide**: `docs/configuration.md` - Config file reference
- **File Header Standards**: `.ai/docs/FILE_HEADER_STANDARDS.md` - Suppressions section format
- **How to Fix**: `.ai/howtos/how-to-fix-lazy-ignores.md` - AI agent fix guide

## Contributing

Report issues or suggest improvements:
- GitHub Issues: https://github.com/be-wise-be-kind/thai-lint/issues
- Feature requests: Tag with `enhancement`
- Bug reports: Tag with `bug`
