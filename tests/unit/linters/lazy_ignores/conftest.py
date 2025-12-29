"""
Purpose: Shared pytest fixtures for lazy-ignores linter tests

Scope: Fixtures for mock contexts, sample code, and configurations

Overview: Provides shared fixtures and helper functions for lazy-ignores linter testing.
    Includes mock context creation, temporary file fixtures, and standard test data
    constants. Supports testing of Python, TypeScript, and thai-lint ignore patterns.

Dependencies: pytest, pathlib, tempfile, unittest.mock

Exports: Fixture functions and test data constants

Interfaces: Factory functions for test setup

Implementation: pytest fixtures with factory pattern for flexible test setup
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from src.linters.lazy_ignores.config import LazyIgnoresConfig


def create_mock_context(
    code: str,
    filename: str = "test.py",
    language: str = "python",
    metadata: dict[str, Any] | None = None,
) -> Mock:
    """Create mock lint context for testing."""
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = metadata or {}
    return context


@pytest.fixture
def temp_dir():
    """Create isolated temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def default_config() -> LazyIgnoresConfig:
    """Create default lazy-ignores configuration for testing."""
    return LazyIgnoresConfig()


@pytest.fixture
def mock_context(temp_dir: Path):
    """Factory for creating mock lint contexts."""

    def _create(code: str, filename: str = "test.py") -> Mock:
        context = Mock()
        context.file_path = temp_dir / filename
        context.file_content = code
        context.language = "python" if filename.endswith(".py") else "typescript"
        context.metadata = {}
        return context

    return _create


# Test data constants
PYTHON_WITH_NOQA = '''"""
Purpose: Test module
Overview: Module for testing
"""

x = 1  # noqa
'''

PYTHON_WITH_NOQA_RULE = '''"""
Purpose: Test module
Overview: Module for testing
"""

def complex_func():  # noqa: PLR0912
    pass
'''

PYTHON_WITH_TYPE_IGNORE = '''"""
Purpose: Test module
Overview: Module for testing
"""

x: int = "string"  # type: ignore
'''

PYTHON_WITH_PYLINT_DISABLE = '''"""
Purpose: Test module
Overview: Module for testing
"""

obj.method()  # pylint: disable=no-member
'''

PYTHON_WITH_NOSEC = '''"""
Purpose: Test module
Overview: Module for testing
"""

subprocess.run(cmd, shell=True)  # nosec B602
'''

PYTHON_WITH_HEADER_SUPPRESSION = '''"""
Purpose: Test module
Overview: Module for testing

Suppressions:
    PLR0912: Complex function - refactoring pending
"""

def complex_func():  # noqa: PLR0912
    pass
'''

PYTHON_WITH_ORPHANED_SUPPRESSION = '''"""
Purpose: Test module
Overview: Module for testing

Suppressions:
    PLR0912: This is unused
"""

def simple_func():
    return 1
'''
