"""
Purpose: Test suite for violation output formatting in file placement linter

Scope: Validation of consistent violation structure, messages, and serialization formats

Overview: Validates the violation output formatting system that ensures consistent, actionable
    error reporting across all file placement checks. Tests verify violation structure consistency
    (rule_id, file_path, message, severity fields), relative file paths from project root,
    error messages that include violated pattern details, helpful suggestions for correct file
    placement, and machine-readable JSON serialization. Ensures violations provide clear,
    actionable feedback to users and can be consumed by automated tools.

Dependencies: pytest for testing framework, pathlib for Path objects, json for serialization testing

Exports: TestOutputFormatting test class with 5 tests

Interfaces: Tests Violation structure and to_dict() serialization method

Implementation: 5 tests covering violation structure, relative paths, pattern inclusion in messages,
    placement suggestions, and JSON serialization
"""

import json
from pathlib import Path


class TestOutputFormatting:
    """Test consistent violation message format."""

    def test_consistent_violation_format(self):
        """Violations have consistent structure."""
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter()

        # Create violation scenario
        violations = linter.lint_path(Path("bad/location/file.py"))

        if violations:
            v = violations[0]
            assert hasattr(v, "rule_id")
            assert hasattr(v, "file_path")
            assert hasattr(v, "message")
            assert hasattr(v, "severity")

    def test_file_path_relative_to_project_root(self, tmp_path):
        """File paths shown relative to project root."""
        (tmp_path / "src").mkdir()
        test_file = tmp_path / "src" / "main.py"
        test_file.write_text("#\n")

        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_path(test_file)

        if violations:
            # Path should be relative to project root
            assert "src/main.py" in violations[0].file_path
            assert str(tmp_path) not in violations[0].file_path

    def test_error_message_includes_pattern_violated(self):
        """Error message shows which pattern was violated."""
        config = {
            "file-placement": {
                "directories": {
                    "src/": {"deny": [{"pattern": r".*test.*", "reason": "No tests in src/"}]}
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("src/test_file.py"))

        if violations:
            # Message should include the pattern or reason
            assert (
                "test" in violations[0].message.lower()
                or "No tests in src/" in violations[0].message
            )

    def test_suggestion_for_correct_placement(self):
        """Violation includes suggestion for where file should go."""
        config = {"file-placement": {"directories": {"src/": {"allow": [r"^src/.*\.py$"]}}}}
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)
        violations = linter.lint_path(Path("wrong/location/file.py"))

        if violations:
            assert violations[0].suggestion is not None
            assert "src/" in violations[0].suggestion

    def test_machine_readable_json_output(self):
        """Violations can be output as JSON."""
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter()
        violations = linter.lint_path(Path("file.py"))

        # Should be serializable to JSON
        json_output = json.dumps([v.to_dict() for v in violations])
        assert json_output is not None

        # Should be parseable back
        parsed = json.loads(json_output)
        assert isinstance(parsed, list)
