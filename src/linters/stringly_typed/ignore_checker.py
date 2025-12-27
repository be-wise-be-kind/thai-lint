"""
Purpose: Ignore directive checking for stringly-typed linter violations

Scope: Line-level, block-level, and file-level ignore directive support

Overview: Provides ignore directive checking functionality for the stringly-typed linter.
    Wraps the centralized IgnoreDirectiveParser to filter violations based on inline comments
    like `# thailint: ignore[stringly-typed]`. Supports line-level, block-level
    (ignore-start/ignore-end), file-level (ignore-file), and next-line directives.
    Handles both Python (# comment) and TypeScript (// comment) syntax.

Dependencies: IgnoreDirectiveParser from src.linter_config.ignore, Violation type, pathlib

Exports: IgnoreChecker class

Interfaces: IgnoreChecker.filter_violations(violations) -> list[Violation]

Implementation: Uses cached IgnoreDirectiveParser singleton, reads file content on demand,
    supports both stringly-typed.* and stringly-typed specific rule matching
"""

from pathlib import Path

from src.core.types import Violation
from src.linter_config.ignore import get_ignore_parser


class IgnoreChecker:
    """Checks for ignore directives in stringly-typed linter violations.

    Wraps the centralized IgnoreDirectiveParser to filter stringly-typed
    violations based on inline ignore comments.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize with project root for ignore parser.

        Args:
            project_root: Optional project root directory. Defaults to cwd.
        """
        self._ignore_parser = get_ignore_parser(project_root)
        self._file_content_cache: dict[str, str] = {}

    def filter_violations(self, violations: list[Violation]) -> list[Violation]:
        """Filter violations based on ignore directives.

        Args:
            violations: List of violations to filter

        Returns:
            List of violations not suppressed by ignore directives
        """
        return [v for v in violations if not self._should_ignore(v)]

    def _should_ignore(self, violation: Violation) -> bool:
        """Check if a violation should be ignored.

        Args:
            violation: Violation to check

        Returns:
            True if violation should be ignored
        """
        file_content = self._get_file_content(violation.file_path)
        return self._ignore_parser.should_ignore_violation(violation, file_content)

    def _get_file_content(self, file_path: str) -> str:
        """Get file content with caching.

        Args:
            file_path: Path to file

        Returns:
            File content or empty string if unreadable
        """
        if file_path in self._file_content_cache:
            return self._file_content_cache[file_path]

        content = self._read_file_content(file_path)
        self._file_content_cache[file_path] = content
        return content

    def _read_file_content(self, file_path: str) -> str:
        """Read file content from disk.

        Args:
            file_path: Path to file

        Returns:
            File content or empty string if unreadable
        """
        try:
            path = Path(file_path)
            if path.exists():
                return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass
        return ""

    def clear_cache(self) -> None:
        """Clear file content cache."""
        self._file_content_cache.clear()
