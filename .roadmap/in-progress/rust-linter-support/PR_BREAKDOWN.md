# Rust Linter Support - PR Breakdown

**Purpose**: Detailed implementation breakdown of Rust Linter Support into manageable, atomic pull requests

**Scope**: Complete feature implementation from infrastructure through novel AI-focused lint rules

**Overview**: Comprehensive breakdown of the Rust Linter Support feature into 6 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward complete Rust support. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR. Includes validation trials against
    popular Rust repositories to ensure zero false positives before release.

**Dependencies**: tree-sitter, tree-sitter-rust (optional)

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with detailed step-by-step implementation guidance and comprehensive testing validation

---

## Overview
This document breaks down the Rust Linter Support feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

---

## PR1: Rust Infrastructure & Language Detection

### Objective
Establish the foundation for Rust support: language detection, tree-sitter parsing, and base analyzer class.

### Files to Create/Modify

#### 1. Modify: `src/orchestrator/language_detector.py`

Add Rust to the extension map:

```python
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",  # ADD THIS
}
```

#### 2. Create: `src/analyzers/rust_base.py`

Mirror the TypeScriptBaseAnalyzer pattern:

```python
"""
Purpose: Base class for Rust AST analysis with tree-sitter parsing

Scope: Common tree-sitter initialization, parsing, and traversal utilities for Rust

Overview: Provides shared infrastructure for Rust code analysis using tree-sitter parser.
    Implements common tree-sitter initialization with language setup and parser configuration.
    Provides reusable parsing methods that convert Rust source to AST nodes. Includes
    shared traversal utilities for walking AST trees recursively and finding nodes by type.
    Serves as foundation for specialized Rust analyzers.

Dependencies: tree-sitter, tree-sitter-rust (optional)

Exports: RustBaseAnalyzer class with parsing and traversal utilities

Interfaces: parse_rust(code), walk_tree(node, node_type), extract_node_text(node)

Implementation: Tree-sitter parser singleton, recursive AST traversal, composition pattern

Suppressions:
    - type:ignore[assignment]: Tree-sitter RUST_PARSER fallback when import fails
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
"""

from typing import Any

try:
    import tree_sitter_rust as tsrust
    from tree_sitter import Language, Node, Parser

    RUST_LANGUAGE = Language(tsrust.language())
    RUST_PARSER = Parser(RUST_LANGUAGE)
    TREE_SITTER_RUST_AVAILABLE = True
except ImportError:
    TREE_SITTER_RUST_AVAILABLE = False
    RUST_PARSER = None  # type: ignore[assignment]
    Node = Any  # type: ignore[assignment,misc]


class RustBaseAnalyzer:
    """Base analyzer for Rust code using tree-sitter."""

    def __init__(self) -> None:
        """Initialize Rust base analyzer."""
        self.tree_sitter_available = TREE_SITTER_RUST_AVAILABLE

    def parse_rust(self, code: str) -> Node | None:
        """Parse Rust code to AST using tree-sitter."""
        if not TREE_SITTER_RUST_AVAILABLE or RUST_PARSER is None:
            return None
        tree = RUST_PARSER.parse(bytes(code, "utf8"))
        return tree.root_node

    def walk_tree(self, node: Node, node_type: str) -> list[Node]:
        """Find all nodes of a specific type in the AST."""
        if not TREE_SITTER_RUST_AVAILABLE or node is None:
            return []
        nodes: list[Node] = []
        self._walk_tree_recursive(node, node_type, nodes)
        return nodes

    def _walk_tree_recursive(self, node: Node, node_type: str, nodes: list[Node]) -> None:
        """Recursively walk tree to find nodes of specific type."""
        if node.type == node_type:
            nodes.append(node)
        for child in node.children:
            self._walk_tree_recursive(child, node_type, nodes)

    def extract_node_text(self, node: Node) -> str:
        """Extract text content from a tree-sitter node."""
        text = node.text
        if text is None:
            return ""
        return text.decode()

    def find_child_by_type(self, node: Node, child_type: str) -> Node | None:
        """Find first child node of a specific type."""
        for child in node.children:
            if child.type == child_type:
                return child
        return None

    def find_children_by_types(self, node: Node, child_types: set[str]) -> list[Node]:
        """Find all children matching any of the given types."""
        return [child for child in node.children if child.type in child_types]

    def extract_identifier_name(self, node: Node) -> str:
        """Extract identifier name from node children."""
        for child in node.children:
            if child.type == "identifier":
                return self.extract_node_text(child)
        return "anonymous"

    def is_inside_test(self, node: Node) -> bool:
        """Check if node is inside a test function or module.

        Walks up the tree looking for #[test] or #[cfg(test)] attributes.
        """
        current = node
        while current is not None:
            if current.type == "function_item":
                # Check for #[test] attribute
                for child in current.children:
                    if child.type == "attribute_item":
                        attr_text = self.extract_node_text(child)
                        if "test" in attr_text:
                            return True
            elif current.type == "mod_item":
                # Check for #[cfg(test)] on module
                for child in current.children:
                    if child.type == "attribute_item":
                        attr_text = self.extract_node_text(child)
                        if "cfg(test)" in attr_text:
                            return True
            current = current.parent
        return False

    def is_async_function(self, node: Node) -> bool:
        """Check if a function_item is async."""
        for child in node.children:
            if child.type == "async":
                return True
        return False
```

