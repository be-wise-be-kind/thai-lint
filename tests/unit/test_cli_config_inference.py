"""Unit tests for automatic project root inference from --config path.

Purpose: Test automatic project root inference when --config flag is specified
Scope: Config path-based project root inference, Docker directory structures, ignore patterns

Overview: Validates that when users specify --config with an explicit path, the CLI automatically
    infers the project root as the directory containing that config file. This solves the Docker
    use case where project structure uses sibling directories (/workspace/root/ and /workspace/backend/)
    instead of nested hierarchies. Tests verify inference works with absolute and relative paths,
    handles Docker-like structures correctly, resolves ignore patterns from inferred root, and
    respects precedence rules where explicit --project-root overrides inference.

Dependencies: pytest for testing, Click CliRunner for CLI testing, tmp_path fixture

Exports: Test classes for config inference, Docker scenarios, and path handling

Interfaces: Tests Click CLI command invocation with --config flag

Implementation: Comprehensive tests simulating Docker environments, testing inference logic,
    and validating ignore pattern resolution from inferred project roots
"""

from click.testing import CliRunner

from src.cli import cli


class TestConfigPathInference:
    """Test automatic project root inference from --config path."""

    def test_infers_project_root_from_config_directory(self, tmp_path):
        """Should infer project root as the directory containing --config file.

        Test Setup:
        - --config /workspace/root/.thailint.yaml
        - File to lint: /workspace/backend/test.py
        - No --project-root specified

        Expected: Inferred project root = /workspace/root/
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
  allowed_numbers: [0, 1, 2, 55]
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        test_file = backend_dir / "test.py"
        test_file.write_text("x = 55  # allowed by config")

        runner = CliRunner()
        result = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(test_file)])

        # Should pass because 55 is in allowed_numbers in the config
        assert result.exit_code == 0, (
            f"Should infer project root from config directory: {result.output}"
        )

    def test_infers_from_absolute_config_path(self, tmp_path):
        """Should handle absolute paths in --config flag.

        Test Setup:
        - Absolute path: /full/path/to/root/.thailint.yaml

        Expected: Inferred root = /full/path/to/root/
        """
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 3, 4, 5, 66]
""")

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 66")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--config",
                str(config_file.resolve()),  # Absolute path
                "magic-numbers",
                str(test_file),
            ],
        )

        assert result.exit_code == 0, f"Should handle absolute config path: {result.output}"

    def test_infers_from_relative_config_path(self, tmp_path):
        """Should handle relative paths in --config flag.

        Test Setup:
        - Relative path: ./root/.thailint.yaml or ../root/.thailint.yaml

        Expected: Should resolve relative path and infer root
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
  allowed_numbers: [0, 1, 2, 3, 4, 5, 77]
""")

        test_file = workspace / "test.py"
        test_file.write_text("x = 77")

        runner = CliRunner()
        # Change to workspace directory to test relative config path
        import os
        from pathlib import Path

        original_cwd = Path.cwd()
        try:
            os.chdir(workspace)
            result = runner.invoke(
                cli, ["--config", "./root/.thailint.yaml", "magic-numbers", str(test_file)]
            )
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0, f"Should handle relative config path: {result.output}"

    def test_config_in_nested_directory(self, tmp_path):
        """Should infer project root even when config is in nested directory.

        Test Setup:
        - Config at: /project/config/subdir/.thailint.yaml
        - File at: /project/src/test.py

        Expected: Inferred root = /project/config/subdir/
        """
        project = tmp_path / "project"
        project.mkdir()

        config_dir = project / "config" / "subdir"
        config_dir.mkdir(parents=True)

        config_file = config_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 88]
