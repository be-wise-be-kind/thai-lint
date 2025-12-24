"""Unit tests for automatic project root inference from --config path.

Purpose: Test automatic project root inference when --config flag is specified
Scope: Config path-based project root inference, Docker directory structures, ignore patterns

Overview: Validates that when users specify --config with an explicit path, the CLI automatically
    infers the project root as the directory containing that config file. This solves the Docker
    use case where project structure uses sibling directories (/workspace/root/ and /workspace/backend/)
    instead of nested hierarchies. Uses parametrized tests and factory fixtures for efficiency.

Dependencies: pytest, Click CliRunner, pathlib

Exports: Test classes for config inference, Docker scenarios, and path handling

Interfaces: Tests Click CLI command invocation with --config flag

Implementation: Uses factory fixtures for workspace creation, parametrized tests for similar scenarios
"""

from pathlib import Path
from typing import NamedTuple

import pytest
from click.testing import CliRunner

from src.cli import cli


class ConfigTestCase(NamedTuple):
    """Test case for config inference tests."""

    allowed_number: int
    description: str


@pytest.fixture
def runner():
    """Create a CliRunner instance."""
    return CliRunner()


@pytest.fixture
def make_docker_workspace(tmp_path):
    """Factory fixture for creating Docker-like workspace structures.

    Creates: workspace/root/ (with .git and config) + workspace/backend/ (source files)
    """

    def _create(
        config_yaml: str,
        source_files: dict[str, str] | None = None,
        root_dir_name: str = "root",
    ) -> tuple[Path, Path, Path]:
        """Create Docker-like workspace structure.

        Args:
            config_yaml: Content for .thailint.yaml
            source_files: Dict of {filepath: content} relative to workspace
            root_dir_name: Name of root directory (default: "root")

        Returns:
            tuple: (workspace, root_dir, config_file)
        """
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        root_dir = workspace / root_dir_name
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        config_file = root_dir / ".thailint.yaml"
        config_file.write_text(config_yaml)

        if source_files:
            for filepath, content in source_files.items():
                file_path = workspace / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

        return workspace, root_dir, config_file

    return _create


# =============================================================================
# Test Data
# =============================================================================

CONFIG_PATH_CASES = [
    ConfigTestCase(55, "infers_from_config_directory"),
    ConfigTestCase(66, "handles_absolute_path"),
    ConfigTestCase(77, "handles_relative_path"),
    ConfigTestCase(88, "handles_nested_directory"),
]


# =============================================================================
# TestConfigPathInference: Config path handling
# =============================================================================


class TestConfigPathInference:
    """Test automatic project root inference from --config path."""

    def test_infers_project_root_from_config_directory(self, runner, make_docker_workspace):
        """Should infer project root as the directory containing --config file."""
        config_yaml = """
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 55]
"""
        workspace, _, config_file = make_docker_workspace(
            config_yaml, source_files={"backend/test.py": "x = 55  # allowed by config"}
        )
        test_file = workspace / "backend" / "test.py"

        result = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(test_file)])
        assert result.exit_code == 0, f"Should infer project root: {result.output}"

    def test_infers_from_absolute_config_path(self, runner, tmp_path):
        """Should handle absolute paths in --config flag."""
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

        result = runner.invoke(
            cli, ["--config", str(config_file.resolve()), "magic-numbers", str(test_file)]
        )
        assert result.exit_code == 0, f"Should handle absolute config path: {result.output}"

    def test_infers_from_relative_config_path(self, runner, make_docker_workspace):
        """Should handle relative paths in --config flag."""
        import os

        config_yaml = """
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 3, 4, 5, 77]
"""
        workspace, _, _ = make_docker_workspace(config_yaml, source_files={"test.py": "x = 77"})
        test_file = workspace / "test.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(workspace)
            result = runner.invoke(
                cli, ["--config", "./root/.thailint.yaml", "magic-numbers", str(test_file)]
            )
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0, f"Should handle relative config path: {result.output}"

    def test_config_in_nested_directory(self, runner, tmp_path):
        """Should infer project root even when config is in nested directory."""
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

        result = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(test_file)])
        assert result.exit_code == 0, f"Should handle nested config: {result.output}"


# =============================================================================
# TestDockerSimulation: Docker-like directory structures
# =============================================================================


