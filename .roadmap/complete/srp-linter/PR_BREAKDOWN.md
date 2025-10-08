# SRP (Single Responsibility Principle) Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of SRP Linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from test suite creation through documentation and dogfooding

**Overview**: Comprehensive breakdown of the SRP Linter feature into 6 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: Python ast module, tree-sitter for TypeScript, core orchestrator framework, existing linter patterns (nesting, file_placement)

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with detailed step-by-step implementation guidance and comprehensive testing validation

---

## 🚀 PROGRESS TRACKER - MUST BE UPDATED AFTER EACH PR!


---

## Overview
This document breaks down the SRP Linter feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

---

## PR1: Complete Test Suite (Pure TDD)

**Scope**: Write 60-80 tests with ZERO implementation code

**Objective**: Define the SRP linter API through comprehensive tests before any implementation exists.

### Implementation Steps

#### Step 1: Create Test Directory Structure
```bash
mkdir -p tests/unit/linters/srp
touch tests/unit/linters/srp/__init__.py
```

#### Step 2: Write Python SRP Tests (test_python_srp.py)

**Test Categories (15-20 tests)**:

1. **Method Count Violations** (5 tests):
   - Class with 8+ methods violates (threshold: 7)
   - Class with exactly 7 methods passes
   - Class with 6 methods passes
   - Class with 15+ methods violates (severe)
   - Empty class passes

2. **Lines of Code Violations** (5 tests):
   - Class with 201+ LOC violates (threshold: 200)
   - Class with exactly 200 LOC passes
   - Class with 150 LOC passes
   - Class with 500+ LOC violates (severe)
   - Single-line class passes

3. **Responsibility Keyword Detection** (5 tests):
   - Class named "UserManager" violates (contains "Manager")
   - Class named "DataHandler" violates (contains "Handler")
   - Class named "RequestProcessor" violates (contains "Processor")
   - Class named "UtilityHelper" violates (contains both "Utility" and "Helper")
   - Class named "User" passes (no keywords)

4. **Combined Violations** (5 tests):
   - Class with 8 methods AND 201 LOC violates both
   - Class with "Manager" name AND 8 methods violates both
   - Class with all three violations (severe)
   - Nested class definitions work correctly
   - Multiple classes in one file detected independently

**Example Test**:
```python
def test_method_count_violation():
    \"\"\"Class with more than 7 methods should violate.\"\"\"
    code = '''
class UserManager:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass  # Violation at method 8
'''
    rule = SRPRule()
    context = create_context(code, "python")
    violations = rule.check(context)
    assert len(violations) > 0
    assert "8 methods" in violations[0].message
```

#### Step 3: Write TypeScript SRP Tests (test_typescript_srp.py)

**Same test structure as Python** (15-20 tests), covering:
- Method count in classes
- Lines of code in classes
- Responsibility keywords
- Interface method count
- Constructor parameter count

#### Step 4: Write Config Loading Tests (test_config_loading.py)

**Test Categories** (8-10 tests):
1. Default thresholds (max_methods=7, max_loc=200)
2. Custom threshold from config file
3. Per-file threshold via metadata
4. Invalid threshold values handled gracefully
5. Missing config uses defaults

#### Step 5: Write Violation Message Tests (test_violation_messages.py)

**Test Categories** (6-8 tests):
1. Violation includes class name
2. Violation includes metric values (e.g., "8 methods")
3. Violation includes helpful suggestion
4. Multiple violations reported separately
5. Message format is consistent

#### Step 6: Write Ignore Directive Tests (test_ignore_directives.py)

**Test Categories** (8-10 tests):
1. `# thailint: ignore srp` on class definition
2. `// thailint: ignore srp` in TypeScript
3. Block ignore (ignore-start/ignore-end)
4. Ignore specific rule: `srp.too-many-methods`
5. Ignore doesn't affect other violations

#### Step 7: Write CLI Interface Tests (test_cli_interface.py)

**Test Categories** (4-6 tests):
1. `thai-lint srp <path>` command exists
2. `--max-methods` flag works
3. `--max-loc` flag works
4. Output format options work
5. Exit codes correct (0 = pass, 1 = violations)

