# SRP (Single Responsibility Principle) Linter - AI Context

**Purpose**: AI agent context document for implementing SRP Linter

**Scope**: Heuristic-based detection of Single Responsibility Principle violations in Python and TypeScript classes

**Overview**: Comprehensive context document for AI agents working on the SRP Linter feature.
    Provides architectural overview, design decisions, detection heuristics, integration patterns,
    and implementation guidance. Explains why heuristic-based detection is practical for SRP
    (which is inherently subjective), how to balance false positives vs false negatives, and
    patterns for effective class-level static analysis across multiple languages.

**Dependencies**: Python ast module, tree-sitter, core orchestrator framework, nesting linter pattern

**Exports**: Architectural context, detection strategies, heuristic definitions, integration guidance

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Heuristic-based SRP detection using method count, LOC, naming patterns, and coupling metrics

---

## Overview

The SRP (Single Responsibility Principle) Linter detects classes that violate the Single Responsibility Principle - one of the five SOLID principles of object-oriented design. Unlike syntax errors or nesting depth (which are objective), SRP violations are inherently subjective and context-dependent. This linter uses practical heuristics to flag likely violations while minimizing false positives.

## Project Background

thai-lint is a multi-language linter focused on AI-generated code quality. The SRP linter is the third production linter (after file_placement and nesting), continuing the pattern of TDD-first development with comprehensive dogfooding.

### Why SRP Detection Matters for AI Code

AI code assistants often generate code that:
- Accumulates responsibilities in "Manager" or "Handler" classes
- Creates god classes with 10+ methods
- Mixes multiple concerns in a single class
- Uses overly generic naming ("Utility", "Helper")

These patterns indicate potential SRP violations that human developers would refactor but AI may not recognize as problematic.

## Feature Vision

### Goals
1. **Practical Detection**: Use heuristics that catch 80% of obvious violations with <10% false positives
2. **Actionable Feedback**: Provide refactoring suggestions (Extract Class, Split Responsibilities)
3. **Configurable Thresholds**: Allow teams to adjust for their coding standards
4. **Multi-Language**: Support both Python and TypeScript with consistent heuristics
5. **CI/CD Integration**: Fast enough for pre-commit hooks (<100ms per file)

### Non-Goals
1. **Perfect SRP Detection**: SRP is subjective - we provide guidance, not absolute truth
2. **Semantic Analysis**: No dependency injection analysis, no interface conformance checking
3. **Refactoring Automation**: We suggest, not auto-fix (too complex)
4. **Runtime Analysis**: Static analysis only, no profiling or metrics

## Current Application Context

### Existing Linter Framework
- **BaseLintRule Interface**: All linters implement check(context) → list[Violation]
- **Orchestrator**: Auto-discovers rules, handles language detection, manages configuration
- **Configuration**: .thailint.yaml with per-rule settings
- **Ignore Directives**: `# thailint: ignore srp` inline comments

### Existing Patterns to Follow
1. **Nesting Linter**: Most similar - class/function level analysis with thresholds
2. **File Placement Linter**: Configuration loading pattern
3. **TDD Approach**: Test suite first (PR1), then implementation (PR2)

## Target Architecture

### Core Components

#### 1. SRPRule (src/linters/srp/linter.py)
Main rule class implementing BaseLintRule interface.

**Responsibilities**:
- Load configuration from context metadata
- Route to Python or TypeScript analyzer based on language
- Aggregate violations from class-level analysis
- Apply ignore directives

#### 2. PythonSRPAnalyzer (src/linters/srp/python_analyzer.py)
Python AST-based class analyzer.

**Responsibilities**:
- Find all ClassDef nodes in AST
- Extract class metrics (method count, LOC, name)
- Return structured metrics for violation detection

#### 3. TypeScriptSRPAnalyzer (src/linters/srp/typescript_analyzer.py)
TypeScript tree-sitter based class analyzer.

**Responsibilities**:
- Find all class_declaration nodes
- Extract same metrics as Python analyzer
- Handle TypeScript-specific patterns (interfaces, constructors)

#### 4. Heuristics Module (src/linters/srp/heuristics.py)
Reusable detection logic.

