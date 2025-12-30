"""
Purpose: Detect TypeScript/JavaScript linting ignore directives in source code

Scope: @ts-ignore, @ts-nocheck, @ts-expect-error, eslint-disable pattern detection

Overview: Provides TypeScriptIgnoreDetector class that scans TypeScript and JavaScript source
    code for common linting ignore patterns. Detects TypeScript-specific patterns (@ts-ignore,
    @ts-nocheck, @ts-expect-error) and ESLint patterns (eslint-disable-next-line, eslint-disable
    block comments, eslint-disable-line). Handles both single-line (//) and block (/* */)
    comment styles. Returns list of IgnoreDirective objects with line/column positions for
    violation reporting.

Dependencies: re for pattern matching, pathlib for file paths, types module for dataclasses

Exports: TypeScriptIgnoreDetector

Interfaces: find_ignores(code: str, file_path: Path | str | None) -> list[IgnoreDirective]

Implementation: Regex-based line-by-line scanning with pattern-specific rule ID extraction
"""

import re
from pathlib import Path

from src.linters.lazy_ignores.directive_utils import create_directive, normalize_path
from src.linters.lazy_ignores.types import IgnoreDirective, IgnoreType


class TypeScriptIgnoreDetector:
    """Detects TypeScript/JavaScript linting ignore directives in source code."""

    # Regex patterns for each ignore type
    # Single-line comment patterns (//)
    SINGLE_LINE_PATTERNS: dict[IgnoreType, re.Pattern[str]] = {
        IgnoreType.TS_IGNORE: re.compile(
            r"//\s*@ts-ignore(?:\s|$)",
        ),
        IgnoreType.TS_NOCHECK: re.compile(
            r"//\s*@ts-nocheck(?:\s|$)",
        ),
        IgnoreType.TS_EXPECT_ERROR: re.compile(
            r"//\s*@ts-expect-error(?:\s|$)",
        ),
        IgnoreType.THAILINT_IGNORE: re.compile(
            r"//\s*thailint:\s*ignore(?!-)(?:\[([^\]]+)\])?",
            re.IGNORECASE,
        ),
        IgnoreType.THAILINT_IGNORE_FILE: re.compile(
            r"//\s*thailint:\s*ignore-file(?:\[([^\]]+)\])?",
            re.IGNORECASE,
        ),
    }

    # ESLint patterns (can be single-line or inline)
    ESLINT_PATTERNS: dict[str, re.Pattern[str]] = {
        "next-line": re.compile(
            r"//\s*eslint-disable-next-line(?:\s+([a-zA-Z0-9\-/,\s]+))?(?:\s|$)",
        ),
        "inline": re.compile(
            r"//\s*eslint-disable-line(?:\s+([a-zA-Z0-9\-/,\s]+))?(?:\s|$)",
        ),
        "block-start": re.compile(
            r"/\*\s*eslint-disable(?:\s+([a-zA-Z0-9\-/,\s]+))?\s*\*/",
        ),
    }

    def find_ignores(self, code: str, file_path: Path | str | None = None) -> list[IgnoreDirective]:
        """Find all TypeScript/JavaScript ignore directives in code.

        Args:
            code: TypeScript/JavaScript source code to scan
            file_path: Optional path to the source file (Path or string)

        Returns:
            List of IgnoreDirective objects for each detected ignore pattern
        """
        directives: list[IgnoreDirective] = []
        effective_path = normalize_path(file_path)

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

        # Check TypeScript-specific patterns
        found.extend(self._scan_typescript_patterns(line, line_num, file_path))

        # Check ESLint patterns
        found.extend(self._scan_eslint_patterns(line, line_num, file_path))

        return found

    def _scan_typescript_patterns(
        self, line: str, line_num: int, file_path: Path
    ) -> list[IgnoreDirective]:
        """Scan for TypeScript-specific ignore patterns.

        Args:
            line: Line of code to scan
            line_num: 1-indexed line number
            file_path: Path to the source file

        Returns:
            List of IgnoreDirective objects for TypeScript patterns
        """
        found: list[IgnoreDirective] = []
        for ignore_type, pattern in self.SINGLE_LINE_PATTERNS.items():
            match = pattern.search(line)
            if match:
                found.append(create_directive(match, ignore_type, line_num, file_path))
        return found

    def _scan_eslint_patterns(
        self, line: str, line_num: int, file_path: Path
    ) -> list[IgnoreDirective]:
        """Scan for ESLint disable patterns.

        Args:
            line: Line of code to scan
            line_num: 1-indexed line number
            file_path: Path to the source file

        Returns:
            List of IgnoreDirective objects for ESLint patterns
        """
        found: list[IgnoreDirective] = []
        for pattern in self.ESLINT_PATTERNS.values():
            match = pattern.search(line)
            if match:
                found.append(
                    create_directive(match, IgnoreType.ESLINT_DISABLE, line_num, file_path)
                )
        return found
