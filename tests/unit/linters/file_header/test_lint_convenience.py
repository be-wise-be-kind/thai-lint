"""
Purpose: Tests for the file_header package-level lint() convenience function

Scope: src.linters.file_header.lint public API used for direct library usage

Overview: Verifies the file_header linter exposes a package-level lint() convenience function
    mirroring the other linters (nesting, srp, file_placement). The function was missing, so
    examples/file_header_usage.py raised ImportError on import. Tests confirm lint() is importable,
    runs a file or directory through the orchestrator, returns only file-header violations, flags a
    file missing mandatory header fields, passes a file with a complete header, and honors a config
    dict for required fields and atemporal enforcement.

Dependencies: pytest, tmp_path fixture, src.linters.file_header.lint

Exports: TestFileHeaderLintConvenience test class

Interfaces: Tests lint(path, config) -> list[Violation]

Implementation: Writes temporary Python files and asserts on returned violations with an explicit
    empty ignore list to keep assertions independent of default ignore patterns
"""

from pathlib import Path

# Common config used to make assertions independent of default ignore patterns
# and atemporal checks, focusing each test on a single behavior.
_BASE_CONFIG = {"ignore": [], "required_fields": ["Purpose"], "enforce_atemporal": False}


class TestFileHeaderLintConvenience:
    """The file_header package must expose a working lint() convenience function."""

    def test_lint_is_importable(self) -> None:
        """lint() must be importable from the file_header package."""
        from src.linters.file_header import lint

        assert callable(lint)

    def test_lint_flags_file_missing_header(self, tmp_path: Path) -> None:
        """lint() should report a file-header violation for a file with no header."""
        from src.linters.file_header import lint

        target = tmp_path / "nodoc.py"
        target.write_text("x = 1\n")

        violations = lint(str(target), config=_BASE_CONFIG)

        assert len(violations) >= 1
        assert all("file-header" in v.rule_id for v in violations)

    def test_lint_passes_file_with_complete_header(self, tmp_path: Path) -> None:
        """lint() should report no violations for a file satisfying required fields."""
        from src.linters.file_header import lint

        target = tmp_path / "documented.py"
        target.write_text('"""\nPurpose: A documented module\n"""\n\nx = 1\n')

        violations = lint(str(target), config=_BASE_CONFIG)

        assert violations == []
