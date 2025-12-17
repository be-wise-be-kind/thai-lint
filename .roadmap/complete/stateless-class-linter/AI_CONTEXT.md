# Stateless Class Linter - AI Context

**Purpose**: AI agent context document for implementing Stateless Class Linter

**Scope**: Python linter to detect classes without constructors/state that should be module-level functions

**Overview**: Comprehensive context document for AI agents working on the Stateless Class Linter feature.
    Provides architectural context, design decisions, integration patterns, and implementation guidance for
    building a new linter that detects a common anti-pattern in AI-generated Python code: stateless wrapper
    classes that add no value over module-level functions.

**Dependencies**: Python AST module, pytest, existing linter framework (DRY/SRP patterns)

**Exports**: Architectural vision, design decisions, integration patterns, implementation guidance

**Related**: PR_BREAKDOWN.md for TDD implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Test-Driven Development with AST-based static analysis following existing linter patterns

---

## Overview

The Stateless Class Linter detects a common anti-pattern in Python code where classes are used as namespaces
for grouping functions, despite having no instance state or constructor. This is particularly prevalent in
AI-generated code where LLMs over-apply class-based organization.

**The Anti-Pattern**:
```python
# ❌ BAD: Stateless class (should be module functions)
class TokenHasher:
    def tokenize(self, code: str) -> list[str]:
        return self._strip_comments(code)

    def _strip_comments(self, code: str) -> str:
        return code.split('#')[0]
```

**The Solution**:
```python
# ✅ GOOD: Module-level functions
def tokenize(code: str) -> list[str]:
    return _strip_comments(code)

def _strip_comments(code: str) -> str:
    return code.split('#')[0]
```

## Project Background

### The Problem
During our research into Python linters, we discovered:
1. **Pylint removed `no-self-use`** from defaults (moved to optional extension) - "too opinionated"
2. **Pylint's `R0903` (too-few-public-methods)** is too weak - doesn't catch classes with 2+ methods
3. **Ruff doesn't implement** PLR0903 at all
4. **No flake8 plugin** exists for this pattern
5. **Commercial tools** (SonarQube, etc.) don't check for this

### The Gap
**TypeScript has this**: `@typescript-eslint/no-extraneous-class` detects this pattern and is widely used.
**Python doesn't**: No popular linter catches stateless classes effectively.

### Why This Matters
- **Performance**: Instantiating classes is slower than calling functions
- **Clarity**: `tokenize(code)` is clearer than `TokenHasher().tokenize(code)`
- **AI code quality**: AI assistants frequently create these wrapper classes
- **Maintainability**: Future developers might assume state exists when it doesn't

## Feature Vision

### Goals
1. **Fill the gap** - Provide the linter rule that Python ecosystem is missing
2. **AI-focused** - Catch common mistakes in AI-generated code
3. **Low false positives** - Don't flag legitimate patterns (ABC, Protocol, decorators)
4. **Actionable** - Provide clear guidance on how to fix violations
5. **Performant** - Analyze files quickly (<100ms per file)

### Non-Goals
- Don't replace existing linters (complement them)
- Don't be overly opinionated (configurable exclusions)
- Don't break existing patterns (respect framework requirements)

## Current Application Context

### thai-lint Architecture
```
thai-lint/
├── src/
│   ├── cli.py                    # Click-based CLI
│   ├── linters/
│   │   ├── dry/                  # DRY linter (duplicate code detection)
│   │   ├── srp/                  # SRP linter (Single Responsibility)
│   │   └── stateless_class/      # NEW: Our linter
│   └── core/
│       └── linter_utils.py       # Shared linter utilities
└── tests/
    └── test_linters/
        ├── test_dry/
        ├── test_srp/
        └── test_stateless_class/  # NEW: Our tests
```

### Existing Linter Patterns to Follow

**Pattern 1: AST-based detection**
```python
# Example from DRY linter
class DuplicateDetector(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        # Analyze AST node
        self.generic_visit(node)
```

**Pattern 2: Violation model**
```python
# Standard violation structure
class Violation:
    def __init__(self, message: str, line_number: int, ...):
        self.message = message
        self.line_number = line_number
```

**Pattern 3: CLI integration**
```python
# src/cli.py
@cli.command()
@click.argument('path')
def linter_name(path):
    """Linter description."""
    # Run linter, report violations
```

## Target Architecture

### Core Components

#### 1. Detector (`src/linters/stateless_class/detector.py`)
**Responsibility**: AST-based detection of stateless classes