#### 3. Modify: `pyproject.toml`

Add tree-sitter-rust as optional dependency (check exact format used for tree-sitter-typescript):

```toml
[tool.poetry.dependencies]
# ... existing deps ...
tree-sitter-rust = { version = "^0.21", optional = true }

[tool.poetry.extras]
# ... existing extras ...
rust = ["tree-sitter", "tree-sitter-rust"]
all = ["tree-sitter", "tree-sitter-typescript", "tree-sitter-rust"]  # Update existing 'all' extra
```

#### 4. Create: `tests/unit/analyzers/test_rust_base.py`

```python
"""Tests for RustBaseAnalyzer."""

import pytest
from src.analyzers.rust_base import RustBaseAnalyzer, TREE_SITTER_RUST_AVAILABLE


class TestRustBaseAnalyzer:
    """Test suite for RustBaseAnalyzer."""

    def test_init(self) -> None:
        """Test analyzer initialization."""
        analyzer = RustBaseAnalyzer()
        assert analyzer.tree_sitter_available == TREE_SITTER_RUST_AVAILABLE

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_parse_rust_simple(self) -> None:
        """Test parsing simple Rust code."""
        analyzer = RustBaseAnalyzer()
        code = "fn main() { println!(\"Hello\"); }"
        node = analyzer.parse_rust(code)
        assert node is not None
        assert node.type == "source_file"

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_walk_tree_finds_functions(self) -> None:
        """Test walking tree to find function items."""
        analyzer = RustBaseAnalyzer()
        code = """
        fn foo() {}
        fn bar() {}
        """
        node = analyzer.parse_rust(code)
        functions = analyzer.walk_tree(node, "function_item")
        assert len(functions) == 2

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_is_inside_test_detects_test_attribute(self) -> None:
        """Test detection of #[test] attribute."""
        analyzer = RustBaseAnalyzer()
        code = """
        #[test]
        fn test_something() {
            let x = foo().unwrap();
        }
        """
        node = analyzer.parse_rust(code)
        # Find the unwrap call
        calls = analyzer.walk_tree(node, "call_expression")
        # Should detect it's inside a test
        # (Implementation detail: need to check the call is inside test fn)

    def test_parse_rust_without_tree_sitter(self) -> None:
        """Test graceful handling when tree-sitter-rust not available."""
        analyzer = RustBaseAnalyzer()
        if not TREE_SITTER_RUST_AVAILABLE:
            result = analyzer.parse_rust("fn main() {}")
            assert result is None
```

#### 5. Create: `tests/unit/orchestrator/test_language_detector_rust.py`

