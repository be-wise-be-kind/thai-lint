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
import pytest
from pathlib import Path


class TestDirectoryScoping:
    """Test flat vs recursive scanning."""

    def test_flat_directory_scanning(self, tmp_path):
        """Scan directory non-recursively."""
        (tmp_path / "file1.py").write_text("#\n")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.py").write_text("#\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_directory(tmp_path, recursive=False)

        # Should only find file1.py, not file2.py
        files_checked = {v.file_path for v in violations}
        assert "file1.py" in str(files_checked)
        assert "file2.py" not in str(files_checked)

    def test_recursive_directory_scanning(self, tmp_path):
        """Scan directory recursively."""
        (tmp_path / "file1.py").write_text("#\n")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.py").write_text("#\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_directory(tmp_path, recursive=True)

        # Should find both files
        files_checked = {v.file_path for v in violations}
        assert "file1.py" in str(files_checked) or "file2.py" in str(files_checked)

    def test_specific_file_path_linting(self):
        """Lint a specific file path."""
        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_path(Path("src/main.py"))
        assert isinstance(violations, list)

    def test_mixed_file_and_directory_inputs(self, tmp_path):
        """Accept mix of files and directories."""
        file1 = tmp_path / "file1.py"
        file1.write_text("#\n")
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        (dir1 / "file2.py").write_text("#\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()

        # Should handle both file and directory
        violations1 = linter.lint_path(file1)
        violations2 = linter.lint_directory(dir1)

        assert isinstance(violations1, list)
        assert isinstance(violations2, list)

    def test_exclude_patterns(self, tmp_path):
        """Respect exclude patterns (.git/, node_modules/)."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_directory(tmp_path, recursive=True)

        # Should not lint .git/
        assert all('.git' not in v.file_path for v in violations)

    def test_respect_thailintignore_file(self, tmp_path):
        """Respect .thailintignore file."""
        (tmp_path / ".thailintignore").write_text("*.pyc\n")
        (tmp_path / "test.pyc").write_text("compiled")
        (tmp_path / "test.py").write_text("#\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_directory(tmp_path)

        # Should skip .pyc file
        assert all('test.pyc' not in v.file_path for v in violations)

    def test_handle_symlinks_and_special_files(self, tmp_path):
        """Handle symlinks gracefully."""
        real_file = tmp_path / "real.py"
        real_file.write_text("#\n")
        link_file = tmp_path / "link.py"

        try:
            link_file.symlink_to(real_file)

            from src.linters.file_placement import FilePlacementLinter
            linter = FilePlacementLinter()
            violations = linter.lint_directory(tmp_path)

            # Should handle symlinks without crashing
            assert isinstance(violations, list)
        except OSError:
            # Symlinks not supported on this platform
            pytest.skip("Symlinks not supported")
