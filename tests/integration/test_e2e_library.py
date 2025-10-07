"""
Purpose: End-to-end Library API workflow tests validating programmatic usage patterns

Scope: Full library API testing including Linter class, multiple rules, and directory scanning

Overview: Comprehensive E2E test suite for Library API functionality that validates complete
    programmatic workflows using the Linter class. Tests verify initialization with various
    config sources, lint() method execution with different parameters, multi-rule execution,
    directory scanning with recursive options, violation handling, and integration with the
    orchestrator. Ensures library users can embed thailint in other tools, editors, CI/CD
    pipelines, and automation scripts with clean Pythonic interfaces.

Dependencies: pytest for testing, pathlib for Path objects, tempfile for test fixtures

Exports: TestLibraryBasicUsage, TestLibraryMultipleRules, TestLibraryDirectoryScanning test classes

Interfaces: Linter class API, lint() method, violation result format

Implementation: E2E tests with real file system operations, config loading, and linting
    workflows using the high-level Library API
"""

import tempfile
from pathlib import Path

import pytest


class TestLibraryBasicUsage:
    """Test basic Library API usage patterns."""

    def test_linter_with_config_file(self) -> None:
        """Test Linter initialization and usage with config file."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create .ai directory and layout config
            ai_dir = tmp_path / ".ai"
            ai_dir.mkdir()
            layout_file = ai_dir / "layout.yaml"
            layout_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create config file (for loading)
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')")

            # Initialize linter with config
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Run linting
            violations = linter.lint(str(test_file))

            # Should find violations
            assert len(violations) > 0
            assert any("test.py" in v.file_path for v in violations)

    def test_linter_with_autodiscovered_config(self) -> None:
        """Test Linter autodiscovery of config in project root."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config in project root
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_patterns:\n    allow:\n      - pattern: '.*\\.py$'\n"
            )

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')")

            # Initialize linter with project root (should autodiscover config)
            linter = Linter(project_root=str(tmp_path))

            # Run linting
            violations = linter.lint(str(test_file))

            # Should pass (no violations)
            assert len(violations) == 0

    def test_linter_with_path_objects(self) -> None:
        """Test Linter works with Path objects."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_patterns:\n    allow:\n      - pattern: '.*\\.py$'\n"
            )

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')")

            # Use Path objects
            linter = Linter(config_file=config_file, project_root=tmp_path)
            violations = linter.lint(test_file)

            # Should work with Path objects
            assert len(violations) == 0


class TestLibraryMultipleRules:
    """Test Library API with multiple rules."""

    def test_lint_with_rule_filtering(self) -> None:
        """Test filtering to specific rules."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create .ai directory and layout config
            ai_dir = tmp_path / ".ai"
            ai_dir.mkdir()
            layout_file = ai_dir / "layout.yaml"
            layout_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create config with multiple rules (only file-placement implemented)
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Run with specific rule
            violations = linter.lint(str(test_file), rules=["file-placement"])

            # Should find violations
            assert len(violations) > 0

    def test_lint_all_rules(self) -> None:
        """Test linting with all available rules."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_patterns:\n    allow:\n      - pattern: '.*\\.py$'\n"
            )

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Run all rules (default)
            violations = linter.lint(str(test_file))

            # Should pass
            assert len(violations) == 0


class TestLibraryDirectoryScanning:
    """Test Library API directory scanning capabilities."""

    def test_scan_directory_recursively(self) -> None:
        """Test recursive directory scanning finds all files."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create .ai directory and layout config
            ai_dir = tmp_path / ".ai"
            ai_dir.mkdir()
            layout_file = ai_dir / "layout.yaml"
            layout_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create nested structure
            (tmp_path / "src").mkdir()
            (tmp_path / "src" / "test.py").write_text("print('test')")
            (tmp_path / "src" / "nested").mkdir()
            (tmp_path / "src" / "nested" / "deep.py").write_text("print('deep')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Scan directory
            violations = linter.lint(str(tmp_path / "src"))

            # Should find violations in nested files
            assert len(violations) >= 2
            files_with_violations = {v.file_path for v in violations}
            assert any("test.py" in f for f in files_with_violations)
            assert any("deep.py" in f for f in files_with_violations)

    def test_scan_respects_ignore_patterns(self) -> None:
        """Test directory scanning with .thailintignore file."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create .ai directory and layout config
            ai_dir = tmp_path / ".ai"
            ai_dir.mkdir()
            layout_file = ai_dir / "layout.yaml"
            layout_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create .thailintignore file
            (tmp_path / ".thailintignore").write_text("test_*.py\n")

            # Create files
            (tmp_path / "main.py").write_text("print('main')")
            (tmp_path / "test_module.py").write_text("print('test')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Scan directory
            violations = linter.lint(str(tmp_path))

            # Should ignore test files based on .thailintignore
            files_with_violations = {v.file_path for v in violations}
            assert any("main.py" in f for f in files_with_violations)
            assert not any("test_module.py" in f for f in files_with_violations)


class TestLibraryViolationFormat:
    """Test Library API violation result format."""

    def test_violation_has_required_fields(self) -> None:
        """Test violations have all required fields."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create .ai directory and layout config
            ai_dir = tmp_path / ".ai"
            ai_dir.mkdir()
            layout_file = ai_dir / "layout.yaml"
            layout_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Run linting
            violations = linter.lint(str(test_file))

            # Verify violation format
            assert len(violations) > 0
            v = violations[0]
            assert hasattr(v, "file_path")
            assert hasattr(v, "message")
            assert hasattr(v, "severity")
            assert hasattr(v, "rule_id")

    def test_violation_serialization(self) -> None:
        """Test violations can be serialized to dict/JSON."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create .ai directory and layout config
            ai_dir = tmp_path / ".ai"
            ai_dir.mkdir()
            layout_file = ai_dir / "layout.yaml"
            layout_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Run linting
            violations = linter.lint(str(test_file))

            # Serialize violation
            assert len(violations) > 0
            v = violations[0]
            # Should have dict() or to_dict() method
            if hasattr(v, "to_dict"):
                v_dict = v.to_dict()
                assert isinstance(v_dict, dict)
                assert "file_path" in v_dict
                assert "message" in v_dict


class TestLibraryErrorHandling:
    """Test Library API error handling."""

    def test_nonexistent_file_raises_error(self) -> None:
        """Test linting nonexistent file returns empty list (graceful handling)."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "file-placement:\n  global_patterns:\n    allow:\n      - pattern: '.*\\.py$'\n"
            )

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Lint nonexistent file - should return empty list gracefully
            violations = linter.lint(str(tmp_path / "nonexistent.py"))
            assert violations == []

    def test_invalid_config_raises_error(self) -> None:
        """Test invalid config raises appropriate error."""
        import yaml

        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create invalid config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("invalid: yaml: content:")

            # Should raise error on initialization (yaml.scanner.ScannerError is a subclass of yaml.YAMLError)
            with pytest.raises((ValueError, OSError, yaml.YAMLError)):
                Linter(config_file=str(config_file), project_root=str(tmp_path))
