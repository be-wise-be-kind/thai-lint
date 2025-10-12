# Magic Numbers Linter - AI Context

**Purpose**: AI agent context document for implementing Magic Numbers Linter

**Scope**: Detection of unnamed numeric literals (magic numbers) in Python and TypeScript code, encouraging use of named constants for better code maintainability

**Overview**: Comprehensive context document for AI agents working on the Magic Numbers Linter feature.
    Provides architectural guidance, design decisions, integration points, and implementation patterns for
    detecting magic numbers across Python and TypeScript codebases. Explains the rationale for TDD approach,
    acceptable contexts where numbers are permitted, and strategies for minimizing false positives while
    maintaining high detection accuracy. Essential reading before implementing any PR in this roadmap.

**Dependencies**: BaseLintRule interface, Python AST module, Tree-sitter (TypeScript), thai-lint orchestrator

**Exports**: Architectural guidance, design patterns, integration strategies, and AI agent decision-making framework

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: TDD-driven development with AST/Tree-sitter analysis, configurable rules, and context-aware detection

---

## Overview

Magic numbers are unnamed numeric literals scattered throughout code that reduce readability and maintainability. For example, `timeout = 3600` is less clear than `timeout = SECONDS_PER_HOUR`. This linter detects such literals and encourages extraction to named constants.

**Key Goals**:
1. Detect magic numbers in Python and TypeScript
2. Support configurable allowed numbers (0, 1, 2, etc.)
3. Recognize acceptable contexts (constants, test files, small integers in loops)
4. Minimize false positives through intelligent context analysis
5. Support ignore directives for legitimate cases

**Out of Scope**:
- Magic strings (string literals) - different rule
- Complex numbers in Python - specialized use case
- Numbers in type annotations - type system concern

## Project Background

**thai-lint** is a multi-language linter for AI-generated code. It follows a consistent architecture:

- **BaseLintRule interface**: All linters implement this interface
- **Orchestrator pattern**: Central orchestrator discovers and runs rules
- **Language-specific analyzers**: Python uses AST, TypeScript uses Tree-sitter
- **TDD approach**: Tests written first, implementation follows
- **Strict quality gates**: Pylint 10.00/10, Xenon A-grade complexity

