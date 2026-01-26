# Rust Linter Support - AI Context

**Purpose**: AI agent context document for implementing Rust Linter Support

**Scope**: Novel AI-focused Rust lint rules that complement (not duplicate) existing tools like Clippy

**Overview**: Comprehensive context document for AI agents working on the Rust Linter Support feature.
    Adds Rust language support to thai-lint with focus on detecting anti-patterns commonly generated
    by AI coding assistants. Implements tree-sitter-based parsing for Rust code analysis and provides
    3 novel lint rules targeting unwrap abuse, clone abuse, and blocking-in-async patterns.

**Dependencies**: tree-sitter, tree-sitter-rust (optional), existing thai-lint infrastructure

**Exports**: RustBaseAnalyzer, 3 novel Rust linters, extended universal linters for Rust

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: tree-sitter parsing with pattern detection, following existing TypeScript analyzer patterns

---

## Overview

This feature adds Rust language support to thai-lint. The key principle is **complementing, not duplicating** existing tools like Clippy. We focus on:

1. **Patterns Clippy doesn't enforce by default** - Rules that exist in Clippy but are `allow-by-default`
2. **Novel patterns** - Rules that don't exist in Clippy at all
3. **AI-specific focus** - Patterns that AI code generators commonly produce incorrectly

## Project Background

### Why Rust Support?

1. **Growing Rust adoption** - Rust is increasingly popular for systems programming
2. **AI code quality issues** - AI assistants generate Rust code with common anti-patterns
3. **Clippy gaps** - Many useful rules are disabled by default or missing entirely
4. **Unified tooling** - thai-lint provides consistent experience across languages

### Research Findings

From web research on Rust anti-patterns and AI-generated code:

| Pattern | Clippy Status | AI Frequency | thai-lint Value |
|---------|---------------|--------------|-----------------|
| `.unwrap()` abuse | allow-by-default | Very High | High |
| `.clone()` abuse | partial detection | High | High |
| Blocking in async | Not covered | High | Very High (novel) |
| Magic numbers | Not covered well | Medium | Medium |

## Feature Vision

### Goals
- Detect top 3 AI-generated Rust code smells
- Zero duplication of Clippy's default-enabled rules
- Graceful degradation without tree-sitter-rust installed
- Consistent experience with Python/TypeScript linters

