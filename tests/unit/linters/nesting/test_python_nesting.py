"""
Purpose: Test suite for Python nesting depth analysis

Scope: Python AST-based nesting depth calculation and violation detection

Overview: Comprehensive tests for Python code nesting depth analysis covering simple nesting
    patterns (single if/for/while statements), complex multi-level nesting, various Python
    statement types (if, for, while, with, try, match), accurate depth calculation algorithms,
    and violation detection at configurable limits. Verifies depth counting starts at 1 for
    function body and correctly increments for nested blocks. Tests both passing scenarios
    (depth within configured limits) and violation scenarios (depth exceeds limits). Validates
    AST-based analysis approach matches reference implementation behavior.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, src.core.types for Violation

Exports: TestSimplePythonNesting (4 tests), TestPythonStatementTypes (6 tests),
    TestPythonDepthCalculation (5 tests) - total 15 test cases

Interfaces: Tests NestingDepthRule.check(context) -> list[Violation] with Python code samples

Implementation: Uses inline Python code strings as test fixtures, creates mock contexts with
    file_path and file_content, verifies violation detection and depth calculation accuracy
"""

from pathlib import Path
from unittest.mock import Mock


class TestSimplePythonNesting:
    """Test basic Python nesting depth detection."""

    def test_no_nesting_passes(self):
        """Function with no nesting should pass."""
        code = """
def simple_function():
    x = 1
    y = 2
    return x + y
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0, "Simple function with no nesting should not violate"

    def test_single_if_within_limit(self):
        """Single if statement (depth 2) should pass with limit 4."""
        code = """
def check_value(x):
    if x > 0:
        return True
    return False
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Depth: function=1, if=2 → passes with limit 4
        assert len(violations) == 0, "Single if (depth 2) should pass with default limit 4"

    def test_triple_nesting_within_limit(self):
        """Triple nesting (depth 4) should pass with limit 4."""
        code = """
def process_data(items):
    for item in items:
        if item.valid:
            for sub in item.children:
                print(sub)
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Depth: function=1, for=2, if=3, for=4 → passes with limit 4
        assert len(violations) == 0, "Triple nesting (depth 4) should pass with limit 4"

    def test_quad_nesting_violates_default(self):
        """Quadruple nesting (depth 5) should violate default limit 4."""
        code = """
def complex_logic(data):
    for item in data:
        if item.active:
            for child in item.children:
                if child.valid:
                    print(child)
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Depth: function=1, for=2, if=3, for=4, if=5 → VIOLATION
        assert len(violations) > 0, "Quadruple nesting (depth 5) should violate limit 4"
        assert "complex_logic" in violations[0].message, "Violation should mention function name"


class TestPythonStatementTypes:
    """Test various Python statement types that increase nesting."""

    def test_for_loop_nesting(self):
        """For loops should increase nesting depth."""
        code = """
def nested_loops():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print(i, j, k, m)
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Four nested for loops = depth 5 (function=1, for=2, for=3, for=4, for=5)
        assert len(violations) > 0, "Four nested for loops should violate"

    def test_while_loop_nesting(self):
        """While loops should increase nesting depth."""
        code = """
def nested_whiles(x):
    while x > 0:
        while x > 10:
            while x > 20:
                while x > 30:
                    x -= 1
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Four nested while loops = depth 5
        assert len(violations) > 0, "Four nested while loops should violate"

    def test_with_statement_nesting(self):
        """With statements should increase nesting depth."""
        code = """
def nested_withs():
    with open('a') as a:
        with open('b') as b:
            with open('c') as c:
                with open('d') as d:
                    pass
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Four nested with statements = depth 5
        assert len(violations) > 0, "Four nested with statements should violate"

    def test_try_except_nesting(self):
        """Try/except blocks should increase nesting depth."""
        code = """
def nested_tries():
    try:
        try:
            try:
                try:
                    risky_operation()
                except:
                    pass
            except:
                pass
        except:
            pass
    except:
        pass
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Four nested try blocks = depth 5
        assert len(violations) > 0, "Four nested try blocks should violate"

    def test_match_statement_nesting(self):
        """Match statements (Python 3.10+) should increase nesting depth."""
        code = """
def nested_matches(x):
    match x:
        case 1:
            match x:
                case 2:
                    match x:
                        case 3:
                            match x:
                                case 4:
                                    pass
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Four nested match statements = depth 5+
        assert len(violations) > 0, "Four nested match statements should violate"

    def test_mixed_statement_nesting(self):
        """Mixed statement types should all contribute to depth."""
        code = """
def mixed_nesting(data):
    if data:
        for item in data:
            while item.valid:
                with open(item.file) as f:
                    try:
                        process(f)
                    except:
                        pass
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # if + for + while + with + try = depth 6
        assert len(violations) > 0, "Mixed statements with depth 6 should violate"


class TestPythonDepthCalculation:
    """Test accurate depth calculation for Python code."""

    def test_depth_starts_at_one_for_function_body(self):
        """Function body statements should start at depth 1."""
        code = """
def simple():
    x = 1
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Simple statement at depth 1 should not violate
        assert len(violations) == 0, "Depth 1 should not violate"

    def test_sibling_blocks_dont_increase_depth(self):
        """Sequential (non-nested) blocks should not increase depth."""
        code = """
def multiple_ifs(x):
    if x > 0:
        print("positive")
    if x < 0:
        print("negative")
    if x == 0:
        print("zero")
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # All three ifs are depth 2 (siblings), not cumulative
        # Max depth = 2, should not violate limit 4
        assert len(violations) == 0, "Sibling blocks should not accumulate depth"

    def test_max_depth_tracking(self):
        """Should report maximum depth found, not current depth."""
        code = """
def branching(x):
    if x > 0:
        if x > 10:
            if x > 100:
                if x > 1000:
                    print("very large")
    print("done")
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Max depth is 5 (in the nested ifs), even though final statement is depth 1
        assert len(violations) > 0, "Should report max depth of 5"

    def test_async_function_nesting(self):
        """Async functions should track nesting same as sync."""
        code = """
async def async_nested():
    for i in range(5):
        if i > 0:
            for j in range(5):
                if j > 0:
                    await something()
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Depth 5: for=2, if=3, for=4, if=5
        assert len(violations) > 0, "Async function with depth 5 should violate"

    def test_nested_function_definitions_start_fresh(self):
        """Nested function definitions should start depth counting fresh."""
        code = """
def outer():
    if condition:
        def inner():
            if other:
                if another:
                    if more:
                        if too_many:
                            pass
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # inner() function has depth 5 (if=2, if=3, if=4, if=5) - starts fresh
        # outer() has depth 2 (if=2) - no violation
        # Should have at least 1 violation from inner()
        assert len(violations) > 0, "Nested function with depth 5 should violate"
