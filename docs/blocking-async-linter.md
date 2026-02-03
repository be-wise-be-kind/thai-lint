# Blocking in Async Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the blocking-in-async linter for detecting blocking operations inside async Rust functions

    **Scope**: Configuration, usage, refactoring patterns, and best practices for blocking-in-async detection in Rust

    **Overview**: Comprehensive documentation for the blocking-in-async linter that detects blocking operations inside async functions in Rust code. Covers how the linter works using Tree-sitter AST analysis to identify std::fs I/O, std::thread::sleep, and std::net calls within async function bodies. Includes configuration options, CLI and library usage, wrapper function exclusions, common refactoring patterns, and CI/CD integration. This rule is novel and not covered by Clippy, filling a gap in the Rust linting ecosystem. Helps teams prevent thread starvation and deadlocks in async Rust applications by suggesting async-compatible alternatives from the Tokio ecosystem.

    **Dependencies**: tree-sitter (Rust parser), Tokio ecosystem (suggested alternatives)

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: Tree-sitter AST-based detection with call path extraction and async wrapper function exclusion

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thailint
thailint blocking-async src/
```

**Example output:**
```
src/lib.rs:15 - Blocking std::fs operation inside async function: fs::read_to_string
  Suggestion: Use tokio::fs equivalents (e.g., tokio::fs::read_to_string) for async-compatible file I/O operations.