```python
"""Tests for Rust language detection."""

from pathlib import Path
from src.orchestrator.language_detector import detect_language


class TestRustLanguageDetection:
    """Test Rust file detection."""

    def test_detect_rs_extension(self) -> None:
        """Test .rs files detected as Rust."""
        assert detect_language(Path("main.rs")) == "rust"
        assert detect_language(Path("lib.rs")) == "rust"
        assert detect_language(Path("src/module.rs")) == "rust"

    def test_detect_rs_case_insensitive(self) -> None:
        """Test .RS extension detected as Rust."""
        assert detect_language(Path("MAIN.RS")) == "rust"
```

### Testing Checklist
- [ ] `detect_language(Path("foo.rs"))` returns "rust"
- [ ] `RustBaseAnalyzer` initializes without error
- [ ] Parsing works when tree-sitter-rust installed
- [ ] Graceful None return when tree-sitter-rust not installed
- [ ] All existing tests still pass
- [ ] `just lint-full` passes

### Success Criteria
- Language detection works for .rs files
- RustBaseAnalyzer can parse Rust code
- Optional dependency handled gracefully
- No regressions in existing functionality

---

## PR2: Unwrap Abuse Detector

### Objective
Detect `.unwrap()` and `.expect()` abuse in non-test Rust code - a top AI code smell.

### Why This Rule?
Clippy has `clippy::unwrap_used` and `clippy::expect_used` but they are **allow-by-default**. AI-generated Rust code heavily abuses `.unwrap()` because it's the path of least resistance. This rule enforces safer patterns by default.

### Files to Create

#### 1. Create: `src/linters/rust_unwrap/__init__.py`
```python
"""Rust unwrap abuse detector."""
```

#### 2. Create: `src/linters/rust_unwrap/config.py`
```python
"""Configuration for Rust unwrap detector."""

from dataclasses import dataclass, field


@dataclass
class RustUnwrapConfig:
    """Configuration for unwrap abuse detection."""

    enabled: bool = True
    allow_in_tests: bool = True
    allow_in_main: bool = False
    allow_expect: bool = False  # If True, only flag unwrap, not expect
    ignored_paths: list[str] = field(default_factory=lambda: ["examples/", "benches/"])
```

#### 3. Create: `src/linters/rust_unwrap/analyzer.py`
```python
"""Analyzer for detecting unwrap/expect abuse in Rust code."""

from dataclasses import dataclass
from src.analyzers.rust_base import RustBaseAnalyzer, TREE_SITTER_RUST_AVAILABLE

if TREE_SITTER_RUST_AVAILABLE:
    from tree_sitter import Node


@dataclass
class UnwrapCall:
    """Represents a detected unwrap/expect call."""

    line: int
    column: int
    method: str  # "unwrap" or "expect"
    is_in_test: bool
    context: str  # Surrounding code snippet


class RustUnwrapAnalyzer(RustBaseAnalyzer):
    """Analyzer for detecting unwrap/expect calls."""

    def find_unwrap_calls(self, code: str) -> list[UnwrapCall]:
        """Find all unwrap() and expect() calls in code."""
        if not self.tree_sitter_available:
            return []

        root = self.parse_rust(code)
        if root is None:
            return []

        calls: list[UnwrapCall] = []
        self._find_unwrap_recursive(root, code, calls)
        return calls

    def _find_unwrap_recursive(self, node: Node, code: str, calls: list[UnwrapCall]) -> None:
        """Recursively find unwrap/expect method calls."""
        if node.type == "call_expression":
            # Check if this is a method call to unwrap or expect
            method_name = self._get_method_name(node)
            if method_name in ("unwrap", "expect"):
                calls.append(UnwrapCall(
                    line=node.start_point[0] + 1,  # 1-indexed
                    column=node.start_point[1],
                    method=method_name,
                    is_in_test=self.is_inside_test(node),
                    context=self._get_context(node, code),
                ))

        for child in node.children:
            self._find_unwrap_recursive(child, code, calls)

    def _get_method_name(self, call_node: Node) -> str:
        """Extract method name from call expression."""
        # In Rust tree-sitter, method calls are field_expression -> identifier
        for child in call_node.children:
            if child.type == "field_expression":
                for subchild in child.children:
                    if subchild.type == "field_identifier":
                        return self.extract_node_text(subchild)
        return ""

    def _get_context(self, node: Node, code: str) -> str:
        """Get code context around the node."""
        lines = code.split("\n")
        line_idx = node.start_point[0]
        if 0 <= line_idx < len(lines):
            return lines[line_idx].strip()
        return ""
```