### Non-Goals
- Replace Clippy (it's excellent for what it does)
- Implement all Clippy rules
- Deep semantic analysis (ownership tracking, lifetime analysis)
- Rust compiler integration

## Current Application Context

### Existing Multi-Language Architecture

thai-lint already supports multiple languages through:

1. **Language Detection** (`src/orchestrator/language_detector.py`)
   - Extension-based detection
   - Easy to extend with new languages

2. **Base Analyzers** (`src/analyzers/`)
   - `TypeScriptBaseAnalyzer` - tree-sitter for TypeScript
   - Pattern to follow for `RustBaseAnalyzer`

3. **Multi-Language Rules** (`src/core/base.py`)
   - `BaseLintRule` with language dispatch
   - Rules can support multiple languages via `_check_<language>()` methods

### Existing Linters to Extend

| Linter | Python | TypeScript | Rust (New) |
|--------|--------|------------|------------|
| SRP | AST | tree-sitter | tree-sitter |
| Nesting | AST | tree-sitter | tree-sitter |
| Magic Numbers | AST | tree-sitter | tree-sitter |

## Target Architecture

### Core Components

```
src/
├── analyzers/
│   ├── typescript_base.py    # Existing
│   └── rust_base.py          # NEW - tree-sitter Rust parsing
├── linters/
│   ├── rust_unwrap/          # NEW - Unwrap abuse detection
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── analyzer.py
│   │   └── linter.py
│   ├── rust_clone/           # NEW - Clone abuse detection
│   │   └── ...
│   ├── rust_async/           # NEW - Blocking-in-async detection
│   │   └── ...
│   ├── srp/
│   │   ├── rust_analyzer.py  # NEW - Rust SRP analysis
│   │   └── linter.py         # MODIFY - Add _check_rust()
│   └── ...
└── orchestrator/
    └── language_detector.py  # MODIFY - Add .rs -> rust
```

### Dependency Graph

```
PR1 (Infrastructure)
  ↓
  ├─→ PR2 (Unwrap Detector)
  ├─→ PR3 (Clone Detector)
  ├─→ PR4 (Async Detector)
  └─→ PR5 (Universal Linters)
```

All PRs after PR1 can be developed in parallel.

### User Journey

1. User runs `thai-lint rust` on a Rust project
2. Language detector identifies `.rs` files
3. Rust analyzers parse code using tree-sitter
4. Novel rules detect AI-generated anti-patterns
5. Violations reported in text/json/sarif format
6. User fixes issues, improving code quality

## Key Decisions Made

### Decision 1: tree-sitter for Parsing

**Choice**: Use tree-sitter-rust for AST parsing

**Rationale**:
- Already used for TypeScript (proven pattern)
- Fast, reliable parsing
- Consistent API across languages
- Optional dependency (graceful degradation)

**Alternatives Considered**:
- Regex-based detection: Too fragile, high false positive rate
- syn crate (Rust AST): Would require Rust toolchain, heavy dependency
- rustc AST: Same issues as syn, plus unstable API

### Decision 2: Optional Dependency

**Choice**: Make tree-sitter-rust optional like tree-sitter-typescript

**Rationale**:
- Users who don't need Rust support don't need the dependency
- Consistent with existing TypeScript approach
- Graceful degradation (return empty results, don't crash)

### Decision 3: Novel Rules Only

**Choice**: Only implement rules that Clippy doesn't enforce by default

**Rationale**:
- Avoid duplication of effort
- Clippy is excellent and well-maintained
- Focus on unique value (AI code quality)
- Users can run both tools together

### Decision 4: Test-Aware Detection

**Choice**: Unwrap detector ignores `#[test]` functions and `#[cfg(test)]` modules

**Rationale**:
- `.unwrap()` is idiomatic in test code
- Reduces false positives significantly
- Matches Rust community conventions

## Integration Points

### With Existing Features

1. **CLI Integration**
   - Add `thai-lint rust` command group
   - Follow existing CLI patterns
   - Support all output formats

2. **Configuration**
   - Use existing config loading system
   - Add Rust-specific config sections
   - Support `.thailint.yaml` configuration

3. **Output Formats**
   - Violations use existing `Violation` dataclass
   - SARIF, JSON, text formatters work unchanged
   - Rule IDs follow `rust-<category>.<rule>` pattern

### With External Tools

1. **Clippy**
   - Complementary, not competitive
   - Users can run both in CI
   - No overlapping default rules

2. **rustfmt**
   - thai-lint doesn't handle formatting
   - Users should use rustfmt for style

3. **cargo**
   - thai-lint is language-agnostic, doesn't use cargo
   - Works on individual .rs files

## Success Metrics

### Technical
- [ ] Parsing 1000-line Rust file < 100ms
- [ ] Zero crashes on malformed input
- [ ] Works with and without tree-sitter-rust

### Quality
- [ ] < 5% false positive rate
- [ ] Actionable suggestions for each violation
- [ ] Clear error messages

### Adoption
- [ ] Users report catching AI-generated issues
- [ ] Positive feedback on rule value

## Validation Strategy

Before release, all Rust linters must pass validation trials against popular, well-maintained Rust repositories. This ensures rules don't flag idiomatic code as violations.

### Target Repositories

| Repository | Purpose |
|------------|---------|
| **ripgrep** | Gold standard Rust - if we flag this, we're wrong |
| **tokio** | Async runtime - validates async detector doesn't false positive |
| **serde** | Macro-heavy - validates parser robustness |
| **clap** | CLI library - good struct patterns |
| **reqwest** | HTTP client - async patterns |
| **actix-web** | Web framework - complex async |

### Acceptance Criteria

1. **False Positive Rate < 5%** per rule across all repos
2. **True Positives Documented** - any real issues found prove value
3. **Rules Tuned** - adjust based on findings before release

### What Counts as False Positive?

| Scenario | Classification |
|----------|----------------|
| Flagging idiomatic `.unwrap()` in builder pattern | False Positive |
| Flagging `.clone()` where borrow would break code | False Positive |
| Flagging std::fs in sync helper called from async | False Positive |
| Flagging `.unwrap()` in quick script/example | True Positive (intentional) |
| Flagging unnecessary `.clone()` | True Positive |

See PR_BREAKDOWN.md PR6 for detailed test protocol.

## Technical Constraints

1. **No Runtime Execution**
   - Static analysis only
   - No Rust toolchain required
   - No cargo integration

2. **Optional Dependencies**
   - tree-sitter-rust must be optional
   - Graceful degradation required

3. **Performance**
   - Must not significantly slow down non-Rust linting
   - Lazy loading of Rust analyzers

4. **Compatibility**
   - Python 3.10+
   - No breaking changes to existing linters

## AI Agent Guidance

### When Implementing Analyzers

1. **Follow TypeScriptBaseAnalyzer pattern**
   - Same structure, different tree-sitter language
   - Same methods: `parse_*`, `walk_tree`, `extract_*`

2. **Handle missing tree-sitter gracefully**
   ```python
   try:
       import tree_sitter_rust
       AVAILABLE = True
   except ImportError:
       AVAILABLE = False
   ```

3. **Use tree-sitter node types**
   - Rust functions: `function_item`
   - Structs: `struct_item`
   - Impl blocks: `impl_item`
   - Method calls: `call_expression` with `field_expression`

### When Implementing Rules

1. **Follow existing linter patterns**
   - Config dataclass in `config.py`
   - Analyzer in `analyzer.py`
   - Rule in `linter.py`

2. **Provide actionable suggestions**
   - Not just "bad pattern detected"
   - Suggest specific alternatives

3. **Consider context**
   - Test code vs production code
   - Async vs sync functions
   - File paths (examples/, tests/)

### Common Patterns

#### Detecting Method Calls
```python
# tree-sitter structure for foo.unwrap():
# call_expression
#   field_expression
#     identifier: "foo"
#     field_identifier: "unwrap"
#   arguments
```

#### Checking if Inside Test
```python
def is_inside_test(self, node: Node) -> bool:
    """Walk up tree looking for #[test] or #[cfg(test)]."""
    current = node
    while current is not None:
        if current.type == "function_item":
            for attr in self._get_attributes(current):
                if "test" in attr:
                    return True
        current = current.parent
    return False
```

#### Checking if Function is Async
```python
def is_async_function(self, node: Node) -> bool:
    """Check for 'async' keyword in function_item."""
    for child in node.children:
        if child.type == "async":
            return True
    return False
```

## Risk Mitigation

### Risk: tree-sitter-rust API Changes

**Mitigation**: Pin version in pyproject.toml, test against specific version

### Risk: High False Positive Rate

**Mitigation**:
- Extensive test cases with real-world Rust code
- Configurable rules (can disable specific patterns)
- Test-aware detection reduces noise
- **PR6 Validation Trials**: Run against 6 popular repos before release
  - ripgrep, tokio, serde, clap, reqwest, actix-web
  - Must achieve < 5% false positive rate per rule
  - Tune rules based on real-world findings

### Risk: Performance Issues

**Mitigation**:
- Lazy loading of Rust parser
- Efficient tree traversal
- Benchmark during development

### Risk: Maintenance Burden

**Mitigation**:
- Follow existing patterns exactly
- Comprehensive test coverage
- Clear documentation

## Future Enhancements

After initial implementation, potential additions:

1. **More Async Patterns**
   - Detect `.await` without timeout
   - Detect unbounded channel usage

2. **Unsafe Code Patterns**
   - Basic unsafe block detection
   - Common unsafe anti-patterns

3. **Error Handling Patterns**
   - Detect `Box<dyn Error>` abuse
   - Suggest thiserror/anyhow patterns

4. **Ownership Patterns**
   - Detect unnecessary `&String` vs `&str`
   - Suggest more efficient borrowing

These would be separate PRs after the initial 6-PR implementation (including validation trials).
