"""
Purpose: Detect Python linting ignore directives in source code

Scope: noqa, type:ignore, pylint:disable, nosec pattern detection

Overview: Provides PythonIgnoreDetector class that scans Python source code for common
    linting ignore patterns. Detects bare patterns (e.g., # noqa) and rule-specific
    patterns (e.g., # noqa: PLR0912). Handles case-insensitive matching and extracts
    rule IDs from comma-separated lists. Returns list of IgnoreDirective objects with
    line/column positions for violation reporting. Skips patterns inside docstrings
    and string literals to avoid false positives.

Dependencies: re for pattern matching, pathlib for file paths, types module for dataclasses

Exports: PythonIgnoreDetector

Interfaces: find_ignores(code: str, file_path: Path | None) -> list[IgnoreDirective]

Implementation: Regex-based line-by-line scanning with docstring-aware state tracking
"""

import re
from pathlib import Path

from src.linters.lazy_ignores.directive_utils import create_directive
from src.linters.lazy_ignores.types import IgnoreDirective, IgnoreType


def _count_unescaped_triple_quotes(line: str, quote: str) -> int:
    """Count unescaped triple-quote occurrences in a line.

    Uses regex to find non-escaped triple quotes.

    Args:
        line: Line to scan
        quote: Triple-quote pattern to count (single or double)

    Returns:
        Number of unescaped triple-quote occurrences
    """
    # Pattern matches triple quotes not preceded by odd number of backslashes
    # Escape the quote for regex
    escaped_quote = re.escape(quote)
    pattern = re.compile(rf"(?<!\\){escaped_quote}")
    return len(pattern.findall(line))


def _count_unescaped_single_quotes(text: str, quote_char: str) -> int:
    """Count unescaped single quote characters in text.

    Args:
        text: Text to scan
        quote_char: The quote character (' or ")

    Returns:
        Number of unescaped quote characters
    """
    count = 0
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == quote_char:
            count += 1
    return count


def _is_pattern_in_string_literal(line: str, match_start: int) -> bool:
    """Check if a match position is inside a string literal.

    Args:
        line: The line of code
        match_start: The start position of the pattern match

    Returns:
        True if the match is inside a string literal
    """
    before_match = line[:match_start]
    single_count = _count_unescaped_single_quotes(before_match, "'")
    double_count = _count_unescaped_single_quotes(before_match, '"')
    return (single_count % 2 == 1) or (double_count % 2 == 1)


class PythonIgnoreDetector:
    """Detects Python linting ignore directives in source code."""

    # Regex patterns for each ignore type
    # Each pattern captures optional rule IDs in group 1
    PATTERNS: dict[IgnoreType, re.Pattern[str]] = {
        IgnoreType.NOQA: re.compile(
            r"#\s*noqa(?::\s*([A-Z0-9,\s]+))?(?:\s|$)",
            re.IGNORECASE,
        ),
        IgnoreType.TYPE_IGNORE: re.compile(
            r"#\s*type:\s*ignore(?:\[([^\]]+)\])?",
        ),
        IgnoreType.PYLINT_DISABLE: re.compile(
            r"#\s*pylint:\s*disable=([a-z0-9\-,\s]+)",
            re.IGNORECASE,
        ),
        IgnoreType.NOSEC: re.compile(
            r"#\s*nosec(?:\s+([A-Z0-9,\s]+))?(?:\s|$)",
            re.IGNORECASE,
        ),
        IgnoreType.THAILINT_IGNORE: re.compile(
            r"#\s*thailint:\s*ignore(?!-)(?:\[([^\]]+)\])?",
            re.IGNORECASE,
        ),
        IgnoreType.THAILINT_IGNORE_FILE: re.compile(
            r"#\s*thailint:\s*ignore-file(?:\[([^\]]+)\])?",
            re.IGNORECASE,
        ),
        IgnoreType.THAILINT_IGNORE_NEXT: re.compile(
            r"#\s*thailint:\s*ignore-next-line(?:\[([^\]]+)\])?",
            re.IGNORECASE,
        ),
        IgnoreType.THAILINT_IGNORE_BLOCK: re.compile(
            r"#\s*thailint:\s*ignore-start(?:\[([^\]]+)\])?",
            re.IGNORECASE,
        ),
    }

    def find_ignores(self, code: str, file_path: Path | None = None) -> list[IgnoreDirective]:
        """Find all Python ignore directives in code.

        Tracks docstring state across lines to avoid false positives from
        patterns mentioned in documentation.

        Args:
            code: Python source code to scan
            file_path: Optional path to the source file

        Returns:
            List of IgnoreDirective objects for each detected ignore pattern
        """
        effective_path = file_path or Path("unknown")
        scannable_lines = self._get_scannable_lines(code)
        directives: list[IgnoreDirective] = []
        for line_num, line in scannable_lines:
            directives.extend(self._scan_line(line, line_num, effective_path))
        return directives

    def _get_scannable_lines(self, code: str) -> list[tuple[int, str]]:
        """Get lines that are not inside docstrings.

        Args:
            code: Source code to analyze

        Returns:
            List of (line_number, line_text) tuples for scannable lines
        """
        in_docstring = [False, False]  # [triple_double, triple_single]
        quotes = ['"""', "'''"]
        scannable: list[tuple[int, str]] = []

        for line_num, line in enumerate(code.splitlines(), start=1):
            was_in_docstring = in_docstring[0] or in_docstring[1]
            self._update_docstring_state(line, quotes, in_docstring)
            if not was_in_docstring:
                scannable.append((line_num, line))

        return scannable

    def _update_docstring_state(self, line: str, quotes: list[str], state: list[bool]) -> None:
        """Update docstring tracking state based on quotes in line.

        Args:
            line: Line to analyze
            quotes: List of quote patterns to check
            state: Mutable list tracking in-docstring state for each quote type
        """
        for i, quote in enumerate(quotes):
            if _count_unescaped_triple_quotes(line, quote) % 2 == 1:
                state[i] = not state[i]

    def _scan_line(self, line: str, line_num: int, file_path: Path) -> list[IgnoreDirective]:
        """Scan a single line for ignore patterns.

        Skips patterns that appear inside string literals.

        Args:
            line: Line of code to scan
            line_num: 1-indexed line number
            file_path: Path to the source file

        Returns:
            List of IgnoreDirective objects found on this line
        """
        found: list[IgnoreDirective] = []
        for ignore_type, pattern in self.PATTERNS.items():
            match = pattern.search(line)
            if not match:
                continue
            if _is_pattern_in_string_literal(line, match.start()):
                continue
            found.append(create_directive(match, ignore_type, line_num, file_path))
        return found
