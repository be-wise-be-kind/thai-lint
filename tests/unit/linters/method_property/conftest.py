"""
Purpose: Shared pytest fixtures for method property linter tests

Scope: Fixture definitions for method-should-be-property detection test scenarios

Overview: Provides pytest fixtures for method property linter tests including standard
    configuration fixtures, sample Python code with various method patterns, and code samples
    demonstrating exclusion scenarios. Centralizes common test setup patterns to ensure
    consistency across test modules and reduce code duplication. Fixtures cover detection
    patterns like simple attribute returns, get_* prefix methods, and computed values, as
    well as exclusion scenarios like methods with parameters, side effects, and decorators.

Dependencies: pytest for fixture support, pathlib for Path handling

Exports: method_property_config, simple_attribute_return_code, get_prefix_code,
    simple_computation_code, method_with_params_code, method_with_side_effects_code,
    decorated_methods_code, complex_body_code, dunder_methods_code fixtures

Interfaces: pytest fixtures with function scope returning configuration dicts or code strings

Implementation: Pytest fixture decorators with function-scoped lifecycle, provides reusable
    test data for method property detection tests
"""

import pytest


@pytest.fixture
def method_property_config():
    """Standard method property configuration for testing.

    Returns:
        dict: Configuration with default settings
    """
    return {
        "enabled": True,
        "max_body_statements": 3,
        "ignore": [],
    }


@pytest.fixture
def simple_attribute_return_code():
    """Python code with methods returning simple attributes.

    Returns:
        str: Python code with simple accessor methods that should be properties
    """
    return """
class User:
    def __init__(self, name):
        self._name = name
        self._email = None
        self.value = 42

    def name(self):
        return self._name

    def email(self):
        return self._email

    def get_value(self):
        return self.value
"""


@pytest.fixture
def get_prefix_code():
    """Python code with Java-style get_* methods.

    Returns:
        str: Python code with get_* prefix methods that should be properties
    """
    return """
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

    def get_total(self):
        return self._count * 2
"""


@pytest.fixture
def simple_computation_code():
    """Python code with simple computed value methods.

    Returns:
        str: Python code with simple computations that should be properties
    """
    return """
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._first = "John"
        self._last = "Doe"
        self._value = 50

    def area(self):
        return self._width * self._height

    def full_name(self):
        return f"{self._first} {self._last}"

    def is_valid(self):
        return self._value > 0 and self._value < 100

    def display_name(self):
        return self._first.upper()
"""


@pytest.fixture
def chained_attribute_code():
    """Python code with chained attribute access.

    Returns:
        str: Python code with chained attribute access that should be properties
    """
    return """
class Service:
    def __init__(self, connection, config):
        self._connection = connection
        self._config = config

    def database(self):
        return self._connection.database

    def settings(self):
        return self._config.settings.general
"""


@pytest.fixture
def method_with_params_code():
    """Python code with methods that have parameters (should NOT be flagged).

    Returns:
        str: Python code with parameterized methods
    """
    return """
class Container:
    def __init__(self):
        self._items = []
        self._value = None

    def get_item(self, index):
        return self._items[index]

    def value_with_default(self, default=None):
        return self._value or default

    def get_range(self, start, end):
        return self._items[start:end]
"""


@pytest.fixture
def method_with_side_effects_code():
    """Python code with methods that have side effects (should NOT be flagged).

    Returns:
        str: Python code with side effect methods
    """
    return """
class Counter:
    def __init__(self):
        self._count = 0
        self._cached = False
        self._value = 42
        self._data = []

    def cached_value(self):
        self._cached = True
        return self._value

    def increment_and_get(self):
        self._count += 1
        return self._count

    def items(self):
        for item in self._data:
            yield item

    def filtered_values(self):
        result = []
        for v in self._data:
            if v > 0:
                result.append(v)
        return result
"""


@pytest.fixture
def method_with_try_except_code():
    """Python code with methods that have try/except (should NOT be flagged).

    Returns:
        str: Python code with error handling methods
    """
    return """
class SafeContainer:
    def __init__(self):
        self._value = None

    def safe_value(self):
        try:
            return self._value
        except AttributeError:
            return None
"""


@pytest.fixture
def method_with_external_calls_code():
    """Python code with methods that call external functions (should NOT be flagged).

    Returns:
        str: Python code with external function calls
    """
    return """
def format_date(date):
    return str(date)

def validate(value):
    pass

class Formatter:
    def __init__(self):
        self._date = None
        self._value = 42

    def formatted_date(self):
        return format_date(self._date)

    def validated_value(self):
        validate(self._value)
        return self._value
"""


@pytest.fixture
def decorated_methods_code():
    """Python code with decorated methods (should NOT be flagged).

    Returns:
        str: Python code with various decorators
    """
    return """
from abc import abstractmethod
import functools

class Base:
    def __init__(self):
        self._name = "test"
        self._value = 42

    @staticmethod
    def create_default():
        return Base()

    @classmethod
    def from_dict(cls, data):
        return cls()

    @abstractmethod
    def compute(self):
        pass

    @property
    def name(self):
        return self._name

    @functools.cached_property
    def expensive_value(self):
        return self._value * 100
"""


@pytest.fixture
def complex_body_code():
    """Python code with complex method bodies (should NOT be flagged).

    Returns:
        str: Python code with methods exceeding max body statements
    """
    return """
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


@pytest.fixture
def dunder_methods_code():
    """Python code with dunder methods (should NOT be flagged).

    Returns:
        str: Python code with special methods
    """
    return """
class Entity:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __str__(self):
        return self._name

    def __repr__(self):
        return f"Entity({self._value})"

    def __len__(self):
        return len(self._name)
"""


@pytest.fixture
def async_methods_code():
    """Python code with async methods (should NOT be flagged).

    Returns:
        str: Python code with async/await
    """
    return """
class AsyncService:
    def __init__(self):
        self._data = None

    async def data(self):
        return await self._fetch_data()

    async def _fetch_data(self):
        return self._data
"""


@pytest.fixture
def methods_returning_none_code():
    """Python code with methods returning None (should NOT be flagged).

    Returns:
        str: Python code with void-like methods
    """
    return """
class Logger:
    def __init__(self):
        self._value = 42

    def initialize(self):
        pass

    def log_value(self):
        print(self._value)
        return None

    def setup(self):
        return
"""


@pytest.fixture
def mixed_methods_code():
    """Python code with mix of valid property candidates and exclusions.

    Returns:
        str: Python code with various method patterns
    """
    return """
class MixedClass:
    def __init__(self):
        self._name = "test"
        self._value = 42
        self._items = []

    # Should be flagged
    def name(self):
        return self._name

    # Should be flagged
    def get_value(self):
        return self._value

    # Should NOT be flagged (has parameter)
    def get_item(self, index):
        return self._items[index]

    # Should NOT be flagged (side effect)
    def count(self):
        self._value += 1
        return self._value

    # Should NOT be flagged (already property)
    @property
    def items(self):
        return self._items
"""
