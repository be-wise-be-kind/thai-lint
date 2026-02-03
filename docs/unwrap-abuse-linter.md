# Unwrap Abuse Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the unwrap abuse linter for detecting `.unwrap()` and `.expect()` calls in Rust code that may panic at runtime

    **Scope**: Configuration, usage, refactoring patterns, and best practices for unwrap/expect abuse detection

    **Overview**: Comprehensive documentation for the unwrap abuse linter that detects `.unwrap()` and `.expect()` calls in Rust code. Covers how the linter works using tree-sitter AST analysis, configuration options (including test-aware filtering), CLI and library usage, Rust code examples with safer alternatives, common refactoring patterns using the `?` operator, `unwrap_or()`, `unwrap_or_default()`, `match`/`if let`, and `anyhow::Context`, and integration with CI/CD pipelines. Helps teams write more robust Rust code by encouraging explicit error handling instead of panicking.

    **Dependencies**: tree-sitter-rust (AST parsing), src.analyzers.rust_base (base analyzer)

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: Tree-sitter AST-based detection with test-aware filtering and configurable allow/ignore rules

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thai-lint
thailint unwrap-abuse src/
```

**Example output:**
```
src/main.rs:15 - .unwrap() call may panic at runtime: let config = File::open("config.toml").unwrap();
  Suggestion: Use the ? operator, .unwrap_or(), .unwrap_or_default(), or match/if-let for safe error handling.
```

**Fix it:** Replace `.unwrap()` calls with the `?` operator, `unwrap_or()`, `unwrap_or_default()`, or `match`/`if let` expressions for safe error handling.

---

## Overview

The unwrap abuse linter detects `.unwrap()` and `.expect()` calls in Rust code that may panic at runtime. It analyzes Rust source files using tree-sitter AST parsing to identify method calls that bypass proper error handling.

### What is Unwrap Abuse?

**Unwrap abuse** is the practice of calling `.unwrap()` or `.expect()` on `Result<T, E>` or `Option<T>` values without handling the error or `None` case. These calls panic if the value is `Err` or `None`, crashing the program:

```rust
// Bad - panics if file doesn't exist
fn load_config() -> Config {
    let file = File::open("config.toml").unwrap();
    let contents = std::io::read_to_string(file).unwrap();
    toml::from_str(&contents).unwrap()
}

// Good - propagates errors to caller
fn load_config() -> Result<Config, Box<dyn Error>> {
    let file = File::open("config.toml")?;
    let contents = std::io::read_to_string(file)?;
    let config = toml::from_str(&contents)?;
    Ok(config)
}
```

### Why Eliminate Unwrap Abuse?

Unwrap abuse is problematic because:
- **Runtime panics**: `.unwrap()` crashes the program on unexpected input
- **Poor error messages**: Bare `.unwrap()` provides no context about why it failed
- **Fragile code**: Works during development but fails in production with edge cases
- **Hides error paths**: Skips error handling rather than addressing failure scenarios
- **Infectious pattern**: AI-generated code frequently uses `.unwrap()` as a shortcut

### Benefits

- **Robustness**: Programs handle errors gracefully instead of crashing
- **Better diagnostics**: Error messages propagate context about what went wrong
- **Production safety**: Code handles edge cases that only appear under real workloads
- **Idiomatic Rust**: Follows Rust community best practices for error handling
- **Team consistency**: Enforces shared code quality standards for error handling

---

## How It Works

### Tree-Sitter AST Detection

The linter uses tree-sitter AST parsing to analyze Rust code structure:

1. **Parse source code** into AST using `tree-sitter-rust`

2. **Find method calls** by traversing the AST for `call_expression` nodes:
   - Inspects `field_expression` children for `field_identifier` nodes
   - Matches method names `"unwrap"` or `"expect"`

3. **Determine test context** for each call:
   - Checks if the call is inside a `#[test]` function
   - Checks if the call is inside a `#[cfg(test)]` module
   - Uses `is_inside_test()` from the base Rust analyzer

4. **Apply configuration filters**:
   - Skip calls in test code (if `allow_in_tests` is enabled)
   - Skip `.expect()` calls (if `allow_expect` is enabled)
   - Skip files matching ignore patterns

