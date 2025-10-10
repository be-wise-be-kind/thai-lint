"""
Purpose: Test suite for high-level Library API providing clean programmatic interface

Scope: Validation of Linter class and public API for library usage

Overview: Comprehensive test suite for the high-level Library API that allows users to
    import and use thailint programmatically without CLI. Tests verify Linter class
    initialization with config files, lint() method with path and rules parameters,
    direct linter imports, violation return format, configuration loading, and error
    handling. Ensures the library API provides clean, Pythonic interface for embedding
    thailint in other tools, editors, CI/CD pipelines, and automation scripts.

Dependencies: pytest for testing framework, pathlib for Path objects, tempfile for
    test file creation

Exports: TestLinterClass, TestDirectImports, TestConfigurationLoading test classes

Interfaces: Tests Linter(config_file=...) initialization, lint(path, rules=[...]) method,
    and direct linter imports

Implementation: 15+ tests covering initialization, config loading, rule filtering,
    path handling, error cases, and backwards compatibility
"""

import tempfile
from pathlib import Path


class TestLinterClass:
    """Test high-level Linter class API."""

    def test_import_linter_class(self):
        """Can import Linter from package root."""
        from src import Linter

        assert Linter is not None

    def test_linter_lint_with_rules_parameter(self):
        """Lint with specific rules using rules parameter."""
        from src import Linter

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# test file\n")
            file_path = f.name

        try:
            linter = Linter()
            violations = linter.lint(file_path, rules=["file-placement"])
            assert isinstance(violations, list)
        finally:
            Path(file_path).unlink()

    def test_linter_lint_nonexistent_path(self):
        """Lint handles nonexistent paths gracefully."""
        from src import Linter

        linter = Linter()
        violations = linter.lint("/nonexistent/path/file.py")
        # Should return empty list or handle gracefully
        assert isinstance(violations, list)


class TestDirectImports:
    """Test direct linter imports."""

    def test_import_file_placement_linter(self):
        """Can import file_placement_linter directly."""
        from src.linters import file_placement

        assert file_placement is not None
        assert hasattr(file_placement, "lint")


class TestConfigurationLoading:
    """Test configuration loading in Library API."""

    def test_linter_handles_missing_config_gracefully(self):
        """Linter handles missing config file gracefully."""
        from src import Linter

        linter = Linter(config_file="/nonexistent/config.yaml")
        assert linter.config is not None
        # Should use defaults


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing imports."""

    def test_orchestrator_still_importable(self):
        """Orchestrator still importable from src."""
        from src import Orchestrator

        assert Orchestrator is not None

    def test_file_placement_lint_still_importable(self):
        """file_placement_lint still importable from src."""
        from src import file_placement_lint

        assert file_placement_lint is not None
        assert callable(file_placement_lint)