#### 4. Create: `src/linters/rust_unwrap/linter.py`
```python
"""Rust unwrap abuse linter rule."""

from pathlib import Path
from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation, Severity
from src.linters.rust_unwrap.config import RustUnwrapConfig
from src.linters.rust_unwrap.analyzer import RustUnwrapAnalyzer


class RustUnwrapRule(BaseLintRule):
    """Detects unwrap/expect abuse in Rust code."""

    def __init__(self) -> None:
        self._analyzer = RustUnwrapAnalyzer()

    @property
    def rule_id(self) -> str:
        return "rust-unwrap.abuse"

    @property
    def rule_name(self) -> str:
        return "Rust Unwrap Abuse"

    @property
    def description(self) -> str:
        return (
            "Detects .unwrap() and .expect() calls that may panic at runtime. "
            "Prefer ?, unwrap_or(), unwrap_or_default(), or proper error handling."
        )

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for unwrap abuse in Rust code."""
        if context.language != "rust":
            return []

        if context.file_content is None:
            return []

        config = self._load_config(context)
        if not config.enabled:
            return []

        # Check ignored paths
        if context.file_path and self._is_ignored_path(context.file_path, config):
            return []

        calls = self._analyzer.find_unwrap_calls(context.file_content)
        return self._build_violations(calls, config, context)

    def _load_config(self, context: BaseLintContext) -> RustUnwrapConfig:
        """Load configuration from context or defaults."""
        # TODO: Load from context.metadata if available
        return RustUnwrapConfig()

    def _is_ignored_path(self, file_path: Path, config: RustUnwrapConfig) -> bool:
        """Check if file path is in ignored paths."""
        path_str = str(file_path)
        return any(ignored in path_str for ignored in config.ignored_paths)

    def _build_violations(
        self,
        calls: list,
        config: RustUnwrapConfig,
        context: BaseLintContext
    ) -> list[Violation]:
        """Convert unwrap calls to violations."""
        violations: list[Violation] = []

        for call in calls:
            # Skip if in test and allowed
            if call.is_in_test and config.allow_in_tests:
                continue

            # Skip expect if allowed
            if call.method == "expect" and config.allow_expect:
                continue

            suggestion = self._get_suggestion(call.method)
            violations.append(Violation(
                rule_id=self.rule_id,
                file_path=str(context.file_path) if context.file_path else "",
                line=call.line,
                column=call.column,
                message=f"Avoid .{call.method}() - it panics on None/Err. {suggestion}",
                severity=Severity.WARNING,
                suggestion=suggestion,
            ))

        return violations

    def _get_suggestion(self, method: str) -> str:
        """Get suggestion based on method type."""
        if method == "unwrap":
            return "Use ? operator, .unwrap_or(), .unwrap_or_default(), or match/if-let."
        return "Use ? operator with descriptive error, or proper error handling."
```

#### 5. Create: `src/cli/linters/rust_unwrap.py`
CLI command integration (follow existing linter CLI patterns).

#### 6. Create: `tests/unit/linters/rust_unwrap/test_analyzer.py`
#### 7. Create: `tests/unit/linters/rust_unwrap/test_linter.py`

### Test Cases
```rust
// Should flag:
let x = foo().unwrap();
let y = bar().expect("failed");
result.unwrap();

// Should NOT flag (in test):
#[test]
fn test_foo() {
    foo().unwrap();  // OK in tests
}

// Should NOT flag (proper handling):
let x = foo()?;
let y = foo().unwrap_or_default();
let z = foo().unwrap_or(fallback);
```

### Success Criteria
- [ ] Detects unwrap() in non-test code
- [ ] Detects expect() in non-test code
- [ ] Ignores calls in #[test] functions
- [ ] Ignores calls in #[cfg(test)] modules
- [ ] Provides actionable suggestions
- [ ] All output formats work (text, json, sarif)

---

## PR3: Excessive Clone Detector

### Objective
Detect `.clone()` abuse patterns common in AI-generated Rust code.