5. **Report violations** with suggestions for safer alternatives

### Rule IDs

| Rule ID | Trigger | Description |
|---------|---------|-------------|
| `unwrap-abuse.unwrap-call` | `.unwrap()` | Bare unwrap call without error context |
| `unwrap-abuse.expect-call` | `.expect()` | Expect call with message, still panics |

### Test-Aware Detection

The linter understands Rust test conventions and skips calls inside test code by default:

```rust
// Skipped - inside #[test] function
#[test]
fn test_parsing() {
    let result = parse("input").unwrap();  // OK in tests
    assert_eq!(result, expected);
}

// Skipped - inside #[cfg(test)] module
#[cfg(test)]
mod tests {
    fn helper() {
        let val = compute().unwrap();  // OK in test modules
    }
}

// Flagged - production code
fn process_request(input: &str) -> Response {
    let data = parse(input).unwrap();  // VIOLATION
    build_response(data)
}
```

---

## Configuration

### Basic Configuration

Create `.thailint.yaml`:

```yaml
unwrap-abuse:
  enabled: true
  allow_in_tests: true        # Allow in #[test] and #[cfg(test)]
  allow_expect: true           # Allow .expect() (provides panic context)
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable unwrap abuse linter |
| `allow_in_tests` | boolean | `true` | Allow `.unwrap()`/`.expect()` in `#[test]` functions and `#[cfg(test)]` modules |
| `allow_expect` | boolean | `true` | Allow `.expect()` calls (community-recommended alternative to bare `.unwrap()`) |
| `ignore` | array | `["examples/", "benches/", "tests/"]` | File path patterns to ignore |

### Recommended Configurations

**Strict** (flag everything):
```yaml
unwrap-abuse:
  enabled: true
  allow_in_tests: false
  allow_expect: false
  ignore: []
```

**Standard** (default - allow tests and expect):
```yaml
unwrap-abuse:
  enabled: true
  allow_in_tests: true
  allow_expect: true
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
```

**Lenient** (only flag bare unwrap in production code):
```yaml
unwrap-abuse:
  enabled: true
  allow_in_tests: true
  allow_expect: true
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
    - "build.rs"
```

### Rationale for Defaults

- **`allow_in_tests: true`**: Test code uses `.unwrap()` idiomatically because panicking is the desired behavior for test failures. Flagging test code generates excessive noise.
- **`allow_expect: true`**: The Rust community recommends `.expect("descriptive message")` as a deliberate alternative to bare `.unwrap()`. It provides panic context and signals intentional design rather than lazy error handling.
- **`ignore: ["examples/", "benches/", "tests/"]`**: Example and benchmark code prioritizes clarity over robustness. Test directories are ignored at the file-path level in addition to the AST-level `allow_in_tests` check.

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for complete ignore guide.

**Quick examples:**

```rust
// Line-level ignore
let port = env::var("PORT").unwrap();  // thailint: ignore[unwrap-abuse] - Set by orchestrator, guaranteed present

// File-level ignore (at top of file)
// thailint: ignore-file[unwrap-abuse]
```

---

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check specific directory
thailint unwrap-abuse src/

# Check specific file
thailint unwrap-abuse src/main.rs

# Recursive check
thailint unwrap-abuse --recursive src/
```

#### With Configuration

```bash
# Use config file
thailint unwrap-abuse --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint unwrap-abuse src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint unwrap-abuse src/

# JSON output for CI/CD
thailint unwrap-abuse --format json src/

# SARIF output for GitHub Code Scanning
thailint unwrap-abuse --format sarif src/ > report.sarif

# JSON with exit code check
thailint unwrap-abuse --format json src/ > report.json
echo "Exit code: $?"
```

#### Additional Options

```bash
# Verbose output (debug logging)
thailint unwrap-abuse --verbose src/

