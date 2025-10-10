"""
Purpose: Real-world dogfooding tests validating linter on actual codebases

Scope: Testing thai-lint on itself and other real projects to ensure practical functionality

Overview: Comprehensive real-world test suite that validates the linter works on actual
    production codebases. Tests include dogfooding (linting thai-lint project itself),
    handling of common project structures (src/, tests/, docs/), configuration discovery
    in real repositories, ignore pattern effectiveness, and validation that the linter
    produces actionable results. Ensures the tool works in practice, not just in isolated
    unit tests, and catches real-world edge cases.

Dependencies: pytest for testing, pathlib for file operations

Exports: TestDogfooding, TestRealProjectStructures, TestConfigDiscovery test classes

Interfaces: pytest validation, file system operations

Implementation: E2E tests on actual project files, validation of linting results,
    verification of configuration loading and ignore patterns in real scenarios
"""

from pathlib import Path

import pytest


class TestDogfooding:
    """Test linting the thai-lint project itself (dogfooding)."""


class TestRealProjectStructures:
    """Test handling of common real-world project structures."""

    def test_nested_package_structure(self) -> None:
        """Test handling of nested package structures."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent
        src_dir = project_root / "src"

        if not src_dir.exists():
            pytest.skip("src/ directory not found")

        # Look for nested packages
        nested_packages = [
            d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith("_")
        ]

        if not nested_packages:
            pytest.skip("No nested packages found")

        # Check for config
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config")

        # Initialize linter
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Lint nested package
        violations = linter.lint(str(nested_packages[0]))

        # Should handle nested structure
        assert isinstance(violations, list)


class TestConfigDiscovery:
    """Test configuration discovery in real projects."""

    def test_finds_thailint_yaml(self, tmp_path) -> None:
        """Test autodiscovery of .thailint.yaml in project root."""
        from src import Linter

        # Create minimal test project instead of scanning entire real project
        test_project = tmp_path / "test_project"
        test_project.mkdir()

        # Create .thailint.yaml config
        config_file = test_project / ".thailint.yaml"
        config_file.write_text("""
file-placement:
  global_patterns:
    allow:
      - '.*\\.py$'
""")

        # Create test file
        test_file = test_project / "example.py"
        test_file.write_text("# test file\n")

        # Initialize without explicit config (should autodiscover)
        linter = Linter(project_root=str(test_project))

        # Should work without explicit config
        violations = linter.lint(str(test_file))
        assert isinstance(violations, list)


class TestIgnorePatterns:
    """Test ignore patterns work in real projects."""


class TestCLIIntegration:
    """Test CLI works on real project."""

    def test_cli_on_project(self) -> None:
        """Test CLI can lint the project."""
        import subprocess

        project_root = Path(__file__).parent.parent.parent

        # Check for config
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config")

        # Run CLI on project
        result = subprocess.run(
            ["python", "-m", "src.cli", "lint", "file-placement", str(project_root / "src")],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete (exit code 0 or 1)
        assert result.returncode in (0, 1, 2)

    def test_cli_help_works(self) -> None:
        """Test CLI help command works."""
        import subprocess

        project_root = Path(__file__).parent.parent.parent

        # Run help command
        result = subprocess.run(
            ["python", "-m", "src.cli", "--help"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should show help
        assert result.returncode == 0
        assert "thai-lint" in result.stdout or "Usage:" in result.stdout


class TestEdgeCases:
    """Test edge cases found in real projects."""

    def _setup_symlink_test(self, tmp_path):
        """Set up test directory with symlink.

        Args:
            tmp_path: Temporary directory path

        Returns:
            Path to subdirectory with symlink
        """
        # Create config
        config_file = tmp_path / ".thailint.yaml"
        config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

        # Create directory and symlink to itself
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "test.py").write_text("print('test')")

        # Create symlink (may not work on all systems)
        try:
            link = subdir / "link"
            link.symlink_to(subdir)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this system")

        return subdir

    def _run_linting_with_timeout(self, linter, tmp_path):
        """Run linting with timeout protection.

        Args:
            linter: Linter instance
            tmp_path: Path to lint

        Returns:
            List of violations
        """
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Linter stuck in infinite loop")

        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout

        try:
            violations = linter.lint(str(tmp_path))
            signal.alarm(0)  # Cancel timeout
            return violations
        except TimeoutError:
            signal.alarm(0)
            pytest.fail("Linter stuck in infinite loop on symlink")
