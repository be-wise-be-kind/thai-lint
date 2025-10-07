# Nesting Depth Linter - AI Context & Architecture

**Purpose**: Architectural context and design decisions for the Nesting Depth Linter feature

**Scope**: Technical architecture, AST analysis approach, multi-language support, and integration patterns

**Overview**: Comprehensive architectural documentation for the Nesting Depth Linter feature. Explains
    the design decisions behind AST-based depth analysis, visitor pattern implementation, multi-language
    support strategy (Python + TypeScript), configuration schema, integration with the orchestrator
    framework, and refactoring pattern recommendations. Provides technical context for AI agents to
    understand the implementation approach, key algorithms, and design trade-offs. Essential reading
    before starting implementation work.

**Dependencies**: Python ast module, @typescript-eslint/typescript-estree, orchestrator framework, configuration system

**Exports**: Architecture documentation, design patterns, algorithm explanations, integration guidance

**Related**: PROGRESS_TRACKER.md for current status, PR_BREAKDOWN.md for implementation steps, reference implementation at /home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/style/nesting_rules.py

**Implementation**: AST visitor pattern with depth tracking, configurable limits, multi-language analyzers, helpful violation messages

---

## Feature Overview

### What is Nesting Depth?

Nesting depth refers to how many levels of control structures (if, for, while, try, etc.) are nested within a function. Excessive nesting harms code readability and is a sign that a function is doing too much.

**Example**:
```python
def process_data(items):          # Function body = depth 1
    for item in items:             # Depth 2
        if item.valid:             # Depth 3
            for child in item.children:  # Depth 4
                if child.active:   # Depth 5 - VIOLATION (if limit is 4)
                    print(child)
```

### Why This Linter Matters

1. **Readability**: Deeply nested code is hard to understand
2. **Maintainability**: Fewer bugs in flatter code structures
3. **Testability**: Simpler functions are easier to test
4. **Code Smell**: Deep nesting signals need for refactoring

### Goals

1. Detect excessive nesting depth in Python and TypeScript
2. Provide helpful, actionable violation messages
3. Support configurable limits (default: 4)
4. Integrate seamlessly with existing linter framework
5. Dogfood on thai-lint itself to validate usefulness

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator                            │
│  (Auto-discovers NestingDepthRule via registry)             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Calls check(context)
                  │
        ┌─────────▼──────────┐
        │  NestingDepthRule  │
        │   (BaseLintRule)   │
        └─────────┬──────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
   ┌────▼────────────┐  ┌────▼─────────────────┐
   │ PythonNesting   │  │ TypeScriptNesting    │
   │ Analyzer        │  │ Analyzer             │
   │ (ast module)    │  │ (typescript-estree)  │
   └─────────────────┘  └──────────────────────┘
```

### Component Responsibilities

#### 1. NestingDepthRule
- **Purpose**: Main rule class implementing BaseLintRule interface
- **Responsibilities**:
  - Load configuration (max_nesting_depth, enabled)
  - Route to language-specific analyzer (Python vs TypeScript)
  - Create Violation objects with helpful messages
  - Handle syntax errors gracefully
- **Pattern**: Strategy pattern for language-specific analysis

#### 2. PythonNestingAnalyzer
- **Purpose**: Python AST-based depth calculator
- **Responsibilities**:
  - Parse Python code using `ast.parse()`
  - Find all function definitions (FunctionDef, AsyncFunctionDef)
  - Calculate maximum nesting depth for each function
  - Return depth and line number of deepest nesting
- **Pattern**: Visitor pattern for AST traversal

#### 3. TypeScriptNestingAnalyzer
- **Purpose**: TypeScript AST-based depth calculator
- **Responsibilities**:
  - Parse TypeScript code using typescript-estree
  - Find all function definitions (FunctionDeclaration, ArrowFunctionExpression, etc.)
  - Calculate maximum nesting depth for each function
  - Return depth and line number of deepest nesting
- **Pattern**: Visitor pattern for AST traversal

#### 4. NestingConfig
- **Purpose**: Configuration schema
- **Responsibilities**:
  - Define max_nesting_depth (default: 4)
  - Validate configuration values (positive integers)
  - Load from YAML/JSON config files
  - Support per-file/per-directory overrides
- **Pattern**: Dataclass with validation

---

## Algorithm Details

### Depth Calculation Algorithm

Based on reference implementation at `/home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/style/nesting_rules.py`:

```python
def calculate_max_depth(func_node):
    """Calculate maximum nesting depth in a function.

    Algorithm:
    1. Start at depth 1 for function body statements
    2. For each statement, recursively visit AST nodes
    3. Increment depth when encountering nesting node types
    4. Track maximum depth seen (not just current depth)
    5. Return max_depth and line number where it occurred
    """
    max_depth = 0
    max_depth_line = func_node.lineno

    def visit_node(node, current_depth=0):
        nonlocal max_depth, max_depth_line

        # Update max if current is higher
        if current_depth > max_depth:
            max_depth = current_depth
            max_depth_line = node.lineno

        # Check if this node increases nesting
        if isinstance(node, NESTING_NODE_TYPES):
            current_depth += 1

        # Recursively visit all children
        for child in ast.iter_child_nodes(node):
            visit_node(child, current_depth)

    # Start at depth 1 for function body
    for stmt in func_node.body:
        visit_node(stmt, 1)

    return max_depth, max_depth_line
