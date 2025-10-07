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

    def test_linter_initialization_no_config(self):
        """Initialize Linter without config file."""
        from src import Linter

        linter = Linter()
        assert linter is not None

    def test_linter_initialization_with_config_file(self):
        """Initialize Linter with config_file parameter."""
        from src import Linter

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")
            config_path = f.name

        try:
            linter = Linter(config_file=config_path)
            assert linter is not None
            assert linter.config is not None
        finally:
            Path(config_path).unlink()

    def test_linter_initialization_with_project_root(self):
        """Initialize Linter with project_root parameter."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            linter = Linter(project_root=tmpdir)
            assert linter is not None
            assert linter.project_root == Path(tmpdir)

    def test_linter_lint_method_exists(self):
        """Linter has lint() method."""
        from src import Linter

        linter = Linter()
        assert hasattr(linter, "lint")
        assert callable(linter.lint)

    def test_linter_lint_single_file(self):
        """Lint a single file using Linter.lint()."""
        from src import Linter

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# test file\n")
            file_path = f.name

        try:
            linter = Linter()
            violations = linter.lint(file_path)
            assert isinstance(violations, list)
        finally:
            Path(file_path).unlink()

    def test_linter_lint_directory(self):
        """Lint a directory using Linter.lint()."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# test file\n")

            linter = Linter()
            violations = linter.lint(tmpdir)
            assert isinstance(violations, list)

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

    def test_linter_lint_with_path_object(self):
        """Lint accepts Path objects."""
        from src import Linter

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# test file\n")
            file_path = Path(f.name)

        try:
            linter = Linter()
            violations = linter.lint(file_path)
            assert isinstance(violations, list)
        finally:
            file_path.unlink()

    def test_linter_lint_with_string_path(self):
        """Lint accepts string paths."""
        from src import Linter

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# test file\n")
            file_path = f.name

        try:
            linter = Linter()
            violations = linter.lint(file_path)
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

    def test_linter_violation_structure(self):
        """Violations have proper structure with required attributes."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file that may trigger violations
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# test\n")

            linter = Linter()
            violations = linter.lint(tmpdir)

            # Check structure if violations exist
            if violations:
                v = violations[0]
                assert hasattr(v, "rule_id")
                assert hasattr(v, "file_path")
                assert hasattr(v, "message")
                assert hasattr(v, "severity")


class TestDirectImports:
    """Test direct linter imports."""

    def test_import_file_placement_linter(self):
        """Can import file_placement_linter directly."""
        from src.linters import file_placement

        assert file_placement is not None
        assert hasattr(file_placement, "lint")

    def test_direct_linter_lint_function(self):
        """Direct linter has lint() function."""
        from src.linters import file_placement

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# test\n")
            file_path = f.name

        try:
            violations = file_placement.lint(Path(file_path))
            assert isinstance(violations, list)
        finally:
            Path(file_path).unlink()

    def test_direct_linter_with_config(self):
        """Direct linter accepts config parameter."""
        from src.linters import file_placement

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# test\n")
            file_path = f.name

        try:
            config = {"allow": [r".*\.py$"]}
            violations = file_placement.lint(Path(file_path), config)
            assert isinstance(violations, list)
        finally:
            Path(file_path).unlink()


class TestConfigurationLoading:
    """Test configuration loading in Library API."""

    def test_linter_loads_yaml_config(self):
        """Linter loads YAML config file."""
        from src import Linter

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")
            config_path = f.name

        try:
            linter = Linter(config_file=config_path)
            assert linter.config is not None
            assert "rules" in linter.config
        finally:
            Path(config_path).unlink()

    def test_linter_loads_json_config(self):
        """Linter loads JSON config file."""
        from src import Linter

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"rules": {"file-placement": {"allow": [".*\\\\.py$"]}}}\n')
            config_path = f.name

        try:
            linter = Linter(config_file=config_path)
            assert linter.config is not None
            assert "rules" in linter.config
        finally:
            Path(config_path).unlink()

    def test_linter_handles_missing_config_gracefully(self):
        """Linter handles missing config file gracefully."""
        from src import Linter

        linter = Linter(config_file="/nonexistent/config.yaml")
        assert linter.config is not None
        # Should use defaults

    def test_linter_autodiscovers_config_in_project_root(self):
        """Linter autodiscovers .thailint.yaml in project root."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            linter = Linter(project_root=tmpdir)
            assert linter.config is not None


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
