"""Unit tests for project root detection utilities.

Purpose: Test is_project_root() and get_project_root() functions
Scope: Comprehensive testing of project root detection logic
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