```

**Fix it:** Replace blocking standard library calls with their Tokio async equivalents.

---

## Overview

The blocking-in-async linter detects blocking operations inside async functions in Rust code. It identifies three categories of blocking calls -- `std::fs` I/O, `std::thread::sleep`, and `std::net` networking -- that can cause thread starvation and deadlocks when used within async contexts.

### The Blocking-in-Async Problem

Async runtimes like Tokio use a small thread pool (typically equal to the number of CPU cores) to multiplex many concurrent tasks. When a task calls a blocking operation, it occupies an entire thread for the duration of the blocking call. Other tasks waiting for that thread cannot make progress.

```rust
// Dangerous - blocks the async runtime thread
async fn load_config() -> String {
    // This blocks the entire thread while waiting for disk I/O.
    // No other async tasks can run on this thread until the read completes.
    std::fs::read_to_string("config.toml").unwrap()
}
```

### Thread Starvation and Deadlocks

If enough tasks make blocking calls simultaneously, the runtime exhausts its thread pool. Tasks waiting for threads to become available cannot proceed, and tasks holding threads are blocked on I/O. This creates a deadlock condition where the entire application hangs:

```
Thread 1: blocked on std::fs::read_to_string(...)
Thread 2: blocked on std::fs::write(...)
Thread 3: blocked on std::thread::sleep(...)
Thread 4: blocked on std::net::TcpStream::connect(...)
Tasks 5-100: waiting for a free thread... forever
```

### A Novel Rule Beyond Clippy

This linter addresses a gap in the Rust linting ecosystem. Clippy does not include a lint for detecting blocking standard library calls inside async functions. While experienced Rust developers learn to avoid this pattern, AI-generated code frequently introduces blocking calls inside async functions because language models do not distinguish between sync and async contexts. This linter catches these mistakes automatically.

### Benefits

- **Prevent thread starvation**: Identify blocking calls before they reach production
- **Catch AI-generated mistakes**: AI code generators frequently mix sync and async APIs
- **Suggest alternatives**: Each violation includes a specific Tokio replacement
- **Configurable**: Tune detection per sub-rule, ignore test code, exclude wrapper functions

## How It Works

### Tree-sitter AST Detection

The linter uses Tree-sitter to parse Rust source code into an AST and applies the following analysis:

1. **Locate async functions**: Identify function items with the `async` keyword
2. **Walk call expressions**: Find all `call_expression` nodes within async function bodies
3. **Extract call paths**: Read `scoped_identifier` children to reconstruct fully-qualified or short call paths (e.g., `std::fs::read_to_string` or `fs::read_to_string`)
4. **Match blocking patterns**: Compare call paths against known blocking API signatures
5. **Check wrapper exclusions**: Skip calls wrapped in async-safe functions like `spawn_blocking`
6. **Report violations**: Emit diagnostics with rule ID, message, and suggested fix

### Three Sub-Rules

The linter enforces three sub-rules, each targeting a different category of blocking operation:

#### `blocking-async.fs-in-async` -- Blocking File I/O

Detects `std::fs` operations inside async functions. These operations block the thread while waiting for disk I/O.

**Detected functions**: `read_to_string`, `read`, `write`, `create_dir`, `create_dir_all`, `remove_file`, `remove_dir`, `remove_dir_all`, `rename`, `copy`, `metadata`, `read_dir`, `canonicalize`, `read_link`

**Violation message**: "Blocking std::fs operation inside async function: {context}"

**Suggestion**: "Use tokio::fs equivalents (e.g., tokio::fs::read_to_string) for async-compatible file I/O operations. Blocking std::fs calls in async functions can cause thread starvation and deadlocks."

#### `blocking-async.sleep-in-async` -- Blocking Sleep

Detects `std::thread::sleep` inside async functions. This blocks the entire thread, preventing other async tasks from executing on it.

**Detected patterns**: `std::thread::sleep`, `thread::sleep`

**Violation message**: "Blocking std::thread::sleep inside async function: {context}"

**Suggestion**: "Use tokio::time::sleep instead of std::thread::sleep in async functions. Blocking the thread with std::thread::sleep prevents the async runtime from processing other tasks on the same thread."

#### `blocking-async.net-in-async` -- Blocking Networking

Detects `std::net` types inside async functions. These perform synchronous DNS resolution, connection establishment, and data transfer.

**Detected types**: `TcpStream`, `TcpListener`, `UdpSocket`

**Violation message**: "Blocking std::net operation inside async function: {context}"

**Suggestion**: "Use tokio::net equivalents (e.g., tokio::net::TcpStream) for async-compatible networking. Blocking std::net calls in async functions can cause thread starvation and deadlocks in the async runtime."

### Wrapper Function Exclusion

The linter recognizes async-safe wrapper functions that correctly offload blocking work to a thread pool. Calls wrapped in these functions are excluded from detection:

- `asyncify` -- Common utility to run blocking code on a thread pool
- `spawn_blocking` -- Tokio's built-in mechanism to run blocking code
- `block_in_place` -- Tokio's mechanism for blocking within the runtime thread

```rust
async fn safe_read() -> String {
    // Not flagged -- spawn_blocking correctly offloads to a thread pool
    tokio::task::spawn_blocking(|| {
        std::fs::read_to_string("config.toml").unwrap()
    }).await.unwrap()
}
```

## Configuration

### Basic Configuration

Create or update `.thailint.yaml`:

```yaml
blocking-async:
  enabled: true
  allow_in_tests: true
  detect_fs_in_async: true
  detect_sleep_in_async: true
  detect_net_in_async: true
  ignore:
    - "examples/"
    - "benches/"
    - "tests/"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable blocking-in-async linter |
| `allow_in_tests` | boolean | `true` | Allow blocking calls in `#[test]` functions and `#[cfg(test)]` modules |
| `detect_fs_in_async` | boolean | `true` | Detect `std::fs` operations in async functions |
| `detect_sleep_in_async` | boolean | `true` | Detect `std::thread::sleep` in async functions |
| `detect_net_in_async` | boolean | `true` | Detect `std::net` blocking calls in async functions |
| `ignore` | array | `["examples/", "benches/", "tests/"]` | Paths to exclude from analysis |

### Selective Sub-Rule Configuration

Disable individual sub-rules when specific blocking patterns are acceptable for a project:

```yaml
# Example: Allow blocking sleep (e.g., for rate-limiting scripts)
# but still catch fs and net blocking
blocking-async:
  enabled: true
  detect_fs_in_async: true
  detect_sleep_in_async: false
  detect_net_in_async: true
```

### JSON Configuration

```json
{
  "blocking-async": {
    "enabled": true,
    "allow_in_tests": true,
    "detect_fs_in_async": true,
    "detect_sleep_in_async": true,
    "detect_net_in_async": true,
    "ignore": ["examples/", "benches/", "tests/"]
  }
}
```

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for the complete ignore guide.

