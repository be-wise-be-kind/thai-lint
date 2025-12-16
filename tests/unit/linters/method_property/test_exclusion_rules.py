"""
Purpose: Unit tests for method-should-be-property exclusion rules

Scope: Testing scenarios where methods should NOT be flagged as property candidates

Overview: Comprehensive test suite for exclusion rules in method-should-be-property detection.
    Validates that the linter correctly excludes methods with parameters, side effects, loops,
    try/except blocks, external function calls, decorators (@staticmethod, @classmethod,
    @abstractmethod, @property), complex bodies, dunder methods, test files, methods returning
    None, and async methods. Ensures the linter minimizes false positives by properly respecting
    all exclusion criteria defined in the feature specification.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock,
    src.linters.method_property.linter.MethodPropertyRule

Exports: TestParameterExclusions, TestSideEffectExclusions, TestDecoratorExclusions,
    TestComplexBodyExclusions, TestSpecialCases test classes

Interfaces: test methods validating MethodPropertyRule.check(context) returns no violations
    for excluded patterns

Implementation: Uses Mock objects for context creation, inline Python code strings as test
    fixtures, validates zero violations for each exclusion scenario
"""

from pathlib import Path
from unittest.mock import Mock


class TestParameterExclusions:
    """Methods with parameters should NOT be flagged."""

    def test_ignores_method_with_required_param(self):
        """Should NOT flag method with required parameter beyond self."""
        code = """
class Container:
    def __init__(self):
        self._items = []

    def get_item(self, index):
        return self._items[index]
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("container.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_default_param(self):
        """Should NOT flag method with default parameter."""
        code = """