**Functions**:
- `count_methods(class_node) -> int`: Count non-property methods
- `count_loc(class_node, source) -> int`: Count logical lines of code
- `has_responsibility_keyword(class_name, keywords) -> bool`: Check naming patterns
- `has_property_decorator(func_node) -> bool`: Filter out properties

#### 5. SRPConfig (src/linters/srp/config.py)
Configuration dataclass.

**Fields**:
- `enabled: bool = True`: Enable/disable linter
- `max_methods: int = 7`: Method count threshold
- `max_loc: int = 200`: Lines of code threshold
- `check_keywords: bool = True`: Enable keyword detection
- `keywords: list[str]`: Responsibility keywords (default: Manager, Handler, Processor, Utility, Helper)

### Detection Heuristics

#### Heuristic 1: Method Count
**Rationale**: Classes with 8+ methods likely have multiple responsibilities.

**Thresholds**:
- 1-7 methods: ✅ Pass
- 8-12 methods: ⚠️ Warning - likely violation
- 13+ methods: 🚨 Severe violation

**Edge Cases**:
- Don't count `@property` decorators
- Don't count inherited methods (only defined in this class)
- Don't count `__init__` separately (it's a method)
- Abstract base classes with many abstract methods may be acceptable (future enhancement)

#### Heuristic 2: Lines of Code
**Rationale**: Large classes (200+ LOC) often mix multiple concerns.

**Thresholds**:
- 1-200 LOC: ✅ Pass
- 201-400 LOC: ⚠️ Warning - likely violation
- 401+ LOC: 🚨 Severe violation

**LOC Counting Rules**:
- Exclude blank lines
- Exclude comment-only lines
- Include class definition line
- Include all method code

#### Heuristic 3: Responsibility Keywords
**Rationale**: Names like "Manager", "Handler", "Processor" often indicate god classes.

**Default Keywords**:
- Manager
- Handler
- Processor
- Utility
- Helper
- Facade (debatable - sometimes legitimate)
- Service (debatable - microservices use this)

**Detection**:
- Case-sensitive substring match
- "UserManager" violates (contains "Manager")
- "User" passes (no keywords)
- "ManagerInterface" violates (contains "Manager")

**Customization**:
Teams can override keywords list via config to match their conventions.

#### Heuristic 4: Combined Violations
**Scoring**:
- 1 heuristic violated: Possible issue (report it)
- 2 heuristics violated: Likely violation (strong suggestion)
- 3 heuristics violated: Severe violation (definite problem)

**Example**:
```python
class UserAccountDataManager:  # Keyword violation ("Manager")
    # 12 methods (method count violation)
    # 350 lines of code (LOC violation)
    # → All 3 heuristics = SEVERE VIOLATION
```

### User Journey

#### Developer Workflow
1. Write code (or AI generates code)
2. Run `thai-lint srp .` or `just lint-srp`
3. See violations with specific metrics:
   ```
   src/services/user_manager.py:15:0
   Class 'UserManager' may violate SRP: 8 methods (max: 7), 245 lines (max: 200), responsibility keyword in name
   Suggestion: Consider extracting related methods into separate classes. Avoid generic names like Manager, Handler, Processor.
   ```
4. Refactor class:
   - Extract UserValidator class (validation methods)
   - Extract UserRepository class (database methods)
   - Rename to UserService (more specific)
5. Re-run linter: Zero violations ✅

#### CI/CD Integration
```yaml
# .github/workflows/quality.yml
- name: Run SRP Linter
  run: just lint-srp
  # Fails build if violations found
```

## Key Decisions Made

### Decision 1: Heuristic-Based vs Semantic Analysis

**Choice**: Heuristic-based (method count, LOC, keywords)

**Rationale**:
- SRP is inherently subjective - no "correct" answer exists
- Semantic analysis (data flow, coupling graphs) is expensive and complex
- Heuristics catch 80% of obvious violations with simple implementation
- Fast enough for pre-commit hooks (<100ms per file)

**Trade-offs**:
- False positives: Some legitimate classes will be flagged (acceptable - user can ignore)
- False negatives: Some subtle violations will be missed (acceptable - focus on obvious cases)

### Decision 2: Class-Level Analysis Only

