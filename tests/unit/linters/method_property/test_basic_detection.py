"""
Purpose: Unit tests for basic method-should-be-property detection

Scope: Testing core detection patterns for methods that should be @property decorators

Overview: Comprehensive test suite for method-should-be-property detection covering simple
    attribute returns, get_* prefix methods (Java-style), simple computed values, and chained
    attribute access. Validates that the linter correctly identifies methods that should be
    converted to @property decorators following Pythonic conventions. Tests various patterns
    including direct attribute access, string formatting, arithmetic operations, and boolean
    expressions. Uses TDD approach - tests are written before implementation and should fail
    initially.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock,
    src.linters.method_property.linter.MethodPropertyRule

Exports: TestSimpleAttributeReturn, TestGetPrefixMethods, TestSimpleComputation,
    TestChainedAttributeAccess test classes

Interfaces: test methods validating MethodPropertyRule.check(context) for various detection
    patterns

Implementation: Uses Mock objects for context creation, inline Python code strings as test
    fixtures, validates violation line numbers and messages
"""

from pathlib import Path
from unittest.mock import Mock


class TestSimpleAttributeReturn:
    """Tests for methods returning self._attribute or self.attribute."""

    def test_detects_return_private_attribute(self):
        """Should flag method that returns self._name."""
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
        assert violations[0].line == 6
        assert "name" in violations[0].message

    def test_detects_return_public_attribute(self):
        """Should flag method that returns self.value."""
        code = """
class Data:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("data.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "get_value" in violations[0].message

    def test_detects_return_nested_attribute(self):
        """Should flag method that returns self._settings.config."""
        code = """
class Service:
    def __init__(self, settings):
        self._settings = settings

    def config(self):
        return self._settings.config
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("service.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "config" in violations[0].message

    def test_detects_multiple_simple_accessors(self):
        """Should flag all simple accessor methods in a class."""
        code = """
class User:
    def __init__(self, name, email):
        self._name = name
        self._email = email

    def name(self):
        return self._name

    def email(self):
        return self._email
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 2


class TestGetPrefixMethods:
    """Tests for get_* prefixed methods (Java-style)."""

    def test_detects_get_prefix_simple(self):
        """Should flag get_name() method returning self._name."""
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
        assert "get_name" in violations[0].message
        # Should suggest converting to 'name' property
        assert "name" in violations[0].suggestion.lower()

    def test_detects_get_prefix_computed(self):
        """Should flag get_total() with simple computation."""
        code = """
class Cart:
    def __init__(self):
        self._count = 10
        self._price = 5

    def get_total(self):
        return self._count * self._price
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("cart.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "get_total" in violations[0].message

    def test_detects_multiple_get_methods(self):
        """Should flag all get_* methods in a class."""
        code = """
class DataStore:
    def __init__(self):
        self._data = []
        self._count = 0
        self._config = {}

    def get_data(self):
        return self._data

    def get_count(self):
        return self._count

    def get_config(self):
        return self._config
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("store.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 3


class TestSimpleComputation:
    """Tests for simple computed property candidates."""

    def test_detects_arithmetic_computation(self):
        """Should flag method with simple arithmetic on self attributes."""
        code = """
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def area(self):
        return self._width * self._height
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("shapes.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "area" in violations[0].message

    def test_detects_string_formatting(self):
        """Should flag method with string formatting of self attributes."""
        code = """
class Person:
    def __init__(self, first, last):
        self._first = first
        self._last = last

    def full_name(self):
        return f"{self._first} {self._last}"
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("person.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "full_name" in violations[0].message

    def test_detects_boolean_expression(self):
        """Should flag method with boolean expression on self attributes."""
        code = """
class Validator:
    def __init__(self, value):
        self._value = value

    def is_valid(self):
        return self._value > 0 and self._value < 100
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("validator.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "is_valid" in violations[0].message

    def test_detects_string_method_call(self):
        """Should flag method with string method call on self attribute."""
        code = """
class Formatter:
    def __init__(self, name):
        self._name = name

    def display_name(self):
        return self._name.upper()
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("formatter.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "display_name" in violations[0].message

    def test_detects_addition_operation(self):
        """Should flag method with addition on self attributes."""
        code = """
class Stats:
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def total(self):
        return self._a + self._b
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("stats.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "total" in violations[0].message


class TestChainedAttributeAccess:
    """Tests for methods returning nested/chained attribute access."""

    def test_detects_single_chain(self):
        """Should flag method returning self._connection.database."""
        code = """
class Service:
    def __init__(self, connection):
        self._connection = connection

    def database(self):
        return self._connection.database
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("service.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "database" in violations[0].message

    def test_detects_double_chain(self):
        """Should flag method returning self._config.settings.general."""
        code = """
class App:
    def __init__(self, config):
        self._config = config

    def settings(self):
        return self._config.settings.general
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "settings" in violations[0].message


class TestMultipleClasses:
    """Tests for files with multiple classes."""

    def test_detects_across_multiple_classes(self):
        """Should detect violations in all classes in a file."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

class Product:
    def __init__(self, price):
        self._price = price

    def get_price(self):
        return self._price
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("models.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 2

    def test_detects_in_nested_class(self):
        """Should detect violations in nested classes."""
        code = """
class Outer:
    def __init__(self):
        self._value = 42

    def value(self):
        return self._value

    class Inner:
        def __init__(self):
            self._data = []

        def data(self):
            return self._data
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("nested.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 2
