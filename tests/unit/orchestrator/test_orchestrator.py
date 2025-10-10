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


class TestOrchestrator:
    """Test main Orchestrator class."""

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
