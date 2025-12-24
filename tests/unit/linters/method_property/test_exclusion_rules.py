"""
Purpose: Unit tests for method-should-be-property exclusion rules

Scope: Testing scenarios where methods should NOT be flagged as property candidates

Overview: Comprehensive test suite for exclusion rules in method-should-be-property detection.
    Validates that the linter correctly excludes methods with parameters, side effects, loops,
    try/except blocks, external function calls, decorators (@staticmethod, @classmethod,
    @abstractmethod, @property), complex bodies, dunder methods, test files, methods returning
    None, and async methods. Uses parametrized tests for efficiency.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock,
    src.linters.method_property.linter.MethodPropertyRule

Exports: Test classes for each exclusion category

Interfaces: Parametrized test methods validating MethodPropertyRule.check(context)

Implementation: Uses factory fixtures for context creation, parametrized tests for code samples,
    validates zero violations for exclusion scenarios and specific counts for mixed patterns
"""

from pathlib import Path
from typing import NamedTuple
from unittest.mock import Mock

import pytest

from src.linters.method_property.linter import MethodPropertyRule


class ExclusionTestCase(NamedTuple):
    """Test case for exclusion rule testing."""

    code: str
    filename: str
    description: str


@pytest.fixture
def rule():
    """Create a MethodPropertyRule instance."""
    return MethodPropertyRule()


@pytest.fixture
def create_context():
    """Factory fixture for creating mock contexts."""

    def _create(code: str, filename: str = "test.py") -> Mock:
        context = Mock()
        context.file_path = Path(filename)
        context.file_content = code
        context.language = "python"
        return context

    return _create


# =============================================================================
# Test Data: Code samples for exclusion tests
# =============================================================================

PARAMETER_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
class Container:
    def __init__(self):
        self._items = []

    def get_item(self, index):
        return self._items[index]
""",
        filename="container.py",
        description="method_with_required_param",
    ),
    ExclusionTestCase(
        code="""
class ValueHolder:
    def __init__(self):
        self._value = None

    def get_value(self, default=None):
        return self._value or default
""",
        filename="holder.py",
        description="method_with_default_param",
    ),
    ExclusionTestCase(
        code="""
class Aggregator:
    def __init__(self):
        self._items = []

    def get_items(self, *args):
        return self._items
""",
        filename="aggregator.py",
        description="method_with_args",
    ),
    ExclusionTestCase(
        code="""
class Config:
    def __init__(self):
        self._settings = {}

    def get_settings(self, **kwargs):
        return self._settings
""",
        filename="config.py",
        description="method_with_kwargs",
    ),
    ExclusionTestCase(
        code="""
class DataStore:
    def __init__(self):
        self._data = {}

    def get_range(self, start, end, step=1):
        return self._data
""",
        filename="store.py",
        description="method_with_multiple_params",
    ),
]

SIDE_EFFECT_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
class Cache:
    def __init__(self):
        self._cached = False
        self._value = 42

    def cached_value(self):
        self._cached = True
        return self._value
""",
        filename="cache.py",
        description="method_with_assignment",
    ),
    ExclusionTestCase(
        code="""
class Counter:
    def __init__(self):
        self._count = 0

    def increment_and_get(self):
        self._count += 1
        return self._count
""",
        filename="counter.py",
        description="method_with_augmented_assignment",
    ),
    ExclusionTestCase(
        code="""
class DataProcessor:
    def __init__(self):
        self._data = [1, 2, 3]

    def items(self):
        for item in self._data:
            yield item
""",
        filename="processor.py",
        description="method_with_for_loop",
    ),
    ExclusionTestCase(
        code="""
class Iterator:
    def __init__(self):
        self._items = []
        self._index = 0

    def next_item(self):
        while self._index < len(self._items):
            self._index += 1
        return self._items
""",
        filename="iterator.py",
        description="method_with_while_loop",
    ),
    ExclusionTestCase(
        code="""
class Filter:
    def __init__(self):
        self._data = [1, 2, 3, 4, 5]

    def filtered_values(self):
        result = [v for v in self._data if v > 0]
        return result
""",
        filename="filter.py",
        description="method_with_list_comprehension_assignment",
    ),
]

TRY_EXCEPT_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
class SafeContainer:
    def __init__(self):
        self._value = None

    def safe_value(self):
        try:
            return self._value
        except AttributeError:
            return None
