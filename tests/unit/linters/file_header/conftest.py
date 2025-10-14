"""
File: tests/unit/linters/file_header/conftest.py

Purpose: Shared fixtures and test utilities for file header linter tests

Exports: Test fixtures for mock context creation, configuration, and sample code

Depends: pytest fixture framework, unittest.mock for context mocking, pathlib for Path handling

Implements: pytest fixture decorators with function-scoped lifecycle

Related: tests/unit/linters/magic_numbers/conftest.py for pattern reference

Overview: Provides reusable pytest fixtures for file header linter tests including
    helper functions for mock context creation, standard configuration fixtures, and
    sample Python code with various header patterns. Centralizes common test setup
    to ensure consistency across test modules and reduce duplication. Supports testing
    mandatory field detection, atemporal language validation, and edge cases.

Usage: Fixtures automatically discovered by pytest and injectable into test functions

Notes: Follows project test patterns from magic-numbers linter tests
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


def create_mock_context(code: str, file_path: str = "test.py", language: str = "python") -> Mock:
    """Create mock lint context for testing.

    Args:
        code: Source code content
        file_path: Path to file being linted
        language: Programming language

    Returns:
        Mock context object with required attributes
    """
    context = Mock()
    context.file_path = Path(file_path)
    context.file_content = code
    context.language = language
    context.metadata = {}
    return context


@pytest.fixture
def file_header_config():
    """Standard file header configuration for testing.

    Returns:
        dict: Configuration with default required fields and settings
    """
    return {
        "enabled": True,
        "required_fields_python": [
            "Purpose",
            "Scope",
            "Overview",
            "Dependencies",
            "Exports",
            "Interfaces",
            "Implementation",
        ],
        "enforce_atemporal": True,
        "ignore": ["test/**", "**/migrations/**", "**/__init__.py"],
    }


@pytest.fixture
def valid_python_header():
    """Python code with valid, complete header.

    Returns:
        str: Python code with all mandatory fields in atemporal language
    """
    return '''"""
Purpose: Authentication handler for user login and session management

Scope: User authentication across the application

Overview: Handles user authentication using OAuth and SAML protocols. Provides
    secure login functionality with session management and token handling. Supports
    multi-factor authentication and password reset workflows.

Dependencies: oauth2, saml, bcrypt, jwt

Exports: AuthHandler, AuthToken, AuthError

Interfaces: authenticate(), validate_token(), refresh_session()

Implementation: Uses JWT tokens with 24-hour expiration and refresh token rotation
"""

def authenticate(username, password):
    pass
'''


@pytest.fixture
def python_header_missing_purpose():
    """Python code with header missing Purpose field.

    Returns:
        str: Python code with incomplete header
    """
    return '''"""
Scope: User authentication

Overview: Handles user authentication

Dependencies: oauth2

Exports: AuthHandler

Interfaces: authenticate()

Implementation: Uses JWT tokens
"""

def authenticate():
    pass
'''


@pytest.fixture
def python_header_with_date():
    """Python code with temporal language (date).

    Returns:
        str: Python code with date in header
    """
    return '''"""
Purpose: Created 2025-01-15 for user authentication

Scope: User authentication

Overview: Handles user authentication

Dependencies: oauth2

Exports: AuthHandler

Interfaces: authenticate()

Implementation: Uses JWT tokens
"""

def authenticate():
    pass
'''


@pytest.fixture
def python_header_with_currently():
    """Python code with temporal language (currently).

    Returns:
        str: Python code with "currently" in header
    """
    return '''"""
Purpose: Authentication handler

Scope: User authentication

Overview: Currently supports OAuth and SAML authentication methods

Dependencies: oauth2, saml

Exports: AuthHandler

Interfaces: authenticate()

Implementation: Uses JWT tokens
"""

def authenticate():
    pass
'''


@pytest.fixture
def python_code_without_docstring():
    """Python code without any docstring.

    Returns:
        str: Python code with no header
    """
    return """
def authenticate(username, password):
    return True
"""


@pytest.fixture
def python_code_empty_file():
    """Empty Python file.

    Returns:
        str: Empty string
    """
    return ""
