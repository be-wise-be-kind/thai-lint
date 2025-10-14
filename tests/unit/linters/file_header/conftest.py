"""
File: tests/unit/linters/file_header/conftest.py
Purpose: Shared pytest fixtures and test helpers for file header linter tests
Exports: create_mock_context helper function
Depends: pytest, pathlib.Path, unittest.mock.Mock, src.core.base.BaseLintContext
Related: All test files in this directory

Overview:
    Provides shared pytest fixtures and helper functions for file header linter
    test suite. Includes mock context creation utilities following the pattern
    established in magic_numbers linter tests. Helper functions simplify test
    setup and reduce duplication across test files.

Usage:
    context = create_mock_context(code="...", filename="test.py")
"""

from pathlib import Path
from unittest.mock import Mock

from src.core.base import BaseLintContext


def create_mock_context(
    code: str, filename: str = "test.py", language: str = "python", metadata: dict | None = None
) -> BaseLintContext:
    """Create mock lint context for testing.

    Args:
        code: Python source code content
        filename: Name of the file (default: test.py)
        language: Programming language (default: python)
        metadata: Optional metadata dictionary

    Returns:
        Mock BaseLintContext with configured attributes
    """
    context = Mock(spec=BaseLintContext)
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = metadata or {}
    return context