""",
        filename="safe.py",
        description="method_with_try_except",
    ),
    ExclusionTestCase(
        code="""
class Resource:
    def __init__(self):
        self._resource = None
        self._lock = None

    def resource(self):
        try:
            return self._resource
        finally:
            self._lock = False
""",
        filename="resource.py",
        description="method_with_try_finally",
    ),
]

EXTERNAL_CALL_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
def format_date(date):
    return str(date)

class Formatter:
    def __init__(self):
        self._date = None

    def formatted_date(self):
        return format_date(self._date)
""",
        filename="formatter.py",
        description="method_with_external_function_call",
    ),
    ExclusionTestCase(
        code="""
def validate(value):
    pass

class Validator:
    def __init__(self):
        self._value = 42

    def validated_value(self):
        validate(self._value)
        return self._value
""",
        filename="validator.py",
        description="method_with_side_effect_call",
    ),
    ExclusionTestCase(
        code="""
class Logger:
    def __init__(self):
        self._message = "test"

    def log_and_get(self):
        print(self._message)
        return self._message
""",
        filename="logger.py",
        description="method_with_builtin_side_effect",
    ),
]

DECORATOR_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
class Factory:
    @staticmethod
    def create_default():
        return Factory()
""",
        filename="factory.py",
        description="staticmethod",
    ),
    ExclusionTestCase(
        code="""
class Builder:
    @classmethod
    def from_dict(cls, data):
        return cls()
""",
        filename="builder.py",
        description="classmethod",
    ),
    ExclusionTestCase(
        code="""
from abc import abstractmethod, ABC

class Base(ABC):
    @abstractmethod
    def compute(self):
        pass
""",
        filename="base.py",
        description="abstractmethod",
    ),
    ExclusionTestCase(
        code="""
class User:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
""",
        filename="user.py",
        description="property_already",
    ),
    ExclusionTestCase(
        code="""
import functools

class Expensive:
    def __init__(self):
        self._value = 42

    @functools.cached_property
    def expensive_value(self):
        return self._value * 100
""",
        filename="expensive.py",
        description="cached_property",
    ),
    ExclusionTestCase(
        code="""
def cache(func):
    return func

class Service:
    def __init__(self):
        self._data = []

    @cache
    def data(self):
        return self._data
""",
        filename="service.py",
        description="custom_decorator",
    ),
]

COMPLEX_BODY_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
class Processor:
    def __init__(self):
        self._raw_value = "  Test-Value  "

    def processed_value(self):
        value = self._raw_value
        value = value.strip()
        value = value.lower()
        value = value.replace("-", "_")
        return value
""",
        filename="processor.py",
        description="body_over_3_statements",
    ),
    ExclusionTestCase(
        code="""
class Conditional:
    def __init__(self):
        self._value = None

    def value_or_default(self):
        if self._value is None:
            return "default"
        return self._value
""",
        filename="conditional.py",
        description="method_with_if_statement",
    ),
]

SPECIAL_CASE_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
class Entity:
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name

    def __repr__(self):
        return f"Entity({self._name})"

    def __len__(self):
        return len(self._name)
""",
        filename="entity.py",
        description="dunder_methods",
    ),
    ExclusionTestCase(
        code="""
class TestUser:
    def __init__(self):
        self._mock_data = []

    def get_mock_value(self):
        return self._mock_data
""",
        filename="test_user.py",
        description="test_files_prefix",
    ),
    ExclusionTestCase(
        code="""
class UserTest:
    def __init__(self):
        self._mock_data = []

    def get_mock_value(self):
        return self._mock_data
""",
        filename="user_test.py",
        description="test_files_suffix",
    ),
    ExclusionTestCase(
        code="""
class Initializer:
    def __init__(self):
        self._value = 42

    def log_value(self):
        print(self._value)
        return None
""",
        filename="init.py",
        description="returns_none",
    ),
    ExclusionTestCase(
        code="""
class Setup:
    def __init__(self):
        self._value = 42

    def initialize(self):
        pass

    def setup(self):
        return
""",
        filename="setup.py",
        description="no_return",
    ),
]

ASYNC_EXCLUSION_CASES = [
    ExclusionTestCase(
        code="""
class AsyncService:
    def __init__(self):
        self._data = None

    async def data(self):
        return await self._fetch_data()

    async def _fetch_data(self):
        return self._data