# Parallel execution
thailint unwrap-abuse --parallel src/
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with unwrap-abuse rule
violations = linter.lint('src/', rules=['unwrap-abuse'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line} - {v.message}")
```

#### Direct Rule API

```python
from src.linters.unwrap_abuse import UnwrapAbuseRule, UnwrapAbuseConfig

# Create rule with default config
rule = UnwrapAbuseRule()

# Create rule with custom config
config = UnwrapAbuseConfig(
    allow_in_tests=True,
    allow_expect=False,  # Flag .expect() calls too
    ignore=["examples/"],
)
rule = UnwrapAbuseRule(config=config)
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest unwrap-abuse /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest unwrap-abuse \
  --config /config/.thailint.yaml /workspace/src/
```

---

## Violation Examples

### Example 1: File I/O with Unwrap

**Code with violations:**
```rust
use std::fs::File;
use std::io::Read;

fn load_settings() -> String {
    let mut file = File::open("settings.json").unwrap();  // VIOLATION
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();          // VIOLATION
    contents
}
```

**Violation messages:**
```
src/config.rs:5 - .unwrap() call may panic at runtime: let mut file = File::open("settings.json").unwrap();
  Suggestion: Use the ? operator, .unwrap_or(), .unwrap_or_default(), or match/if-let for safe error handling.

src/config.rs:7 - .unwrap() call may panic at runtime: file.read_to_string(&mut contents).unwrap();
  Suggestion: Use the ? operator, .unwrap_or(), .unwrap_or_default(), or match/if-let for safe error handling.
```

**Refactored code:**
```rust
use std::fs::File;
use std::io::{self, Read};

fn load_settings() -> io::Result<String> {
    let mut file = File::open("settings.json")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}
```

### Example 2: Option Handling with Unwrap

**Code with violations:**
```rust
fn get_first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap()  // VIOLATION - panics on empty string
}

fn find_user(users: &[User], id: u64) -> User {
    users.iter().find(|u| u.id == id).unwrap().clone()  // VIOLATION - panics if not found
}
```

**Violation messages:**
```
src/parser.rs:2 - .unwrap() call may panic at runtime: text.split_whitespace().next().unwrap()
  Suggestion: Use the ? operator, .unwrap_or(), .unwrap_or_default(), or match/if-let for safe error handling.

src/parser.rs:6 - .unwrap() call may panic at runtime: users.iter().find(|u| u.id == id).unwrap().clone()
  Suggestion: Use the ? operator, .unwrap_or(), .unwrap_or_default(), or match/if-let for safe error handling.
```

**Refactored code:**
```rust
fn get_first_word(text: &str) -> Option<&str> {
    text.split_whitespace().next()
}

fn find_user(users: &[User], id: u64) -> Option<&User> {
    users.iter().find(|u| u.id == id)
}
```

### Example 3: Expect Calls (Flagged When `allow_expect: false`)

**Code with violations (when `allow_expect: false`):**
```rust
fn connect_database() -> Connection {
    let url = env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set");            // VIOLATION

    Connection::establish(&url)
        .expect("Failed to connect to database");       // VIOLATION
}
```

**Violation messages:**
```
src/db.rs:3 - .expect() call may panic at runtime: .expect("DATABASE_URL must be set");
  Suggestion: Use the ? operator with a descriptive error via .context() or .with_context(), or use match/if-let for explicit error handling.

src/db.rs:6 - .expect() call may panic at runtime: .expect("Failed to connect to database");
  Suggestion: Use the ? operator with a descriptive error via .context() or .with_context(), or use match/if-let for explicit error handling.
```

**Refactored code:**
```rust
use anyhow::{Context, Result};

fn connect_database() -> Result<Connection> {
    let url = env::var("DATABASE_URL")
        .context("DATABASE_URL must be set")?;

    let conn = Connection::establish(&url)
        .context("Failed to connect to database")?;

    Ok(conn)
}
```

### Example 4: Acceptable Contexts (No Violations)

```rust
// Test code - OK (allow_in_tests: true)
#[test]
fn test_parsing() {
    let result = parse("valid input").unwrap();
    assert_eq!(result.value, 42);
}

// Test module - OK (allow_in_tests: true)
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_connection() {
        let conn = connect("localhost").unwrap();
        assert!(conn.is_alive());
    }
}