**Quick examples:**

```rust
// Line-level ignore
std::fs::read_to_string("config.toml").unwrap() // thailint: ignore[blocking-async.fs-in-async] - One-time config load at startup

// File-level ignore
// thailint: ignore-file[blocking-async]
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thailint blocking-async .

# Check specific directory
thailint blocking-async src/

# Check specific file
thailint blocking-async src/server.rs

# Recursive scan
thailint blocking-async --recursive src/
```

#### With Configuration

```bash
# Use config file
thailint blocking-async --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint blocking-async src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint blocking-async src/

# JSON output for CI/CD
thailint blocking-async --format json src/

# SARIF output for GitHub Code Scanning
thailint blocking-async --format sarif src/ > results.sarif

# Verbose output for debugging
thailint blocking-async --verbose src/

# Parallel processing for large codebases
thailint blocking-async --parallel src/
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with blocking-async rule
violations = linter.lint('src/', rules=['blocking-async'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line_number} - {v.message}")
```

#### Direct Linter API

```python
from src.linters.blocking_async import lint

# Lint specific path
violations = lint('src/server.rs')

# With custom configuration
violations = lint(
    'src/',
    config={
        'detect_fs_in_async': True,
        'detect_sleep_in_async': True,
        'detect_net_in_async': False,
    }
)

# Process results
for violation in violations:
    print(f"Line {violation.line_number}: {violation.message}")
    print(f"  Suggestion: {violation.suggestion}")
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest blocking-async /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest blocking-async \
  --config /config/.thailint.yaml /workspace/src/
```

## Violation Examples

### Example 1: Blocking File I/O in Async (`blocking-async.fs-in-async`)

**Code with violation:**
```rust
use std::fs;

async fn load_user_data(path: &str) -> Result<String, std::io::Error> {
    // Blocks the async runtime thread while reading from disk
    let contents = fs::read_to_string(path)?;
    Ok(contents)
}

async fn save_report(path: &str, data: &[u8]) -> Result<(), std::io::Error> {
    // Blocks the async runtime thread while writing to disk
    fs::write(path, data)?;
    Ok(())
}
```

**Violation messages:**
```
src/data.rs:5 - Blocking std::fs operation inside async function: fs::read_to_string
  Suggestion: Use tokio::fs equivalents (e.g., tokio::fs::read_to_string) for async-compatible file I/O operations.

src/data.rs:11 - Blocking std::fs operation inside async function: fs::write
  Suggestion: Use tokio::fs equivalents (e.g., tokio::fs::read_to_string) for async-compatible file I/O operations.
```

**Refactored code:**
```rust
use tokio::fs;

async fn load_user_data(path: &str) -> Result<String, std::io::Error> {
    // Async file read -- yields to the runtime while waiting for disk I/O
    let contents = fs::read_to_string(path).await?;
    Ok(contents)
}

async fn save_report(path: &str, data: &[u8]) -> Result<(), std::io::Error> {
    // Async file write -- yields to the runtime while waiting for disk I/O
    fs::write(path, data).await?;
    Ok(())
}
```

### Example 2: Blocking Sleep in Async (`blocking-async.sleep-in-async`)

**Code with violation:**
```rust
use std::thread;
use std::time::Duration;

async fn retry_with_backoff<F, T>(mut operation: F) -> T
where
    F: FnMut() -> Result<T, String>,
{
    let mut delay = 1;
    loop {
        match operation() {
            Ok(result) => return result,
            Err(_) => {
                // Blocks the entire thread -- other tasks on this thread cannot run
                thread::sleep(Duration::from_secs(delay));
                delay *= 2;
            }
        }
    }
}
```

**Violation message:**
```
src/retry.rs:14 - Blocking std::thread::sleep inside async function: thread::sleep
  Suggestion: Use tokio::time::sleep instead of std::thread::sleep in async functions.
```