""",
        filename="async_service.py",
        description="async_method_with_await",
    ),
    ExclusionTestCase(
        code="""
class AsyncContainer:
    def __init__(self):
        self._value = 42

    async def value(self):
        return self._value
""",
        filename="async_container.py",
        description="async_def_without_await",
    ),
]


# =============================================================================
# Parametrized Tests: Zero Violations Expected
# =============================================================================


class TestParameterExclusions:
    """Methods with parameters should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        PARAMETER_EXCLUSION_CASES,
        ids=[c.description for c in PARAMETER_EXCLUSION_CASES],
    )
    def test_ignores_methods_with_parameters(self, rule, create_context, case):
        """Should NOT flag methods with parameters beyond self."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


class TestSideEffectExclusions:
    """Methods with side effects should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        SIDE_EFFECT_EXCLUSION_CASES,
        ids=[c.description for c in SIDE_EFFECT_EXCLUSION_CASES],
    )
    def test_ignores_methods_with_side_effects(self, rule, create_context, case):
        """Should NOT flag methods with assignments, loops, or generators."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


class TestTryExceptExclusions:
    """Methods with try/except should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        TRY_EXCEPT_EXCLUSION_CASES,
        ids=[c.description for c in TRY_EXCEPT_EXCLUSION_CASES],
    )
    def test_ignores_methods_with_try_except(self, rule, create_context, case):
        """Should NOT flag methods with try/except or try/finally blocks."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


class TestExternalCallExclusions:
    """Methods with external function calls should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        EXTERNAL_CALL_EXCLUSION_CASES,
        ids=[c.description for c in EXTERNAL_CALL_EXCLUSION_CASES],
    )
    def test_ignores_methods_with_external_calls(self, rule, create_context, case):
        """Should NOT flag methods that call external or builtin functions."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


class TestDecoratorExclusions:
    """Decorated methods should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        DECORATOR_EXCLUSION_CASES,
        ids=[c.description for c in DECORATOR_EXCLUSION_CASES],
    )
    def test_ignores_decorated_methods(self, rule, create_context, case):
        """Should NOT flag methods with decorators."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


class TestComplexBodyExclusions:
    """Complex method bodies should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        COMPLEX_BODY_EXCLUSION_CASES,
        ids=[c.description for c in COMPLEX_BODY_EXCLUSION_CASES],
    )
    def test_ignores_complex_bodies(self, rule, create_context, case):
        """Should NOT flag methods with complex bodies."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


class TestSpecialCases:
    """Special cases that should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        SPECIAL_CASE_EXCLUSION_CASES,
        ids=[c.description for c in SPECIAL_CASE_EXCLUSION_CASES],
    )
    def test_ignores_special_cases(self, rule, create_context, case):
        """Should NOT flag dunder methods, test files, or void methods."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


class TestAsyncExclusions:
    """Async methods should NOT be flagged."""

    @pytest.mark.parametrize(
        "case",
        ASYNC_EXCLUSION_CASES,
        ids=[c.description for c in ASYNC_EXCLUSION_CASES],
    )
    def test_ignores_async_methods(self, rule, create_context, case):
        """Should NOT flag async methods."""
        context = create_context(case.code, case.filename)
        violations = rule.check(context)
        assert len(violations) == 0


# =============================================================================
# Mixed Pattern Tests: Specific Violation Counts
# =============================================================================


class TestMixedPatterns:
    """Test files with mix of flaggable and non-flaggable methods."""

    def test_flags_exactly_two_candidates(self, rule, create_context, mixed_methods_code):
        """Should flag exactly two property candidates in mixed code."""
        context = create_context(mixed_methods_code, "mixed.py")
        violations = rule.check(context)
        assert len(violations) == 2

    def test_flags_name_method_in_mixed(self, rule, create_context, mixed_methods_code):
        """Should flag 'name' method in mixed code."""
        context = create_context(mixed_methods_code, "mixed.py")
        violations = rule.check(context)
        combined = " ".join(v.message for v in violations)
        assert "name" in combined

    def test_flags_get_value_method_in_mixed(self, rule, create_context, mixed_methods_code):
        """Should flag 'get_value' method in mixed code."""
        context = create_context(mixed_methods_code, "mixed.py")
        violations = rule.check(context)
        combined = " ".join(v.message for v in violations)
        assert "get_value" in combined
