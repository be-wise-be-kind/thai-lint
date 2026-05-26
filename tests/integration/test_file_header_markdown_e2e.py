"""
Purpose: End-to-end test that file-header validates Markdown files through the orchestrator

Scope: Regression coverage for the language-detection gap that silently skipped .md files

Overview: Exercises the full linting pipeline via the public Linter API to confirm that a
    Markdown file lacking YAML frontmatter is reported by the file-header linter. The original
    defect was that the orchestrator's language detector returned "unknown" for .md files, so
    FileHeaderRule short-circuited before reaching the registered MarkdownHeaderParser. Unit
    tests injected the language directly and therefore never caught the gap; this test routes a
    real file through detect_language so the regression cannot recur.

Dependencies: pytest, tmp_path fixture, src.api.Linter

Exports: TestMarkdownFileHeaderEndToEnd test class

Interfaces: Tests Linter.lint(path) -> list[Violation] for .md files

Implementation: Creates a frontmatter-less Markdown file in a temp project and asserts the
    file-header rule emits at least one violation for it
"""

from pathlib import Path

from src.api import Linter


class TestMarkdownFileHeaderEndToEnd:
    """Validate Markdown file-header detection through the orchestrator."""

    def test_markdown_without_frontmatter_is_flagged(self, tmp_path: Path) -> None:
        """A .md file with no frontmatter should be reported by file-header."""
        md_file = tmp_path / "unheadered.md"
        md_file.write_text("# Just a heading, no YAML frontmatter, no fields at all.\n")

        linter = Linter(project_root=str(tmp_path))
        violations = linter.lint(str(md_file), rules=["file-header.validation"])

        assert len(violations) >= 1, "file-header should flag a frontmatter-less .md file"
