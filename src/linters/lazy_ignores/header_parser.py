"""
Purpose: Parse Suppressions section from file headers

Scope: Python docstrings and TypeScript JSDoc comment header parsing

Overview: Provides SuppressionsParser class for extracting the Suppressions section from
    file headers. Parses Python triple-quoted docstrings and TypeScript JSDoc comments.
    Extracts rule IDs and justifications, normalizing rule IDs for case-insensitive matching.
    Delegates entry splitting to the entry parser so wrapped justification prose stays with
    its entry. Returns dictionary mapping normalized rule IDs to their justifications.

Dependencies: re for pattern matching, Language enum for type safety, entry_parser for entry splitting

Exports: SuppressionsParser

Interfaces: parse(header: str) -> dict[str, str], extract_header(code: str, language: Language)

Implementation: Regex-based section extraction with indentation-aware entry splitting
"""

import re

from src.core.constants import Language
from src.linters.lazy_ignores.entry_parser import split_entries


class SuppressionsParser:
    """Parses Suppressions section from file headers."""

    # Pattern to find Suppressions section (case-insensitive)
    # Matches "Suppressions:" followed by indented lines
    SUPPRESSIONS_SECTION = re.compile(
        r"Suppressions:\s*\n((?:[ \t]+\S.*\n?)+)",
        re.MULTILINE | re.IGNORECASE,
    )

    # Pattern for JSDoc-style suppressions (* prefixed lines)
    JSDOC_SUPPRESSIONS_SECTION = re.compile(
        r"Suppressions:\s*\n((?:\s*\*\s+\S.*\n?)+)",
        re.MULTILINE | re.IGNORECASE,
    )

    def parse(self, header: str) -> dict[str, str]:
        """Parse Suppressions section, return rule_id -> justification mapping.

        Args:
            header: File header content (docstring or JSDoc)

        Returns:
            Dictionary mapping normalized rule IDs to justification strings
        """
        # Try standard Python-style first, then JSDoc-style
        section_match = self.SUPPRESSIONS_SECTION.search(header)
        if not section_match:
            section_match = self.JSDOC_SUPPRESSIONS_SECTION.search(header)

        if not section_match:
            return {}

        entries: dict[str, str] = {}
        for rule_id, justification in split_entries(section_match.group(1)):
            # Skip entries with empty justification
            if justification:
                entries[self.normalize_rule_id(rule_id)] = justification

        return entries

    def normalize_rule_id(self, rule_id: str) -> str:
        """Normalize rule ID for case-insensitive matching.

        Strips common list prefixes (-, *, •) and normalizes to lowercase.

        Args:
            rule_id: Original rule ID string

        Returns:
            Normalized rule ID (lowercase, no list prefix)
        """
        normalized = rule_id.lower().strip()
        # Strip common list prefixes (bullet points)
        if normalized.startswith(("- ", "* ", "• ")):
            normalized = normalized[2:]
        elif normalized.startswith(("-", "*", "•")):
            normalized = normalized[1:].lstrip()
        return normalized

    def extract_header(self, code: str, language: str | Language = Language.PYTHON) -> str:
        """Extract the header section from code.

        Args:
            code: Full source code
            language: Programming language (Language enum or string)

        Returns:
            Header content as string, or empty string if not found
        """
        lang = Language(language) if isinstance(language, str) else language
        if lang == Language.PYTHON:
            return self._extract_python_header(code)
        if lang in (Language.TYPESCRIPT, Language.JAVASCRIPT):
            return self._extract_ts_header(code)
        return ""

    def _extract_python_header(self, code: str) -> str:
        """Extract Python docstring header.

        Args:
            code: Python source code

        Returns:
            Docstring content or empty string
        """
        # Match triple-quoted docstring at start of file
        # Skip leading whitespace, comments, and encoding declarations
        stripped = self._skip_leading_comments(code)

        # Try double quotes first
        match = re.match(r'^"""(.*?)"""', stripped, re.DOTALL)
        if match:
            return match.group(0)

        # Try single quotes
        match = re.match(r"^'''(.*?)'''", stripped, re.DOTALL)
        if match:
            return match.group(0)

        return ""

    def _skip_leading_comments(self, code: str) -> str:
        """Skip leading comments and empty lines to find docstring.

        Args:
            code: Python source code

        Returns:
            Code with leading comments/empty lines removed
        """
        lines = code.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip empty lines
            if not stripped:
                continue
            # Skip comment lines (including pylint/noqa/type comments)
            if stripped.startswith("#"):
                continue
            # Found non-comment, non-empty line - return from here
            return "\n".join(lines[i:])
        return ""

    def _extract_ts_header(self, code: str) -> str:
        """Extract TypeScript/JavaScript JSDoc header.

        Args:
            code: TypeScript/JavaScript source code

        Returns:
            JSDoc comment content or empty string
        """
        stripped = code.lstrip()
        match = re.match(r"^/\*\*(.*?)\*/", stripped, re.DOTALL)
        if match:
            return match.group(0)
        return ""
