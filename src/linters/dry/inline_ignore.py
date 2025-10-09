"""
Purpose: Inline ignore directive parsing for DRY linter

Scope: Parses and tracks inline ignore directives in source files

Overview: Parses source code for inline ignore directives (# dry: ignore-block, # dry: ignore-next).
    Tracks line ranges that should be ignored based on directives. Used by violation_generator
    to filter violations that fall within ignored ranges. Supports both block-level ignores
    (entire block) and next-line ignores (next statement only).

Dependencies: None (standalone utility)

Exports: InlineIgnoreParser class

Interfaces: InlineIgnoreParser.parse(content) -> dict, should_ignore(file_path, line) -> bool

Implementation: Regex-based comment parsing, line range tracking
"""

import re
from pathlib import Path


class InlineIgnoreParser:
    """Parses inline ignore directives from source code."""

    def __init__(self) -> None:
        """Initialize parser with ignore ranges tracking."""
        self._ignore_ranges: dict[str, list[tuple[int, int]]] = {}

    def parse_file(self, file_path: Path, content: str) -> None:
        """Parse file for ignore directives and store ranges.

        Args:
            file_path: Path to the file
            content: File content to parse
        """
        lines = content.split("\n")
        ranges = self._extract_ignore_ranges(lines)

        if ranges:
            self._ignore_ranges[str(file_path)] = ranges

    def _extract_ignore_ranges(self, lines: list[str]) -> list[tuple[int, int]]:
        """Extract ignore ranges from lines.

        Args:
            lines: List of lines to process

        Returns:
            List of (start, end) tuples for ignore ranges
        """
        ranges = []

        for i, line in enumerate(lines, start=1):
            ignore_range = self._parse_ignore_directive(line, i, len(lines))
            if ignore_range:
                ranges.append(ignore_range)

        return ranges

    def _parse_ignore_directive(
        self, line: str, line_num: int, total_lines: int
    ) -> tuple[int, int] | None:
        """Parse a single line for ignore directives.

        Args:
            line: Line content
            line_num: Current line number
            total_lines: Total number of lines

        Returns:
            (start, end) tuple if directive found, None otherwise
        """
        # Check for ignore-block directive
        if re.search(r"#\s*dry:\s*ignore-block", line):
            start = line_num + 1
            end = min(line_num + 10, total_lines)
            return (start, end)

        # Check for ignore-next directive
        if re.search(r"#\s*dry:\s*ignore-next", line):
            return (line_num + 1, line_num + 1)

        return None

    def should_ignore(self, file_path: str, line: int, end_line: int | None = None) -> bool:
        """Check if a line or range should be ignored.

        Args:
            file_path: Path to the file
            line: Starting line number to check
            end_line: Optional ending line number (for range check)

        Returns:
            True if line/range should be ignored
        """
        ranges = self._ignore_ranges.get(str(Path(file_path)), [])
        if not ranges:
            return False

        if end_line is not None:
            return self._check_range_overlap(line, end_line, ranges)

        return self._check_single_line(line, ranges)

    def _check_range_overlap(self, line: int, end_line: int, ranges: list[tuple[int, int]]) -> bool:
        """Check if range overlaps with any ignore range.

        Args:
            line: Starting line number
            end_line: Ending line number
            ranges: List of ignore ranges

        Returns:
            True if ranges overlap
        """
        for ign_start, ign_end in ranges:
            if line <= ign_end and end_line >= ign_start:
                return True
        return False

    def _check_single_line(self, line: int, ranges: list[tuple[int, int]]) -> bool:
        """Check if single line is in any ignore range.

        Args:
            line: Line number to check
            ranges: List of ignore ranges

        Returns:
            True if line is in any range
        """
        for start, end in ranges:
            if start <= line <= end:
                return True
        return False

    def clear(self) -> None:
        """Clear all stored ignore ranges."""
        self._ignore_ranges.clear()
