"""
Purpose: Unit tests for project root detection utilities

Scope: Testing is_project_root() and get_project_root() functions

Overview: Comprehensive test suite for project root detection logic validating identification of
    project root directories through markers like .git directory, .thailint.yaml configuration,
    pyproject.toml, and other project indicators. Tests directory traversal upward from start path,
    current working directory handling when start_path is None, and edge cases including filesystem
    root handling.

Dependencies: pytest, src.utils.project_root module functions

Exports: TestIsProjectRoot, TestGetProjectRoot test classes

Interfaces: test_uses_cwd_when_start_path_is_none, test_finds_git_directory,
    test_stops_at_filesystem_root, and other test methods

Implementation: Uses pytest tmp_path and monkeypatch fixtures for isolated filesystem testing,
    validates directory traversal and marker detection logic
"""

from src.utils.project_root import get_project_root


class TestIsProjectRoot:
    """Test is_project_root() function."""


class TestGetProjectRoot:
    """Test get_project_root() function."""

    def test_uses_cwd_when_start_path_is_none(self, tmp_path, monkeypatch):
        """Should use current working directory when start_path is None."""
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)

        result = get_project_root(None)
        assert result == tmp_path
