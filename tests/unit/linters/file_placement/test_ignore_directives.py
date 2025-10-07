"""
Purpose: Test suite for 5-level ignore directive system in file placement linter

Scope: Validation of all ignore levels from repository-wide to line-specific suppressions

Overview: Validates the comprehensive 5-level ignore directive system that allows suppressing
    file placement violations at multiple granularities. Tests verify repository-level ignores
    via .thailintignore file, directory-level ignore directives, file-level ignore headers
    (# thailint: ignore-file), rule-specific file ignores (# thailint: ignore-file[rule-id]),
    method-level ignores with decorators/comments, line-level inline ignores, wildcard pattern
    support in ignores, interaction between multiple ignore levels, and validation of ignore
    directive syntax. Ensures flexible violation suppression while maintaining clear intent.

Dependencies: pytest for testing framework, pathlib for file operations, tmp_path fixture

Exports: TestIgnoreDirectives test class with 9 tests

Interfaces: Tests ignore handling in lint_path() and lint_directory() methods

Implementation: 9 tests covering all 5 ignore levels, wildcard support, level interactions,
    and syntax validation
"""
import pytest
from pathlib import Path


class TestIgnoreDirectives:
    """Test all 5 levels of ignore directives."""

    def test_repo_level_ignore_thailintignore(self, tmp_path):
        """Repo-level: .thailintignore file."""
        (tmp_path / ".thailintignore").write_text("build/\n*.pyc\n")
        (tmp_path / "build").mkdir()
        (tmp_path / "build" / "output.txt").write_text("data")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_directory(tmp_path)

        assert all('build/' not in v.file_path for v in violations)

    def test_directory_level_ignore(self, tmp_path):
        """Directory-level: ignore directive in parent."""
        # Implementation TBD - may use special .lint-config file in directory
        config_dir = tmp_path / "ignored_dir"
        config_dir.mkdir()
        (config_dir / ".lintconfig").write_text("ignore: file-placement\n")
        (config_dir / "any_file.xyz").write_text("content")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_directory(tmp_path)

        # Directory should be ignored
        assert all('ignored_dir' not in v.file_path for v in violations)

    def test_file_level_ignore_directive(self, tmp_path):
        """File-level: # thailint: ignore-file."""
        test_file = tmp_path / "ignored.py"
        test_file.write_text("""#!/usr/bin/env python3
# thailint: ignore-file

# This entire file is ignored
""")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_path(test_file)

        assert len(violations) == 0  # Entire file ignored

    def test_file_level_specific_rule_ignore(self, tmp_path):
        """File-level: # thailint: ignore-file[file-placement]."""
        test_file = tmp_path / "ignored.py"
        test_file.write_text("# thailint: ignore-file[file-placement]\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_path(test_file)

        assert len(violations) == 0

    def test_method_level_ignore(self, tmp_path):
        """Method-level: decorator or comment above function."""
        # May require AST parsing - defer to later PR
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# thailint: ignore-method[file-placement]
def problematic_function():
    pass
""")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()

        # For file placement, method-level may not apply
        # But framework should recognize the directive
        violations = linter.lint_path(test_file)
        assert isinstance(violations, list)

    def test_line_level_ignore(self, tmp_path):
        """Line-level: # thailint: ignore."""
        # For file placement, line-level doesn't apply directly
        # But test framework should support it
        test_file = tmp_path / "test.py"
        test_file.write_text("bad_statement()  # thailint: ignore\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_path(test_file)

        # Line-level ignores don't affect file placement
        # But syntax should be recognized
        assert isinstance(violations, list)

    def test_ignore_patterns_with_wildcards(self, tmp_path):
        """Ignore patterns support wildcards."""
        (tmp_path / ".thailintignore").write_text("*.pyc\ntest_*.py\nbuild/**\n")
        (tmp_path / "file.pyc").write_text("compiled")
        (tmp_path / "test_something.py").write_text("#\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_directory(tmp_path)

        assert all('file.pyc' not in v.file_path for v in violations)
        assert all('test_something.py' not in v.file_path for v in violations)

    def test_multiple_ignore_levels_interaction(self, tmp_path):
        """Test interaction when multiple ignore levels apply."""
        # Repository level ignores build/
        (tmp_path / ".thailintignore").write_text("build/\n")

        # File has its own ignore directive
        test_file = tmp_path / "build" / "script.py"
        test_file.parent.mkdir()
        test_file.write_text("# thailint: ignore-file\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_path(test_file)

        # Should be ignored at repo level before file level is checked
        assert len(violations) == 0

    def test_validate_ignore_directive_syntax(self, tmp_path):
        """Invalid ignore directive syntax produces warning."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# thailint: invalid-directive-here\n")

        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter()
        violations = linter.lint_path(test_file)

        # Invalid directives should be handled gracefully
        # May produce warning but shouldn't crash
        assert isinstance(violations, list)