**Existing linters**:
- File placement (file organization rules)
- Nesting depth (detects deeply nested code)
- SRP violations (Single Responsibility Principle)
- DRY violations (Don't Repeat Yourself)

Magic numbers linter follows these established patterns.

## Feature Vision

### User Stories

**As a developer**, I want to:
- Be notified when I use unnamed numeric literals
- Understand which numbers are acceptable in context (0, 1, small loop counters)
- Get suggestions for naming constants
- Suppress false positives with ignore directives

**As a team lead**, I want to:
- Enforce consistent constant naming across the codebase
- Reduce "what does this 3600 mean?" questions in code reviews
- Improve code self-documentation

**As an AI code generator**, I want to:
- Receive feedback when generating magic numbers
- Learn acceptable patterns (range(10) is okay, timeout=3600 is not)

### Success Vision

When complete:
1. **Python support**: Detects magic numbers in Python files with < 5% false positive rate
2. **TypeScript support**: Detects magic numbers in TS/JS files with same accuracy
3. **Self-validating**: thai-lint's own codebase passes the linter
4. **Well-documented**: Users understand when and how to use it
5. **CI/CD ready**: Integrates seamlessly into existing workflows

## Current Application Context

### Existing Architecture

```
thai-lint/
├── src/
│   ├── core/
│   │   ├── base.py              # BaseLintRule, BaseLintContext
│   │   ├── types.py             # Violation dataclass
│   │   └── linter_utils.py      # Helper functions
│   ├── orchestrator/
│   │   └── core.py              # Rule discovery and execution
│   ├── linters/
│   │   ├── nesting/             # Example: Nesting depth linter
│   │   │   ├── __init__.py
│   │   │   ├── linter.py        # Main rule class
│   │   │   ├── config.py        # Configuration dataclass
│   │   │   ├── python_analyzer.py
│   │   │   ├── typescript_analyzer.py
│   │   │   └── violation_builder.py
│   │   └── magic_numbers/       # NEW - To be created
│   └── cli.py                   # CLI interface
└── tests/
    └── unit/
        └── linters/
            └── magic_numbers/   # NEW - To be created
```

### Integration Points

1. **BaseLintRule interface**: Magic numbers linter implements this
2. **Orchestrator**: Auto-discovers MagicNumberRule via import
3. **CLI**: Accessible via `--rule magic-numbers`
4. **Configuration**: Loads from `.artifacts/generated-config.yaml`
5. **Ignore directives**: Parses `# thailint: ignore[magic-numbers]` comments

## Target Architecture

### Core Components

#### 1. MagicNumberRule (Main Linter Class)

```python
class MagicNumberRule(BaseLintRule):
    """Detects magic numbers in code.

    Responsibilities:
    - Implement BaseLintRule interface
    - Dispatch to language-specific analyzers
    - Coordinate configuration loading
    - Handle ignore directives
    """

    @property
    def rule_id(self) -> str:
        return "magic-numbers.numeric-literal"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Main entry point from orchestrator."""
        # Load config
        # Dispatch to Python or TypeScript analyzer
        # Filter by ignore directives
        # Return violations
```

#### 2. PythonMagicNumberAnalyzer

```python
class PythonMagicNumberAnalyzer:
    """Analyzes Python AST for magic numbers.

    Responsibilities:
    - Parse Python code into AST
    - Visit Constant nodes (ast.Constant)
    - Filter numeric types (int, float)
    - Collect violations with line numbers
    """

    def find_magic_numbers(self, tree: ast.AST, config: MagicNumberConfig) -> list:
        """Find all magic numbers in AST."""
        # Walk AST
        # Check each ast.Constant node
        # Filter by type (int, float only)
        # Return list of (node, value, line) tuples
```

#### 3. ContextAnalyzer

```python
class ContextAnalyzer:
    """Determines if a number is acceptable based on context.

    Acceptable contexts:
    - Constant definitions (UPPERCASE_NAME = value)
    - Small integers in range() or enumerate()
    - Test files (test_*.py)
    - Configuration contexts (__init__, setup, config functions)
    - Inside mathematical operations (may be formulas)
    """

    def is_acceptable_context(self, node: ast.Constant, context) -> bool:
        """Check if number is acceptable in current context."""
        # Check if constant definition
        # Check if in range/enumerate
        # Check if test file
        # etc.
```

#### 4. TypeScriptMagicNumberAnalyzer

```python
class TypeScriptMagicNumberAnalyzer:
    """Analyzes TypeScript using Tree-sitter.

    Responsibilities:
    - Parse TypeScript with Tree-sitter
    - Query for (number) nodes
    - Detect enum contexts (acceptable)
    - Return violations with positions
    """

    def find_magic_numbers(self, source: str, config) -> list:
        """Find magic numbers in TypeScript source."""
        # Parse with Tree-sitter
        # Query: (number) @literal
        # Check enum context
        # Return violations
```

#### 5. MagicNumberConfig

```python
@dataclass
class MagicNumberConfig:
    """Configuration for magic number detection."""

    enabled: bool = True
    allowed_numbers: set[int | float] = field(
        default_factory=lambda: {-1, 0, 1, 2, 10, 100, 1000}
    )
    max_small_integer: int = 10  # For range() context
```

### User Journey

#### Developer Writing Code

1. Developer writes Python code with magic number:
   ```python
   def retry_connection():
       max_attempts = 5
       timeout = 3600
   ```

2. Runs linter:
   ```bash
   python -m src.cli lint src/connection.py
   ```

3. Receives violation:
   ```
   src/connection.py:3:16 - magic-numbers.numeric-literal
   Magic number 3600 should be a named constant
   Suggestion: TIMEOUT_SECONDS = 3600
   ```

4. Fixes code:
   ```python
   TIMEOUT_SECONDS = 3600
   MAX_RETRY_ATTEMPTS = 5

   def retry_connection():
       max_attempts = MAX_RETRY_ATTEMPTS
       timeout = TIMEOUT_SECONDS
   ```

5. Linter passes ✅

#### Developer with Acceptable Number

1. Developer writes code with small loop counter:
   ```python
   def process_batch():
       for i in range(10):  # Small integer in range - acceptable
           process_item(i)
   ```

2. Runs linter:
   ```bash
   python -m src.cli lint src/batch.py
   ```

3. No violation (10 in range() is acceptable context) ✅

#### Developer with False Positive

1. Developer writes code where number has specific meaning:
   ```python
   def parse_header():
       magic_bytes = file.read(4)  # File format: 4-byte header
   ```

2. Receives violation (4 is not in allowed_numbers)

3. Adds ignore directive with justification:
   ```python
   def parse_header():
       # thailint: ignore[magic-numbers] - File format specifies 4-byte header
       magic_bytes = file.read(4)
   ```

4. Linter respects directive ✅

## Key Decisions Made

### Decision 1: Numbers Only, No Strings

**Rationale**: Magic strings are a separate concern with different patterns:
- Strings often have different acceptable contexts (URLs, SQL queries, templates)
- String detection has higher false positive rate
- Can be separate linter rule later

**Implementation**: Filter `isinstance(node.value, (int, float))` only

### Decision 2: TDD Approach (Tests First)

**Rationale**:
- Complex detection logic needs comprehensive test coverage
- Tests document expected behavior clearly
- Prevents regressions during refactoring
- Aligns with project standards (AGENTS.md mandates TDD for complex features)

**Implementation**:
- PR1: Write failing tests
- PR2: Implement to pass tests
- Repeat for TypeScript

### Decision 3: Context-Aware Detection

**Rationale**:
- Blanket "all numbers are magic" has too many false positives
- Some contexts legitimately use bare numbers (0, 1, loop counters)
- Users will disable linter if false positive rate > 10%

**Acceptable contexts**:
1. **Constant definitions**: `MAX_SIZE = 100` (defining a constant is okay)
2. **Small integers in range()**: `range(10)` (loop counters are clear in context)
3. **Test files**: Tests often use literal values for assertions
4. **Allowed numbers**: 0, 1, 2 are universally understood

**Implementation**: `ContextAnalyzer` class encapsulates decision logic

### Decision 4: Configurable Allowed Numbers

**Rationale**:
- Different projects have different conventions
- Some domains use specific numbers frequently (HTTP codes, exit codes)
- Users need escape hatch for project-specific patterns

**Implementation**:
```yaml
magic-numbers:
  allowed_numbers: [0, 1, 2, 10, 100, 200, 404, 500]  # HTTP codes allowed
  max_small_integer: 10
```

### Decision 5: Two Separate Analyzers (Python vs TypeScript)

**Rationale**:
- Python and TypeScript have different AST structures
- Python uses built-in `ast` module, TypeScript uses Tree-sitter
- Separation allows specialized optimizations
- Follows pattern from nesting linter

**Implementation**:
- `PythonMagicNumberAnalyzer` - Uses `ast` module
- `TypeScriptMagicNumberAnalyzer` - Uses Tree-sitter queries

### Decision 6: Self-Dogfooding Required (PR5)

**Rationale**:
- Best validation is running on real code (thai-lint itself)
- Discovers edge cases that contrived tests miss
- Proves linter is useful in practice
- Forces refinement of acceptable contexts

**Implementation**: PR5 dedicated to running linter on thai-lint codebase

## Integration Points

### With Existing Features

#### 1. BaseLintRule Interface

Magic numbers linter must implement:
```python
class MagicNumberRule(BaseLintRule):
    @property
    def rule_id(self) -> str: ...
    @property
    def rule_name(self) -> str: ...
    @property
    def description(self) -> str: ...
    def check(self, context: BaseLintContext) -> list[Violation]: ...
```

**Integration**: Return `Violation` objects matching `src/core/types.py` structure

#### 2. Configuration System

Load config from `.artifacts/generated-config.yaml`:
```yaml
magic-numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 10, 100, 1000]
  max_small_integer: 10
```

**Integration**: Use `load_linter_config(context, "magic-numbers", MagicNumberConfig)`

#### 3. Ignore Directive System

Respect inline ignore comments:
```python
timeout = 3600  # thailint: ignore[magic-numbers]
```

**Integration**: Use `IgnoreDirectiveParser` from `src/linter_config/ignore.py`

#### 4. Orchestrator Discovery

Orchestrator auto-discovers rules via import:
```python
# src/linters/magic_numbers/__init__.py
from .linter import MagicNumberRule

__all__ = ["MagicNumberRule"]
```

**Integration**: Export rule class in `__init__.py`

#### 5. CLI Integration

Accessible via CLI:
```bash
python -m src.cli lint --rule magic-numbers src/
```

**Integration**: Orchestrator handles CLI routing, no changes needed

### With Tree-sitter (TypeScript)

**Tree-sitter queries**:
```scheme
(number) @literal  ; Matches all numeric literals
```

**Enum context detection**:
```python
# Check if parent node is enum_declaration
parent = node.parent
while parent:
    if parent.type == "enum_declaration":
        return True  # Acceptable context
    parent = parent.parent
```

**Integration**: Follow pattern from `src/linters/nesting/typescript_analyzer.py`

## Success Metrics

### Technical Success
- [ ] Python magic number detection working
- [ ] TypeScript magic number detection working
- [ ] False positive rate < 5%
- [ ] Test coverage ≥ 80%
- [ ] Pylint score 10.00/10
- [ ] Xenon complexity A-grade
- [ ] No failing tests

### Feature Success
- [ ] Self-dogfooding: thai-lint passes its own magic numbers linter
- [ ] Documentation complete and clear
- [ ] Examples demonstrate real-world usage
- [ ] CI/CD integration seamless
- [ ] User feedback positive

## Technical Constraints

### Performance
- **AST parsing overhead**: Parsing large files is expensive
  - Mitigation: Cache parsed ASTs when possible
  - Mitigation: Orchestrator handles file filtering
- **Tree-sitter overhead**: Loading Tree-sitter parser takes time
  - Mitigation: Lazy load parser only when needed
  - Mitigation: Reuse parser instance across files

### Compatibility
- **Python versions**: Support Python 3.9+
  - Constraint: Use `ast` module features available in 3.9
- **TypeScript versions**: Support TS 4.0+
  - Constraint: Tree-sitter grammar must support modern TS

### False Positives
- **Trade-off**: Strict detection = more false positives, lenient = misses violations
  - Balance: Default allowed_numbers covers 90% of common cases
  - Escape hatch: Users can configure or use ignore directives

## AI Agent Guidance

### When Writing Tests (PR1, PR3)

1. **Start with simplest cases**:
   ```python
   def test_detects_simple_integer():
       """Should detect x = 42 as violation."""
   ```

2. **Progress to edge cases**:
   ```python
   def test_ignores_constant_definition():
       """Should not flag MAX_SIZE = 100."""
   ```

3. **Cover ignore directives**:
   ```python
   def test_respects_inline_ignore():
       """Should skip violations with ignore comment."""
   ```

4. **Use parametrized tests for variations**:
   ```python
   @pytest.mark.parametrize("value", [3.14, 42, 1e6, -273.15])
   def test_detects_various_numeric_types(value):
       # Test detection across different numeric formats
   ```

5. **Verify tests FAIL** (TDD RED phase):
   ```bash
   pytest tests/unit/linters/magic_numbers/ -v
   # Expected: All fail (implementation doesn't exist yet)
   ```

### When Implementing (PR2, PR4)

1. **Start with minimal implementation**:
   - Get one test passing
   - Add features incrementally
   - Refactor after tests pass

2. **Follow composition pattern**:
   ```python
   # Good: Small, focused classes
   class MagicNumberRule:
       def __init__(self):
           self._analyzer = PythonMagicNumberAnalyzer()
           self._context = ContextAnalyzer()
           self._violations = ViolationBuilder()

   # Bad: Monolithic class doing everything
   ```

3. **Keep functions A-grade complexity**:
   - Extract helper functions when cyclomatic complexity > 3
   - Use early returns to reduce nesting
   - Break complex conditions into named predicates

4. **Validate incrementally**:
   ```bash
   # After each function
   pytest tests/unit/linters/magic_numbers/test_python_magic_numbers.py::TestBasicDetection -v
   just lint-full
   ```

### When Dogfooding (PR5)

1. **Run linter on codebase**:
   ```bash
   python -m src.cli lint --rule magic-numbers src/ > violations.txt
   ```

2. **Categorize violations**:
   - True positives → Fix by extracting constants
   - False positives → Add to allowed_numbers or adjust context detection
   - Acceptable in context → Add ignore directive with justification

3. **Get user permission for ignore directives**:
   ```
   "Found 3 cases where numbers are acceptable in context (array indices).
   May I add ignore directives with justifications?"
   ```

4. **Document learnings**:
   - Note any unexpected patterns
   - Update tests if new edge cases found
   - Adjust configuration defaults if needed

### Common Patterns

#### Pattern 1: AST Visitor for Python
```python
class MagicNumberVisitor(ast.NodeVisitor):
    def __init__(self, config, context_analyzer):
        self.violations = []
        self.config = config
        self.context_analyzer = context_analyzer

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            if not self._is_acceptable(node):
                self.violations.append((node, node.value))
        self.generic_visit(node)
```

#### Pattern 2: Tree-sitter Query for TypeScript
```python
def find_numeric_literals(tree):
    query = language.query("(number) @literal")
    captures = query.captures(tree.root_node)
    return [node for node, _ in captures]
```

#### Pattern 3: Context Detection
```python
def is_acceptable_context(node, ast_tree):
    # Check constant definition
    if is_constant_definition(node):
        return True

    # Check range context
    if is_in_range_call(node):
        return True

    # Check test file
    if is_test_file(context.file_path):
        return True

    return False
```

## Risk Mitigation

### Risk 1: High False Positive Rate
**Impact**: Users disable linter if too many false alarms
**Mitigation**:
- Extensive acceptable context detection
- Configurable allowed_numbers
- Self-dogfooding validates real-world usefulness
- User can always use ignore directives

### Risk 2: Performance Degradation
**Impact**: Linting becomes too slow on large codebases
**Mitigation**:
- Limit to numeric literals only (no strings)
- Efficient AST traversal (single pass)
- Orchestrator handles parallelization

### Risk 3: Complexity Violations
**Impact**: Implementation fails quality gates (Xenon A-grade)
**Mitigation**:
- Composition pattern (small, focused classes)
- Extract helper functions early
- Continuous validation during development

### Risk 4: Inconsistent Behavior Python vs TypeScript
**Impact**: Users confused by different rules for different languages
**Mitigation**:
- Share configuration structure
- Document language-specific acceptable contexts
- Keep core detection logic similar

## Future Enhancements

### Enhancement 1: Magic Strings Detection
Detect unnamed string literals:
```python
# Could detect
response.status_code = "SUCCESS"  # Should be constant

# But high false positive risk with:
print("Hello, world!")  # Acceptable
sql = "SELECT * FROM users"  # Depends on context
```

**Complexity**: High (string contexts are more varied than numbers)

### Enhancement 2: Constant Naming Suggestions
Suggest better constant names based on context:
```python
# Violation detected
timeout = 3600

# Suggestion based on variable name
TIMEOUT_SECONDS = 3600  # "timeout" → "TIMEOUT_SECONDS"
```

**Complexity**: Medium (requires NLP or pattern matching)

### Enhancement 3: Auto-fix Capability
Automatically extract constants to top of file:
```python
# Before
def foo():
    x = 42

# After auto-fix
MAGIC_VALUE = 42

def foo():
    x = MAGIC_VALUE
```

**Complexity**: High (requires safe refactoring, scope analysis)

### Enhancement 4: Domain-Specific Contexts
Recognize domain-specific patterns:
- HTTP status codes (200, 404, 500)
- Exit codes (0, 1, 2)
- Signal numbers in UNIX

**Complexity**: Medium (requires domain knowledge database)

### Enhancement 5: Multi-Language Support
Add support for more languages:
- Java
- Go
- Rust

**Complexity**: Medium (requires language-specific parsers)

---

## Quick Reference for AI Agents

### Essential Files to Read
1. **PROGRESS_TRACKER.md** - Current status, next PR
2. **PR_BREAKDOWN.md** - Detailed implementation steps
3. **THIS FILE** - Architectural context

### Key Commands
```bash
# Run tests
pytest tests/unit/linters/magic_numbers/ -v

# Lint code
just lint-full

# Run magic numbers linter
python -m src.cli lint --rule magic-numbers src/
```

### Quality Gates
- [ ] Tests pass: `pytest` exit code 0
- [ ] Linting passes: `just lint-full` exit code 0
- [ ] Pylint score: Exactly 10.00/10
- [ ] Complexity: Xenon A-grade (no B, C, D)

### Getting Unstuck
1. Review example: `/home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/literals/magic_number_rules.py`
2. Check pattern: `src/linters/nesting/` (similar structure)
3. Read guide: `.ai/howtos/how-to-write-tests.md`
4. Ask user for clarification

---

**Remember**: This is a TDD project. Tests come before implementation. Quality gates are non-negotiable. When in doubt, ask the user.