**Choice**: Analyze classes, not modules or functions

**Rationale**:
- SRP primarily applies to classes (cohesive unit of data + behavior)
- Module-level SRP is too coarse (entire file)
- Function-level SRP overlaps with nesting linter (complexity)
- Classes are the right granularity for responsibility analysis

**Not Covered**:
- Module organization (too subjective)
- Function complexity (nesting linter handles this)
- Package structure (file_placement linter handles this)

### Decision 3: Configurable Thresholds

**Choice**: Default thresholds with full customization

**Rationale**:
- Different teams have different standards
- Domain complexity varies (business logic vs CRUD)
- Defaults based on industry best practices (7 methods from "Clean Code")
- Easy per-project override via .thailint.yaml

**Defaults**:
- max_methods: 7 (from Robert Martin's "Clean Code")
- max_loc: 200 (from "Code Complete" recommendations)
- keywords: ["Manager", "Handler", "Processor", "Utility", "Helper"]

### Decision 4: No Auto-Fix

**Choice**: Detection only, no automated refactoring

**Rationale**:
- Refactoring is context-dependent and complex
- Extracting classes requires understanding relationships
- Naming new classes requires domain knowledge
- Suggestion is better than incorrect automation

**Suggestions Provided**:
- Extract Class pattern
- Split Responsibilities pattern
- Composition over Inheritance
- Naming guidance (avoid "Manager", use specific domain names)

## Integration Points

### With Existing Features

#### Orchestrator Integration
```python
# Auto-discovery pattern (same as nesting/file_placement)
class SRPRule(BaseLintRule):
    @property
    def rule_id(self) -> str:
        return "srp.violation"

    def check(self, context: BaseLintContext) -> list[Violation]:
        # Implementation
```

Orchestrator finds SRPRule automatically via:
1. Directory scanning (src/linters/srp/)
2. Class introspection (subclass of BaseLintRule)
3. Rule registration (rule_id property)

#### Configuration System
```yaml
# .thailint.yaml
srp:
  enabled: true
  max_methods: 7
  max_loc: 200
  check_keywords: true
  keywords:
    - Manager
    - Handler
    - Processor
```

Loaded via:
```python
def _load_config(self, context: BaseLintContext) -> SRPConfig:
    metadata = getattr(context, "metadata", None)
    config_dict = metadata.get("srp", {})
    return SRPConfig.from_dict(config_dict)
```

#### Ignore Directives
```python
# Python
class UserManager:  # thailint: ignore srp
    # Large class allowed

# TypeScript
class DataProcessor {  // thailint: ignore srp
    // Many methods allowed
}
```

Handled by IgnoreDirectiveParser (shared with nesting linter).

### With CLI
```python
@cli.command()
@click.argument("path")
@click.option("--max-methods", type=int)
@click.option("--max-loc", type=int)
def srp(path: str, max_methods: int | None, max_loc: int | None):
    # CLI implementation
```

### With Library API
```python
# Direct import
from src import srp_lint
violations = srp_lint("/path/to/code")

# Orchestrator integration
from src import Linter
linter = Linter()
results = linter.lint("/path/to/code", rules=["srp"])

# Direct rule usage
from src.linters.srp import SRPRule
rule = SRPRule()
violations = rule.check(context)
```

## Success Metrics

### Technical Metrics
- Test coverage >85% on SRP modules
- <100ms per file analysis time
- 60-80 tests all passing
- Both Python and TypeScript working
- Zero Pylint/Xenon violations in SRP code

### Feature Metrics
- Catches god classes (8+ methods)
- Catches large classes (200+ LOC)
- Catches keyword violations ("Manager", "Handler")
- Provides actionable refactoring suggestions
- Integrated into just lint-full

### Quality Metrics
- thai-lint codebase has zero SRP violations
- Dogfooding reveals real-world issues
- Refactoring improves codebase maintainability

## Technical Constraints

### Performance
- Must complete in <100ms per file (pre-commit hook requirement)
- AST parsing is fast (Python ast module, tree-sitter)
- Simple heuristics are fast (linear time)
- No network calls or external tools

### Compatibility
- Python 3.11+ (using modern type hints)
- TypeScript via tree-sitter (no Node.js required)
- Works on Linux, macOS, Windows
- Docker support for CI/CD

### Accuracy
- Target: 80% true positive rate (real violations)
- Acceptable: <10% false positive rate (incorrect flags)
- Balance: Prefer false positives over false negatives (developer can ignore)

## AI Agent Guidance

### When Writing Tests (PR1)
1. Read existing test patterns from nesting linter
2. Create tests that define the API (no implementation)
3. Include both passing and violation cases
4. Test edge cases (empty classes, properties, abstract classes)
5. Verify all tests FAIL before implementing (TDD validation)

### When Implementing (PR2)
1. Follow nesting linter structure closely
2. Use ast.walk() for finding classes in Python
3. Use tree-sitter for TypeScript classes
4. Keep heuristics simple and fast
5. Provide helpful violation messages with suggestions
6. Ensure just lint-full passes (Pylint 10.00/10, Xenon A-grade)

### When Integrating (PR3)
1. Follow CLI pattern from nesting linter
2. Export via src/__init__.py like other linters
3. Write integration tests for all deployment modes
4. Verify auto-discovery works

### When Dogfooding (PR4-PR5)
1. Run linter on thai-lint codebase
2. Expect violations (codebase not yet SRP-compliant)
3. Categorize violations by refactoring difficulty
4. Apply Extract Class, Split Responsibilities patterns
5. Verify zero violations after refactoring
6. Confirm no functionality broken (all tests pass)

### Common Patterns

#### Pattern 1: Extract Class Refactoring
**Before**:
```python
class UserManager:  # 12 methods, 300 LOC
    def validate_email(self): ...
    def validate_password(self): ...
    def save_to_db(self): ...
    def load_from_db(self): ...
    def send_welcome_email(self): ...
    # ... 7 more methods
```

**After**:
```python
class UserValidator:  # 3 methods, 80 LOC
    def validate_email(self): ...
    def validate_password(self): ...
    def validate_all(self): ...

class UserRepository:  # 3 methods, 90 LOC
    def save(self, user): ...
    def load(self, user_id): ...
    def delete(self, user_id): ...

class UserNotifier:  # 2 methods, 50 LOC
    def send_welcome_email(self, user): ...
    def send_password_reset(self, user): ...

class UserService:  # 4 methods, 80 LOC (orchestrates)
    def __init__(self):
        self.validator = UserValidator()
        self.repository = UserRepository()
        self.notifier = UserNotifier()

    def create_user(self, email, password):
        self.validator.validate_all(email, password)
        user = self.repository.save(email, password)
        self.notifier.send_welcome_email(user)
        return user
```

**Result**: Zero SRP violations, improved testability, clearer responsibilities

#### Pattern 2: Avoiding Keyword Names
**Before**:
```python
class DataHandler:  # Keyword violation
    pass
```

**After**:
```python
class OrderProcessor:  # Domain-specific name
    pass
```

## Risk Mitigation

### Risk: High False Positive Rate
**Mitigation**:
- Configurable thresholds per project
- Ignore directives for legitimate cases
- Clear violation messages explaining why

### Risk: Performance Issues
**Mitigation**:
- Simple heuristics (no graph analysis)
- AST parsing is fast
- Target <100ms per file

### Risk: Subjectivity Complaints
**Mitigation**:
- Document that SRP is inherently subjective
- Provide rationale in violation messages
- Allow disabling via config

## Future Enhancements

### Post-MVP Features
1. **Cohesion Metrics**: Analyze method field usage (LCOM metric)
2. **Coupling Detection**: Count imports and dependencies
3. **Interface Segregation**: Detect interface bloat
4. **Severity Levels**: Warning vs Error based on violation count
5. **Historical Tracking**: Show SRP trends over time

### Integration Opportunities
1. **IDE Plugins**: Real-time SRP feedback in VSCode
2. **GitHub Integration**: Comment on PRs with SRP violations
3. **Dashboards**: Visualize SRP compliance across projects

---

**Remember**: SRP detection is about providing guidance, not absolute truth. The goal is to help developers recognize potential design issues and consider refactoring options, not to enforce rigid rules.
