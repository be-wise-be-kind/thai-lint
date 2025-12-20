"""
Purpose: Shared fixtures for stringly-typed linter tests

Scope: Reusable test fixtures and helper functions for stringly-typed pattern detection testing

Overview: Provides pytest fixtures for stringly-typed linter tests including standard
    configuration fixtures, sample Python code with stringly-typed patterns, and sample
    TypeScript code. Centralizes common test setup patterns to ensure consistency across
    test modules and reduce code duplication. Fixtures support testing various detection
    scenarios, configuration options, and edge cases with minimal setup code in individual
    tests.

Dependencies: pytest for fixture support

Exports: stringly_typed_config fixture, sample code fixtures

Interfaces: pytest fixture discovery and dependency injection

Implementation: pytest fixture decorators with function-scoped lifecycle
"""

import pytest


@pytest.fixture
def stringly_typed_config() -> dict:
    """Standard stringly-typed configuration for testing.

    Returns:
        dict: Configuration with default thresholds and settings
    """
    return {
        "enabled": True,
        "min_occurrences": 2,
        "min_values_for_enum": 2,
        "max_values_for_enum": 6,
        "require_cross_file": True,
        "ignore": [],
        "allowed_string_sets": [],
        "exclude_variables": [],
    }


@pytest.fixture
def custom_stringly_typed_config() -> dict:
    """Custom stringly-typed configuration with non-default values.

    Returns:
        dict: Configuration with custom thresholds and settings
    """
    return {
        "enabled": True,
        "min_occurrences": 3,
        "min_values_for_enum": 3,
        "max_values_for_enum": 8,
        "require_cross_file": False,
        "ignore": ["tests/**", "**/fixtures.py"],
        "allowed_string_sets": [["debug", "info", "warning", "error"]],
        "exclude_variables": ["log_level", "severity"],
    }


@pytest.fixture
def python_code_with_membership_validation() -> str:
    """Python code sample with membership validation pattern.

    Returns:
        str: Python code with 'x in ("a", "b")' patterns
    """
    return """
def validate_environment(env: str) -> bool:
    if env not in ("staging", "production"):
        raise ValueError(f"Invalid environment: {env}")
    return True

def check_status(status: str) -> bool:
    if status in {"pending", "completed", "failed"}:
        return True
    return False
"""


@pytest.fixture
def python_code_with_equality_chain() -> str:
    """Python code sample with equality chain pattern.

    Returns:
        str: Python code with 'if x == "a" elif x == "b"' patterns
    """
    return """
def handle_status(status: str) -> None:
    if status == "success":
        print("Completed successfully")
    elif status == "failure":
        print("Operation failed")
    elif status == "pending":
        print("Still waiting...")
"""


@pytest.fixture
def typescript_code_with_stringly_typed() -> str:
    """TypeScript code sample with stringly-typed patterns.

    Returns:
        str: TypeScript code with includes() and switch patterns
    """
    return """
function validateEnv(env: string): boolean {
    if (!["staging", "production"].includes(env)) {
        throw new Error(`Invalid environment: ${env}`);
    }
    return true;
}

function handleMode(mode: string): void {
    switch (mode) {
        case "debug":
            console.log("Debug mode");
            break;
        case "release":
            console.log("Release mode");
            break;
    }
}
"""
