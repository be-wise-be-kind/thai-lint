"""
File: tests/unit/linters/print_statements/conftest.py

Purpose: Shared fixtures for print statements linter tests

Exports: print_statements_config fixture, sample code fixtures

Depends: pytest for fixture support, pathlib for Path handling

Implements: pytest fixture discovery and dependency injection

Related: tests/unit/linters/magic_numbers/conftest.py

Overview: Provides pytest fixtures for print statements linter tests including standard
    configuration fixtures, sample Python code with print statements, and sample TypeScript
    code with console calls. Centralizes common test setup patterns to ensure consistency
    across test modules and reduce code duplication.

Usage: Fixtures are auto-discovered by pytest through conftest.py

Notes: pytest fixture decorators with function-scoped lifecycle
"""

import pytest


@pytest.fixture
def print_statements_config():
    """Standard print statements configuration for testing.

    Returns:
        dict: Configuration with default settings
    """
    return {
        "enabled": True,
        "allow_in_scripts": True,
        "console_methods": {"log", "warn", "error", "debug", "info"},
    }


@pytest.fixture
def python_code_with_print():
    """Python code sample containing print statements.

    Returns:
        str: Python code with print() calls
    """
    return """
def process_data(data):
    print("Processing data...")
    result = transform(data)
    print(f"Result: {result}")
    return result
"""


@pytest.fixture
def python_code_with_main_block():
    """Python code with print in __main__ block.

    Returns:
        str: Python code with acceptable __main__ print usage
    """
    return """
def main():
    print("This should be flagged")

if __name__ == "__main__":
    print("This should NOT be flagged with allow_in_scripts=True")
"""


@pytest.fixture
def typescript_code_with_console():
    """TypeScript code sample containing console statements.

    Returns:
        str: TypeScript code with console.* calls
    """
    return """
function processData(data: any): any {
    console.log("Processing data...");
    const result = transform(data);
    console.warn("Check this value");
    console.error("An error occurred");
    return result;
}
"""


@pytest.fixture
def typescript_code_with_various_console():
    """TypeScript code with various console methods.

    Returns:
        str: TypeScript code with multiple console method types
    """
    return """
function test() {
    console.log("log message");
    console.warn("warn message");
    console.error("error message");
    console.debug("debug message");
    console.info("info message");
}
"""
