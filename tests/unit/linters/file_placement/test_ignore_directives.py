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

        assert all("build/" not in v.file_path for v in violations)

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
        assert all("ignored_dir" not in v.file_path for v in violations)