// .expect() with message - OK (allow_expect: true, default)
fn init() {
    let logger = Logger::init().expect("Logger must initialize");
}
```

---

## Refactoring Patterns

### Pattern 1: The `?` Operator (Error Propagation)

The most idiomatic Rust pattern for handling `Result` and `Option` values.

**Before:**
```rust
fn read_config(path: &str) -> Config {
    let file = File::open(path).unwrap();
    let contents = std::io::read_to_string(file).unwrap();
    serde_json::from_str(&contents).unwrap()
}
```

**After:**
```rust
fn read_config(path: &str) -> Result<Config, Box<dyn Error>> {
    let file = File::open(path)?;
    let contents = std::io::read_to_string(file)?;
    let config = serde_json::from_str(&contents)?;
    Ok(config)
}
```

**When to use**: Whenever the calling function can return a `Result` or `Option`. This is the preferred pattern for most Rust code.

### Pattern 2: `unwrap_or()` (Default Value)

Provides a fallback value when the operation fails or returns `None`.

**Before:**
```rust
fn get_port() -> u16 {
    env::var("PORT").unwrap().parse().unwrap()
}

fn get_username(user: &Option<User>) -> String {
    user.as_ref().unwrap().name.clone()
}
```

**After:**
```rust
fn get_port() -> u16 {
    env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .unwrap_or(8080)
}

fn get_username(user: &Option<User>) -> String {
    user.as_ref()
        .map(|u| u.name.clone())
        .unwrap_or_else(|| "anonymous".to_string())
}
```

**When to use**: When a sensible default value exists and the error case is not exceptional.

### Pattern 3: `unwrap_or_default()` (Type Default)

Uses the type's `Default` implementation as the fallback.

**Before:**
```rust
fn get_items(data: &HashMap<String, Vec<String>>, key: &str) -> Vec<String> {
    data.get(key).unwrap().clone()
}

fn parse_count(input: &str) -> i32 {
    input.parse().unwrap()
}
```

**After:**
```rust
fn get_items(data: &HashMap<String, Vec<String>>, key: &str) -> Vec<String> {
    data.get(key).cloned().unwrap_or_default()
}

fn parse_count(input: &str) -> i32 {
    input.parse().unwrap_or_default()  // Returns 0 for i32
}
```

**When to use**: When the type implements `Default` and the default value (e.g., `0`, `""`, `[]`) is appropriate for the error case.

### Pattern 4: `match` / `if let` (Explicit Handling)

Handles each case explicitly with custom logic.

**Before:**
```rust
fn process_message(queue: &mut VecDeque<Message>) {
    let msg = queue.pop_front().unwrap();
    handle(msg);
}

fn get_value(map: &HashMap<String, String>, key: &str) -> String {
    map.get(key).unwrap().clone()
}
```

**After:**
```rust
fn process_message(queue: &mut VecDeque<Message>) {
    if let Some(msg) = queue.pop_front() {
        handle(msg);
    } else {
        log::warn!("Queue is empty, skipping processing");
    }
}

fn get_value(map: &HashMap<String, String>, key: &str) -> String {
    match map.get(key) {
        Some(value) => value.clone(),
        None => {
            log::warn!("Key '{}' not found, using empty string", key);
            String::new()
        }
    }
}
```

**When to use**: When different error cases need different handling, or when logging/metrics are needed for the failure path.

### Pattern 5: `anyhow::Context` / `.context()` (Rich Errors)

Adds descriptive context to errors using the `anyhow` crate, replacing `.expect()` with non-panicking alternatives.

**Before:**
```rust
fn load_database() -> Database {
    let url = env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set");

    let pool = Pool::connect(&url)
        .expect("Failed to establish database connection");

    Database::new(pool)
}
```

**After:**
```rust
use anyhow::{Context, Result};

