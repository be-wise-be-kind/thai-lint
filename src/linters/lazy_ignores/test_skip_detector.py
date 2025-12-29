"""
Purpose: Detect test skip patterns without proper justification in source code

Scope: pytest.mark.skip, pytest.skip(), it.skip(), describe.skip(), test.skip() pattern detection

Overview: Provides TestSkipDetector class that scans Python and JavaScript/TypeScript source
    code for test skip patterns that lack proper justification. For Python, detects bare
    @pytest.mark.skip and pytest.skip() without reason arguments. For JavaScript/TypeScript,
    detects it.skip(), describe.skip(), and test.skip() patterns. Returns list of
    IgnoreDirective objects with line/column positions for violation reporting.

Dependencies: re for pattern matching, pathlib for file paths, types module for dataclasses

Exports: TestSkipDetector

Interfaces: find_skips(code: str, file_path: Path | str | None, language: str) -> list[IgnoreDirective]

Implementation: Regex-based line-by-line scanning with language-specific pattern detection
"""

import re
from collections.abc import Callable
from pathlib import Path

from src.core.constants import Language
from src.linters.lazy_ignores.directive_utils import (
    create_directive_no_rules,
    normalize_path,
)
from src.linters.lazy_ignores.types import IgnoreDirective, IgnoreType


def _is_comment_line(line: str) -> bool:
    """Check if a line is a Python comment.

    Args:
        line: Line of code to check

    Returns:
        True if the line is a comment (starts with # after whitespace)
    """
    return line.strip().startswith("#")


def _scan_empty(_line: str, _line_num: int, _file_path: Path) -> list[IgnoreDirective]:
    """No-op scanner for unsupported languages.

    Args:
        _line: Unused - required for scanner interface
        _line_num: Unused - required for scanner interface
        _file_path: Unused - required for scanner interface

    Returns:
        Empty list
    """
    return []


def _count_unescaped_triple_quotes(line: str, quote: str) -> int:
    """Count unescaped triple-quote occurrences in a line.

    Uses regex to find non-escaped triple quotes.

    Args:
        line: Line to scan
        quote: Triple-quote pattern to count (single or double)

    Returns:
        Number of unescaped triple-quote occurrences
    """
    escaped_quote = re.escape(quote)
    pattern = re.compile(rf"(?<!\\){escaped_quote}")
    return len(pattern.findall(line))


def _update_docstring_state(line: str, quotes: list[str], state: list[bool]) -> None:
    """Update docstring tracking state based on quotes in line.

    Args:
        line: Line to analyze
        quotes: List of quote patterns to check
        state: Mutable list tracking in-docstring state for each quote type
    """
    for i, quote in enumerate(quotes):
        if _count_unescaped_triple_quotes(line, quote) % 2 == 1:
            state[i] = not state[i]