**Refactored code:**
```rust
use std::time::Duration;
use tokio::time;

async fn retry_with_backoff<F, T>(mut operation: F) -> T
where
    F: FnMut() -> Result<T, String>,
{
    let mut delay = 1;
    loop {
        match operation() {
            Ok(result) => return result,
            Err(_) => {
                // Yields to the runtime -- other tasks can run while waiting
                time::sleep(Duration::from_secs(delay)).await;
                delay *= 2;
            }
        }
    }
}
```

### Example 3: Blocking Network I/O in Async (`blocking-async.net-in-async`)

**Code with violation:**
```rust
use std::net::TcpStream;
use std::io::{Read, Write};

async fn check_service_health(addr: &str) -> bool {
    // Blocking TCP connection -- blocks the async runtime thread
    match TcpStream::connect(addr) {
        Ok(mut stream) => {
            stream.write_all(b"PING").unwrap();
            let mut buf = [0u8; 4];
            stream.read_exact(&mut buf).unwrap();
            &buf == b"PONG"
        }
        Err(_) => false,
    }
}
```

**Violation message:**
```
src/health.rs:6 - Blocking std::net operation inside async function: TcpStream::connect
  Suggestion: Use tokio::net equivalents (e.g., tokio::net::TcpStream) for async-compatible networking.
```

**Refactored code:**
```rust
use tokio::net::TcpStream;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

async fn check_service_health(addr: &str) -> bool {
    // Async TCP connection -- yields to the runtime during connection and I/O
    match TcpStream::connect(addr).await {
        Ok(mut stream) => {
            stream.write_all(b"PING").await.unwrap();
            let mut buf = [0u8; 4];
            stream.read_exact(&mut buf).await.unwrap();
            &buf == b"PONG"
        }
        Err(_) => false,
    }
}
```

## Refactoring Patterns

### Pattern 1: Replace `std::fs` with `tokio::fs`

The most straightforward refactoring -- swap `std::fs` imports for `tokio::fs` and add `.await` to each call.

**Before:**
```rust
use std::fs;

async fn process_config() -> Result<(), Box<dyn std::error::Error>> {
    let config = fs::read_to_string("config.toml")?;
    fs::create_dir_all("output/")?;
    fs::write("output/result.json", processed_data)?;
    Ok(())
}
```

**After:**
```rust
use tokio::fs;

async fn process_config() -> Result<(), Box<dyn std::error::Error>> {
    let config = fs::read_to_string("config.toml").await?;
    fs::create_dir_all("output/").await?;
    fs::write("output/result.json", processed_data).await?;
    Ok(())
}
```

**Key consideration**: `tokio::fs` mirrors the `std::fs` API, so most replacements are mechanical.

### Pattern 2: Replace `std::thread::sleep` with `tokio::time::sleep`

**Before:**
```rust
use std::thread;
use std::time::Duration;

async fn poll_status(url: &str) {
    loop {
        let status = check(url).await;
        if status.is_ready() {
            break;
        }
        thread::sleep(Duration::from_millis(500));
    }
}
```

**After:**
```rust
use std::time::Duration;
use tokio::time;

async fn poll_status(url: &str) {
    loop {
        let status = check(url).await;
        if status.is_ready() {
            break;
        }
        time::sleep(Duration::from_millis(500)).await;
    }
}
```

**Key consideration**: `tokio::time::sleep` returns a `Future` that must be `.await`ed. It yields to the runtime, allowing other tasks to progress during the wait.

### Pattern 3: Replace `std::net` with `tokio::net`

**Before:**
```rust
use std::net::{TcpListener, TcpStream};
use std::io::{Read, Write};

async fn run_proxy(listen_addr: &str, upstream_addr: &str) {
    let listener = TcpListener::bind(listen_addr).unwrap();
    for stream in listener.incoming() {
        let mut client = stream.unwrap();
        let mut upstream = TcpStream::connect(upstream_addr).unwrap();
        let mut buf = vec![0u8; 4096];
        let n = client.read(&mut buf).unwrap();
        upstream.write_all(&buf[..n]).unwrap();
    }
}
```

