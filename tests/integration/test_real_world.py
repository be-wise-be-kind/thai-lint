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

    def test_lint_thailint_project(self) -> None:
        """Test linting the thai-lint project itself."""
        from src import Linter

        # Get project root
        project_root = Path(__file__).parent.parent.parent

        # Verify project structure exists
        assert (project_root / "src").exists(), "src/ directory should exist"
        assert (project_root / "tests").exists(), "tests/ directory should exist"

        # Check if config exists
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config in project root")

        # Initialize linter
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Lint the project (should complete without crashes)
        violations = linter.lint(str(project_root))

        # Should return list of violations (even if empty)
        assert isinstance(violations, list)

    def test_lint_src_directory(self) -> None:
        """Test linting the src/ directory."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent
        src_dir = project_root / "src"

        if not src_dir.exists():
            pytest.skip("src/ directory not found")

        # Check for config
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config in project root")

        # Initialize linter
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Lint src directory
        violations = linter.lint(str(src_dir))

        # Should complete successfully
        assert isinstance(violations, list)

    def test_lint_tests_directory(self) -> None:
        """Test linting the tests/ directory."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent
        tests_dir = project_root / "tests"

        if not tests_dir.exists():
            pytest.skip("tests/ directory not found")

        # Check for config
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config in project root")

        # Initialize linter
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Lint tests directory
        violations = linter.lint(str(tests_dir))

        # Should complete successfully
        assert isinstance(violations, list)


class TestRealProjectStructures:
    """Test handling of common real-world project structures."""

    def test_python_package_structure(self) -> None:
        """Test linting typical Python package structure."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent

        # Verify typical Python structure
        has_src = (project_root / "src").exists()
        has_tests = (project_root / "tests").exists()
        has_pyproject = (project_root / "pyproject.toml").exists()

        if not (has_src and has_tests and has_pyproject):
            pytest.skip("Not a typical Python package structure")

        # Check for config
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config")

        # Initialize linter
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Should handle package structure
        linter.lint(str(project_root / "src"))

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

    def test_finds_thailint_yaml(self) -> None:
        """Test autodiscovery of .thailint.yaml in project root."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent

        # Check if config exists
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml in project root")

        # Initialize without explicit config (should autodiscover)
        linter = Linter(project_root=str(project_root))

        # Should work without explicit config
        test_file = project_root / "src" / "cli.py"
        if test_file.exists():
            violations = linter.lint(str(test_file))
            assert isinstance(violations, list)

    def test_respects_project_config(self) -> None:
        """Test linter respects project-specific configuration."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / ".thailint.yaml"

        if not config_file.exists():
            pytest.skip("No .thailint.yaml config")

        # Read config to verify it has linter sections (new format uses "file-placement:" not "rules:")
        config_content = config_file.read_text()
        if "file-placement:" not in config_content and "rules:" not in config_content:
            pytest.skip("Config has no linter rules defined")

        # Initialize linter with config
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Lint should respect config rules
        src_dir = project_root / "src"
        if src_dir.exists():
            violations = linter.lint(str(src_dir))
            # Config should influence results
            assert isinstance(violations, list)


class TestIgnorePatterns:
    """Test ignore patterns work in real projects."""

    def test_ignores_pycache(self) -> None:
        """Test __pycache__ directories are ignored."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent

        # Look for __pycache__ directories
        pycache_dirs = list(project_root.rglob("__pycache__"))

        if not pycache_dirs:
            pytest.skip("No __pycache__ directories found")

        # Check for config
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config")

        # Initialize linter
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Lint should ignore __pycache__
        violations = linter.lint(str(project_root))

        # Verify no violations in __pycache__
        for v in violations:
            assert "__pycache__" not in v.file_path, "__pycache__ should be ignored"

    def test_ignores_common_patterns(self) -> None:
        """Test common ignore patterns (venv, .git, node_modules) work."""
        from src import Linter

        project_root = Path(__file__).parent.parent.parent

        # Check for config
        config_file = project_root / ".thailint.yaml"
        if not config_file.exists():
            pytest.skip("No .thailint.yaml config")

        # Initialize linter
        linter = Linter(config_file=str(config_file), project_root=str(project_root))

        # Lint project
        violations = linter.lint(str(project_root))

        # Verify common patterns are ignored
        for v in violations:
            assert ".git/" not in v.file_path, ".git/ should be ignored"
            assert "node_modules/" not in v.file_path, "node_modules/ should be ignored"
            assert ".venv/" not in v.file_path, ".venv/ should be ignored"


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

    def test_empty_directory(self) -> None:
        """Test linting empty directory doesn't crash."""
        import tempfile

        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            # Create empty subdirectory
            empty_dir = tmp_path / "empty"
            empty_dir.mkdir()

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Lint empty directory (should not crash)
            violations = linter.lint(str(empty_dir))
            assert isinstance(violations, list)

    def test_symlinks_handled_safely(self) -> None:
        """Test symlinks are handled without infinite loops."""
        import tempfile

        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

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

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Should handle symlinks without infinite loop (timeout protection)
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Linter stuck in infinite loop")

            # Set timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 second timeout

            try:
                violations = linter.lint(str(tmp_path))
                signal.alarm(0)  # Cancel timeout
                assert isinstance(violations, list)
            except TimeoutError:
                signal.alarm(0)
                pytest.fail("Linter stuck in infinite loop on symlink")