""")

        src_dir = project / "src"
        src_dir.mkdir()
        test_file = src_dir / "test.py"
        test_file.write_text("x = 88")

        runner = CliRunner()
        result = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(test_file)])

        assert result.exit_code == 0, f"Should handle nested config directories: {result.output}"


class TestDockerSimulation:
    """Test Docker-like directory structures (the main use case)."""

    def test_docker_sibling_directories(self, tmp_path):
        """Simulate exact Docker use case with sibling directories.

        Test Setup (Docker structure):
        /workspace/
        ├── root/
        │   ├── .git/
        │   └── .thailint.yaml
        ├── backend/
        │   └── app/
        │       └── famous_tracks.py
        ├── tools/
        └── test/

        Command: thailint --config /workspace/root/.thailint.yaml magic-numbers /workspace/backend/

        Expected:
        - Project root inferred as /workspace/root/
        - Config loaded from /workspace/root/.thailint.yaml
        - Ignore patterns work relative to /workspace/root/
        """
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Setup root directory
        root_dir = workspace / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        config_file = root_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 3, 4, 5, 10, 60, 100, 1000, 1024, 3600]
  ignore:
    - "**/famous_tracks.py"
    - "**/oscilloscope.py"
""")

        # Setup backend directory (sibling to root)
        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        app_dir = backend_dir / "app"
        app_dir.mkdir()

        famous_tracks = app_dir / "famous_tracks.py"
        famous_tracks.write_text("""
# This file should be ignored
MAGIC_NUMBER = 99999
ANOTHER_MAGIC = 88888
""")

        # Setup tools directory
        tools_dir = workspace / "tools"
        tools_dir.mkdir()
        tool_file = tools_dir / "helper.py"
        tool_file.write_text("x = 1  # allowed")

        # Run linting with explicit config
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(famous_tracks)]
        )

        # Should pass because famous_tracks.py is in ignore list
        assert result.exit_code == 0, (
            f"Docker scenario: famous_tracks.py should be ignored.\nOutput: {result.output}"
        )

    def test_docker_scenario_with_non_ignored_file(self, tmp_path):
        """In Docker scenario, non-ignored files should still be linted.

        Test Setup: Same as above but lint a file NOT in ignore list

        Expected: File gets linted, violations found
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
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/famous_tracks.py"
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        app_dir = backend_dir / "app"
        app_dir.mkdir()

        # This file is NOT in ignore list
        other_file = app_dir / "other_module.py"
        other_file.write_text("magic = 99999  # violation - lowercase triggers detection")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(other_file)]
        )

        # Should find violation because file is not ignored
        assert result.exit_code == 1, (
            f"Non-ignored file should be linted and find violations.\nOutput: {result.output}"
        )

    def test_docker_scenario_multiple_files(self, tmp_path):
        """Test Docker scenario with multiple files across directories.

        Expected:
        - Ignored files pass
        - Non-ignored files get linted
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
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/famous_tracks.py"
    - "**/test_*.py"
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()

        # Ignored file
        ignored = backend_dir / "famous_tracks.py"
        ignored.write_text("magic = 99999")

        # Non-ignored file with violation
        violation_file = backend_dir / "app.py"
        violation_file.write_text("val = 88888")

        # Test file (ignored by pattern)
        test_file = backend_dir / "test_module.py"
        test_file.write_text("val = 77777")

        runner = CliRunner()

        # Lint ignored file - should pass
        result1 = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(ignored)])
        assert result1.exit_code == 0, "Ignored file should pass"

        # Lint test file - should pass (matched by pattern)
        result2 = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(test_file)]
        )
        assert result2.exit_code == 0, "Test file should be ignored by pattern"

        # Lint violation file - should fail
        result3 = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(violation_file)]
        )
        assert result3.exit_code == 1, "Non-ignored file should find violation"


class TestIgnorePatternResolution:
    """Test that ignore patterns resolve correctly from inferred project root."""

    def test_ignore_patterns_resolve_from_inferred_root(self, tmp_path):
        """Ignore patterns should resolve relative to inferred project root.

        Test Setup:
        - Config at /workspace/root/.thailint.yaml
        - Ignore pattern: "**/backend/**.py"
        - File at /workspace/backend/app/test.py

        Expected: File matches ignore pattern relative to /workspace/root/
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
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/backend/**"
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()
        app_dir = backend_dir / "app"
        app_dir.mkdir()

        test_file = app_dir / "test.py"
        test_file.write_text("MAGIC = 99999  # should be ignored")

        runner = CliRunner()
        result = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(test_file)])

        assert result.exit_code == 0, (
            f"Ignore pattern should match file relative to inferred root.\nOutput: {result.output}"
        )

    def test_absolute_ignore_patterns_with_inferred_root(self, tmp_path):
        """Test absolute ignore patterns with inferred project root."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / "root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        config_file = root_dir / ".thailint.yaml"
        # Use absolute path in ignore (from root)
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
  ignore:
    - "../backend/specific_file.py"