**After:**
```rust
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

async fn run_proxy(listen_addr: &str, upstream_addr: &str) {
    let listener = TcpListener::bind(listen_addr).await.unwrap();
    loop {
        let (mut client, _) = listener.accept().await.unwrap();
        let mut upstream = TcpStream::connect(upstream_addr).await.unwrap();
        let mut buf = vec![0u8; 4096];
        let n = client.read(&mut buf).await.unwrap();
        upstream.write_all(&buf[..n]).await.unwrap();
    }
}
```

**Key consideration**: `tokio::net::TcpListener` uses `.accept().await` instead of `.incoming()`. Error handling patterns may differ slightly.

### Pattern 4: Use `spawn_blocking` for Unavoidable Blocking Work

When async alternatives do not exist (e.g., CPU-heavy computation, FFI calls, or libraries that only provide synchronous APIs), use `spawn_blocking` to offload work to a dedicated thread pool.

**Before:**
```rust
async fn compress_file(path: &str) -> Vec<u8> {
    // No async compression library available
    let data = std::fs::read(path).unwrap();
    heavy_compress(&data)  // CPU-bound, blocks the thread
}
```

**After:**
```rust
async fn compress_file(path: &str) -> Vec<u8> {
    let path = path.to_string();
    tokio::task::spawn_blocking(move || {
        let data = std::fs::read(&path).unwrap();
        heavy_compress(&data)
    }).await.unwrap()
}
```

**Key consideration**: `spawn_blocking` runs the closure on a separate thread pool sized for blocking work. The async task `.await`s the result without blocking the runtime.

### Pattern 5: Use Async Channels for Producer-Consumer Patterns

When blocking I/O feeds data to async processing, use async channels to decouple the blocking producer from the async consumer.

**Before:**
```rust
async fn watch_directory(path: &str) {
    // Blocking directory scan inside async function
    loop {
        let entries = std::fs::read_dir(path).unwrap();
        for entry in entries {
            let entry = entry.unwrap();
            process_file(entry.path()).await;
        }
        std::thread::sleep(std::time::Duration::from_secs(5));
    }
}
```

**After:**
```rust
use tokio::sync::mpsc;
use std::path::PathBuf;

async fn watch_directory(path: &str) {
    let (tx, mut rx) = mpsc::channel::<PathBuf>(100);
    let path = path.to_string();

    // Blocking work runs on a dedicated thread
    tokio::task::spawn_blocking(move || {
        loop {
            let entries = std::fs::read_dir(&path).unwrap();
            for entry in entries {
                let entry = entry.unwrap();
                tx.blocking_send(entry.path()).unwrap();
            }
            std::thread::sleep(std::time::Duration::from_secs(5));
        }
    });

    // Async consumer processes files without blocking
    while let Some(file_path) = rx.recv().await {
        process_file(file_path).await;
    }
}
```

**Key consideration**: `mpsc::Sender::blocking_send` allows the blocking thread to send into the channel without requiring an async runtime. The async consumer receives items with `.recv().await`.

### Pattern 6: Use `tokio::time::interval` for Periodic Tasks

Replace `loop` + `thread::sleep` patterns with `tokio::time::interval` for periodic async work.

**Before:**
```rust
async fn metrics_reporter() {
    loop {
        collect_and_send_metrics().await;
        std::thread::sleep(std::time::Duration::from_secs(60));
    }
}
```

**After:**
```rust
use tokio::time::{self, Duration};

async fn metrics_reporter() {
    let mut interval = time::interval(Duration::from_secs(60));
    loop {
        interval.tick().await;
        collect_and_send_metrics().await;
    }
}
```

**Key consideration**: `tokio::time::interval` accounts for the time spent in the loop body, providing more consistent timing than `sleep` at the end of each iteration.

## Language Support

### Rust Support

**Fully Supported**

The blocking-in-async linter supports Rust exclusively. It uses Tree-sitter to parse Rust source files and analyze async function bodies for blocking call patterns.

**Detection covers:**

