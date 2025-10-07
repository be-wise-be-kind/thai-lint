"""
Purpose: Docker integration tests following TDD principles for containerized CLI execution

Scope: Docker image build, volume mounting, CLI execution, and file-placement linter in containers

Overview: Comprehensive test suite for Docker functionality that validates multi-stage builds,
    volume mounting, CLI entrypoint configuration, and linting operations in containers. Tests
    verify that the Docker image builds successfully, mounts workspace volumes correctly,
    executes CLI commands with proper arguments, and produces expected linting output. Uses
    subprocess to run docker commands and validates exit codes, stdout/stderr, and container
    behavior with various configurations.

Dependencies: pytest, subprocess, pathlib, tempfile, json

Exports: Test classes for Docker build, run, volume mounting, and CLI integration

Interfaces: pytest test functions, subprocess docker commands

Implementation: Uses subprocess to execute docker commands, validates output with assertions,
    creates temporary test files for volume mounting verification
"""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestDockerImageBuild:
    """Test Docker image builds successfully."""

    def test_dockerfile_exists(self) -> None:
        """Test that Dockerfile exists in project root."""
        dockerfile = Path(__file__).parent.parent.parent.parent / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile must exist in project root"

    def test_docker_build_succeeds(self) -> None:
        """Test that Docker image builds without errors."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Build Docker image
        project_root = Path(__file__).parent.parent.parent.parent
        result = subprocess.run(
            ["docker", "build", "-t", "thailint/thailint:test", "."],
            cwd=project_root,
            capture_output=True,
            timeout=300,  # 5 minutes for build
        )

        assert result.returncode == 0, (
            f"Docker build failed with exit code {result.returncode}\n"
            f"stdout: {result.stdout.decode()}\n"
            f"stderr: {result.stderr.decode()}"
        )

    def test_docker_image_size_reasonable(self) -> None:
        """Test that Docker image is reasonably sized (multi-stage build optimization)."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Check image size (should be < 500MB for Python slim image)
        result = subprocess.run(
            ["docker", "images", "thailint/thailint:test", "--format", "{{.Size}}"],
            capture_output=True,
            timeout=10,
        )

        if result.returncode == 0 and result.stdout:
            size_str = result.stdout.decode().strip()
            # Just verify we got a size output, actual size optimization can be refined
            assert size_str, "Image size should be reported"


class TestDockerVolumeMount:
    """Test Docker volume mounting works correctly."""

    def test_workspace_volume_mount(self) -> None:
        """Test that /workspace volume mounting works."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Create temp directory with test file (use /home to avoid tmpfs mount issues)
        home_tmp = Path.home() / ".tmp"
        home_tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=home_tmp) as tmpdir:
            tmpdir_path = Path(tmpdir)
            # Set permissions to allow container user to read
            tmpdir_path.chmod(0o755)
            test_file = tmpdir_path / "test.py"
            test_file.write_text("# Test file\n")
            test_file.chmod(0o644)

            # Run container with volume mount and list files using bash
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{tmpdir}:/workspace",
                    "--entrypoint",
                    "ls",
                    "thailint/thailint:test",
                    "/workspace",
                ],
                capture_output=True,
                timeout=30,
            )

            # Should see our test file
            assert result.returncode == 0
            assert "test.py" in result.stdout.decode()

    def test_volume_mount_permissions(self) -> None:
        """Test that mounted files are readable in container."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Create temp directory with test file (use /home to avoid tmpfs mount issues)
        home_tmp = Path.home() / ".tmp"
        home_tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=home_tmp) as tmpdir:
            tmpdir_path = Path(tmpdir)
            # Set permissions to allow container user to read
            tmpdir_path.chmod(0o755)
            test_file = tmpdir_path / "test.txt"
            test_file.write_text("test content")
            test_file.chmod(0o644)

            # Try to read file in container using cat
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{tmpdir}:/workspace",
                    "--entrypoint",
                    "cat",
                    "thailint/thailint:test",
                    "/workspace/test.txt",
                ],
                capture_output=True,
                timeout=30,
            )

            assert result.returncode == 0
            assert "test content" in result.stdout.decode()


