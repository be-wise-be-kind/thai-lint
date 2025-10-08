"""
Purpose: Pytest fixtures for DRY linter tests

Scope: Shared test utilities for creating test files, configs, and duplicate code scenarios

Overview: Provides reusable pytest fixtures to reduce code duplication in DRY linter tests.
    Includes fixtures for creating Python/TypeScript files, configuration files, duplicate code
    blocks, and common test scenarios. Enables consistent test setup and reduces boilerplate
    across 106 test cases.

Dependencies: pytest, pathlib

Exports: Fixtures for file creation, config setup, and duplicate scenarios

Interfaces: Pytest fixture protocol - functions decorated with @pytest.fixture

Implementation: Uses tmp_path fixture from pytest for isolated test file creation.
    Provides factory fixtures for flexible file/config generation.
"""

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def create_python_file(tmp_path):
    """Factory fixture to create Python files with given content.

    Returns:
        Callable that takes (name, content) and returns Path to created file
    """

    def _create(name: str, content: str) -> Path:
        """Create a Python file in tmp_path.

        Args:
            name: Filename (with or without .py extension)
            content: File content

        Returns:
            Path to created file
        """
        if not name.endswith(".py"):
            name = f"{name}.py"
        file_path = tmp_path / name
        file_path.write_text(content)
        return file_path

    return _create


@pytest.fixture
def create_typescript_file(tmp_path):
    """Factory fixture to create TypeScript files with given content.

    Returns:
        Callable that takes (name, content) and returns Path to created file
    """

    def _create(name: str, content: str, extension: str = ".ts") -> Path:
        """Create a TypeScript/JavaScript file in tmp_path.

        Args:
            name: Filename (without extension)
            content: File content
            extension: File extension (.ts or .js), defaults to .ts

        Returns:
            Path to created file
        """
        if not name.endswith((".ts", ".js")):
            name = f"{name}{extension}"
        file_path = tmp_path / name
        file_path.write_text(content)
        return file_path

    return _create


@pytest.fixture
def create_config(tmp_path):
    """Factory fixture to create .thailint.yaml config files.

    Returns:
        Callable that takes config options and returns Path to config file
    """

    def _create(
        enabled: bool = True,
        min_duplicate_lines: int = 3,
        cache_enabled: bool = False,
        **kwargs: Any,
    ) -> Path:
        """Create a .thailint.yaml config file in tmp_path.

        Args:
            enabled: Enable DRY linter
            min_duplicate_lines: Minimum lines for duplicate detection
            cache_enabled: Enable SQLite cache
            **kwargs: Additional config options

        Returns:
            Path to created config file
        """
        config_path = tmp_path / ".thailint.yaml"
        config_lines = [
            "dry:",
            f"  enabled: {str(enabled).lower()}",
            f"  min_duplicate_lines: {min_duplicate_lines}",
            f"  cache_enabled: {str(cache_enabled).lower()}",
        ]

        for key, value in kwargs.items():
            if isinstance(value, bool):
                config_lines.append(f"  {key}: {str(value).lower()}")
            elif isinstance(value, (int, float)):
                config_lines.append(f"  {key}: {value}")
            elif isinstance(value, str):
                config_lines.append(f'  {key}: "{value}"')
            elif isinstance(value, list):
                config_lines.append(f"  {key}:")
                for item in value:
                    config_lines.append(f'    - "{item}"')

        config_path.write_text("\n".join(config_lines))
        return config_path

    return _create


@pytest.fixture
def create_duplicate_files(tmp_path, create_python_file):
    """Factory fixture to create multiple files with duplicate code.

    Returns:
        Callable that creates files with specified duplicate patterns
    """

    def _create(
        duplicate_code: str, count: int = 2, prefix: str = "file", extension: str = ".py"
    ) -> list[Path]:
        """Create multiple files containing the same duplicate code.

        Args:
            duplicate_code: The code block to duplicate across files
            count: Number of files to create
            prefix: Filename prefix (e.g., 'file' creates file1.py, file2.py)
            extension: File extension

        Returns:
            List of Path objects for created files
        """
        files = []
        for i in range(1, count + 1):
            name = f"{prefix}{i}{extension}"
            file_path = tmp_path / name
            content = f"def func_{i}():\n{duplicate_code}\n"
            file_path.write_text(content)
            files.append(file_path)
        return files

    return _create


@pytest.fixture
def duplicate_code_3_lines():
    """Standard 3-line duplicate code block for testing.

    Returns:
        String containing 3-line code block
    """
    return """    for item in items:
        if item.is_valid():
            item.save()"""


@pytest.fixture
def duplicate_code_5_lines():
    """Standard 5-line duplicate code block for testing.

    Returns:
        String containing 5-line code block
    """
    return """    result = []
    for item in data:
        if item.active:
            processed = transform(item)
            result.append(processed)"""


@pytest.fixture
def duplicate_code_10_lines():
    """Standard 10-line duplicate code block for testing.

    Returns:
        String containing 10-line code block
    """
    return """    try:
        connection = establish_connection()
        data = fetch_data(connection)
        validated = validate_schema(data)
        transformed = apply_transformations(validated)
        enriched = enrich_with_metadata(transformed)
        return save_to_database(enriched)
    except Exception as error:
        log_error(error)
        raise"""


@pytest.fixture
def create_subdirectory(tmp_path):
    """Factory fixture to create subdirectories in tmp_path.

    Returns:
        Callable that takes directory path and creates it
    """

    def _create(dir_path: str) -> Path:
        """Create a subdirectory in tmp_path.

        Args:
            dir_path: Relative directory path (e.g., 'src/utils')

        Returns:
            Path to created directory
        """
        full_path = tmp_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path

    return _create


@pytest.fixture
def create_unique_files(tmp_path):
    """Factory fixture to create multiple files with unique content.

    Returns:
        Callable that creates files with unique content (no duplicates)
    """

    def _create(count: int = 10, prefix: str = "unique") -> list[Path]:
        """Create multiple files with unique content.

        Args:
            count: Number of unique files to create
            prefix: Filename prefix

        Returns:
            List of Path objects for created files
        """
        files = []
        for i in range(1, count + 1):
            file_path = tmp_path / f"{prefix}_{i}.py"
            content = f"""
def unique_function_{i}():
    value_{i} = compute_{i}()
    processed_{i} = transform_{i}(value_{i})
    return save_{i}(processed_{i})
"""
            file_path.write_text(content)
            files.append(file_path)
        return files

    return _create


@pytest.fixture
def duplicate_code_ts_3_lines():
    """Standard 3-line TypeScript duplicate code block.

    Returns:
        String containing 3-line TypeScript code block
    """
    return """    for (const item of items) {
        if (item.isValid()) {
            item.save();"""


@pytest.fixture
def duplicate_code_ts_5_lines():
    """Standard 5-line TypeScript duplicate code block.

    Returns:
        String containing 5-line TypeScript code block
    """
    return """    const result = [];
    for (const item of data) {
        if (item.active) {
            const processed = transform(item);
            result.push(processed);"""