| Category | Blocking API | Async Alternative |
|----------|-------------|-------------------|
| File I/O | `std::fs::read_to_string` | `tokio::fs::read_to_string` |
| File I/O | `std::fs::read` | `tokio::fs::read` |
| File I/O | `std::fs::write` | `tokio::fs::write` |
| File I/O | `std::fs::create_dir` | `tokio::fs::create_dir` |
| File I/O | `std::fs::create_dir_all` | `tokio::fs::create_dir_all` |
| File I/O | `std::fs::remove_file` | `tokio::fs::remove_file` |
| File I/O | `std::fs::remove_dir` | `tokio::fs::remove_dir` |
| File I/O | `std::fs::remove_dir_all` | `tokio::fs::remove_dir_all` |
| File I/O | `std::fs::rename` | `tokio::fs::rename` |
| File I/O | `std::fs::copy` | `tokio::fs::copy` |
| File I/O | `std::fs::metadata` | `tokio::fs::metadata` |
| File I/O | `std::fs::read_dir` | `tokio::fs::read_dir` |
| File I/O | `std::fs::canonicalize` | `tokio::fs::canonicalize` |
| File I/O | `std::fs::read_link` | `tokio::fs::read_link` |
| Sleep | `std::thread::sleep` | `tokio::time::sleep` |
| Networking | `std::net::TcpStream` | `tokio::net::TcpStream` |
| Networking | `std::net::TcpListener` | `tokio::net::TcpListener` |
| Networking | `std::net::UdpSocket` | `tokio::net::UdpSocket` |

**Path matching:** Both fully-qualified paths (`std::fs::read_to_string`) and short paths (`fs::read_to_string`) are detected.

### Other Languages

Blocking-in-async detection is Rust-specific. Other languages handle async/blocking interactions differently:

- **Python**: `asyncio` raises warnings for blocking calls in debug mode
- **TypeScript/JavaScript**: Single-threaded event loop; blocking the thread is obvious
- **Go**: Goroutines are cheap and blocking is the expected pattern

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  blocking-async-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for blocking operations in async functions
        run: |
          thailint blocking-async src/

      - name: SARIF upload (optional)
        if: always()
        run: |
          thailint blocking-async --format sarif src/ > blocking-async.sarif

      - name: Upload SARIF to GitHub
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: blocking-async.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: blocking-async-check
        name: Check for blocking operations in async Rust functions
        entry: thailint blocking-async
        language: python
        types: [rust]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-blocking-async:
	@echo "=== Checking for blocking operations in async functions ==="
	@poetry run thailint blocking-async src/ || exit 1

lint-all: lint-blocking-async
	@echo "All checks passed"
```

## Performance

The blocking-in-async linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse (Tree-sitter) | ~5-20ms | <50ms |
| Single file analysis | ~3-10ms | <30ms |
| 100 files | ~300ms | <2s |
| 1000 files | ~1-2s | <10s |

**Optimizations:**

- Tree-sitter provides fast incremental parsing of Rust source files
- AST traversal targets only async function bodies, skipping synchronous code
- Call path extraction uses efficient pattern matching on scoped identifiers
- Wrapper function exclusion short-circuits analysis for correctly-wrapped calls
- Parallel mode (`--parallel`) distributes file analysis across CPU cores

## Troubleshooting

### Common Issues

**Issue: Blocking call in `spawn_blocking` is still flagged**

```rust
// Problem -- nested closure not recognized
async fn read_config() {
    let handle = tokio::task::spawn_blocking(|| {
        let inner = || {
            std::fs::read_to_string("config.toml") // May be flagged
        };
        inner()
    });
    handle.await.unwrap();
}
```

```rust
// Solution -- keep blocking calls directly inside spawn_blocking
async fn read_config() {
    let handle = tokio::task::spawn_blocking(|| {
        std::fs::read_to_string("config.toml").unwrap()
    });
    handle.await.unwrap();
}
```

**Issue: False positive on sync function called from async context**

```rust
// Problem -- sync helper function uses std::fs
fn read_sync(path: &str) -> String {
    std::fs::read_to_string(path).unwrap() // Not flagged (sync function)
}

