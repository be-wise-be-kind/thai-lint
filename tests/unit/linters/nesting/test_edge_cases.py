"""
Purpose: Test edge cases for nesting depth linter

Scope: Empty files, files with no functions, malformed code, and extreme nesting

Overview: Validates robust error handling and edge case behavior for the nesting depth linter
    including empty file handling (no violations), files without functions (module-level code),
    syntax error handling (graceful failure without crashes), extremely deep nesting detection
    (10+ levels), empty function bodies (pass statements only), comment-only functions, mixed
    sync and async function handling, and nested function definitions with independent depth
    tracking. Ensures linter handles unusual inputs gracefully, provides helpful error messages
    for malformed code, and correctly analyzes edge cases without false positives or crashes.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, unittest.mock for Mock objects

Exports: TestEdgeCases (8 tests) covering empty files, no functions, syntax errors, extreme
    nesting, empty bodies, comments, mixed functions, and nested definitions

Interfaces: Tests NestingDepthRule.check(context) with edge case code samples

Implementation: Uses unusual code patterns as test fixtures, verifies graceful handling and
    correct behavior for each edge case
"""

from pathlib import Path
from unittest.mock import Mock


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_file_no_violations(self):
        """Empty file should produce no violations."""
        from src.linters.nesting.linter import NestingDepthRule

        code = ""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should return empty violations list
        assert len(violations) == 0, "Empty file should have no violations"

    def test_no_functions_no_violations(self):
        """File with no functions should produce no violations."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
x = 1
y = 2
print(x + y)

class MyClass:
    pass
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Module-level code has no nesting depth to check
        assert len(violations) == 0, "File without functions should have no violations"

    def test_syntax_error_handled_gracefully(self):
        """Syntax errors should be handled gracefully."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def broken(
  x = 1
"""  # Missing closing paren
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        # Should not crash - either return error violation or empty list
        violations = rule.check(context)
        assert isinstance(violations, list), "Should return a list even for syntax errors"

    def test_extremely_deep_nesting(self):
        """Extremely deep nesting (10+ levels) should be detected."""
        from src.linters.nesting.linter import NestingDepthRule

        # Generate code with 10 nested ifs
        nested_ifs = "\n".join(["    " * (i + 1) + "if True:" for i in range(10)])
        code = f"""
def extremely_nested():
{nested_ifs}
{" " * 44}print("depth 11")
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should detect extreme nesting
        assert len(violations) > 0, "Should detect extremely deep nesting"

    def test_empty_function_body(self):
        """Empty function (only pass) should pass."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def empty():
    pass
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Depth 1, no violations
        assert len(violations) == 0, "Empty function should not violate"

    def test_comments_only_no_nesting(self):
        """Function with only comments should pass."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def documented():
    # This function does nothing
    # But it has comments
    pass
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Comments-only function should not violate"

    def test_mixed_sync_async_functions(self):
        """Mix of sync and async functions should work."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def sync_func():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print("sync violation")

async def async_func():
    print("no nesting")

async def async_violation():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    await something()
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should have violations from both sync_func and async_violation
        assert len(violations) >= 2, "Should detect violations in both sync and async functions"

    def test_nested_function_definitions(self):
        """Nested function definitions should track depth independently."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def outer():
    x = 1
    if True:
        y = 2
        def inner():
            # Inner function depth tracking starts fresh
            for i in range(5):
                for j in range(5):
                    for k in range(5):
                        for m in range(5):
                            print("inner violation")
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # inner() function has depth 5 - should violate
        # outer() has depth 2 - should not violate
        assert len(violations) >= 1, "Should detect violation in inner function"
