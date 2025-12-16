"""
Purpose: Unit tests for method-should-be-property ignore directive support

Scope: Testing inline ignore directives for suppressing specific violations

Overview: Comprehensive test suite for ignore directive support in method-should-be-property
    detection. Validates that the linter respects inline comments for suppressing violations
    including thailint-specific directives (thailint: ignore, thailint: ignore[method-property])
    and standard noqa directives. Tests various directive formats and placements to ensure
    proper suppression behavior.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock,
    src.linters.method_property.linter.MethodPropertyRule

Exports: TestInlineIgnore, TestIgnoreDirectiveFormats test classes

Interfaces: test methods validating ignore directive parsing and violation suppression

Implementation: Uses Mock objects for context creation, inline Python code with various
    ignore directive formats, validates correct suppression of flagged methods
"""

from pathlib import Path
from unittest.mock import Mock


class TestInlineIgnore:
    """Test inline ignore directives."""

    def test_respects_thailint_ignore_specific(self):
        """Should respect thailint: ignore[method-property] directive."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  # thailint: ignore[method-property]
        return self._name

    def get_email(self):
        return self._email
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # get_name should be ignored, get_email should be flagged
        assert len(violations) == 1
        assert "get_email" in violations[0].message

    def test_respects_thailint_ignore_generic(self):
        """Should respect generic thailint: ignore directive."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  # thailint: ignore
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_respects_noqa(self):
        """Should respect noqa directive."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  # noqa
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_multiple_ignores_in_file(self):
        """Should handle multiple ignore directives in same file."""
        code = """
class Data:
    def __init__(self):
        self._a = 1
        self._b = 2
        self._c = 3

    def get_a(self):  # thailint: ignore
        return self._a

    def get_b(self):  # noqa
        return self._b

    def get_c(self):
        return self._c
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("data.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Only get_c should be flagged
        assert len(violations) == 1
        assert "get_c" in violations[0].message


class TestIgnoreDirectiveFormats:
    """Test various ignore directive formats."""

    def test_ignore_with_extra_spaces(self):
        """Should handle ignore directive with extra spaces."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  #   thailint:   ignore
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignore_with_reason(self):
        """Should handle ignore directive with reason comment."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  # thailint: ignore - legacy API compatibility
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignore_case_insensitive(self):
        """Should handle ignore directive case insensitively."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  # THAILINT: IGNORE
        return self._name

    def get_email(self):  # Thailint: Ignore
        return self._email
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignore_on_method_line_only(self):
        """Should only ignore when directive is on method definition line."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    # thailint: ignore
    def get_name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Comment on previous line should NOT suppress
        # (depends on implementation decision - could go either way)
        # For now, assume inline only
        assert len(violations) == 1

    def test_noqa_with_specific_code(self):
        """Should handle noqa with specific code (if supported)."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  # noqa: method-property
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestMethodLevelIgnore:
    """Test method-level ignore patterns from docstrings."""

    def test_ignores_with_docstring_directive(self):
        """Should respect ignore directive in docstring."""
        code = '''
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        """Get user name.

        thailint: ignore[method-property]
        """
        return self._name
'''
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Docstring directive should suppress
        assert len(violations) == 0