class ValueHolder:
    def __init__(self):
        self._value = None

    def get_value(self, default=None):
        return self._value or default
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("holder.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_args(self):
        """Should NOT flag method with *args."""
        code = """
class Aggregator:
    def __init__(self):
        self._items = []

    def get_items(self, *args):
        return self._items
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("aggregator.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_kwargs(self):
        """Should NOT flag method with **kwargs."""
        code = """
class Config:
    def __init__(self):
        self._settings = {}

    def get_settings(self, **kwargs):
        return self._settings
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("config.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_multiple_params(self):
        """Should NOT flag method with multiple parameters."""
        code = """
class DataStore:
    def __init__(self):
        self._data = {}

    def get_range(self, start, end, step=1):
        return self._data
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("store.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestSideEffectExclusions:
    """Methods with side effects should NOT be flagged."""

    def test_ignores_method_with_assignment(self):
        """Should NOT flag method with assignment statement."""
        code = """
class Cache:
    def __init__(self):
        self._cached = False
        self._value = 42

    def cached_value(self):
        self._cached = True
        return self._value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("cache.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_augmented_assignment(self):
        """Should NOT flag method with augmented assignment (+=, -=, etc.)."""
        code = """
class Counter:
    def __init__(self):
        self._count = 0

    def increment_and_get(self):
        self._count += 1
        return self._count
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("counter.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_for_loop(self):
        """Should NOT flag method with for loop."""
        code = """
class DataProcessor:
    def __init__(self):
        self._data = [1, 2, 3]

    def items(self):
        for item in self._data:
            yield item
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("processor.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_while_loop(self):
        """Should NOT flag method with while loop."""
        code = """
class Iterator:
    def __init__(self):
        self._items = []
        self._index = 0

    def next_item(self):
        while self._index < len(self._items):
            self._index += 1
        return self._items
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("iterator.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_list_comprehension_assignment(self):
        """Should NOT flag method with list comprehension that assigns."""
        code = """
class Filter:
    def __init__(self):
        self._data = [1, 2, 3, 4, 5]

    def filtered_values(self):
        result = [v for v in self._data if v > 0]
        return result
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("filter.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # This has an assignment statement so should not be flagged
        assert len(violations) == 0


class TestTryExceptExclusions:
    """Methods with try/except should NOT be flagged."""

    def test_ignores_method_with_try_except(self):
        """Should NOT flag method with try/except block."""
        code = """
class SafeContainer:
    def __init__(self):
        self._value = None

    def safe_value(self):
        try:
            return self._value
        except AttributeError:
            return None
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("safe.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_try_finally(self):
        """Should NOT flag method with try/finally block."""
        code = """
class Resource:
    def __init__(self):
        self._resource = None
        self._lock = None

    def resource(self):
        try:
            return self._resource
        finally:
            self._lock = False
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("resource.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestExternalCallExclusions:
    """Methods with external function calls should NOT be flagged."""

    def test_ignores_method_with_external_function_call(self):
        """Should NOT flag method that calls external function."""
        code = """
def format_date(date):
    return str(date)

class Formatter:
    def __init__(self):
        self._date = None

    def formatted_date(self):
        return format_date(self._date)
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("formatter.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_side_effect_call(self):
        """Should NOT flag method that calls function with side effects."""
        code = """
def validate(value):
    pass

class Validator:
    def __init__(self):
        self._value = 42

    def validated_value(self):
        validate(self._value)
        return self._value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("validator.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_builtin_that_has_side_effects(self):
        """Should NOT flag method that calls print()."""
        code = """
class Logger:
    def __init__(self):
        self._message = "test"

    def log_and_get(self):
        print(self._message)
        return self._message
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("logger.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestDecoratorExclusions:
    """Decorated methods should NOT be flagged."""

    def test_ignores_staticmethod(self):
        """Should NOT flag @staticmethod."""
        code = """
class Factory:
    @staticmethod
    def create_default():
        return Factory()
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("factory.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_classmethod(self):
        """Should NOT flag @classmethod."""
        code = """
class Builder:
    @classmethod
    def from_dict(cls, data):
        return cls()
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("builder.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_abstractmethod(self):
        """Should NOT flag @abstractmethod."""
        code = """
from abc import abstractmethod, ABC

class Base(ABC):
    @abstractmethod
    def compute(self):
        pass
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("base.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_property_already(self):
        """Should NOT flag method already decorated with @property."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    @property
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
        assert len(violations) == 0

    def test_ignores_cached_property(self):
        """Should NOT flag @functools.cached_property."""
        code = """
import functools

class Expensive:
    def __init__(self):
        self._value = 42

    @functools.cached_property
    def expensive_value(self):
        return self._value * 100
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("expensive.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_custom_decorator(self):
        """Should NOT flag method with custom decorator."""
        code = """
def cache(func):
    return func

class Service:
    def __init__(self):
        self._data = []

    @cache
    def data(self):
        return self._data
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("service.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestComplexBodyExclusions:
    """Complex method bodies should NOT be flagged."""

    def test_ignores_body_over_3_statements(self):
        """Should NOT flag method with more than 3 statements."""
        code = """
class Processor:
    def __init__(self):
        self._raw_value = "  Test-Value  "

    def processed_value(self):
        value = self._raw_value
        value = value.strip()
        value = value.lower()
        value = value.replace("-", "_")
        return value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("processor.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_method_with_if_statement(self):
        """Should NOT flag method with if/else statement (adds complexity)."""
        code = """
class Conditional:
    def __init__(self):
        self._value = None

    def value_or_default(self):
        if self._value is None:
            return "default"
        return self._value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("conditional.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestSpecialCases:
    """Special cases that should NOT be flagged."""

    def test_ignores_dunder_methods(self):
        """Should NOT flag dunder methods like __str__."""
        code = """
class Entity:
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name

    def __repr__(self):
        return f"Entity({self._name})"

    def __len__(self):
        return len(self._name)
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("entity.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_test_files(self):
        """Should NOT flag methods in test files."""
        code = """
class TestUser:
    def __init__(self):
        self._mock_data = []

    def get_mock_value(self):
        return self._mock_data
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("test_user.py")  # Test file naming
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_test_files_suffix(self):
        """Should NOT flag methods in *_test.py files."""
        code = """
class UserTest:
    def __init__(self):
        self._mock_data = []

    def get_mock_value(self):
        return self._mock_data
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user_test.py")  # Test file naming
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_returns_none(self):
        """Should NOT flag methods that return None."""
        code = """
class Initializer:
    def __init__(self):
        self._value = 42

    def log_value(self):
        print(self._value)
        return None
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("init.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_no_return(self):
        """Should NOT flag methods with no return statement."""
        code = """
class Setup:
    def __init__(self):
        self._value = 42

    def initialize(self):
        pass

    def setup(self):
        return
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("setup.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestAsyncExclusions:
    """Async methods should NOT be flagged."""

    def test_ignores_async_method(self):
        """Should NOT flag async method with await."""
        code = """
class AsyncService:
    def __init__(self):
        self._data = None

    async def data(self):
        return await self._fetch_data()

    async def _fetch_data(self):
        return self._data
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("async_service.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_async_def_without_await(self):
        """Should NOT flag async def even without explicit await."""
        code = """
class AsyncContainer:
    def __init__(self):
        self._value = 42

    async def value(self):
        return self._value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("async_container.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestMixedPatterns:
    """Test files with mix of flaggable and non-flaggable methods."""

    def test_flags_exactly_two_candidates(self, mixed_methods_code):
        """Should flag exactly two property candidates in mixed code."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("mixed.py")
        context.file_content = mixed_methods_code
        context.language = "python"

        violations = rule.check(context)
        # Should flag 'name' and 'get_value' only
        assert len(violations) == 2

    def test_flags_name_method_in_mixed(self, mixed_methods_code):
        """Should flag 'name' method in mixed code."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("mixed.py")
        context.file_content = mixed_methods_code
        context.language = "python"

        violations = rule.check(context)
        combined = " ".join(v.message for v in violations)
        assert "name" in combined

    def test_flags_get_value_method_in_mixed(self, mixed_methods_code):
        """Should flag 'get_value' method in mixed code."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("mixed.py")
        context.file_content = mixed_methods_code
        context.language = "python"

        violations = rule.check(context)
        combined = " ".join(v.message for v in violations)
        assert "get_value" in combined