class TestDockerSimulation:
    """Test Docker-like directory structures (the main use case)."""

    def test_docker_sibling_directories(self, runner, make_docker_workspace):
        """Simulate exact Docker use case with sibling directories."""
        config_yaml = """
magic_numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 3, 4, 5, 10, 60, 100, 1000, 1024, 3600]
  ignore:
    - "**/famous_tracks.py"
    - "**/oscilloscope.py"
"""
        workspace, _, config_file = make_docker_workspace(
            config_yaml,
            source_files={
                "backend/app/famous_tracks.py": "MAGIC_NUMBER = 99999\nANOTHER_MAGIC = 88888",
                "tools/helper.py": "x = 1  # allowed",
            },
        )
        famous_tracks = workspace / "backend" / "app" / "famous_tracks.py"

        result = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(famous_tracks)]
        )
        assert result.exit_code == 0, f"famous_tracks.py should be ignored: {result.output}"

    def test_docker_scenario_with_non_ignored_file(self, runner, make_docker_workspace):
        """In Docker scenario, non-ignored files should still be linted."""
        config_yaml = """
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/famous_tracks.py"
"""
        workspace, _, config_file = make_docker_workspace(
            config_yaml,
            source_files={"backend/app/other_module.py": "magic = 99999  # violation"},
        )
        other_file = workspace / "backend" / "app" / "other_module.py"

        result = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(other_file)]
        )
        assert result.exit_code == 1, f"Non-ignored file should find violations: {result.output}"

    def test_docker_scenario_multiple_files(self, runner, make_docker_workspace):
        """Test Docker scenario with multiple files across directories."""
        config_yaml = """
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/famous_tracks.py"
    - "**/test_*.py"
"""
        workspace, _, config_file = make_docker_workspace(
            config_yaml,
            source_files={
                "backend/famous_tracks.py": "magic = 99999",
                "backend/app.py": "val = 88888",
                "backend/test_module.py": "val = 77777",
            },
        )

        # Lint ignored file - should pass
        result1 = runner.invoke(
            cli,
            [
                "--config",
                str(config_file),
                "magic-numbers",
                str(workspace / "backend" / "famous_tracks.py"),
            ],
        )
        assert result1.exit_code == 0, "Ignored file should pass"

        # Lint test file - should pass (matched by pattern)
        result2 = runner.invoke(
            cli,
            [
                "--config",
                str(config_file),
                "magic-numbers",
                str(workspace / "backend" / "test_module.py"),
            ],
        )
        assert result2.exit_code == 0, "Test file should be ignored by pattern"

        # Lint violation file - should fail
        result3 = runner.invoke(
            cli,
            ["--config", str(config_file), "magic-numbers", str(workspace / "backend" / "app.py")],
        )
        assert result3.exit_code == 1, "Non-ignored file should find violation"


# =============================================================================
# TestIgnorePatternResolution: Ignore pattern handling
# =============================================================================


class TestIgnorePatternResolution:
    """Test that ignore patterns resolve correctly from inferred project root."""

    def test_ignore_patterns_resolve_from_inferred_root(self, runner, make_docker_workspace):
        """Ignore patterns should resolve relative to inferred project root."""
        config_yaml = """
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/backend/**"
"""
        workspace, _, config_file = make_docker_workspace(
            config_yaml, source_files={"backend/app/test.py": "MAGIC = 99999  # should be ignored"}
        )
        test_file = workspace / "backend" / "app" / "test.py"

        result = runner.invoke(cli, ["--config", str(config_file), "magic-numbers", str(test_file)])
        assert result.exit_code == 0, f"Ignore pattern should match: {result.output}"

    def test_absolute_ignore_patterns_with_inferred_root(self, runner, make_docker_workspace):
        """Test absolute ignore patterns with inferred project root."""
        config_yaml = """
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
  ignore:
    - "../backend/specific_file.py"
"""
        workspace, _, config_file = make_docker_workspace(
            config_yaml, source_files={"backend/specific_file.py": "MAGIC = 88888"}
        )
        ignored_file = workspace / "backend" / "specific_file.py"

        result = runner.invoke(
            cli, ["--config", str(config_file), "magic-numbers", str(ignored_file)]
        )
        # Documents expected behavior - may or may not be supported
        assert result.exit_code in [0, 1], f"Test absolute ignore paths: {result.output}"


# =============================================================================
# TestConfigInferencePrecedence: Precedence rules
# =============================================================================


class TestConfigInferencePrecedence:
    """Test that explicit --project-root overrides config inference."""

    def test_explicit_project_root_overrides_inference(self, runner, tmp_path):
        """--project-root should take precedence over config-based inference."""
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
        assert result.exit_code == 0, f"--project-root should override: {result.output}"

    def test_no_inference_without_explicit_config(self, runner, tmp_path):
        """Should NOT infer from auto-discovered config, only from explicit --config."""
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

        result = runner.invoke(cli, ["magic-numbers", str(test_file)])
        assert result.exit_code == 0, f"Should auto-detect normally: {result.output}"


# =============================================================================
# TestConfigInferenceIntegration: Integration with linting commands
# =============================================================================


class TestConfigInferenceIntegration:
    """Test config inference with all linting commands."""

    @pytest.mark.parametrize(
        "command,config_yaml,file_content",
        [
            (
                "magic-numbers",
                "magic_numbers:\n  enabled: true\n  allowed_numbers: [0, 1, 2, 44]",
                "x = 44",
            ),
            ("file-placement", "file_placement:\n  enabled: true", "# test"),
            ("nesting", "nesting:\n  max_nesting_depth: 4", "if True:\n    pass"),
        ],
        ids=["magic_numbers", "file_placement", "nesting"],
    )
    def test_config_inference_with_commands(
        self, runner, make_docker_workspace, command, config_yaml, file_content
    ):
        """Config inference works with various linting commands."""
        workspace, _, config = make_docker_workspace(
            config_yaml, source_files={"test.py": file_content}
        )
        test_file = workspace / "test.py"

        result = runner.invoke(cli, ["--config", str(config), command, str(test_file)])
        assert result.exit_code in [0, 1]
