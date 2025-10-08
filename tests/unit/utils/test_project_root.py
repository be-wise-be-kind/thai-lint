"""Unit tests for project root detection utilities.

Purpose: Test is_project_root() and get_project_root() functions
Scope: Comprehensive testing of project root detection logic
"""

from src.utils.project_root import get_project_root, is_project_root


class TestIsProjectRoot:
    """Test is_project_root() function."""

    def test_returns_true_for_directory_with_git(self, tmp_path):
        """Should return True when .git directory exists."""
        (tmp_path / ".git").mkdir()
        assert is_project_root(tmp_path) is True

    def test_returns_true_for_directory_with_pyproject(self, tmp_path):
        """Should return True when pyproject.toml file exists."""
        (tmp_path / "pyproject.toml").touch()
        assert is_project_root(tmp_path) is True

    def test_returns_true_when_both_markers_exist(self, tmp_path):
        """Should return True when both .git and pyproject.toml exist."""
        (tmp_path / ".git").mkdir()
        (tmp_path / "pyproject.toml").touch()
        assert is_project_root(tmp_path) is True

    def test_returns_false_for_directory_without_markers(self, tmp_path):
        """Should return False when no project markers exist."""
        assert is_project_root(tmp_path) is False

    def test_returns_false_for_nonexistent_path(self, tmp_path):
        """Should return False for nonexistent path."""
        nonexistent = tmp_path / "does_not_exist"
        assert is_project_root(nonexistent) is False

    def test_returns_false_for_file_path(self, tmp_path):
        """Should return False when path is a file, not a directory."""
        file_path = tmp_path / "file.txt"
        file_path.touch()
        assert is_project_root(file_path) is False


class TestGetProjectRoot:
    """Test get_project_root() function."""

    def test_finds_root_with_git_marker(self, tmp_path):
        """Should find project root when .git directory exists."""
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "src" / "nested"
        subdir.mkdir(parents=True)

        result = get_project_root(subdir)
        assert result == tmp_path

    def test_finds_root_with_pyproject_marker(self, tmp_path):
        """Should find project root when pyproject.toml exists."""
        (tmp_path / "pyproject.toml").touch()
        subdir = tmp_path / "src" / "nested"
        subdir.mkdir(parents=True)

        result = get_project_root(subdir)
        assert result == tmp_path

    def test_finds_root_from_nested_subdirectory(self, tmp_path):
        """Should walk up tree to find root from deeply nested directory."""
        (tmp_path / ".git").mkdir()
        deep_subdir = tmp_path / "a" / "b" / "c" / "d"
        deep_subdir.mkdir(parents=True)

        result = get_project_root(deep_subdir)
        assert result == tmp_path

    def test_returns_start_path_when_no_markers_found(self, tmp_path):
        """Should return start_path when no project markers found."""
        subdir = tmp_path / "src"
        subdir.mkdir()

        result = get_project_root(subdir)
        assert result == subdir.resolve()

    def test_uses_cwd_when_start_path_is_none(self, tmp_path, monkeypatch):
        """Should use current working directory when start_path is None."""
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)

        result = get_project_root(None)
        assert result == tmp_path

    def test_stops_at_first_marker_going_up(self, tmp_path):
        """Should stop at the first project root marker found when walking up."""
        # Create outer project root
        outer_root = tmp_path / "outer"
        outer_root.mkdir()
        (outer_root / ".git").mkdir()

        # Create inner project root
        inner_root = outer_root / "inner"
        inner_root.mkdir()
        (inner_root / "pyproject.toml").touch()

        # Search from inside inner project
        search_start = inner_root / "src"
        search_start.mkdir()

        result = get_project_root(search_start)
        # Should find inner root first
        assert result == inner_root

    def test_handles_file_path_as_start(self, tmp_path):
        """Should handle when start_path is a file by checking parent directories."""
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "src"
        subdir.mkdir()
        file_path = subdir / "test.py"
        file_path.touch()

        result = get_project_root(file_path)
        assert result == tmp_path

    def test_returns_resolved_absolute_path(self, tmp_path):
        """Should return resolved absolute path."""
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "src"
        subdir.mkdir()

        # Use relative path with ..
        relative_path = subdir / ".." / "src"

        result = get_project_root(relative_path)
        assert result.is_absolute()
        assert result == tmp_path
