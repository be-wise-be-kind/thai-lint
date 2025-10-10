"""
Purpose: Test suite for allow pattern matching in file placement linter

Scope: Pattern matching validation for allow rules including regex, wildcards, and directory-specific patterns

Overview: Validates the allow pattern matching system that determines if files are placed in correct
    locations according to configured allow patterns. Tests verify simple and complex regex matching,
    multiple pattern evaluation (file allowed if matches ANY pattern), rejection of non-matching files,
    nested directory patterns with globbing, wildcard extension matching, directory-specific rules,
    and root vs subdirectory differentiation. Ensures the linter correctly identifies files that
    match configured allow patterns and rejects files that don't match any allowed pattern.

Dependencies: pytest for testing framework, pathlib for Path objects, tmp_path fixture

Exports: TestAllowPatternMatching test class with 8 tests

Interfaces: Tests FilePlacementLinter.lint_path(Path) and check_file_allowed(Path) methods

Implementation: 8 tests covering simple patterns, multiple patterns, rejection logic, case sensitivity,
    nested directories, wildcards, directory-specific rules, and root directory handling
"""

from pathlib import Path


class TestAllowPatternMatching:
    """Test files matching allow patterns."""

    def test_nested_directory_patterns(self):
        """Support **/ for nested directories."""
        config = {
            "file-placement": {
                "global_patterns": {
                    "allow": [r".*\.py$"]  # Any .py anywhere
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("src/utils/helpers.py"))
        assert linter.check_file_allowed(Path("deep/nested/path/file.py"))

    def test_root_vs_subdirectory_allow(self):
        """Root directory has different rules than subdirectories."""
        config = {
            "file-placement": {
                "directories": {
                    "/": {"allow": [r"^[^/]+\.(md|txt)$"]},  # Only docs at root
                    "src/": {"allow": [r"^src/.*\.py$"]},
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("README.md"))
        assert linter.check_file_allowed(Path("src/main.py"))
        assert not linter.check_file_allowed(Path("random.py"))  # .py not allowed at root