### Why This Rule?
AI-generated Rust code often uses `.clone()` to satisfy the borrow checker without understanding ownership. This creates performance issues and indicates poor code design.

### Patterns to Detect

1. **Clone in loops** - Cloning inside loop bodies
2. **Clone chains** - `.clone().clone()` or similar
3. **Immediate clone before move** - `let x = y.clone(); consume(x);` where `y` isn't used after

### Files to Create
- `src/linters/rust_clone/__init__.py`
- `src/linters/rust_clone/config.py`
- `src/linters/rust_clone/analyzer.py`
- `src/linters/rust_clone/linter.py`
- `src/cli/linters/rust_clone.py`
- `tests/unit/linters/rust_clone/`

### Test Cases
```rust
// Should flag - clone in loop:
for item in items {
    let copy = item.clone();  // Flag: clone in loop
    process(copy);
}

// Should flag - clone chain:
let x = data.clone().clone();  // Flag: chained clones

// Should NOT flag - necessary clone:
let owned = borrowed.clone();
use_borrowed(borrowed);
use_owned(owned);
```

### Success Criteria
- [ ] Detects clone inside loop bodies
- [ ] Detects chained clones
- [ ] Low false positive rate on idiomatic code
- [ ] Suggests Cow, Rc/Arc, or borrowing where appropriate

---

## PR4: Blocking-in-Async Detector

### Objective
Detect blocking operations inside async functions that can deadlock async runtimes.

### Why This Rule?
This is a **novel rule** - Clippy doesn't have this. AI mixes sync and async code without understanding the implications, causing hard-to-debug runtime issues.

### Patterns to Detect

1. **std::fs operations in async fn** - Should use tokio::fs
2. **std::thread::sleep in async fn** - Should use tokio::time::sleep
3. **Blocking network in async fn** - Should use async equivalents

### Files to Create
- `src/linters/rust_async/__init__.py`
- `src/linters/rust_async/config.py`
- `src/linters/rust_async/analyzer.py`
- `src/linters/rust_async/linter.py`
- `src/cli/linters/rust_async.py`
- `tests/unit/linters/rust_async/`

### Test Cases
```rust
// Should flag:
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();  // Flag!
}

async fn slow() {
    std::thread::sleep(Duration::from_secs(1));  // Flag!
}

// Should NOT flag - correct async usage:
async fn read_file() {
    let content = tokio::fs::read_to_string("file.txt").await?;
}

// Should NOT flag - not async:
fn sync_read() {
    std::fs::read_to_string("file.txt").unwrap();  // OK in sync
}
```

### Success Criteria
- [ ] Detects std::fs::* in async fn
- [ ] Detects std::thread::sleep in async fn
- [ ] Suggests tokio/async-std equivalents
- [ ] Does NOT flag sync functions
- [ ] Handles nested async blocks

---

## PR5: Extend Universal Linters to Rust

### Objective
Add Rust support to existing multi-language linters: SRP, Nesting, Magic Numbers.

### SRP for Rust

**Concept**: In Rust, a struct + its impl blocks = a "class". Count methods across all impl blocks for the struct.

```rust
struct Foo { ... }

impl Foo {
    fn method1() {}
    fn method2() {}
}

impl Foo {
    fn method3() {}  // Same struct, different impl block
}
// Total: 3 methods for Foo
```

### Nesting for Rust

Calculate nesting depth for Rust control flow:
- `if`, `match`, `loop`, `while`, `for`
- Closures add nesting
- `async` blocks add nesting

### Magic Numbers for Rust

Detect numeric literals that should be named constants:
```rust
// Flag:
if items.len() > 100 { ... }

// OK:
const MAX_ITEMS: usize = 100;
if items.len() > MAX_ITEMS { ... }
```

### Files to Create/Modify
- `src/linters/srp/rust_analyzer.py` - New
- `src/linters/nesting/rust_analyzer.py` - New
- `src/linters/magic_numbers/rust_analyzer.py` - New
- `src/linters/srp/linter.py` - Add `_check_rust()` dispatch
- `src/linters/nesting/linter.py` - Add `_check_rust()` dispatch
- `src/linters/magic_numbers/linter.py` - Add `_check_rust()` dispatch