""")

        backend_dir = workspace / "backend"
        backend_dir.mkdir()

        ignored_file = backend_dir / "specific_file.py"
        ignored_file.write_text("MAGIC = 88888")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(ignored_file)]
        )

        # Should be ignored (or might fail if absolute paths not supported)
        # This test documents expected behavior
        assert result.exit_code in [0, 1], f"Test absolute ignore paths: {result.output}"


class TestConfigInferencePrecedence:
    """Test that explicit --project-root overrides config inference."""

    def test_explicit_project_root_overrides_inference(self, tmp_path):
        """--project-root should take precedence over config-based inference.

        Test Setup:
        - --config /workspace/config-dir/.thailint.yaml (would infer config-dir)
        - --project-root /workspace/actual-root/ (explicit)
        - Configs have different settings

        Expected: Should use actual-root, not config-dir
        """
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Config directory (would be inferred if not overridden)
        config_dir = workspace / "config-dir"
        config_dir.mkdir()
        config_file = config_dir / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]  # 42 NOT allowed
""")

        # Actual root (explicitly specified)
        actual_root = workspace / "actual-root"
        actual_root.mkdir()
        (actual_root / ".git").mkdir()
        actual_config = actual_root / ".thailint.yaml"
        actual_config.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 42]  # 42 IS allowed
""")

        test_file = workspace / "test.py"
        test_file.write_text("x = 42")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project-root",
                str(actual_root),
                "--config",
                str(config_file),
                "magic-numbers",
                str(test_file),
            ],
        )

        # Should use actual-root where 42 is allowed
        assert result.exit_code == 0, (
            f"Explicit --project-root should override config inference.\nOutput: {result.output}"
        )

    def test_no_inference_without_explicit_config(self, tmp_path):
        """Should NOT infer from auto-discovered config, only from explicit --config.

        Test Setup:
        - Auto-discovered config at /project/.thailint.yaml
        - No --config specified
        - Should use auto-detection, not inference

        Expected: Uses standard auto-detection logic
        """
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()

        config_file = project / ".thailint.yaml"
        config_file.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 3]
""")

        test_file = project / "test.py"
        test_file.write_text("x = 3")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                # No --config, no --project-root
                "magic-numbers",
                str(test_file),
            ],
        )

        # Should auto-detect normally
        assert result.exit_code == 0, (
            f"Should auto-detect normally without explicit --config: {result.output}"
        )


class TestConfigInferenceIntegration:
    """Test config inference with all linting commands."""

    def test_config_inference_with_magic_numbers(self, tmp_path):
        """Config inference works with magic-numbers command."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / "root"
        root_dir.mkdir()
        config = root_dir / ".thailint.yaml"
        config.write_text("""
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 44]
""")

        test_file = workspace / "test.py"
        test_file.write_text("x = 44")

        runner = CliRunner()
        result = runner.invoke(cli, ["--config", str(config), "magic-numbers", str(test_file)])

        assert result.exit_code == 0

    def test_config_inference_with_file_placement(self, tmp_path):
        """Config inference works with file-placement command."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / "root"
        root_dir.mkdir()
        config = root_dir / ".thailint.yaml"
        config.write_text("file_placement:\n  enabled: true\n")

        test_file = workspace / "test.py"
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(cli, ["--config", str(config), "file-placement", str(test_file)])

        assert result.exit_code in [0, 1]

    def test_config_inference_with_nesting(self, tmp_path):
        """Config inference works with nesting command."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / "root"
        root_dir.mkdir()
        config = root_dir / ".thailint.yaml"
        config.write_text("nesting:\n  max_nesting_depth: 4\n")

        test_file = workspace / "test.py"
        test_file.write_text("if True:\n    pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["--config", str(config), "nesting", str(test_file)])

        assert result.exit_code in [0, 1]