```

### Why Start at Depth 1?

The function body itself is depth 1. This matches the reference implementation and provides intuitive semantics:
- Depth 1: Function body (no nesting)
- Depth 2: One level of nesting (single if/for/while)
- Depth 3: Two levels of nesting
- Depth 4: Three levels (at the default limit)
- Depth 5+: Violation with default limit

**Alternative would be depth 0** for function body, but this is less intuitive because:
- "No nesting" would be depth 0 (confusing)
- "One level of nesting" would be depth 1 (but actually has one nested block)

### Nesting Node Types

#### Python (via ast module)
Nodes that increase nesting depth:
```python
NESTING_NODE_TYPES = (
    ast.If,           # if/elif/else
    ast.For,          # for loops
    ast.While,        # while loops
    ast.With,         # with statements
    ast.AsyncWith,    # async with statements
    ast.Try,          # try blocks
    ast.ExceptHandler,# except clauses
    ast.Match,        # match statements (Python 3.10+)
    ast.match_case,   # case clauses within match
)
```

**Why these nodes?**
- They introduce new indentation levels
- They create nested scopes
- They increase cognitive load when reading code

**Nodes that DON'T increase depth:**
- Function definitions (nested functions start fresh at depth 1)
- Class definitions (depth tracking is per-function)
- Simple assignments, expressions, returns

#### TypeScript (via typescript-estree)
Nodes that increase nesting depth:
```typescript
NESTING_NODE_TYPES = {
    'IfStatement',          // if/else
    'ForStatement',         // for loops
    'ForInStatement',       // for-in loops
    'ForOfStatement',       // for-of loops
    'WhileStatement',       // while loops
    'DoWhileStatement',     // do-while loops
    'TryStatement',         // try blocks
    'CatchClause',          // catch clauses
    'SwitchStatement',      // switch statements
    'WithStatement',        // with statements (deprecated)
}
```

### Handling Edge Cases

#### Empty Functions
```python
def empty():
    pass
```
- Depth: 1 (function body)
- No violation (no nested blocks)

#### Sibling Blocks (Non-nested)
```python
def multiple_ifs(x):
    if x > 0:
        print("positive")
    if x < 0:
        print("negative")
    if x == 0:
        print("zero")
```
- All three `if` statements are at depth 2 (siblings)
- Max depth: 2
- No violation (not cumulative)

#### Nested Functions
```python
def outer():
    if condition:          # Depth 2 in outer
        def inner():
            if other:      # Depth 2 in inner (starts fresh)
                pass
