"""
Shared fixtures for performance linter tests.

Purpose: Provide common test fixtures and utilities for performance linter testing

Scope: Test fixtures, helper functions, and shared constants

Overview: Contains pytest fixtures and utilities used across performance linter tests.
    Provides code parsing helpers, violation assertion utilities, and common test data.

Dependencies: pytest

Exports: Fixtures for test code parsing and violation checking

Related: test_string_concat_loop.py, test_regex_in_loop.py

Implementation: pytest fixtures with helper functions
"""

import pytest


@pytest.fixture
def python_code_samples() -> dict[str, str]:
    """Common Python code samples for testing."""
    return {
        "empty": "",
        "simple_function": """
def hello():
    return "world"
""",
        "simple_loop": """
def process(items):
    for item in items:
        print(item)
""",
    }


@pytest.fixture
def typescript_code_samples() -> dict[str, str]:
    """Common TypeScript code samples for testing."""
    return {
        "empty": "",
        "simple_function": """
function hello(): string {
    return "world";
}
""",
        "simple_loop": """
function process(items: string[]): void {
    for (const item of items) {
        console.log(item);
    }
}
""",
    }