### Success Criteria
- [ ] SRP: Counts methods across all impl blocks for a struct
- [ ] Nesting: Correctly calculates depth for Rust control flow
- [ ] Magic Numbers: Detects numeric literals outside const definitions
- [ ] No regression in Python/TypeScript behavior

---

## PR6: Validation Trials on Popular Repositories

### Objective
Run all Rust linters against popular, well-maintained Rust repositories to ensure zero false positives on idiomatic code and validate the rules provide real value.

### Why This PR?
Before releasing Rust support, we must validate that:
1. **No false positives** on well-maintained, idiomatic Rust code
2. **Rules provide value** - they catch actual issues (even in good codebases)
3. **Thresholds are tuned** - based on real-world data, not guesswork

### Target Repositories

| Repository | GitHub | Stars | Why Test? |
|------------|--------|-------|-----------|
| ripgrep | BurntSushi/ripgrep | 48k+ | Gold standard Rust code, BurntSushi is meticulous |
| tokio | tokio-rs/tokio | 26k+ | Async runtime - validates blocking-in-async detector |
| serde | serde-rs/serde | 9k+ | Macro-heavy, tests parser robustness |
| clap | clap-rs/clap | 14k+ | CLI library, good struct/impl patterns |
| reqwest | seanmonstar/reqwest | 10k+ | HTTP client, async patterns |
| actix-web | actix/actix-web | 21k+ | Web framework, async-heavy |

### Test Protocol

#### Step 1: Setup Trial Infrastructure

Create test script `tests/integration/rust_trials/run_trials.py`:

```python
"""
Run Rust linters against popular repositories to validate zero false positives.
"""

import subprocess
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass

REPOS = [
    ("ripgrep", "https://github.com/BurntSushi/ripgrep.git"),
    ("tokio", "https://github.com/tokio-rs/tokio.git"),
    ("serde", "https://github.com/serde-rs/serde.git"),
    ("clap", "https://github.com/clap-rs/clap.git"),
    ("reqwest", "https://github.com/seanmonstar/reqwest.git"),
    ("actix-web", "https://github.com/actix/actix-web.git"),
]

RULES = [
    "rust-unwrap",
    "rust-clone",
    "rust-async",
    "srp",
    "nesting",
    "magic-numbers",
]


@dataclass
class TrialResult:
    repo: str
    rule: str
    total_files: int
    total_violations: int
    violations: list[dict]


def clone_repo(name: str, url: str, target_dir: Path) -> Path:
    """Clone repository to target directory."""
    repo_path = target_dir / name
    subprocess.run(["git", "clone", "--depth=1", url, str(repo_path)], check=True)
    return repo_path


def run_linter(repo_path: Path, rule: str) -> dict:
    """Run thai-lint rule on repository, return JSON results."""
    result = subprocess.run(
        ["python", "-m", "src.cli", rule, str(repo_path), "--format", "json"],
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout) if result.stdout else {"violations": []}


def run_all_trials() -> list[TrialResult]:
    """Run all trials and collect results."""
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        for repo_name, repo_url in REPOS:
            print(f"Testing {repo_name}...")
            repo_path = clone_repo(repo_name, repo_url, tmp_path)

            # Count .rs files
            rs_files = list(repo_path.rglob("*.rs"))

            for rule in RULES:
                output = run_linter(repo_path, rule)
                violations = output.get("violations", [])

                results.append(TrialResult(
                    repo=repo_name,
                    rule=rule,
                    total_files=len(rs_files),
                    total_violations=len(violations),
                    violations=violations,
                ))

    return results


def generate_report(results: list[TrialResult]) -> str:
    """Generate markdown report of trial results."""
    # ... generate detailed report
```

#### Step 2: Run Trials

```bash
# Run all trials
python tests/integration/rust_trials/run_trials.py > results.json

# Generate report
python tests/integration/rust_trials/generate_report.py results.json > docs/rust-trials-report.md
```

#### Step 3: Review Each Violation

For each violation found, manually classify:

