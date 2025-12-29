"""
Purpose: Shared pytest fixtures for LBYL linter tests

Scope: Fixtures for mock contexts, sample code, and configurations

Overview: Provides shared fixtures and helper functions for LBYL linter testing. Includes
    mock context creation, configuration fixtures, and sample code constants for testing
    LBYL pattern detection. Supports TDD approach for all 8 pattern types.

Dependencies: pytest, pathlib, unittest.mock, ast

Exports: Fixture functions and test data constants

Interfaces: Factory functions for test setup

Implementation: pytest fixtures with factory pattern for flexible test setup
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from src.linters.lbyl.config import LBYLConfig


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
def default_config() -> LBYLConfig:
    """Create default LBYL configuration for testing."""
    return LBYLConfig()


@pytest.fixture
def all_patterns_enabled() -> LBYLConfig:
    """Create config with all patterns enabled (including isinstance and none_check)."""
    return LBYLConfig(
        detect_isinstance=True,
        detect_none_check=True,
    )


@pytest.fixture
def mock_context():
    """Factory for creating mock lint contexts."""

    def _create(code: str, filename: str = "test.py") -> Mock:
        context = Mock()
        context.file_path = Path(filename)
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        return context

    return _create


# Test data constants - Dict Key patterns
DICT_KEY_LBYL_BASIC = """
def process_config(config: dict) -> str:
    if "api_key" in config:
        return config["api_key"]
    return ""
"""

DICT_KEY_LBYL_VARIABLE_KEY = """
def get_value(data: dict, key: str) -> str:
    if key in data:
        return data[key]
    return ""
"""

DICT_KEY_EAFP_CORRECT = """
def process_config(config: dict) -> str:
    try:
        return config["api_key"]
    except KeyError:
        return ""
"""

DICT_KEY_GET_CORRECT = """
def process_config(config: dict) -> str:
    return config.get("api_key", "")
"""

# Test data - Different dict/key (should not flag)
DICT_KEY_DIFFERENT_DICT = """
def process(config1: dict, config2: dict) -> str:
    if "key" in config1:
        return config2["key"]  # Different dict - not LBYL
    return ""
"""

DICT_KEY_DIFFERENT_KEY = """
def process(config: dict) -> str:
    if "key1" in config:
        return config["key2"]  # Different key - not LBYL
    return ""
"""

# Test data - Walrus operator (should not flag)
DICT_KEY_WALRUS = """
def process(config: dict) -> str:
    if (value := config.get("key")) is not None:
        return value
    return ""
"""
