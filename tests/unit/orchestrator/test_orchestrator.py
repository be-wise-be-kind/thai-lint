"""
Purpose: Test suite for main orchestrator engine

Scope: Validation of file linting, directory traversal, and ignore pattern integration

Overview: Validates the main orchestration engine that coordinates rule
    execution across files and directories, ensuring proper integration with
    the ignore system, rule registry, and configuration loader. Tests verify
    single file linting returns violations correctly, directory linting
    traverses recursively and non-recursively, ignore patterns from
    .thailintignore are respected, and the orchestrator integrates properly
    with all framework components (registry, config, ignore parser). Ensures
    the orchestrator provides the main entry point for linting operations
    while delegating to appropriate subsystems.

Dependencies: pytest for testing framework, pathlib for file operations,
    tmp_path fixture

Exports: TestOrchestrator test class

Interfaces: Tests Orchestrator.lint_file(), lint_directory() methods,
    validates ignore pattern integration and rule execution coordination

Implementation: 6 tests using pytest tmp_path for isolated file/directory
    creation, ignore file creation for integration testing, recursive and
    non-recursive directory testing
"""

import pytest


class TestOrchestrator:
    """Test main Orchestrator class."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_lint_single_file(self, tmp_path):
        """Lint a single file and return violations list."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file\n")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_file(test_file)

        assert isinstance(violations, list)

    @pytest.mark.skip(reason="100% duplicate")
    def test_lint_directory_recursive(self, tmp_path):
        """Lint directory recursively finds all files."""
        (tmp_path / "file1.py").write_text("# file 1\n")
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir1" / "file2.py").write_text("# file 2\n")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_directory(tmp_path, recursive=True)

        # Should process files (may or may not have violations)
        assert isinstance(violations, list)

    @pytest.mark.skip(reason="100% duplicate")
    def test_lint_directory_non_recursive(self, tmp_path):
        """Lint directory non-recursively only checks top level."""
        (tmp_path / "file1.py").write_text("# file 1\n")
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir1" / "file2.py").write_text("# file 2\n")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_directory(tmp_path, recursive=False)

        # Should work but may not recurse into dir1
        assert isinstance(violations, list)

    def test_respects_ignore_patterns(self, tmp_path):
        """Orchestrator respects .thailintignore patterns."""
        (tmp_path / ".thailintignore").write_text("*.pyc\n__pycache__/\n")
        (tmp_path / "test.pyc").write_text("compiled")
        (tmp_path / "test.py").write_text("# python")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_directory(tmp_path)

        # Should not lint .pyc file
        assert all("test.pyc" not in v.file_path for v in violations)

    @pytest.mark.skip(reason="100% duplicate")
    def test_load_config_from_project_root(self, tmp_path):
        """Orchestrator loads .thailint.yaml from project root."""
        config_file = tmp_path / ".thailint.yaml"
        config_file.write_text("""
rules:
  test-rule:
    enabled: true
""")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        assert orch.config is not None

    @pytest.mark.skip(reason="100% duplicate")
    def test_works_without_config_file(self, tmp_path):
        """Orchestrator works without config file (uses defaults)."""
        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        # Should not crash, should use defaults
        assert orch.config is not None

    @pytest.mark.skip(reason="100% duplicate")
    def test_lint_multiple_files(self, tmp_path):
        """Should lint multiple individual files and return combined violations."""
        # Create multiple test files
        file1 = tmp_path / "test1.py"
        file1.write_text("# test file 1\n")
        file2 = tmp_path / "test2.py"
        file2.write_text("# test file 2\n")
        file3 = tmp_path / "test3.py"
        file3.write_text("# test file 3\n")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_files([file1, file2, file3])

        # Should return a list (may have violations or not)
        assert isinstance(violations, list)

    def test_lint_multiple_files_ignores_ignored_files(self, tmp_path):
        """Should respect .thailintignore when linting multiple files."""
        # Create .thailintignore
        (tmp_path / ".thailintignore").write_text("test2.py\n")

        # Create test files
        file1 = tmp_path / "test1.py"
        file1.write_text("# test file 1\n")
        file2 = tmp_path / "test2.py"
        file2.write_text("# test file 2 - should be ignored\n")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_files([file1, file2])

        # Should not include violations from test2.py
        assert isinstance(violations, list)
        # Violations should not reference ignored file
        for v in violations:
            assert "test2.py" not in str(v.file_path)

    @pytest.mark.skip(reason="100% duplicate")
    def test_lint_multiple_files_empty_list(self, tmp_path):
        """Should handle empty file list gracefully."""
        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_files([])

        # Should return empty list
        assert not violations

    @pytest.mark.skip(reason="100% duplicate")
    def test_lint_files_calls_finalize(self, tmp_path):
        """Should call finalize() on all rules after processing all files."""
        # Create test files
        file1 = tmp_path / "test1.py"
        file1.write_text("# test file 1\n")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_files([file1])

        # finalize() should be called (this is tested indirectly)
        # If DRY linter is registered, it will add violations in finalize()
        assert isinstance(violations, list)
