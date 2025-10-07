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

    def test_match_simple_allow_pattern(self, tmp_path):
        """File matches simple allow regex."""
        config = {"file-placement": {"directories": {"src/": {"allow": [r"^src/.*\.py$"]}}}}
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        # This file should be allowed
        violations = linter.lint_path(tmp_path / "src" / "main.py")
        assert len(violations) == 0

    def test_match_multiple_allow_patterns(self):
        """File can match any of multiple allow patterns."""
        config = {
            "file-placement": {
                "directories": {"src/": {"allow": [r"^src/.*\.py$", r"^src/.*\.pyi$"]}}
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("src/main.py"))
        assert linter.check_file_allowed(Path("src/types.pyi"))

    def test_reject_files_not_matching_allow(self):
        """File not matching any allow pattern is rejected."""
        config = {"file-placement": {"directories": {"src/": {"allow": [r"^src/.*\.py$"]}}}}
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("src/README.md"))
        assert len(violations) > 0
        assert "does not match allowed patterns" in violations[0].message

    def test_case_insensitive_matching(self):
        """Pattern matching is case-insensitive."""
        config = {"file-placement": {"directories": {"src/": {"allow": [r"^src/.*\.py$"]}}}}
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        # .PY should match .py pattern (case-insensitive)
        assert linter.check_file_allowed(Path("src/main.PY"))

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

    def test_file_extension_wildcards(self):
        """Support wildcard extensions."""
        config = {"file-placement": {"directories": {"src/": {"allow": [r"^src/.*\.(py|pyi)$"]}}}}
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("src/main.py"))
        assert linter.check_file_allowed(Path("src/types.pyi"))

    def test_directory_specific_allow_patterns(self):
        """Different directories have different allow patterns."""
        config = {
            "file-placement": {
                "directories": {
                    "src/": {"allow": [r"^src/.*\.py$"]},
                    "tests/": {"allow": [r"^tests/test_.*\.py$"]},
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("src/main.py"))
        assert linter.check_file_allowed(Path("tests/test_main.py"))

        violations = linter.lint_path(Path("tests/helper.py"))
        assert len(violations) > 0  # Not test_*.py

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