| Classification | Action |
|----------------|--------|
| **True Positive** | Document as proof of value - rule caught a real issue |
| **False Positive** | Must fix the rule - add exception or tune detection |
| **Intentional Pattern** | Add to allowed patterns if common and valid |

#### Step 4: Calculate Metrics

```
False Positive Rate = False Positives / Total Violations × 100%

Target: < 5% per rule
```

#### Step 5: Tune Rules

Based on findings:
- Add exceptions for common valid patterns
- Adjust thresholds
- Improve context detection (e.g., better test detection)

### Files to Create

```
tests/integration/rust_trials/
├── __init__.py
├── run_trials.py           # Main trial runner
├── generate_report.py      # Report generator
├── config.py               # Trial configuration
└── results/                # Trial results (gitignored except summary)
    └── .gitkeep

docs/
└── rust-trials-report.md   # Summary report (committed)
```

### Expected Outcomes

#### Best Case (Target)
- 0 false positives across all repos
- A few true positives found (proves value)
- No rule tuning needed

#### Acceptable Case
- < 5% false positive rate per rule
- True positives documented
- Minor rule tuning required

#### Unacceptable Case (Block Release)
- > 5% false positive rate on any rule
- Rules flag idiomatic patterns as violations
- Must fix before release

### Test Cases for Each Repo

#### ripgrep
- **unwrap**: Should find minimal/zero - BurntSushi uses proper error handling
- **clone**: Should find minimal - highly optimized code
- **async**: N/A - ripgrep is sync

#### tokio
- **unwrap**: May find some in tests (should be ignored)
- **clone**: May find some - async code often needs cloning
- **async**: Should find zero - tokio team knows async

#### serde
- **unwrap**: May find some in macro-generated code
- **clone**: May find some - serialization often clones
- **async**: N/A - serde is sync

### Success Criteria
- [ ] All 6 target repositories tested
- [ ] rust-unwrap: < 5% false positive rate
- [ ] rust-clone: < 5% false positive rate
- [ ] rust-async: < 5% false positive rate
- [ ] Universal linters: < 5% false positive rate
- [ ] Any true positives documented as proof of value
- [ ] Rules tuned based on findings
- [ ] Trial report committed to docs/
- [ ] CI job added to re-run trials on changes

---

## Implementation Guidelines

### Code Standards
- Follow existing linter patterns in `src/linters/`
- All files must have proper headers per `.ai/docs/FILE_HEADER_STANDARDS.md`
- Type hints required on all functions
- Google-style docstrings required

### Testing Requirements
- Unit tests for all analyzers and linters
- Integration tests for CLI commands
- Test both with and without tree-sitter-rust installed
- Test edge cases (empty files, malformed code, etc.)

### Documentation Standards
- Update CLI help text
- Add examples to rule descriptions
- Document configuration options

### Security Considerations
- No execution of Rust code, only static analysis
- Handle malformed input gracefully (no crashes)

### Performance Targets
- Parse and analyze 1000-line Rust file in < 100ms
- Graceful degradation without tree-sitter (return empty results, don't crash)

## Rollout Strategy

### Phase 1: Infrastructure (PR1)
- Merge PR1 first
- Verify CI passes with optional tree-sitter-rust

### Phase 2: Core Rules (PR2-PR4)
- Can be developed in parallel after PR1
- Each PR is independent

### Phase 3: Universal Extension (PR5)
- Depends on PR1
- Can be developed in parallel with PR2-PR4

### Phase 4: Validation (PR6) - GATE FOR RELEASE
- **Must pass before releasing Rust support**
- Run trials against 6 popular Rust repositories
- Verify < 5% false positive rate per rule
- Document findings and tune rules as needed
- Commit trial report to repository

## Success Metrics

### Launch Metrics
- [ ] All 6 PRs merged and tested
- [ ] CI pipeline green for Rust support
- [ ] Zero regressions in existing Python/TypeScript linters
- [ ] **Validation trials pass** (< 5% FP rate)

### Ongoing Metrics
- [ ] User reports of caught AI-generated Rust issues
- [ ] False positive rate < 5%
- [ ] Performance within targets
- [ ] Trial CI job stays green on updates
