"""
Purpose: Unit tests for Python print statement detection

Scope: Testing Python print() call detection and configuration handling

Overview: Comprehensive test suite for Python print() statement detection covering basic detection
    of print() calls, allow_in_scripts feature for __main__ blocks, ignore directives, and
    violation details. Validates that the linter correctly identifies print statements that should
    be replaced with proper logging while respecting configuration options. Tests various print()
    formats including f-strings, multiple arguments, and different code contexts.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock, src.linters.print_statements.linter.PrintStatementRule

Exports: TestBasicDetection, TestMainBlockHandling, TestViolationDetails test classes

Interfaces: test_detects_simple_print, test_flags_print_in_regular_code, test_allows_print_in_main_block,
    and other test methods validating PrintStatementRule.check(context)

Implementation: Uses Mock objects for context creation, inline Python code strings as test fixtures,
    validates violation line numbers and messages
"""

from pathlib import Path
from unittest.mock import Mock


class TestBasicDetection:
    """Test basic print() statement detection in Python code."""

    def test_detects_simple_print(self):
        """Should flag simple print() calls."""
        code = """
x = 1
print("hello")
y = 2
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert violations[0].line == 3
        assert "print()" in violations[0].message

    def test_detects_multiple_prints(self):
        """Should flag multiple print() calls."""
        code = """
def process():
    print("start")
    do_work()
    print("middle")
    cleanup()
    print("end")
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 3

    def test_detects_print_with_arguments(self):
        """Should flag print() with various arguments."""
        code = """
print("simple string")
print(f"formatted {value}")
print(a, b, c, sep=",")
print("with", "multiple", "args")
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 4


class TestMainBlockHandling:
    """Test handling of print() in __main__ blocks."""

    def test_allows_print_in_main_block_by_default(self):
        """Should NOT flag print() in __main__ block when allow_in_scripts=True (default)."""
        code = """
def main():
    print("This should be flagged")

if __name__ == "__main__":
    print("This should NOT be flagged")
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert violations[0].line == 3  # Only the print outside __main__

    def test_flags_all_prints_when_allow_in_scripts_false(self):
        """Should flag print() in __main__ block when allow_in_scripts=False."""
        code = """
def main():
    print("flagged")

if __name__ == "__main__":
    print("also flagged")
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"
        context.config = {"allow_in_scripts": False}

        violations = rule.check(context)
        assert len(violations) == 2

    def test_handles_nested_main_block(self):
        """Should handle nested functions in __main__ block."""
        code = """
if __name__ == "__main__":
    def inner():
        print("nested in main")
    inner()
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Print is inside a function that's inside __main__, should still be allowed
        assert len(violations) == 0


class TestIgnoreDirectives:
    """Test ignore directive support."""

    def test_ignores_with_thailint_ignore(self):
        """Should respect thailint: ignore directive."""
        code = """
print("flagged")
print("ignored")  # thailint: ignore
print("also flagged")
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 2

    def test_ignores_with_noqa(self):
        """Should respect noqa directive."""
        code = """
print("flagged")
print("ignored")  # noqa
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_ignores_with_specific_rule_ignore(self):
        """Should respect thailint: ignore[print-statements] directive."""
        code = """
print("flagged")
print("ignored")  # thailint: ignore[print-statements]
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1


class TestViolationDetails:
    """Test that violations contain appropriate details."""

    def test_violation_has_correct_rule_id(self):
        """Should set correct rule_id on violations."""
        code = 'print("test")'
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert violations[0].rule_id == "improper-logging.print-statement"

    def test_violation_has_correct_line_number(self):
        """Should set correct line number on violations."""
        code = """
x = 1
y = 2
print("on line 4")
z = 3
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert violations[0].line == 4

    def test_violation_has_suggestion(self):
        """Should include helpful suggestion in violation."""
        code = 'print("test")'
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert "logging" in violations[0].suggestion.lower()


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_handles_empty_file(self):
        """Should handle empty file gracefully."""
        code = ""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("empty.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_handles_syntax_error(self):
        """Should handle files with syntax errors gracefully."""
        code = "def broken(:\n    print('test'"
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("broken.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0  # Graceful handling, no crash

    def test_ignores_print_in_string(self):
        """Should not flag 'print' mentioned in strings."""
        code = """
x = "print('hello')"
y = 'print("world")'
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_print_in_comment(self):
        """Should not flag print mentioned in comments."""
        code = """
# print("this is a comment")
x = 1  # print statement would go here
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0