**Key Methods**:
- `detect_stateless_classes(code: str) -> List[Violation]` - Main entry point
- `_has_init_method(class_node) -> bool` - Check for __init__
- `_has_instance_attributes(class_node) -> bool` - Check for self.x assignments
- `_is_exception_case(class_node) -> bool` - Check ABC/Protocol/decorators
- `_count_public_methods(class_node) -> int` - Count non-private methods

**AST Analysis Strategy**:
```python
class StatelessClassVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        # 1. Check if has __init__ or __new__ → skip if yes
        # 2. Check if ABC/Protocol/decorated → skip if yes
        # 3. Check if has class attributes → skip if yes
        # 4. Count public methods → skip if < 2
        # 5. Check for instance attributes in methods → skip if found
        # 6. Flag as violation if all checks pass
```

#### 2. Violation Model (`src/linters/stateless_class/violation.py`)
**Responsibility**: Represent detected violations

```python
class StatelessClassViolation:
    class_name: str
    line_number: int
    message: str
    suggestion: str  # How to fix it
```

#### 3. CLI Integration (`src/cli.py`)
**Responsibility**: Expose linter via command line

```python
@cli.command()
@click.argument('path')
def stateless_class(path):
    """Detect stateless classes that should be functions."""
    # Load file, run detector, report violations
```

### User Journey

1. **Developer runs linter**:
   ```bash
   thai-lint stateless-class src/myfile.py
   ```

2. **Linter detects violation**:
   ```
   src/myfile.py:10:0: Stateless class detected
   Class 'TokenHasher' has no __init__ and no instance state.
   Consider refactoring to module-level functions.

   Suggestion:
   - Convert methods to standalone functions
   - Remove the class wrapper
   ```

3. **Developer refactors**:
   ```python
   # Before
   class TokenHasher:
       def tokenize(self, code): ...

   # After
   def tokenize(code): ...
   ```

4. **Linter passes**:
   ```bash
   thai-lint stateless-class src/myfile.py
   ✓ No violations found
   ```

### Data Flow

```
Python Source Code
      ↓
AST Parser (ast.parse)
      ↓
StatelessClassVisitor (AST traversal)
      ↓
Detection Logic (checks for anti-pattern)
      ↓
Violation List
      ↓
CLI Reporter (format and display)
      ↓
User Output
```

## Key Decisions Made

### Decision 1: Use AST, Not Regex
**Rationale**: AST provides accurate structure analysis, regex is fragile
**Trade-off**: AST is slower, but more reliable
**Alternative considered**: Text-based pattern matching (rejected - too error-prone)

### Decision 2: Require 2+ Public Methods
**Rationale**: Single-method classes might be strategy patterns, decorators, etc.
**Trade-off**: Might miss some violations (acceptable)
**Alternative considered**: Flag all stateless classes (rejected - too many false positives)

### Decision 3: Exclude ABC, Protocol, Decorated Classes
**Rationale**: These are framework requirements, not anti-patterns
**Trade-off**: Might create loopholes for abuse
**Alternative considered**: Flag everything, let user suppress (rejected - bad UX)

### Decision 4: TDD Approach
**Rationale**: Tests define the spec, ensure correctness, enable refactoring
**Trade-off**: Slower initial development
**Alternative considered**: Code-first (rejected - hard to validate correctness)

### Decision 5: Don't Analyze Method Complexity Deeply
**Rationale**: Keep performance high, avoid deep AST traversal
**Trade-off**: Might miss subtle state usage
**Alternative considered**: Deep control flow analysis (rejected - too slow)

## Integration Points

### With Existing Linters

**DRY Linter**:
- Shares AST visitor patterns
- Similar violation reporting
- Can run in sequence

**SRP Linter**:
- Complementary checks (different concerns)
- Similar CLI integration
- Shared configuration format

### With CLI Framework

**Click Integration**:
```python
# Follow existing pattern from DRY/SRP linters
@cli.command()
@click.argument('path', type=click.Path(exists=True))
def stateless_class(path):
    """Detect stateless classes."""
```

### With Configuration System

**Config file** (`.thai-lint.yml`):
```yaml
linters:
  stateless_class:
    enabled: true
    exclude_patterns:
      - "*Mixin"  # Exclude classes ending in Mixin
      - "Abstract*"  # Exclude classes starting with Abstract
```

## Success Metrics