fn load_database() -> Result<Database> {
    let url = env::var("DATABASE_URL")
        .context("DATABASE_URL environment variable must be set")?;

    let pool = Pool::connect(&url)
        .with_context(|| format!("Failed to connect to database at {}", url))?;

    Ok(Database::new(pool))
}
```

**When to use**: When replacing `.expect()` calls and rich error context is needed. The `anyhow` crate provides `.context()` for static messages and `.with_context()` for dynamic messages constructed with closures.

### Pattern 6: Combining Patterns

Real-world code often combines multiple patterns.

**Before:**
```rust
fn process_request(req: &Request) -> Response {
    let auth = req.headers().get("Authorization").unwrap();
    let token = auth.to_str().unwrap();
    let user = validate_token(token).unwrap();
    let data = fetch_data(&user).unwrap();
    let result = transform(data).unwrap();
    Response::ok(result)
}
```

**After:**
```rust
use anyhow::{Context, Result};

fn process_request(req: &Request) -> Result<Response> {
    let auth = req.headers()
        .get("Authorization")
        .context("Missing Authorization header")?;              // Pattern 4 -> Pattern 5

    let token = auth.to_str()
        .context("Authorization header contains invalid UTF-8")?;  // Pattern 5

    let user = validate_token(token)
        .context("Token validation failed")?;                    // Pattern 1 + 5

    let data = fetch_data(&user)
        .with_context(|| format!("Failed to fetch data for user {}", user.id))?;  // Pattern 5

    let result = transform(data)
        .unwrap_or_default();                                    // Pattern 3

    Ok(Response::ok(result))
}
```

---

## Language Support

### Rust Support

**Fully Supported**

**Method calls detected:**
- `.unwrap()` on `Result<T, E>` and `Option<T>`
- `.expect("message")` on `Result<T, E>` and `Option<T>`

**Detection mechanism:**
- Tree-sitter AST parsing via `tree-sitter-rust`
- Matches `call_expression` -> `field_expression` -> `field_identifier` nodes
- Identifies method names `"unwrap"` and `"expect"`

**Test-aware contexts (skipped by default):**
- `#[test]` annotated functions
- `#[cfg(test)]` modules
- Files in `tests/` directory (via ignore config)

**Ignored by default:**
- `examples/` directory
- `benches/` directory
- `tests/` directory

### Other Languages

The unwrap abuse linter is Rust-specific. For error handling patterns in other languages, see:
- **Python**: Exception handling (try/except) -- covered by other linters
- **TypeScript**: Promise handling and null checks -- covered by other linters

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  unwrap-abuse-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for unwrap abuse
        run: |
          thailint unwrap-abuse src/
```

#### With SARIF Upload (GitHub Code Scanning)

```yaml
name: Lint

on: [push, pull_request]

jobs:
  unwrap-abuse-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for unwrap abuse
        run: |
          thailint unwrap-abuse --format sarif src/ > unwrap-abuse.sarif
        continue-on-error: true

      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: unwrap-abuse.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: unwrap-abuse-check
        name: Check for unwrap abuse in Rust
        entry: thailint unwrap-abuse
        language: python
        types: [rust]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-unwrap-abuse:
	@echo "=== Checking for unwrap abuse ==="
	@poetry run thailint unwrap-abuse src/ || exit 1

lint-all: lint-unwrap-abuse
	@echo "All checks passed"
```

---

## Performance

The unwrap abuse linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse (tree-sitter) | ~10-30ms | <100ms |
| Single file analysis | ~5-15ms | <50ms |
| 100 files | ~500ms | <2s |
| 1000 files | ~2-3s | <10s |

**Optimizations:**
- Tree-sitter parsing provides fast, incremental AST construction
- Recursive AST traversal stops early for non-matching node types
- Test context detection uses efficient parent-node traversal
- File-level ignore patterns skip entire files before parsing

---

## Troubleshooting

### Common Issues

**Issue: `.expect()` calls are not flagged**

```yaml
# Problem - allow_expect is true (default)
unwrap-abuse:
  allow_expect: true

# Solution - set allow_expect to false
unwrap-abuse:
  allow_expect: false
```

The `.expect()` method is allowed by default because it provides panic context and is the Rust community recommended alternative to bare `.unwrap()`. Set `allow_expect: false` to flag `.expect()` calls as well.

**Issue: Test code is flagged**

```yaml
# Problem - allow_in_tests is false
unwrap-abuse:
  allow_in_tests: false

# Solution - allow unwrap in test code (default)
unwrap-abuse:
  allow_in_tests: true
