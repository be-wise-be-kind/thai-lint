"""Unit tests for CLI --project-root option functionality.

Purpose: Test --project-root CLI option for explicit project root specification
Scope: CLI project root parameter, precedence rules, and integration with linting commands

Overview: Validates the --project-root CLI option that allows users to explicitly specify
    the project root directory, overriding automatic detection. Tests verify that explicit
    project root takes precedence over inferred roots from --config paths, that config files
    are found relative to the specified root, and that ignore patterns resolve correctly.
    Ensures the option works across all linting commands (magic-numbers, file-placement, etc.)
    and handles edge cases like non-existent paths and relative vs absolute paths.

Dependencies: pytest for testing, Click CliRunner for CLI testing, tmp_path fixture

Exports: Test classes for project root functionality, precedence, edge cases, and integration

Interfaces: Tests Click CLI command invocation with --project-root flag

Implementation: Comprehensive tests covering basic functionality, priority rules, error handling,
    and integration with existing commands
"""

from click.testing import CliRunner

from src.cli import cli


class TestProjectRootOption:
    """Test --project-root CLI option basic functionality."""

    def test_explicit_project_root_overrides_auto_detection(self, tmp_path):
        """Should use explicit --project-root instead of auto-detecting from file location.

        Test Setup:
        - Create /workspace/root/ with .git and .thailint.yaml
        - Create /workspace/backend/test.py
        - Run from /workspace/backend/ but specify --project-root /workspace/root/

        Expected: Should use /workspace/root/ as project root, not /workspace/backend/
        """
        # Setup directory structure similar to Docker environment
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create root directory with project markers
        root_dir = workspace / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()
        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
""")

        # Create backend directory with file to lint (sibling to root)
        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        test_file = backend_dir / "test.py"
        test_file.write_text("x = 42  # magic number")

        # Run with explicit project root
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-root", str(root_dir), "magic-numbers", str(test_file)]
        )

        # Should find config and run linting
        # Exit code 0 = no violations, 1 = violations found, 2 = error
        assert result.exit_code in [0, 1], f"Unexpected error: {result.output}"

    def test_config_found_relative_to_explicit_project_root(self, tmp_path):
        """Should find .thailint.yaml relative to --project-root directory.

        Test Setup:
        - Create /workspace/root/.thailint.yaml
        - Create /workspace/backend/test.py
        - Don't specify --config, rely on auto-discovery from project root

        Expected: Config found at {project_root}/.thailint.yaml
        """
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()
        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 42]  # 42 is allowed
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        test_file = backend_dir / "test.py"
        test_file.write_text("x = 42  # allowed number")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-root", str(root_dir), "magic-numbers", str(test_file)]
        )

        # Should pass because 42 is in allowed_numbers
        assert result.exit_code == 0, f"Should pass with allowed number: {result.output}"

    def test_ignore_patterns_resolve_from_explicit_project_root(self, tmp_path):
        """Should resolve ignore patterns relative to --project-root directory.

        Test Setup:
        - Config has ignore pattern: "**/backend/test.py"
        - File is at /workspace/backend/test.py
        - Project root is /workspace/root/

        Expected: Ignore pattern should match relative to /workspace/root/
        """
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        # Create config with ignore pattern
        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/backend/test.py"
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        test_file = backend_dir / "test.py"
        test_file.write_text("x = 99999  # should be ignored")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-root", str(root_dir), "magic-numbers", str(test_file)]
        )

        # Should pass because file is ignored
        assert result.exit_code == 0, f"File should be ignored: {result.output}"


class TestProjectRootPrecedence:
    """Test precedence rules: --project-root > --config inference > auto-detection."""

    def test_project_root_takes_precedence_over_config_inference(self, tmp_path):
        """--project-root should override project root inferred from --config path.

        Test Setup:
        - --config points to /workspace/wrong-root/.thailint.yaml
        - --project-root points to /workspace/correct-root/
        - Config in correct-root has different settings than wrong-root

        Expected: Should use correct-root as project root, not wrong-root
        """
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Wrong root (where config is specified)
        wrong_root = workspace / "wrong-root"
        wrong_root.mkdir()
        wrong_config = wrong_root / ".thailint.yaml"
        wrong_config.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1]  # 42 NOT allowed
""")

        # Correct root (explicitly specified)
        correct_root = workspace / "correct-root"
        correct_root.mkdir()
        (correct_root / ".git").mkdir()
        correct_config = correct_root / ".thailint.yaml"
        correct_config.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 42]  # 42 IS allowed