```
- Nested function definitions start fresh at depth 1
- Each function tracked independently

#### Syntax Errors
```python
def broken(
    x = 1  # Missing closing paren
```
- ast.parse() will raise SyntaxError
- Catch and return helpful Violation (not crash)
- Suggestion: "Fix syntax errors before checking nesting"

---

## Configuration Design

### Configuration Schema

```yaml
# .thailint.yaml
linters:
  nesting:
    enabled: true
    max_nesting_depth: 4  # Default from reference implementation

# Stricter limit for critical code
directories:
  - path: src/core/
    linters:
      nesting:
        max_nesting_depth: 3

# More lenient for complex domains
  - path: src/orchestrator/
    linters:
      nesting:
        max_nesting_depth: 5
```

### Why max_nesting_depth: 4?

Based on reference implementation and industry best practices:
- **Depth 1-2**: Simple, easy to understand
- **Depth 3-4**: Moderate complexity, still manageable
- **Depth 5+**: High complexity, refactoring recommended

Studies show cognitive load increases exponentially with nesting depth. Limit of 4 balances pragmatism with code quality.

### Per-File Overrides

```yaml
# Global default
linters:
  nesting:
    max_nesting_depth: 4

# Per-file override
files:
  - path: src/cli.py
    linters:
      nesting:
        max_nesting_depth: 5  # CLI arg parsing can be complex
```

---

## Violation Message Design

### Goals for Violation Messages
1. **Identify the problem**: Which function, what depth
2. **Explain the issue**: Why it matters
3. **Suggest solutions**: How to fix it

### Message Template

```
Function '{function_name}' has excessive nesting depth ({depth})

Maximum nesting depth of {depth} exceeds limit of {max_allowed}.
Consider extracting nested logic to separate functions, using early
returns, or applying guard clauses to reduce nesting.
```

### Example Output

```
src/cli.py:45: Function 'load_config' has excessive nesting depth (5)
  Suggestion: Maximum nesting depth of 5 exceeds limit of 4. Consider
  extracting nested logic to separate functions, using early returns,
  or applying guard clauses to reduce nesting.
```

### Violation Context

Each Violation includes metadata:
```python
Violation(
    rule_id='nesting.excessive-depth',
    rule_name='Excessive Nesting Depth',
    message="Function 'load_config' has excessive nesting depth (5)",
    file_path=Path('src/cli.py'),
    line_number=45,
    severity=Severity.ERROR,
    suggestion="Maximum nesting depth of 5 exceeds limit of 4...",
    context={
        'function_name': 'load_config',
        'depth': 5,
        'max_allowed': 4,
        'deepest_line': 52,  # Line where max depth occurred
    }
)
```

---

## Refactoring Patterns

These patterns are recommended in violation suggestions and documented during dogfooding.

### Pattern 1: Early Returns (Guard Clauses)

**When to use**: Multiple nested conditions checking preconditions

**Before** (depth 5):
```python
def validate_input(data):
    if data is not None:
        if isinstance(data, dict):
            if 'key' in data:
                if data['key'] is not None:
                    if data['key'] > 0:
                        return True
    return False
```

**After** (depth 2):
```python
def validate_input(data):
    if data is None:
        return False
    if not isinstance(data, dict):
        return False
    if 'key' not in data:
        return False
    if data['key'] is None:
        return False
    return data['key'] > 0
```

**Benefits**:
- Reduces nesting from 5 to 2
- Explicit failure cases
- Easier to read and test

### Pattern 2: Extract Method

**When to use**: Nested loops or complex nested blocks

**Before** (depth 6):
```python
def process_items(items):
    for item in items:
        if item.valid:
            for child in item.children:
                if child.active:
                    for sub in child.subs:
                        if sub.enabled:
                            print(sub)
```

**After** (depth 3):
```python
def process_items(items):
    for item in items:
        if item.valid:
            _process_children(item.children)

def _process_children(children):
    for child in children:
        if child.active:
            _process_subs(child.subs)

def _process_subs(subs):
    for sub in subs:
        if sub.enabled:
            print(sub)
```

**Benefits**:
- Each function has clear, single responsibility
- Easier to test in isolation
- Reduced cognitive load

### Pattern 3: Combine Conditions

**When to use**: Multiple sequential conditions that can be AND-ed

**Before** (depth 5):
```python
def check_eligibility(user):
    if user.active:
        if user.verified:
            if user.age >= 18:
                if user.country == 'US':
                    return True
    return False
```

**After** (depth 2):
```python
def check_eligibility(user):
    return (
        user.active
        and user.verified
        and user.age >= 18
        and user.country == 'US'
    )
```

**Benefits**:
- Single expression
- Clear logical relationship
- Minimal nesting

### Pattern 4: Functional Approaches

**When to use**: Nested loops with filtering/mapping

**Before** (depth 4):
```python
def get_active_names(items):
    result = []
    for item in items:
        if item.active:
            for child in item.children:
                result.append(child.name)
    return result
```

**After** (depth 2):
```python
def get_active_names(items):
    active_items = [item for item in items if item.active]
    return [
        child.name
        for item in active_items
        for child in item.children
    ]
```

**Benefits**:
- Declarative rather than imperative
- Reduced nesting
- Often more concise

---

## Integration with Orchestrator

### Auto-Discovery

The NestingDepthRule is automatically discovered by the orchestrator's rule registry:

```python
# src/linters/nesting/linter.py
from src.core.base import BaseLintRule

class NestingDepthRule(BaseLintRule):
    """Auto-discovered by registry via inheritance."""
    pass
```

Registry scans `src/linters/**/` and finds all BaseLintRule subclasses.

### Language Routing

Orchestrator detects file language and routes to appropriate analyzer:

```python
# In NestingDepthRule.check()
if context.language == 'python':
    return self._check_python(context, config)
elif context.language in ('typescript', 'javascript'):
    return self._check_typescript(context, config)
else:
    return []  # Unsupported language, no violations
```

### Context Passing

Orchestrator creates LintContext with:
- `file_path`: Path to file being analyzed
- `file_content`: Full file content as string
- `language`: Detected language ('python', 'typescript', etc.)
- `metadata`: Config dictionary with linter settings

---

## Multi-Language Support

### Python Support

**Parser**: Python `ast` module (built-in, no dependencies)

**Advantages**:
- Native Python support
- No external dependencies
- Accurate AST parsing
- Handles all Python versions (3.11+)

**Implementation**:
```python
import ast

tree = ast.parse(file_content)
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        depth = calculate_max_depth(node)
```

### TypeScript Support

**Parser**: `@typescript-eslint/typescript-estree` (Node.js package)

**Challenges**:
- Requires Node.js runtime
- External dependency
- IPC overhead (Python → Node.js)

**Implementation Approaches**:

#### Approach 1: Subprocess (Initial)
```python
import subprocess
import json

def parse_typescript(code: str) -> dict:
    result = subprocess.run(
        ['node', 'parse_typescript.js'],
        input=code,
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)
```

#### Approach 2: Node.js Service (Future)
```python
# Run persistent Node.js service
# Send parse requests via HTTP/socket
# More efficient for multiple files
```

#### Approach 3: Skip TypeScript (Fallback)
```python
def _check_typescript(self, context, config):
    # TODO: Implement TypeScript parsing
    # For now, return empty list
    return []
```

**Recommendation**: Start with Approach 3 (skip) in PR2, add full TypeScript support in future PR if needed.

---

## Testing Strategy

### Test Organization (PR1)

```
tests/unit/linters/nesting/
├── test_python_nesting.py       # 15 tests - Python depth analysis
├── test_typescript_nesting.py   # 15 tests - TypeScript depth analysis
├── test_config_loading.py       # 8 tests - Configuration
├── test_violation_messages.py   # 6 tests - Error messages
├── test_ignore_directives.py    # 8 tests - Inline ignores
├── test_cli_interface.py        # 4 tests - CLI commands
├── test_library_api.py          # 4 tests - Programmatic API
└── test_edge_cases.py           # 8 tests - Edge cases
```

Total: **68 tests**

### Test Patterns

#### Pattern 1: Code String Fixtures
```python
def test_triple_nesting():
    code = '''
def process_data(items):
    for item in items:
        if item.valid:
            for child in item.children:
                print(child)
'''
    # Parse, analyze, assert depth = 4
```

#### Pattern 2: Temporary Files
```python
def test_cli_command(tmp_path):
    file = tmp_path / "test.py"
    file.write_text(violating_code)
    runner = CliRunner()
    result = runner.invoke(cli, ['lint', 'nesting', str(file)])
    assert result.exit_code == 1
```

#### Pattern 3: Parameterized Tests
```python
@pytest.mark.parametrize('depth,should_pass', [
    (2, True),   # Well below limit
    (4, True),   # At limit
    (5, False),  # Above limit
])
def test_depth_limits(depth, should_pass):
    code = generate_nested_code(depth)
    # Assert violation if not should_pass
```

---

## Dogfooding Strategy (PR4-PR6)

### Why Dogfooding Matters

1. **Validates usefulness**: Does the linter find real issues?
2. **Improves implementation**: Find edge cases, improve messages
3. **Documents patterns**: Learn refactoring approaches
4. **Ensures quality**: Linter must meet its own standards

### Discovery Phase (PR4)

**Goal**: Catalog ALL violations without fixing

**Process**:
```bash
# Run linter on entire codebase
thai lint nesting src/ > violations.txt

# Categorize violations
# - Easy: Early returns
# - Medium: Extract method
# - Hard: Complex refactoring

# Document in VIOLATIONS.md
```

**Expected Findings**:
- 20-50 violations (based on typical codebase)
- Most in CLI/orchestrator (complex logic)
- Some in linters (nested parsing)

### Fixing Phase 1 (PR5)

**Goal**: Fix ~50% of violations (easy + medium)

**Patterns to apply**:
- Early returns for validation
- Guard clauses for preconditions
- Extract method for nested loops

**Verification**:
```bash
# After each fix
make test           # Must pass
thai lint nesting   # Should show progress
```

### Fixing Phase 2 (PR6)

**Goal**: Fix remaining violations or acknowledge with ignores

**Complex refactorings**:
- Redesign deeply nested logic
- Apply strategy pattern
- Simplify state management

**Inline ignores**:
```python
def complex_cli_parser(args):  # thailint: ignore nesting
    # Justification: CLI argument parsing inherently complex
    # due to many flag combinations. Refactoring would harm
    # clarity without reducing actual complexity.
    ...
```

**Every ignore MUST have justification comment.**

### Documentation (PR6)

**Capture learnings**:
- Which refactoring patterns worked best?
- What were the common violation causes?
- What suggestions would have been most helpful?

**Update docs**:
- Real-world examples from thai-lint
- Before/after refactoring showcases
- Pattern effectiveness metrics

---

## Performance Considerations

### AST Parsing Overhead

**Concern**: Parsing AST for every file could be slow

**Mitigation**:
1. **Lazy parsing**: Only parse when nesting rule enabled
2. **Caching**: Orchestrator can cache ASTs (future optimization)
3. **Incremental**: Only check modified files in CI/CD

**Benchmarks** (target):
- Single file: <100ms (including parse + analyze)
- 100 files: <1s
- 1000 files: <10s

### Memory Usage

**Concern**: AST can be large for big files

**Mitigation**:
1. Process files one at a time (don't load all)
2. Release AST after analyzing each file
3. Stream results (don't accumulate in memory)

---

## Future Enhancements

### 1. Cognitive Complexity Metric

Beyond simple depth, calculate cognitive complexity:
- Nested conditions: +1 per level
- Recursive calls: +1
- Goto/break/continue: +1

### 2. More Languages

- JavaScript (similar to TypeScript)
- Go (if/for/select statements)
- Java (if/for/while/try statements)
- Rust (if/for/while/match statements)

### 3. Automatic Refactoring Suggestions

AI-powered refactoring suggestions:
```
Violation: Function 'process' has depth 5

Suggested refactoring:
  1. Extract lines 45-52 to helper function '_validate_item'
  2. Apply early return pattern on line 48
  3. Combine conditions on lines 50-51
```

### 4. IDE Integration

Real-time nesting depth indicators in IDEs:
- Visual depth indicators in gutter
- Inline suggestions as you type
- Quick-fix actions for common patterns

---

## References

### Reference Implementation
`/home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/style/nesting_rules.py`

**Key learnings**:
- DEFAULT_MAX_NESTING_DEPTH = 4
- Depth starts at 1 for function body
- Visitor pattern with nonlocal max_depth tracking
- Helpful violation messages with suggestions

### Related Literature

1. **Cyclomatic Complexity** (McCabe, 1976)
   - Related metric: control flow complexity
   - Nesting depth is simpler, more intuitive

2. **Cognitive Complexity** (SonarSource)
   - Extends cyclomatic complexity
   - Accounts for nesting depth

3. **Clean Code** (Robert C. Martin)
   - "Functions should do one thing"
   - Nesting is sign of multiple responsibilities

### Industry Standards

- **Google Python Style Guide**: Recommends max depth of 4
- **PEP 8**: Doesn't specify depth, but emphasizes simplicity
- **SonarQube**: Default max depth of 4-5 depending on language

---

## Summary

The Nesting Depth Linter:
- Detects excessive code nesting in Python and TypeScript
- Uses AST-based analysis with visitor pattern
- Supports configurable limits (default: 4)
- Provides helpful violation messages with refactoring suggestions
- Integrates seamlessly with orchestrator framework
- Will be dogfooded on thai-lint itself to validate usefulness
- Documents effective refactoring patterns learned during dogfooding

**Key Design Decisions**:
1. Depth starts at 1 (not 0) for function body
2. Default limit of 4 (matches reference implementation)
3. Strategy pattern for multi-language support
4. AST-based (accurate, no regex hacks)
5. Helpful messages with actionable suggestions
6. Comprehensive dogfooding to ensure quality

**Success Criteria**:
- 68 tests passing
- Both Python and TypeScript support
- Zero violations in thai-lint codebase (after refactoring)
- Comprehensive documentation with real-world examples
