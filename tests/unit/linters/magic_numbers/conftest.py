"""
Purpose: Shared fixtures for magic numbers linter tests

Scope: Reusable test fixtures and helper functions for magic number detection testing

Overview: Provides pytest fixtures for magic numbers linter tests including standard
    configuration fixtures, sample Python code with magic numbers, and test file creation
    utilities. Centralizes common test setup patterns to ensure consistency across test
    modules and reduce code duplication. Fixtures support testing various detection scenarios,
    configuration options, and edge cases with minimal setup code in individual tests.

Dependencies: pytest for fixture support, pathlib for Path handling

Exports: magic_numbers_config fixture, sample code fixtures

Interfaces: pytest fixture discovery and dependency injection

Implementation: pytest fixture decorators with function-scoped lifecycle
"""

import pytest


@pytest.fixture
def magic_numbers_config():
    """Standard magic numbers configuration for testing.

    Returns:
        dict: Configuration with default allowed numbers and thresholds
    """
    return {
        "enabled": True,
        "allowed_numbers": {-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000},
        "max_small_integer": 10,
    }


@pytest.fixture
def python_code_with_magic_numbers():
    """Python code sample containing magic numbers.

    Returns:
        str: Python code with various magic number patterns
    """
    return """
def calculate_timeout():
    return 3600  # Magic number - should be named constant

def process_items(items):
    for i in range(5):  # Small int in range - acceptable
        items[i] *= 3.14159  # Magic number - PI should be constant
"""


@pytest.fixture
def python_code_with_constants():
    """Python code with acceptable constant definitions.

    Returns:
        str: Python code with UPPERCASE constant definitions
    """
    return """
TIMEOUT_SECONDS = 3600
MAX_RETRIES = 5
PI = 3.14159

def calculate_timeout():
    return TIMEOUT_SECONDS
"""


@pytest.fixture
def python_code_with_range():
    """Python code with small integers in range context.

    Returns:
        str: Python code with acceptable range() usage
    """
    return """
def process_batch():
    for i in range(10):
        process(i)

    for j in enumerate(range(5)):
        handle(j)
"""
