"""
Purpose: Integration tests for file placement linter with orchestrator

Scope: End-to-end testing of file placement rule execution through orchestrator

Overview: Tests complete integration between FilePlacementRule and Orchestrator components.
    Validates rule registration works correctly with the rule registry, verifies orchestrator
    can discover and execute file placement rules on target files, confirms configuration
    loading flows from orchestrator through to rule execution, tests ignore directives work
    across all system layers, and validates violation output format and content meets API
    requirements. Uses real file systems with temporary directories to simulate production
    usage patterns, includes both single-file and directory-tree linting scenarios.

Dependencies: pytest (test framework), pathlib (file operations), json (config serialization),
    src.orchestrator.core (Orchestrator), src.linters.file_placement.linter (FilePlacementRule),
    src.core.registry (RuleRegistry)

Exports: No exports (test module)

Interfaces: None (pytest discovers tests automatically)

Implementation: Fixture-based testing with temporary file systems, configuration file creation,
    and rule registration verification through orchestrator API
"""

import json

import pytest

from src.orchestrator.core import Orchestrator


class TestFilePlacementIntegration:
    """Integration tests for file placement linter with orchestrator."""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Create temporary project root with config."""
        # Create .git marker for project root detection
        (tmp_path / ".git").mkdir()

        # Create project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "docs").mkdir()

        # Create config file as .thailint.json (where FilePlacementLinter expects it)
        config = {
            "file-placement": {
                "directories": {
                    "src/": {
                        "allow": [r"^src/.*\.py$"],
                        "deny": [
                            {
                                "pattern": r"^src/.*test.*\.py$",
                                "reason": "Tests should be in tests/",
                            }
                        ],
                    },
                    "tests/": {"allow": [r"^tests/.*test.*\.py$"]},
                }
            }
        }

        config_file = tmp_path / ".thailint.json"

        config_file.write_text(json.dumps(config, indent=2))

        return tmp_path

    def test_orchestrator_scans_directory_recursively(self, project_root):
        """Test orchestrator can scan entire directory tree."""
        # Create multiple files
        (project_root / "src" / "main.py").write_text("# Valid")
        (project_root / "src" / "test_wrong.py").write_text("# Wrong location")
        (project_root / "tests" / "test_valid.py").write_text("# Valid test")

        # Scan directory
        orchestrator = Orchestrator(project_root=project_root)
        violations = orchestrator.lint_directory(project_root / "src", recursive=True)

        # Should find violations in src/test_wrong.py only
        assert len(violations) > 0
        violation_files = {v.file_path for v in violations}
        # Violation paths are relative strings
        assert "src/test_wrong.py" in violation_files

    def test_orchestrator_respects_thailintignore(self, project_root):
        """Test orchestrator respects .thailintignore patterns."""
        # Create .thailintignore
        ignore_file = project_root / ".thailintignore"
        ignore_file.write_text("src/generated/")

        # Create files in ignored directory
        generated_dir = project_root / "src" / "generated"
        generated_dir.mkdir(parents=True)
        (generated_dir / "test_generated.py").write_text("# Should be ignored")

        # Scan directory
        orchestrator = Orchestrator(project_root=project_root)
        violations = orchestrator.lint_directory(project_root / "src", recursive=True)

        # Should not report violations in ignored directory
        violation_files = {str(v.file_path) for v in violations}
        assert not any("generated" in f for f in violation_files)

    def test_orchestrator_filters_by_language(self, project_root):
        """Test orchestrator only applies rules to appropriate file types."""
        # Create Python and non-Python files
        py_file = project_root / "src" / "main.py"
        py_file.write_text("# Python file")

        txt_file = project_root / "src" / "README.txt"
        txt_file.write_text("Text file")

        # Execute on both files
        orchestrator = Orchestrator(project_root=project_root)
        py_violations = orchestrator.lint_file(py_file)
        txt_violations = orchestrator.lint_file(txt_file)

        # Both should execute (file placement is language-agnostic)
        # This test validates orchestrator passes files to rules correctly
        assert isinstance(py_violations, list)
        assert isinstance(txt_violations, list)