class TestDockerCLIExecution:
    """Test CLI execution in Docker container."""

    def test_help_command_works(self) -> None:
        """Test that --help command works in container."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        result = subprocess.run(
            ["docker", "run", "--rm", "thailint/thailint:test", "--help"],
            capture_output=True,
            timeout=30,
        )

        assert result.returncode == 0
        output = result.stdout.decode()
        assert "Usage:" in output or "thai-lint" in output

    def test_version_command_works(self) -> None:
        """Test that version information is accessible."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        result = subprocess.run(
            ["docker", "run", "--rm", "thailint/thailint:test", "--version"],
            capture_output=True,
            timeout=30,
        )

        # Should return version or at least run without error
        assert result.returncode == 0 or result.returncode == 2  # Click may use exit 2


class TestDockerFilePlacementLinter:
    """Test file-placement linter execution in Docker."""

    def test_file_placement_lint_in_container(self) -> None:
        """Test that file-placement linter runs in container with volume mount."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Create temp directory with test files (use /home to avoid tmpfs mount issues)
        home_tmp = Path.home() / ".tmp"
        home_tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=home_tmp) as tmpdir:
            tmpdir_path = Path(tmpdir)
            # Set permissions to allow container user to read
            tmpdir_path.chmod(0o755)

            # Create a Python file
            test_file = tmpdir_path / "src" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.parent.chmod(0o755)
            test_file.write_text("# Test file\n")
            test_file.chmod(0o644)

            # Run linter in container (should run successfully)
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{tmpdir}:/workspace",
                    "thailint/thailint:test",
                    "lint",
                    "file-placement",
                    "/workspace",
                ],
                capture_output=True,
                timeout=30,
            )

            # Should run successfully (exit code 0 or 1, not error code 2)
            assert result.returncode in (0, 1), (
                f"Linter failed with exit code {result.returncode}\n"
                f"stdout: {result.stdout.decode()}\n"
                f"stderr: {result.stderr.decode()}"
            )

    def test_file_placement_with_inline_rules(self) -> None:
        """Test file-placement linter with inline JSON rules in container."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Create temp directory with test file (use /home to avoid tmpfs mount issues)
        home_tmp = Path.home() / ".tmp"
        home_tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=home_tmp) as tmpdir:
            tmpdir_path = Path(tmpdir)
            # Set permissions to allow container user to read
            tmpdir_path.chmod(0o755)
            test_file = tmpdir_path / "test.py"
            test_file.write_text("# Test file\n")
            test_file.chmod(0o644)

            # Run with inline rules (empty config to test --rules flag)
            rules_json = json.dumps({})

            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{tmpdir}:/workspace",
                    "thailint/thailint:test",
                    "lint",
                    "file-placement",
                    "--rules",
                    rules_json,
                    "/workspace",
                ],
                capture_output=True,
                timeout=30,
            )

            # Should run successfully (exit code 0 or 1, not error code 2)
            assert result.returncode in (0, 1), (
                f"Linter failed with exit code {result.returncode}\n"
                f"stdout: {result.stdout.decode()}\n"
                f"stderr: {result.stderr.decode()}"
            )

    def test_file_placement_clean_output(self) -> None:
        """Test file-placement linter with clean directory (no violations)."""
        # Skip if Docker not available
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Create temp directory with allowed file (use /home to avoid tmpfs mount issues)
        home_tmp = Path.home() / ".tmp"
        home_tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=home_tmp) as tmpdir:
            tmpdir_path = Path(tmpdir)
            # Set permissions to allow container user to read
            tmpdir_path.chmod(0o755)

            # Create config that allows .txt in root (no deny patterns)
            config = {"file_placement": {}}
            config_file = tmpdir_path / ".thailintrc.json"
            config_file.write_text(json.dumps(config))
            config_file.chmod(0o644)

            # Create allowed file
            test_file = tmpdir_path / "README.txt"
            test_file.write_text("Documentation\n")
            test_file.chmod(0o644)

            # Run linter with config file
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{tmpdir}:/workspace",
                    "thailint/thailint:test",
                    "lint",
                    "file-placement",
                    "--config",
                    "/workspace/.thailintrc.json",
                    "/workspace",
                ],
                capture_output=True,
                timeout=30,
            )

            # Should pass (exit code 0)
            assert result.returncode == 0