```

**Issue: Example or benchmark files are flagged**

```yaml
# Problem - ignore list does not include the directory
unwrap-abuse:
  ignore: []

# Solution - add directories to ignore list
unwrap-abuse:
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
```

**Issue: No violations reported for Rust files**

```bash
# Check that tree-sitter-rust is installed
python -c "import tree_sitter_rust; print('OK')"

# Check that the file is detected as Rust
thailint unwrap-abuse --verbose src/main.rs
```

Tree-sitter-rust must be installed for AST-based detection. Without it, the analyzer returns no results.

**Issue: False positives in generated code**

```yaml
# Add generated directories to ignore list
unwrap-abuse:
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
    - "generated/"
    - "target/"
```

**Issue: Violations in third-party vendored code**

```yaml
# Add vendored directories to ignore list
unwrap-abuse:
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
    - "vendor/"
    - "third_party/"
```

---

## Best Practices

### 1. Prefer the `?` Operator Over `.unwrap()`

The `?` operator is the most idiomatic Rust pattern for error propagation:

```rust
// Bad - panics on error
fn read_file(path: &str) -> String {
    std::fs::read_to_string(path).unwrap()
}

// Good - propagates error to caller
fn read_file(path: &str) -> io::Result<String> {
    std::fs::read_to_string(path)
}
```

### 2. Use `.expect()` Only for Programming Errors

Reserve `.expect()` for cases where failure represents a bug, not a runtime condition:

```rust
// Acceptable - programmer error if regex is invalid
let re = Regex::new(r"^\d{4}-\d{2}-\d{2}$")
    .expect("Date regex pattern is valid");

// Bad - runtime condition, not a programming error
let file = File::open(user_provided_path)
    .expect("File should exist");
```

### 3. Add Context to Errors with `anyhow`

Use `anyhow::Context` to provide descriptive error messages:

```rust
use anyhow::{Context, Result};

// Bad - no context on failure
fn load_config() -> Result<Config> {
    let text = std::fs::read_to_string("config.toml")?;
    let config: Config = toml::from_str(&text)?;
    Ok(config)
}

// Good - context explains what failed and why it matters
fn load_config() -> Result<Config> {
    let text = std::fs::read_to_string("config.toml")
        .context("Failed to read config.toml from working directory")?;
    let config: Config = toml::from_str(&text)
        .context("Failed to parse config.toml as valid TOML")?;
    Ok(config)
}
```

### 4. Use `unwrap_or_default()` for Collection Operations

When working with collections, `unwrap_or_default()` provides clean fallbacks:

```rust
// Bad
let items: Vec<String> = map.get("key").unwrap().clone();

// Good
let items: Vec<String> = map.get("key").cloned().unwrap_or_default();
```

### 5. Handle `Option` with `if let` or `map`

Use combinators and pattern matching for `Option` values:

```rust
// Bad
let name = user.name.as_ref().unwrap();

// Good - if let
if let Some(name) = &user.name {
    println!("Hello, {name}");
}

// Good - map/unwrap_or
let greeting = user.name
    .as_ref()
    .map(|n| format!("Hello, {n}"))
    .unwrap_or_else(|| "Hello, stranger".to_string());
```

### 6. Allow `.unwrap()` in Tests

Test code benefits from `.unwrap()` because panicking is the desired behavior for unexpected failures:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_parse() {
        // .unwrap() is appropriate here - test should fail loudly
        let result = parse("valid input").unwrap();
        assert_eq!(result.value, 42);
    }
}
```

Keep `allow_in_tests: true` (the default) to avoid noisy test violations.

### 7. Document Intentional `.unwrap()` Usage

When `.unwrap()` is genuinely safe, document why:

```rust
// The regex is a compile-time constant; this cannot fail at runtime.
let date_pattern = Regex::new(r"^\d{4}-\d{2}-\d{2}$").unwrap();

// The channel receiver is guaranteed to exist while sender is alive.
let msg = rx.recv().unwrap();  // thailint: ignore[unwrap-abuse] - Channel invariant
```

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation
- **[ReadTheDocs](https://thai-lint.readthedocs.io/en/latest/unwrap-abuse-linter/)** - Online documentation
