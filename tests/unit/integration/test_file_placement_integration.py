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

from src.core.registry import RuleRegistry
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

        # Create config file in .artifacts (where FilePlacementLinter expects it)
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

        config_file = tmp_path / ".artifacts" / "generated-config.json"
        config_file.parent.mkdir(exist_ok=True)
        config_file.write_text(json.dumps(config, indent=2))

        return tmp_path

    def test_orchestrator_can_execute_file_placement_rule(self, project_root):
        """Test orchestrator executes file placement rule on valid file."""
        # Create a valid Python file
        test_file = project_root / "src" / "main.py"
        test_file.write_text("# Valid source file")

        # Orchestrator auto-discovers rules from src.linters
        orchestrator = Orchestrator(project_root=project_root)

        # Verify file placement rule was discovered
        rules = orchestrator.registry.list_all()
        rule_ids = [r.rule_id for r in rules]
        assert "file-placement" in rule_ids

        violations = orchestrator.lint_file(test_file)

        # Should have no violations
        assert violations == []

    def test_orchestrator_detects_misplaced_files(self, project_root):
        """Test orchestrator detects file placement violations."""
        # Create a test file in src/ (violation)
        test_file = project_root / "src" / "test_something.py"
        test_file.write_text("# This is a test file in wrong location")

        # Orchestrator auto-discovers rules
        orchestrator = Orchestrator(project_root=project_root)
        violations = orchestrator.lint_file(test_file)

        # Should have violations
        assert len(violations) > 0
        assert any("test" in v.message.lower() for v in violations)

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

    def test_rule_registration_with_auto_discovery(self, project_root):
        """Test file placement rule can be auto-discovered by registry."""
        # Create registry and discover from src.linters
        registry = RuleRegistry()
        count = registry.discover_rules("src.linters")

        # Should discover at least the file placement rule
        assert count >= 1

        # Check rule is available
        rules = registry.list_all()
        rule_ids = [r.rule_id for r in rules]

        assert "file-placement" in rule_ids

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

    def test_violation_format_from_orchestrator(self, project_root):
        """Test violations have correct format when returned by orchestrator."""
        # Create file with violation
        test_file = project_root / "src" / "test_wrong.py"
        test_file.write_text("# Wrong location")

        # Execute
        orchestrator = Orchestrator(project_root=project_root)
        violations = orchestrator.lint_file(test_file)

        # Check violation format
        assert len(violations) > 0
        v = violations[0]
        assert hasattr(v, "rule_id")
        assert hasattr(v, "message")
        assert hasattr(v, "file_path")
        assert hasattr(v, "severity")
        assert v.rule_id == "file-placement"

    def test_orchestrator_handles_nonexistent_config(self, project_root):
        """Test orchestrator handles missing config file gracefully."""
        # Create file
        test_file = project_root / "src" / "main.py"
        test_file.write_text("# Valid file")

        # Should not crash even without layout config
        orchestrator = Orchestrator(project_root=project_root)
        violations = orchestrator.lint_file(test_file)

        # Should return result (may be empty if using defaults)
        assert isinstance(violations, list)

    def test_multiple_rules_in_orchestrator(self, project_root):
        """Test orchestrator can execute multiple rules simultaneously."""
        # Create test file
        test_file = project_root / "src" / "main.py"
        test_file.write_text("# Test file")

        # Execute (orchestrator may have multiple auto-discovered rules)
        orchestrator = Orchestrator(project_root=project_root)
        violations = orchestrator.lint_file(test_file)

        # Should execute without errors
        assert isinstance(violations, list)

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