### Technical Metrics
- **Test coverage**: >90%
- **Performance**: <100ms per file
- **Accuracy**: Zero false positives on exception cases
- **Code quality**: Pylint 10.00/10, all A-grade complexity

### Feature Metrics
- **Detection rate**: Catches TokenHasher and similar patterns
- **False positive rate**: <1% on our own codebase
- **User satisfaction**: Clear, actionable error messages

### Adoption Metrics
- **Dogfooding**: Used on thai-lint codebase itself
- **Documentation**: Complete user guide with examples
- **Integration**: Seamlessly works with existing linters

## Technical Constraints

### Performance Constraints
- Must analyze files quickly (<100ms per file)
- AST traversal should be single-pass
- Avoid deep recursion in method analysis

### Compatibility Constraints
- Python 3.11+ (our target version)
- Must work with existing pytest framework
- Must integrate with Click CLI

### Quality Constraints
- Zero test failures
- Pylint 10.00/10
- All complexity checks pass (A-grade)
- >90% test coverage

## AI Agent Guidance

### When Writing Tests (RED Phase)
1. **Start simple**: Write the most basic test first
2. **Be specific**: Test one behavior per test function
3. **Use clear names**: `test_detects_class_without_init` not `test_case_1`
4. **Include edge cases**: Empty classes, single method, etc.
5. **Test real-world cases**: Use TokenHasher as a test case

**Example test pattern**:
```python
def test_detects_stateless_class_without_init():
    """Should detect class with methods but no __init__."""
    code = '''
class MyClass:
    def method1(self): pass
    def method2(self): pass
'''
    violations = detect_stateless_classes(code)
    assert len(violations) == 1
    assert "MyClass" in violations[0].message
```

### When Implementing (GREEN Phase)
1. **Minimal code**: Only implement what tests require
2. **One test at a time**: Make one test pass, then move to next
3. **Follow patterns**: Study DRY/SRP linters for guidance
4. **Don't over-engineer**: Resist adding features not required by tests

**AST visitor pattern**:
```python
class StatelessClassVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_ClassDef(self, node):
        # Check conditions
        if self._is_stateless(node):
            self.violations.append(...)
        self.generic_visit(node)
```

### When Refactoring (REFACTOR Phase)
1. **Keep tests passing**: Run tests after every change
2. **Extract helpers**: DRY up repeated checks
3. **Add types**: Full type hints on all functions
4. **Document**: Google-style docstrings everywhere
5. **Lint**: Ensure Pylint 10.00/10

### Common Patterns

**Pattern: Checking for method**
```python
def _has_method(class_node: ast.ClassDef, method_name: str) -> bool:
    """Check if class has a method with given name."""
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == method_name:
            return True
    return False
```

**Pattern: Counting methods**
```python
def _count_public_methods(class_node: ast.ClassDef) -> int:
    """Count non-private methods in class."""
    return sum(
        1 for item in class_node.body
        if isinstance(item, ast.FunctionDef) and not item.name.startswith('_')
    )
```

**Pattern: Checking base classes**
```python
def _inherits_from_abc(class_node: ast.ClassDef) -> bool:
    """Check if class inherits from ABC."""
    for base in class_node.bases:
        if isinstance(base, ast.Name) and base.id == 'ABC':
            return True
    return False
```

## Risk Mitigation

### Risk: False Positives
**Mitigation**: Comprehensive exception handling (ABC, Protocol, decorators)
**Validation**: Run on our own codebase before releasing

### Risk: Performance Issues
**Mitigation**: Keep AST traversal simple, avoid deep recursion
**Validation**: Benchmark on large files (>1000 lines)

### Risk: Poor User Experience
**Mitigation**: Clear error messages with suggestions
**Validation**: User testing with example violations

### Risk: Maintenance Burden
**Mitigation**: Follow existing patterns, comprehensive tests
**Validation**: >90% test coverage, clear documentation

## Future Enhancements

### Phase 2 Features (Not in Initial Release)
- **Auto-fix**: Automatically refactor class to functions
- **Multi-language support**: Extend to TypeScript, JavaScript
- **IDE integration**: LSP server for real-time checking
- **Configuration UI**: Visual config editor

### Research Areas
- **Deep analysis**: Detect state usage in complex control flows
- **Semantic analysis**: Understand intent beyond structure
- **ML-based detection**: Learn patterns from codebases

### Community Feedback
After initial release:
- Gather user feedback on false positives
- Identify additional exception cases
- Refine detection heuristics