""")

        test_file = workspace / "test.py"
        test_file.write_text("x = 42")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project-root",
                str(correct_root),
                "--config",
                str(wrong_config),
                "magic-numbers",
                str(test_file),
            ],
        )

        # With explicit project root, should find config at correct-root
        # and 42 should be allowed
        assert result.exit_code == 0, (
            f"Should use correct-root config where 42 is allowed: {result.output}"
        )

    def test_config_inference_works_when_no_project_root(self, tmp_path):
        """Should infer project root from --config path when --project-root not specified.

        Test Setup:
        - --config /workspace/root/.thailint.yaml
        - No --project-root specified
        - File to lint in /workspace/backend/

        Expected: Should infer project root as /workspace/root/
        """
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()
        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 99]
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        test_file = backend_dir / "test.py"
        test_file.write_text("x = 99")

        runner = CliRunner()
        result = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(test_file)])

        # Should infer root from config and pass
        assert result.exit_code == 0, f"Should infer project root from config path: {result.output}"

    def test_auto_detection_when_neither_provided(self, tmp_path):
        """Should fall back to auto-detection when neither --project-root nor --config specified.

        Test Setup:
        - No --project-root
        - No --config
        - File in directory with .git marker

        Expected: Should auto-detect project root via get_project_root()
        """
        # Create project structure with .git
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        config_file = project_root / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
""")

        test_file = project_root / "test.py"
        test_file.write_text("x = 1")

        runner = CliRunner()
        result = runner.invoke(cli, ["magic-numbers", str(test_file)])

        # Should auto-detect and work
        assert result.exit_code in [0, 1], f"Should auto-detect project root: {result.output}"


class TestProjectRootEdgeCases:
    """Test edge cases and error handling for --project-root option."""

    def test_nonexistent_project_root_shows_error(self, tmp_path):
        """Should show clear error when --project-root path doesn't exist.

        Expected: Exit code 2 (error), helpful error message
        """
        nonexistent = tmp_path / "does-not-exist"
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-root", str(nonexistent), "magic-numbers", str(test_file)]
        )

        assert result.exit_code == 2, "Should exit with error code 2"
        assert "does not exist" in result.output.lower() or "not found" in result.output.lower()

    def test_project_root_as_file_shows_error(self, tmp_path):
        """Should show error when --project-root is a file, not a directory.

        Expected: Exit code 2, error about needing directory
        """
        file_not_dir = tmp_path / "file.txt"
        file_not_dir.write_text("not a directory")

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-root", str(file_not_dir), "magic-numbers", str(test_file)]
        )

        assert result.exit_code == 2, "Should exit with error code 2"

    def test_relative_project_root_path(self, tmp_path):
        """Should handle relative --project-root paths correctly.

        Test Setup:
        - Create project/root/ with config
        - Use relative path "./root" or "../root"

        Expected: Should resolve relative path correctly
        """
        project = tmp_path / "project"
        project.mkdir()

        root_dir = project / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 77]
""")

        test_file = project / "test.py"
        test_file.write_text("x = 77")

        runner = CliRunner()
        # Change to project directory to test relative path
        import os
        from pathlib import Path

        original_cwd = Path.cwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                cli, ["--project-root", "./root", "magic-numbers", str(test_file)]
            )
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0, f"Should handle relative path: {result.output}"

    def test_absolute_project_root_path(self, tmp_path):
        """Should handle absolute --project-root paths correctly.

        Expected: Absolute paths work as expected
        """
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 88]
""")

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 88")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project-root",
                str(root_dir.resolve()),  # Absolute path
                "magic-numbers",
                str(test_file),
            ],
        )

        assert result.exit_code == 0, f"Should handle absolute path: {result.output}"


class TestProjectRootIntegration:
    """Test --project-root option integration with all linting commands."""

    def test_project_root_with_file_placement_command(self, tmp_path):
        """Should work with file-placement command."""
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        test_file = tmp_path / "backend" / "test.py"
        test_file.parent.mkdir()
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-root", str(root_dir), "file-placement", str(test_file)]
        )

        assert result.exit_code in [0, 1], f"Should work with file-placement: {result.output}"

    def test_project_root_with_nesting_command(self, tmp_path):
        """Should work with nesting command."""
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        test_file = tmp_path / "test.py"
        test_file.write_text("if True:\n    if True:\n        pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["--project-root", str(root_dir), "nesting", str(test_file)])

        assert result.exit_code in [0, 1], f"Should work with nesting: {result.output}"

    def test_project_root_with_srp_command(self, tmp_path):
        """Should work with srp command."""
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        test_file = tmp_path / "test.py"
        test_file.write_text("class Test:\n    def method(self): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["--project-root", str(root_dir), "srp", str(test_file)])

        assert result.exit_code in [0, 1], f"Should work with srp: {result.output}"

    def test_project_root_with_dry_command(self, tmp_path):
        """Should work with dry command."""
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\ny = 2")

        runner = CliRunner()
        result = runner.invoke(cli, ["--project-root", str(root_dir), "dry", str(test_file)])

        assert result.exit_code in [0, 1], f"Should work with dry: {result.output}"

    def test_project_root_with_magic_numbers_command(self, tmp_path):
        """Should work with magic-numbers command."""
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
""")

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-root", str(root_dir), "magic-numbers", str(test_file)]
        )

        assert result.exit_code in [0, 1], f"Should work with magic-numbers: {result.output}"