async fn handler() {
    let data = read_sync("file.txt"); // The linter flags calls INSIDE async functions
}
```

The linter only inspects calls directly inside async function bodies. If a synchronous helper uses blocking calls, the linter does not trace through the call graph. Use `spawn_blocking` to wrap calls to synchronous helpers:

```rust
async fn handler() {
    let data = tokio::task::spawn_blocking(|| read_sync("file.txt"))
        .await
        .unwrap();
}
```

**Issue: Test functions are flagged**

```rust
// Problem -- allow_in_tests may not cover all test patterns
#[tokio::test]
async fn test_file_processing() {
    std::fs::write("test.txt", "data").unwrap(); // Flagged if not recognized as test
}
```

```yaml
# Solution -- verify allow_in_tests is enabled and test paths are in ignore list
blocking-async:
  allow_in_tests: true
  ignore:
    - "tests/"
    - "test_*.rs"
```

**Issue: Custom async wrapper not recognized**

```rust
// Problem -- project uses a custom wrapper function
async fn handler() {
    my_spawn_blocking(|| {
        std::fs::read_to_string("file.txt").unwrap()
    }).await;
}
```

The linter recognizes `asyncify`, `spawn_blocking`, and `block_in_place`. For custom wrappers, use a line-level ignore:

```rust
async fn handler() {
    my_spawn_blocking(|| {
        std::fs::read_to_string("file.txt").unwrap() // thailint: ignore[blocking-async.fs-in-async] - Wrapped in custom spawn_blocking
    }).await;
}
```

## Best Practices

### 1. Default to Async Alternatives

When writing async Rust code, use Tokio equivalents by default. Treat blocking standard library calls as an explicit choice that requires justification.

```rust
// Prefer tokio::fs over std::fs in async code
use tokio::fs;

async fn read_config(path: &str) -> Result<String, std::io::Error> {
    fs::read_to_string(path).await
}
```

### 2. Use `spawn_blocking` for Unavoidable Blocking

When an async alternative does not exist (FFI, CPU-bound work, legacy libraries), explicitly offload to the blocking thread pool.

```rust
async fn compute_hash(data: Vec<u8>) -> Vec<u8> {
    tokio::task::spawn_blocking(move || {
        expensive_hash_function(&data)
    }).await.unwrap()
}
```

### 3. Keep Blocking and Async Code Separated

Organize code so that synchronous/blocking logic lives in separate modules from async logic. This makes it easier to identify and manage blocking boundaries.

```rust
// sync_io.rs -- all blocking I/O in one place
pub fn read_config_sync(path: &str) -> Config {
    let data = std::fs::read_to_string(path).unwrap();
    toml::from_str(&data).unwrap()
}

// async_handlers.rs -- async code delegates to spawn_blocking
pub async fn load_config(path: &str) -> Config {
    let path = path.to_string();
    tokio::task::spawn_blocking(move || {
        sync_io::read_config_sync(&path)
    }).await.unwrap()
}
```

### 4. Audit AI-Generated Async Code

AI code generators frequently produce async functions that call blocking APIs. Run the blocking-in-async linter as part of the code review process for AI-generated Rust code.

```bash
# Check AI-generated code before merging
thailint blocking-async --format json generated_code/ > report.json
```

### 5. Use `tokio::time::interval` Over `loop` + `sleep`

For periodic tasks, prefer `tokio::time::interval` over manual loop-and-sleep patterns. It provides more consistent timing and integrates with the Tokio runtime.

```rust
use tokio::time::{self, Duration};

async fn heartbeat() {
    let mut interval = time::interval(Duration::from_secs(30));
    loop {
        interval.tick().await;
        send_heartbeat().await;
    }
}
```

### 6. Enable All Sub-Rules in CI/CD

Run all three sub-rules (`fs-in-async`, `sleep-in-async`, `net-in-async`) in CI/CD pipelines to catch all categories of blocking operations. Disable individual sub-rules only at the project level in `.thailint.yaml` when a specific pattern is intentional.

```yaml
# Recommended CI/CD configuration -- all sub-rules enabled
blocking-async:
  enabled: true
  detect_fs_in_async: true
  detect_sleep_in_async: true
  detect_net_in_async: true
```

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation
