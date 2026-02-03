# Clone Abuse Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the clone abuse linter for detecting `.clone()` anti-patterns in Rust code

    **Scope**: Configuration, usage, refactoring patterns, and best practices for clone abuse detection in Rust

    **Overview**: Comprehensive documentation for the clone abuse linter that detects `.clone()` abuse patterns in Rust code. Covers three sub-rules: clone-in-loop (performance-damaging clones inside loops), clone-chain (redundant chained clones), and unnecessary-clone (clones where the source is not reused). Uses tree-sitter AST analysis via RustCloneAnalyzer to walk parent chains for loop detection, inspect receivers for chain detection, and scan subsequent statements for unnecessary clone detection. Helps teams eliminate a common AI-generated Rust anti-pattern where `.clone()` is used as a borrow checker workaround instead of proper ownership, borrowing, or smart pointer strategies.

    **Dependencies**: tree-sitter with Rust grammar for AST parsing, RustBaseAnalyzer for tree-sitter integration

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: [CLI Reference](cli-reference.md) for CLI commands, [Configuration](configuration.md) for config format, [How to Ignore Violations](how-to-ignore-violations.md) for ignore patterns

    **Implementation**: Tree-sitter AST-based detection with parent-chain walking, receiver inspection, and subsequent-statement scanning

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thai-lint
thailint clone-abuse src/
```

**Example output:**
```
src/processor.rs:18 - .clone() called inside a loop body may cause performance issues: let item = data.clone();
  Suggestion: Consider borrowing instead of cloning in a loop. If ownership is needed, use Rc/Arc for shared ownership or collect references.
```

**Fix it:** Replace `.clone()` calls with borrowing, ownership transfer, or smart pointers.

---

## Overview

The clone abuse linter detects `.clone()` abuse patterns in Rust code that indicate improper ownership handling. It analyzes Rust source files using tree-sitter AST parsing to identify clone calls that are unnecessary, redundant, or performance-damaging.

### What is Clone Abuse?

**Clone abuse** occurs when `.clone()` is used as a workaround for the borrow checker instead of properly handling ownership. This is a frequent pattern in AI-generated Rust code, where models reach for `.clone()` to satisfy the compiler rather than designing correct ownership flow:

```rust
// Bad - Clone abuse as borrow checker workaround
fn process_items(items: Vec<String>) {
    for item in &items {
        let owned = item.clone();  // Cloning in a loop
        handle(owned);
    }
}

// Good - Borrow instead of clone
fn process_items(items: Vec<String>) {
    for item in &items {
        handle_ref(item);  // Borrow the reference directly
    }
}
```

### Why Eliminate Clone Abuse?

Clone abuse is problematic because:
- **Performance cost**: `.clone()` performs deep copies, which is expensive for heap-allocated types like `String`, `Vec`, and `HashMap`
- **Hides ownership bugs**: Masking borrow checker errors with clones prevents understanding of data flow
- **Memory waste**: Unnecessary clones duplicate heap allocations that serve no purpose
- **Loop amplification**: Clones inside loops multiply performance costs by iteration count
- **Redundant work**: Chained `.clone().clone()` produces identical results to a single `.clone()`
- **AI anti-pattern**: AI code generators frequently insert `.clone()` to compile code without understanding ownership semantics

### Benefits

- **Improved performance**: Eliminating unnecessary clones reduces allocation overhead
- **Clearer ownership**: Forces explicit ownership design instead of clone-based workarounds
- **Idiomatic Rust**: Encourages borrowing, references, and smart pointers over cloning
- **Better AI output**: Catches a common class of AI-generated Rust mistakes

## How It Works

### Tree-sitter AST Detection

The linter uses tree-sitter with the Rust grammar to analyze code structure:

1. **Parse source code** into an AST using tree-sitter's Rust parser
2. **Find `.clone()` calls** by recursively traversing the AST for `call_expression` nodes where the `field_identifier` is `"clone"`
3. **Classify each call** into one of three abuse patterns (chain, loop, unnecessary)
4. **Filter by context** using configuration (test awareness, path ignoring, pattern toggles)
5. **Report violations** with actionable suggestions for each pattern

### Sub-Rule: `clone-abuse.clone-in-loop`

Detects `.clone()` calls inside loop bodies (`for_expression`, `while_expression`, `loop_expression`).

**Detection method**: Walks the parent chain from the clone call upward. If any ancestor node is a loop expression type, the clone is flagged.

**Why it matters**: Clones inside loops multiply allocation costs by the number of iterations. A clone that takes 100ns per call costs 100ms over 1 million iterations.

```rust
// Detected: clone inside for loop
for item in &items {
    let copy = item.clone();  // clone-abuse.clone-in-loop
    process(copy);
}
```

### Sub-Rule: `clone-abuse.clone-chain`

Detects chained `.clone().clone()` calls where one clone's receiver is itself a `.clone()` call.

**Detection method**: Inspects the receiver of the `field_expression` for the outer clone. If the receiver is a `call_expression` whose method name is also `"clone"`, the chain is flagged.

**Why it matters**: A single `.clone()` produces a fully owned deep copy. Cloning the clone produces an identical copy with double the allocation cost and zero additional value.

```rust
// Detected: chained clone calls
let backup = data.clone().clone();  // clone-abuse.clone-chain
```

### Sub-Rule: `clone-abuse.unnecessary-clone`

Detects `.clone()` calls in `let` declarations where the source identifier does not appear in subsequent statements within the same block.

**Detection method**: Checks three conditions:
1. The clone is inside a `let_declaration` (e.g., `let x = y.clone();`)
2. The receiver `y` is a simple identifier (not `self.field` or `foo.bar()`)
3. The identifier `y` does not appear in any subsequent statement within the enclosing block

**Why it matters**: If the original value is never used after cloning, ownership can be transferred directly with a move, eliminating the allocation entirely.

```rust
// Detected: original 'config' not used after clone
let settings = config.clone();  // clone-abuse.unnecessary-clone
process(settings);
// 'config' never referenced again in this block
```

### Test Awareness

The linter integrates with `is_inside_test()` from `RustBaseAnalyzer` to detect clone calls within `#[test]` functions and `#[cfg(test)]` modules. When `allow_in_tests` is enabled (the default), clones in test code are not flagged, since test code prioritizes clarity over performance.

## Configuration

### Basic Configuration

Create or update `.thailint.yaml`:

```yaml
clone-abuse:
  enabled: true
  allow_in_tests: true
  detect_clone_in_loop: true
  detect_clone_chain: true
  detect_unnecessary_clone: true
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable clone abuse linter |
| `allow_in_tests` | boolean | `true` | Allow `.clone()` in `#[test]` functions and `#[cfg(test)]` modules |
| `detect_clone_in_loop` | boolean | `true` | Detect `.clone()` calls inside loop bodies |
| `detect_clone_chain` | boolean | `true` | Detect chained `.clone().clone()` calls |
| `detect_unnecessary_clone` | boolean | `true` | Detect `.clone()` where the source is not reused |
| `ignore` | array | `["examples/", "benches/", "tests/"]` | File path patterns to exclude from analysis |

### Selective Rule Configuration

Disable individual sub-rules to focus on specific patterns:

```yaml
# Only check for clones in loops (performance-focused)
clone-abuse:
  enabled: true
  detect_clone_in_loop: true
  detect_clone_chain: false
  detect_unnecessary_clone: false
```

```yaml
# Check everything except unnecessary clones (reduces false positives)
clone-abuse:
  enabled: true
  detect_clone_in_loop: true
  detect_clone_chain: true
  detect_unnecessary_clone: false
```

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for the complete ignore guide.

**Quick examples:**

```rust
// Inline suppression (if supported)
let copy = data.clone();  // thailint: ignore[clone-abuse] - Required for FFI boundary

// Add to ignore paths in config
clone-abuse:
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
    - "src/generated/"
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check specific directory
thailint clone-abuse src/

# Check specific file
thailint clone-abuse src/processor.rs

# Recursive scan
thailint clone-abuse --recursive src/
```

#### With Configuration

```bash
# Use config file
thailint clone-abuse --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint clone-abuse src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint clone-abuse src/

# JSON output for CI/CD
thailint clone-abuse --format json src/

# SARIF output for GitHub Code Scanning
thailint clone-abuse --format sarif src/ > report.sarif

# JSON with exit code check
thailint clone-abuse --format json src/ > report.json
echo "Exit code: $?"
```

#### Verbose Mode

```bash
# Enable debug logging
thailint clone-abuse --verbose src/
```

#### Parallel Processing

```bash
# Process files in parallel for large codebases
thailint clone-abuse --parallel src/
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with clone-abuse rule
violations = linter.lint('src/', rules=['clone-abuse'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line} - {v.message}")
```

#### Direct Rule Usage

```python
from src.linters.clone_abuse.linter import CloneAbuseRule
from src.linters.clone_abuse.config import CloneAbuseConfig

# Create rule with custom config
config = CloneAbuseConfig(
    detect_clone_in_loop=True,
    detect_clone_chain=True,
    detect_unnecessary_clone=False,
    allow_in_tests=True,
)
rule = CloneAbuseRule(config=config)
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest clone-abuse /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest clone-abuse \
  --config /config/.thailint.yaml /workspace/src/
```

## Violation Examples

### Example 1: Clone in Loop

**Code with violation:**
```rust
fn collect_names(users: &[User]) -> Vec<String> {
    let mut names = Vec::new();
    for user in users {
        let name = user.name.clone();  // clone-abuse.clone-in-loop
        names.push(name);
    }
    names
}
```

**Violation message:**
```
src/users.rs:4 - .clone() called inside a loop body may cause performance issues: let name = user.name.clone();
  Suggestion: Consider borrowing instead of cloning in a loop. If ownership is needed, use Rc/Arc for shared ownership or collect references.
```

**Refactored code:**
```rust
fn collect_names(users: &[User]) -> Vec<String> {
    users.iter().map(|user| user.name.clone()).collect()
    // Or if references suffice:
    // users.iter().map(|user| &user.name).collect()
}
```

### Example 2: Clone Chain

**Code with violation:**
```rust
fn backup_config(config: &Config) -> Config {
    let backup = config.clone().clone();  // clone-abuse.clone-chain
    backup
}
```

**Violation message:**
```
src/config.rs:2 - Chained .clone().clone() is redundant: let backup = config.clone().clone();
  Suggestion: Chained .clone().clone() is redundant. A single .clone() produces an owned copy; the second clone is unnecessary.
```

**Refactored code:**
```rust
fn backup_config(config: &Config) -> Config {
    config.clone()  // Single clone is sufficient
}
```

### Example 3: Unnecessary Clone

**Code with violation:**
```rust
fn process(data: String) {
    let owned = data.clone();  // clone-abuse.unnecessary-clone
    send(owned);
    // 'data' is never used again in this block
}
```

**Violation message:**
```
src/processor.rs:2 - .clone() may be unnecessary when the original is not used afterward: let owned = data.clone();
  Suggestion: This .clone() may be unnecessary if the original value is not used after cloning. Consider passing ownership directly, borrowing, or using Cow for clone-on-write.
```

**Refactored code:**
```rust
fn process(data: String) {
    send(data);  // Move ownership directly - no clone needed
}
```

### Example 4: Acceptable Contexts (No Violations)

```rust
// Test functions - allowed by default (allow_in_tests: true)
#[test]
fn test_processing() {
    let data = create_test_data();
    let copy = data.clone();  // OK - inside #[test]
    assert_eq!(process(copy), expected);
    assert_eq!(data.len(), 5);
}

// Clone where source IS used afterward - not flagged
fn fork_and_continue(config: Config) {
    let snapshot = config.clone();
    archive(snapshot);
    apply(config);  // 'config' is used after the clone
}

// Files in ignored paths - not flagged
// examples/demo.rs, benches/benchmark.rs, tests/integration.rs
```

## Refactoring Patterns

### Pattern 1: Borrow Instead of Clone

Replace `.clone()` with a reference when the function only needs to read the data.

**Before:**
```rust
fn print_summary(report: &Report) {
    let title = report.title.clone();
    println!("Report: {}", title);
}
```

**After:**
```rust
fn print_summary(report: &Report) {
    println!("Report: {}", &report.title);
}
```

**When to use**: The consuming code only reads the value and does not need ownership.

### Pattern 2: Use Rc/Arc for Shared Ownership

Replace `.clone()` with reference-counted pointers when multiple owners need access to the same data.

**Before:**
```rust
fn spawn_workers(config: &Config) {
    for i in 0..4 {
        let cfg = config.clone();  // Deep copy per thread
        std::thread::spawn(move || {
            worker(i, cfg);
        });
    }
}
```

**After:**
```rust
use std::sync::Arc;

fn spawn_workers(config: Config) {
    let shared_config = Arc::new(config);
    for i in 0..4 {
        let cfg = Arc::clone(&shared_config);  // Cheap reference count increment
        std::thread::spawn(move || {
            worker(i, &cfg);
        });
    }
}
```

**When to use**: Multiple threads or owners need access to the same data. `Rc` for single-threaded, `Arc` for multi-threaded contexts.

### Pattern 3: Use Cow for Clone-on-Write

Replace `.clone()` with `Cow` when the value is read most of the time but occasionally needs mutation.

**Before:**
```rust
fn normalize(input: &str) -> String {
    let result = input.to_string();  // Always allocates
    if result.contains("  ") {
        result.replace("  ", " ")
    } else {
        result
    }
}
```

**After:**
```rust
use std::borrow::Cow;

fn normalize(input: &str) -> Cow<'_, str> {
    if input.contains("  ") {
        Cow::Owned(input.replace("  ", " "))  // Allocate only when needed
    } else {
        Cow::Borrowed(input)  // Zero-cost borrow
    }
}
```

**When to use**: The value is conditionally modified. Cow avoids allocation in the common (unmodified) case.

### Pattern 4: Pass Ownership Directly (Move Semantics)

Replace `.clone()` followed by a move with a direct ownership transfer.

**Before:**
```rust
fn process(data: String) {
    let copy = data.clone();
    consume(copy);
    // 'data' is never used again
}
```

**After:**
```rust
fn process(data: String) {
    consume(data);  // Transfer ownership directly
}
```

**When to use**: The original value is not referenced after the clone. Rust's move semantics handle ownership transfer at zero cost.

### Pattern 5: Collect References Instead of Owned Values

Replace a loop that clones into a collection with one that collects references.

**Before:**
```rust
fn get_active_names(users: &[User]) -> Vec<String> {
    let mut names = Vec::new();
    for user in users {
        if user.active {
            names.push(user.name.clone());  // Clone per iteration
        }
    }
    names
}
```

**After:**
```rust
fn get_active_names(users: &[User]) -> Vec<&str> {
    users
        .iter()
        .filter(|u| u.active)
        .map(|u| u.name.as_str())
        .collect()
}
```

**When to use**: The calling code only needs to read the collected values, not own them. The returned references borrow from the input slice.

### Pattern 6: Use Iterator Adaptors

Replace clone-in-loop patterns with iterator chains that express the transformation declaratively.

**Before:**
```rust
fn transform(items: &[Item]) -> Vec<Output> {
    let mut results = Vec::new();
    for item in items {
        let cloned = item.clone();
        results.push(cloned.into_output());
    }
    results
}
```

**After:**
```rust
fn transform(items: &[Item]) -> Vec<Output> {
    items.iter().map(|item| item.to_output()).collect()
}
```

**When to use**: The loop body clones, transforms, and collects. Iterator adaptors avoid intermediate owned values.

### Pattern 7: Accept Generic References

Redesign function signatures to accept references or generic bounds instead of requiring owned values.

**Before:**
```rust
fn validate(name: String) -> bool {
    name.len() > 0 && name.len() < 100
}

// Caller must clone:
let valid = validate(user.name.clone());
```

**After:**
```rust
fn validate(name: &str) -> bool {
    !name.is_empty() && name.len() < 100
}

// Caller borrows:
let valid = validate(&user.name);
```

**When to use**: The function only reads the value. Accepting `&str` instead of `String` (or `&T` instead of `T`) eliminates the need for callers to clone.

## Language Support

### Rust

**Fully Supported**

The clone abuse linter targets Rust exclusively, where `.clone()` abuse is a significant concern due to ownership semantics.

**Patterns detected:**
- `.clone()` inside `for_expression`, `while_expression`, `loop_expression`
- Chained `.clone().clone()` via receiver inspection
- Unnecessary `.clone()` in `let` declarations where the source is unused afterward

**Test-aware contexts:**
- `#[test]` annotated functions
- `#[cfg(test)]` annotated modules

**AST parser**: tree-sitter with Rust grammar

### Other Languages

Clone abuse detection applies specifically to Rust due to the language's ownership model. Other languages handle value semantics differently (garbage collection, reference counting, copy-on-write) and do not exhibit this class of anti-pattern in the same way.

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  clone-abuse-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thai-lint

      - name: Check for clone abuse
        run: |
          thailint clone-abuse src/

      - name: Upload SARIF (optional)
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: clone-abuse.sarif
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

To include SARIF upload, generate the report first:

```yaml
      - name: Check for clone abuse (SARIF)
        run: |
          thailint clone-abuse --format sarif src/ > clone-abuse.sarif || true
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: clone-abuse-check
        name: Check for clone abuse
        entry: thailint clone-abuse
        language: python
        types: [rust]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-clone-abuse:
	@echo "=== Checking for clone abuse ==="
	@poetry run thailint clone-abuse src/ || exit 1

lint-rust: lint-clone-abuse
	@echo "All Rust checks passed"

lint-all: lint-rust
	@echo "All checks passed"
```

## Performance

The clone abuse linter is designed for speed with tree-sitter's incremental parsing:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse (tree-sitter) | ~5-20ms | <50ms |
| Single file analysis | ~3-10ms | <30ms |
| 100 Rust files | ~300-500ms | <2s |
| 1000 Rust files | ~2-4s | <10s |

**Optimizations:**
- Tree-sitter parsing provides near-instant AST construction
- Pattern classification uses early-exit priority ordering (chain checked before loop)
- Parent-chain walking terminates as soon as a match is found
- Test-awareness and path filtering skip files before AST analysis
- Parallel mode distributes file processing across threads

## Troubleshooting

### Common Issues

**Issue: Clones in test code are flagged**

```rust
#[test]
fn test_process() {
    let data = setup();
    let copy = data.clone();  // Flagged unexpectedly
}
```

```yaml
# Solution: Ensure allow_in_tests is enabled (default)
clone-abuse:
  allow_in_tests: true
```

**Issue: Clones in example files are flagged**

```bash
# Problem: examples/ not in ignore list
# Solution: Add to ignore paths
clone-abuse:
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
```

**Issue: False positive on necessary clone**

```rust
fn fork(data: &Data) {
    let branch_a = data.clone();
    let branch_b = data.clone();  // Both clones are necessary
    process_a(branch_a);
    process_b(branch_b);
}
```

This is handled correctly: `data` is used after both clones, so `unnecessary-clone` does not fire. If a false positive occurs, verify that the source identifier appears in subsequent statements.

**Issue: tree-sitter not available**

```bash
# Problem: tree-sitter Rust grammar not installed
pip install tree-sitter-rust

# Verify tree-sitter availability
python -c "from src.analyzers.rust_base import RustBaseAnalyzer; print(RustBaseAnalyzer().tree_sitter_available)"
```

When tree-sitter is unavailable, the analyzer returns an empty list of violations (safe fallback).

**Issue: Specific sub-rule produces too many results**

```yaml
# Solution: Disable the noisy sub-rule
clone-abuse:
  detect_clone_in_loop: true
  detect_clone_chain: true
  detect_unnecessary_clone: false  # Disable if too many false positives
```

**Issue: Violations in generated code**

```yaml
# Solution: Add generated code paths to ignore list
clone-abuse:
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
    - "src/generated/"
    - "src/proto/"
```

## Best Practices

### 1. Prefer Borrowing Over Cloning

Design functions to accept references (`&T`, `&str`, `&[T]`) instead of owned values. This eliminates the need for callers to clone.

```rust
// Bad - requires caller to clone or give up ownership
fn validate(name: String) -> bool {
    !name.is_empty()
}

// Good - borrows without allocation
fn validate(name: &str) -> bool {
    !name.is_empty()
}
```

### 2. Use Smart Pointers for Shared Data

When multiple components need access to the same data, use `Rc` (single-threaded) or `Arc` (multi-threaded) instead of cloning.

```rust
use std::sync::Arc;

// Good - shared ownership via Arc
let config = Arc::new(load_config());
let worker_config = Arc::clone(&config);  // Cheap: increments reference count
```

### 3. Move Instead of Clone When Source is Unused

If the original variable is not needed after the clone, transfer ownership directly.

```rust
// Bad - clone then discard original
let processed = data.clone();
consume(processed);

// Good - move ownership
consume(data);
```

### 4. Use Cow for Conditional Mutation

When data is read most of the time but occasionally modified, `Cow` avoids allocation in the common case.

```rust
use std::borrow::Cow;

fn sanitize(input: &str) -> Cow<'_, str> {
    if input.contains('<') {
        Cow::Owned(input.replace('<', "&lt;"))
    } else {
        Cow::Borrowed(input)
    }
}
```

### 5. Audit AI-Generated Clone Calls

AI code generators frequently insert `.clone()` to satisfy the borrow checker without understanding ownership. Every `.clone()` in AI-generated Rust code should be reviewed and justified:

- **Does the function need to own the data?** If not, accept a reference.
- **Is the original used after cloning?** If not, move instead of clone.
- **Is the clone inside a hot loop?** If so, restructure to clone outside or use references.
- **Are multiple clones sharing the same data?** If so, use `Rc`/`Arc`.

### 6. Enable All Sub-Rules Initially

Start with all three detection patterns enabled. Disable individual sub-rules only after evaluating which patterns produce actionable results for the specific codebase.

```yaml
# Recommended starting configuration
clone-abuse:
  enabled: true
  allow_in_tests: true
  detect_clone_in_loop: true
  detect_clone_chain: true
  detect_unnecessary_clone: true
```

### 7. Integrate Early in CI/CD

Add clone abuse checks to the CI pipeline alongside other linters. Catching clone abuse at the pull request stage prevents performance regressions from merging.

```yaml
# Add alongside other Rust quality checks
- name: Rust quality checks
  run: |
    thailint clone-abuse src/
    thailint unwrap-abuse src/
    thailint blocking-async src/
```

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation
- **[Unwrap Abuse Linter](https://thai-lint.readthedocs.io/en/latest/unwrap-abuse-linter/)** - Related Rust linter for `.unwrap()` patterns
- **[Blocking Async Linter](https://thai-lint.readthedocs.io/en/latest/blocking-async-linter/)** - Related Rust linter for blocking operations in async functions
