"""
Purpose: Detect Python linting ignore directives in source code

Scope: noqa, type:ignore, pylint:disable, nosec pattern detection

Overview: Provides PythonIgnoreDetector class that scans Python source code for common
    linting ignore patterns. Detects bare patterns (e.g., # noqa) and rule-specific
    patterns (e.g., # noqa: PLR0912). Handles case-insensitive matching and extracts
    rule IDs from comma-separated lists. Returns list of IgnoreDirective objects with
    line/column positions for violation reporting.

Dependencies: re for pattern matching, pathlib for file paths, types module for dataclasses

Exports: PythonIgnoreDetector

Interfaces: find_ignores(code: str, file_path: Path | None) -> list[IgnoreDirective]

Implementation: Regex-based line-by-line scanning with pattern-specific rule ID extraction
"""

import re
from pathlib import Path

from src.linters.lazy_ignores.types import IgnoreDirective, IgnoreType


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
    }

    def find_ignores(self, code: str, file_path: Path | None = None) -> list[IgnoreDirective]:
        """Find all Python ignore directives in code.

        Args:
            code: Python source code to scan
            file_path: Optional path to the source file

        Returns:
            List of IgnoreDirective objects for each detected ignore pattern
        """
        directives: list[IgnoreDirective] = []
        effective_path = file_path or Path("unknown")

        for line_num, line in enumerate(code.splitlines(), start=1):
            directives.extend(self._scan_line(line, line_num, effective_path))

        return directives

    def _scan_line(self, line: str, line_num: int, file_path: Path) -> list[IgnoreDirective]:
        """Scan a single line for ignore patterns.

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
            if match:
                found.append(self._create_directive(match, ignore_type, line_num, file_path))
        return found

    def _create_directive(
        self, match: re.Match[str], ignore_type: IgnoreType, line_num: int, file_path: Path
    ) -> IgnoreDirective:
        """Create an IgnoreDirective from a regex match.

        Args:
            match: Regex match object
            ignore_type: Type of ignore pattern
            line_num: 1-indexed line number
            file_path: Path to source file

        Returns:
            IgnoreDirective for this match
        """
        return IgnoreDirective(
            ignore_type=ignore_type,
            rule_ids=tuple(self._extract_rule_ids(match)),
            line=line_num,
            column=match.start() + 1,
            raw_text=match.group(0).strip(),
            file_path=file_path,
        )

    def _extract_rule_ids(self, match: re.Match[str]) -> list[str]:
        """Extract rule IDs from regex match.

        Args:
            match: Regex match object with optional group 1 containing rule IDs

        Returns:
            List of rule ID strings, empty if no specific rules
        """
        group = match.group(1)
        if not group:
            return []

        # Split on comma and clean up whitespace
        ids = [rule_id.strip() for rule_id in group.split(",")]
        return [rule_id for rule_id in ids if rule_id]
