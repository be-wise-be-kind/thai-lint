"""
Purpose: Test suite for directory scanning and scoping in file placement linter

Scope: Directory traversal validation for flat vs recursive scanning and ignore pattern handling

Overview: Validates the directory scanning system that determines which files to check based on
    scanning mode and exclusion patterns. Tests verify flat (non-recursive) scanning that only
    checks immediate children, recursive scanning that traverses all subdirectories, specific
    file path linting, mixed file/directory inputs, standard exclusions (.git/, node_modules/),
    .thailintignore file respect, and symlink/special file handling. Ensures the linter correctly
    scopes its file discovery based on user intent and standard exclusion patterns.

Dependencies: pytest for testing framework, pathlib for file operations, tmp_path fixture

Exports: TestDirectoryScoping test class with 7 tests

Interfaces: Tests lint_directory(path, recursive=bool) and lint_path(path) methods

Implementation: 7 tests covering flat scanning, recursive scanning, file-specific linting,
    mixed inputs, standard excludes, .thailintignore, and special file handling
"""


class TestDirectoryScoping:
    """Test flat vs recursive scanning."""
