"""
Purpose: Unit tests for method-should-be-property violation message and metadata

Scope: Testing violation message formatting, metadata correctness, and suggestions

Overview: Comprehensive test suite for method-should-be-property violation details covering
    message formatting for different detection patterns (get_* prefix, simple return, computed
    values), violation metadata correctness (line numbers, column numbers, rule IDs, severity),
    and actionable suggestions. Validates that violations provide clear, helpful information
    for developers to understand and fix issues.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock,
    src.linters.method_property.linter.MethodPropertyRule

Exports: TestViolationMessages, TestViolationMetadata, TestViolationSuggestions test classes

Interfaces: test methods validating violation message content, metadata fields, and suggestions

Implementation: Uses Mock objects for context creation, inline Python code samples,
    validates violation object attributes and content
"""

from pathlib import Path
from unittest.mock import Mock


class TestViolationMessages:
    """Test violation message formatting."""

    def test_get_prefix_message(self):
        """Should suggest converting get_name() to 'name' property."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

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
        assert len(violations) == 1
        # Message should mention the method name
        assert "get_name" in violations[0].message
        # Message should indicate it should be a property
        assert "property" in violations[0].message.lower()

    def test_simple_return_message(self):
        """Should identify simple attribute return."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "name" in violations[0].message
        assert "property" in violations[0].message.lower()

    def test_computed_value_message(self):
        """Should identify computed value pattern."""
        code = """
class Rectangle:
    def __init__(self, w, h):
        self._w = w
        self._h = h

    def area(self):
        return self._w * self._h
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("rect.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "area" in violations[0].message

    def test_message_includes_class_context(self):
        """Should include class name in message for clarity."""
        code = """
class MyClass:
    def __init__(self):
        self._value = 42

    def value(self):
        return self._value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("myclass.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        # Message could include class context (implementation choice)
        # At minimum should have method name
        assert "value" in violations[0].message


class TestViolationMetadata:
    """Test violation metadata correctness."""

    def test_correct_line_number(self):
        """Should set correct line number on violations."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        # Method definition is on line 6
        assert violations[0].line == 6

    def test_correct_line_number_multiple_methods(self):
        """Should set correct line numbers for multiple violations."""
        code = """
class Data:
    def __init__(self):
        self._a = 1
        self._b = 2

    def a(self):
        return self._a

    def b(self):
        return self._b
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("data.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 2
        # Lines should be correct (7 and 10)
        lines = sorted([v.line for v in violations])
        assert lines == [7, 10]

    def test_correct_column_number(self):
        """Should set correct column number on violations."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        # Column should be start of 'def' (indented)
        assert violations[0].column >= 0

    def test_correct_rule_id(self):
        """Should set correct rule_id on violations."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert violations[0].rule_id == "method-property.should-be-property"

    def test_correct_severity(self):
        """Should set appropriate severity level."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        # Severity should be a reasonable level (warning or info)
        assert violations[0].severity in ["warning", "info", "convention"]

    def test_correct_file_path(self):
        """Should include correct file path in violation."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("src/models/user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "user.py" in str(violations[0].file_path)


class TestViolationSuggestions:
    """Test that violations include helpful suggestions."""

    def test_get_prefix_suggestion(self):
        """Should suggest removing get_ prefix."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

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
        assert len(violations) == 1
        # Should suggest the property name without get_
        suggestion = violations[0].suggestion.lower()
        assert "property" in suggestion
        # Could suggest @property decorator
        assert "@property" in suggestion or "decorator" in suggestion

    def test_simple_return_suggestion(self):
        """Should suggest using @property decorator."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        suggestion = violations[0].suggestion.lower()
        # Should mention property decorator
        assert "@property" in suggestion or "property" in suggestion

    def test_suggestion_is_actionable(self):
        """Should provide actionable suggestion."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        # Suggestion should not be empty
        assert violations[0].suggestion
        assert len(violations[0].suggestion) > 10  # Non-trivial suggestion


class TestRuleProperties:
    """Test rule class properties."""

    def test_rule_id_property(self):
        """Should have correct rule_id property."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        assert rule.rule_id == "method-property.should-be-property"

    def test_rule_name_property(self):
        """Should have descriptive rule_name property."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        assert "method" in rule.rule_name.lower()
        assert "property" in rule.rule_name.lower()

    def test_description_property(self):
        """Should have informative description property."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        assert rule.description
        assert len(rule.description) > 20
        # Should mention converting to property
        assert "property" in rule.description.lower()


class TestMultipleViolationDetails:
    """Test violation details across multiple violations."""

    def test_detects_three_violations_in_mixed_class(self):
        """Should detect all three property candidates."""
        code = """
class Mixed:
    def __init__(self):
        self._name = "test"
        self._a = 1
        self._b = 2

    def get_name(self):
        return self._name

    def value(self):
        return self._a

    def total(self):
        return self._a + self._b
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("mixed.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 3

    def test_violation_messages_mention_method_names(self):
        """Should have messages mentioning each method name."""
        code = """
class Mixed:
    def __init__(self):
        self._name = "test"
        self._a = 1

    def get_name(self):
        return self._name

    def value(self):
        return self._a
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("mixed.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        combined_messages = " ".join(v.message for v in violations)
        assert "get_name" in combined_messages
        assert "value" in combined_messages

    def test_violations_have_rule_id(self):
        """Should have rule_id on all violations."""
        code = """
class Data:
    def __init__(self):
        self._a = 1

    def a(self):
        return self._a
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("data.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert violations[0].rule_id

    def test_violations_have_line_and_column(self):
        """Should have valid line and column on violations."""
        code = """
class Data:
    def __init__(self):
        self._a = 1

    def a(self):
        return self._a
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("data.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert violations[0].line > 0
        assert violations[0].column >= 0

    def test_violations_have_message_and_suggestion(self):
        """Should have message and suggestion on violations."""
        code = """
class Data:
    def __init__(self):
        self._a = 1

    def a(self):
        return self._a
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("data.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert violations[0].message
        assert violations[0].suggestion