def _get_python_scannable_lines(code: str) -> list[tuple[int, str]]:
    """Get Python lines that are not inside docstrings.

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
        _update_docstring_state(line, quotes, in_docstring)
        if not was_in_docstring:
            scannable.append((line_num, line))

    return scannable


class TestSkipDetector:
    """Detects test skip patterns without proper justification."""

    # Python patterns - violations are skips WITHOUT a reason argument
    # These patterns match skips that should be flagged
    # Must appear at start of line (after optional whitespace), not in comments
    PYTHON_VIOLATION_PATTERNS: dict[IgnoreType, re.Pattern[str]] = {
        # Matches @pytest.mark.skip or @pytest.mark.skip() without reason=
        # Requires @ at start of line (after whitespace) to avoid matching in comments
        IgnoreType.PYTEST_SKIP: re.compile(
            r"^\s*@pytest\.mark\.skip(?:\s*\(\s*\))?(?!\s*\(.*reason\s*=)",
        ),
    }

    # Python patterns that indicate a properly justified skip (no violation)
    PYTHON_ALLOWED_PATTERNS: list[re.Pattern[str]] = [
        # @pytest.mark.skip(reason="...")
        re.compile(r"^\s*@pytest\.mark\.skip\s*\(\s*reason\s*="),
        # @pytest.mark.skipif(..., reason="...")
        re.compile(r"^\s*@pytest\.mark\.skipif\s*\(.*reason\s*="),
        # pytest.skip("reason") - positional reason argument
        re.compile(r"pytest\.skip\s*\(\s*['\"]"),
        # pytest.skip(reason="...")
        re.compile(r"pytest\.skip\s*\(\s*reason\s*="),
    ]

    # Pattern for bare pytest.skip() - needs special handling
    PYTEST_SKIP_CALL_PATTERN = re.compile(
        r"pytest\.skip\s*\(\s*\)",
    )

    # JavaScript/TypeScript patterns - these are always violations
    # The proper way is to remove or fix the test, not skip it
    JS_VIOLATION_PATTERNS: dict[IgnoreType, re.Pattern[str]] = {
        IgnoreType.JEST_SKIP: re.compile(
            r"(?:it|test)\.skip\s*\(",
        ),
        IgnoreType.MOCHA_SKIP: re.compile(
            r"describe\.skip\s*\(",
        ),
    }

    def find_skips(
        self,
        code: str,
        file_path: Path | str | None = None,
        language: str | Language = Language.PYTHON,
    ) -> list[IgnoreDirective]:
        """Find test skip patterns without justification.

        Tracks docstring state across lines to avoid false positives from
        patterns mentioned in documentation.

        Args:
            code: Source code to scan
            file_path: Optional path to the source file (Path or string)
            language: Language of source code (Language enum or string)

        Returns:
            List of IgnoreDirective objects for detected unjustified skips
        """
        effective_path = normalize_path(file_path)
        lang = Language(language) if isinstance(language, str) else language
        scanner = self._get_line_scanner(lang)

        scannable_lines = self._get_scannable_lines(code, lang)
        directives: list[IgnoreDirective] = []
        for line_num, line in scannable_lines:
            directives.extend(scanner(line, line_num, effective_path))
        return directives

    def _get_scannable_lines(self, code: str, lang: Language) -> list[tuple[int, str]]:
        """Get lines that are not inside docstrings (Python) or all lines (other).

        Args:
            code: Source code to analyze
            lang: Programming language

        Returns:
            List of (line_number, line_text) tuples for scannable lines
        """
        if lang != Language.PYTHON:
            return list(enumerate(code.splitlines(), start=1))
        return _get_python_scannable_lines(code)

    def _get_line_scanner(
        self, lang: Language
    ) -> Callable[[str, int, Path], list[IgnoreDirective]]:
        """Get the appropriate line scanner for a language.

        Args:
            lang: Programming language

        Returns:
            Line scanner function for the language
        """
        if lang == Language.PYTHON:
            return self._scan_python_line
        if lang in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            return self._scan_js_line
        return _scan_empty

    def _scan_python_line(self, line: str, line_num: int, file_path: Path) -> list[IgnoreDirective]:
        """Scan a Python line for unjustified skip patterns.

        Args:
            line: Line of code to scan
            line_num: 1-indexed line number
            file_path: Path to the source file

        Returns:
            List of IgnoreDirective objects found on this line
        """
        if _is_comment_line(line) or self._is_justified_python_skip(line):
            return []

        found = self._find_decorator_violations(line, line_num, file_path)
        found.extend(self._find_skip_call_violations(line, line_num, file_path))
        return found

    def _find_decorator_violations(
        self, line: str, line_num: int, file_path: Path
    ) -> list[IgnoreDirective]:
        """Find @pytest.mark.skip decorator violations.

        Args:
            line: Line of code to scan
            line_num: 1-indexed line number
            file_path: Path to source file

        Returns:
            List of IgnoreDirective for decorator violations
        """
        found: list[IgnoreDirective] = []
        for ignore_type, pattern in self.PYTHON_VIOLATION_PATTERNS.items():
            match = pattern.search(line)
            if match:
                found.append(create_directive_no_rules(match, ignore_type, line_num, file_path))
        return found

    def _find_skip_call_violations(
        self, line: str, line_num: int, file_path: Path
    ) -> list[IgnoreDirective]:
        """Find bare pytest.skip() call violations.

        Args:
            line: Line of code to scan
            line_num: 1-indexed line number
            file_path: Path to source file

        Returns:
            List of IgnoreDirective for skip call violations
        """
        match = self.PYTEST_SKIP_CALL_PATTERN.search(line)
        if match:
            return [create_directive_no_rules(match, IgnoreType.PYTEST_SKIP, line_num, file_path)]
        return []

    def _is_justified_python_skip(self, line: str) -> bool:
        """Check if a Python line contains a justified skip.

        Args:
            line: Line of code to check

        Returns:
            True if the line has a skip with proper justification
        """
        return any(pattern.search(line) for pattern in self.PYTHON_ALLOWED_PATTERNS)

    def _scan_js_line(self, line: str, line_num: int, file_path: Path) -> list[IgnoreDirective]:
        """Scan a JavaScript/TypeScript line for skip patterns.

        Args:
            line: Line of code to scan
            line_num: 1-indexed line number
            file_path: Path to the source file

        Returns:
            List of IgnoreDirective objects found on this line
        """
        found: list[IgnoreDirective] = []

        for ignore_type, pattern in self.JS_VIOLATION_PATTERNS.items():
            match = pattern.search(line)
            if match:
                found.append(create_directive_no_rules(match, ignore_type, line_num, file_path))

        return found