#### Step 8: Write Library API Tests (test_library_api.py)

**Test Categories** (4-6 tests):
1. `from src import srp_lint` works
2. `linter.lint(path, rules=['srp'])` works
3. Direct `SRPRule()` instantiation works
4. Programmatic result parsing works

#### Step 9: Write Edge Case Tests (test_edge_cases.py)

**Test Categories** (8-10 tests):
1. Empty file passes
2. File with only functions (no classes) passes
3. File with only imports passes
4. Syntax error handled gracefully
5. Abstract classes handled correctly
6. Dataclasses with many fields (don't count as methods)
7. Property decorators don't count as methods
8. Inherited methods don't count

#### Step 10: Verify All Tests Fail

```bash
pytest tests/unit/linters/srp/ -v
```

**Expected**: All tests fail with ModuleNotFoundError (no src/linters/srp/ exists yet)

### Success Criteria
- [ ] 60-80 tests written across 8 test files
- [ ] All tests fail (no implementation exists)
- [ ] Tests are well-documented with clear expectations
- [ ] Test names are descriptive (test_method_count_violation_at_threshold)
- [ ] Both Python and TypeScript covered equally

### Files Created
```
tests/unit/linters/srp/
├── __init__.py
├── test_python_srp.py (15-20 tests)
├── test_typescript_srp.py (15-20 tests)
├── test_config_loading.py (8-10 tests)
├── test_violation_messages.py (6-8 tests)
├── test_ignore_directives.py (8-10 tests)
├── test_cli_interface.py (4-6 tests)
├── test_library_api.py (4-6 tests)
└── test_edge_cases.py (8-10 tests)
```

---

## PR2: Core Implementation (Python + TypeScript)

**Scope**: Implement SRP analyzers to pass ~80% of PR1 tests

**Objective**: Build the core SRP detection logic using heuristic-based analysis.

### Implementation Steps

#### Step 1: Create Module Structure
```bash
mkdir -p src/linters/srp
touch src/linters/srp/__init__.py
```

#### Step 2: Implement SRPConfig (src/linters/srp/config.py)

```python
from dataclasses import dataclass

@dataclass
class SRPConfig:
    enabled: bool = True
    max_methods: int = 7
    max_loc: int = 200
    check_keywords: bool = True
    keywords: list[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = ["Manager", "Handler", "Processor", "Utility", "Helper"]

    @classmethod
    def from_dict(cls, config: dict) -> "SRPConfig":
        return cls(
            enabled=config.get("enabled", True),
            max_methods=config.get("max_methods", 7),
            max_loc=config.get("max_loc", 200),
            check_keywords=config.get("check_keywords", True),
            keywords=config.get("keywords"),
        )
```

#### Step 3: Implement Heuristics (src/linters/srp/heuristics.py)

```python
import ast
from typing import Any

def count_methods(class_node: ast.ClassDef) -> int:
    \"\"\"Count methods in a class (excludes properties).\"\"\"
    methods = 0
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Don't count @property decorators as methods
            if not has_property_decorator(node):
                methods += 1
    return methods

def count_loc(class_node: ast.ClassDef, source: str) -> int:
    \"\"\"Count lines of code in a class.\"\"\"
    start_line = class_node.lineno
    end_line = class_node.end_lineno or start_line
    lines = source.split('\\n')[start_line-1:end_line]
    # Filter out blank lines and comments
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    return len(code_lines)

def has_responsibility_keyword(class_name: str, keywords: list[str]) -> bool:
    \"\"\"Check if class name contains responsibility keywords.\"\"\"
    return any(keyword in class_name for keyword in keywords)

def has_property_decorator(func_node: ast.FunctionDef) -> bool:
    \"\"\"Check if function has @property decorator.\"\"\"
    for decorator in func_node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == 'property':
            return True
    return False
```

#### Step 4: Implement Python Analyzer (src/linters/srp/python_analyzer.py)

```python
import ast
from typing import Any

class PythonSRPAnalyzer:
    \"\"\"Analyzes Python classes for SRP violations.\"\"\"

    def find_all_classes(self, tree: ast.AST) -> list[ast.ClassDef]:
        \"\"\"Find all class definitions in AST.\"\"\"
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node)
        return classes

    def analyze_class(self, class_node: ast.ClassDef, source: str, config: 'SRPConfig') -> dict[str, Any]:
        \"\"\"Analyze a class for SRP metrics.\"\"\"
        from .heuristics import count_methods, count_loc, has_responsibility_keyword

        method_count = count_methods(class_node)
        loc = count_loc(class_node, source)
        has_keyword = has_responsibility_keyword(class_node.name, config.keywords)

        return {
            "class_name": class_node.name,
            "method_count": method_count,
            "loc": loc,
            "has_keyword": has_keyword,
            "line": class_node.lineno,
            "column": class_node.col_offset,
        }
```

#### Step 5: Implement TypeScript Analyzer (src/linters/srp/typescript_analyzer.py)

Similar structure to Python analyzer, using tree-sitter for parsing.

#### Step 6: Implement Main Rule (src/linters/srp/linter.py)

```python
from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation, Severity
from .config import SRPConfig
from .python_analyzer import PythonSRPAnalyzer
from .typescript_analyzer import TypeScriptSRPAnalyzer

class SRPRule(BaseLintRule):
    \"\"\"Detects Single Responsibility Principle violations.\"\"\"

    @property
    def rule_id(self) -> str:
        return "srp.violation"

    @property
    def rule_name(self) -> str:
        return "Single Responsibility Principle"

    @property
    def description(self) -> str:
        return "Classes should have a single, well-defined responsibility"

    def check(self, context: BaseLintContext) -> list[Violation]:
        config = self._load_config(context)
        if not config.enabled:
            return []

        if context.language == "python":
            return self._check_python(context, config)
        elif context.language in ("typescript", "javascript"):
            return self._check_typescript(context, config)
        return []

    def _check_python(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        tree = ast.parse(context.file_content or "")
        analyzer = PythonSRPAnalyzer()
        classes = analyzer.find_all_classes(tree)

        violations = []
        for class_node in classes:
            metrics = analyzer.analyze_class(class_node, context.file_content, config)
            violation = self._create_violation_if_needed(metrics, config, context)
            if violation:
                violations.append(violation)
        return violations

    def _create_violation_if_needed(self, metrics: dict, config: SRPConfig, context: BaseLintContext) -> Violation | None:
        issues = []

        if metrics["method_count"] > config.max_methods:
            issues.append(f"{metrics['method_count']} methods (max: {config.max_methods})")

        if metrics["loc"] > config.max_loc:
            issues.append(f"{metrics['loc']} lines (max: {config.max_loc})")

        if config.check_keywords and metrics["has_keyword"]:
            issues.append("responsibility keyword in name")

        if not issues:
            return None

        message = f"Class '{metrics['class_name']}' may violate SRP: {', '.join(issues)}"
        suggestion = self._generate_suggestion(issues)

        return Violation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=metrics["line"],
            column=metrics["column"],
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def _generate_suggestion(self, issues: list[str]) -> str:
        suggestions = []
        if any("methods" in i for i in issues):
            suggestions.append("Consider extracting related methods into separate classes")
        if any("lines" in i for i in issues):
            suggestions.append("Consider breaking the class into smaller, focused classes")
        if any("keyword" in i for i in issues):
            suggestions.append("Avoid generic names like Manager, Handler, Processor")
        return ". ".join(suggestions)
```

### Success Criteria
- [ ] ~80% of tests passing (48-64 of 60-80)
- [ ] Python SRP detection accurate
- [ ] TypeScript SRP detection accurate
- [ ] Configurable thresholds working
- [ ] make lint-full exits code 0

### Files Created
```
src/linters/srp/
├── __init__.py
├── linter.py (SRPRule)
├── python_analyzer.py
├── typescript_analyzer.py
├── config.py
└── heuristics.py
```

---

## PR3: Integration (CLI + Library + Docker)

**Scope**: Integrate SRP linter with all deployment modes

**Objective**: Make SRP linter accessible via CLI, Library API, and Docker.

### Implementation Steps

#### Step 1: Add CLI Command (src/cli.py)

```python
@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--max-methods", type=int, help="Maximum methods per class (default: 7)")
@click.option("--max-loc", type=int, help="Maximum lines of code per class (default: 200)")
@click.option("--config", type=click.Path(), help="Configuration file path")
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def srp(path: str, max_methods: int | None, max_loc: int | None, config: str | None, format: str):
    \"\"\"Check for Single Responsibility Principle violations.\"\"\"
    # Implementation here
```

#### Step 2: Add Library API (src/linters/srp/__init__.py)

```python
from .linter import SRPRule

def lint(path: str, config: dict | None = None) -> list[dict]:
    \"\"\"Convenience function for SRP linting.\"\"\"
    # Implementation
```

#### Step 3: Export in src/__init__.py

```python
from src.linters.srp import lint as srp_lint
from src.linters.srp import SRPRule

__all__ = [..., "srp_lint", "SRPRule"]
```

#### Step 4: Write Integration Tests

Test all three deployment modes work end-to-end.

### Success Criteria
- [ ] 100% tests passing
- [ ] CLI command works
- [ ] Library API works
- [ ] Docker deployment works
- [ ] make lint-full exits code 0

---

## PR4: Dogfooding Discovery

**Scope**: Find SRP violations in thai-lint codebase

**Objective**: Run the SRP linter on itself to find real-world violations.

### Implementation Steps

1. Update `.thailint.yaml` with SRP config
2. Create `make lint-srp` target
3. Run linter and catalog all violations
4. Categorize by difficulty
5. Plan refactoring approach

### Success Criteria
- [ ] All violations cataloged in VIOLATIONS.md
- [ ] Refactoring plan created
- [ ] make test exits code 0
- [ ] make lint-srp finds violations (expected)

---

## PR5: Dogfooding Fixes (All Violations)

**Scope**: Refactor code to eliminate all SRP violations

**Objective**: Demonstrate SRP principles by fixing all violations found in PR4.

### Refactoring Patterns
1. Extract Class
2. Split Responsibilities
3. Create Focused Utilities
4. Apply Composition

### Success Criteria
- [ ] **make lint-srp exits code 0 (ZERO violations) ← CRITICAL**
- [ ] make test exits code 0 (no broken functionality)
- [ ] make lint-full exits code 0

---

## PR6: Documentation

**Scope**: Complete documentation for production release

### Files to Create/Modify
- docs/srp-linter.md
- README.md (add SRP section)
- CHANGELOG.md (v0.3.0)
- examples/srp-config-example.yaml

### Success Criteria
- [ ] Comprehensive documentation complete
- [ ] Configuration examples provided
- [ ] Refactoring patterns documented
- [ ] All PR5 quality gates maintained

---

## Implementation Guidelines

### Code Standards
- Follow PEP 8 (enforced by Ruff)
- Type hints required (checked by MyPy)
- Docstrings for all public functions (Google-style)
- Maximum cyclomatic complexity: A-grade (enforced by Xenon)
- Pylint score: 10.00/10

### Testing Requirements
- Minimum 85% coverage on SRP modules
- All tests must pass before PR merge
- Test both passing and violation cases
- Use pytest fixtures for reusable components

### Documentation Standards
- All files require comprehensive headers per FILE_HEADER_STANDARDS.md
- Use atemporal language (no "currently", "now", dates)
- Include Purpose, Scope, Overview, Dependencies, Exports, Implementation

### Performance Targets
- <100ms per file for SRP analysis
- Handle files up to 10,000 LOC
- Support analyzing 1000+ files in single run

## Success Metrics

### Launch Metrics
- All 6 PRs completed
- 100% tests passing
- Zero SRP violations in codebase
- Documentation complete

### Ongoing Metrics
- SRP linter used in CI/CD
- Zero new SRP violations introduced
- Community adoption and feedback
