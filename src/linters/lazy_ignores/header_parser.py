"""
Purpose: Parse Suppressions section from file headers

Scope: Python docstrings and TypeScript JSDoc comment header parsing

Overview: Provides SuppressionsParser class for extracting the Suppressions section from
    file headers. Parses Python triple-quoted docstrings and TypeScript JSDoc comments.
    Extracts rule IDs and justifications, normalizing rule IDs for case-insensitive matching.
    Returns dictionary mapping normalized rule IDs to their justifications.

Dependencies: re for pattern matching, Language enum for type safety

Exports: SuppressionsParser

Interfaces: parse(header: str) -> dict[str, str], extract_header(code: str, language: Language)

Implementation: Regex-based section extraction with line-by-line entry parsing
"""

import re

from src.core.constants import Language


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

    # Pattern to parse individual entries (rule_id: justification)
    # Rule IDs can contain colons (e.g., type:ignore[arg-type])
    # Use greedy match for rule_id, justification must start with word char
    # This ensures we split at the last ": " before the justification text
    ENTRY_PATTERN = re.compile(
        r"^[\s*]*(.+):\s+([A-Za-z].*)$",
        re.MULTILINE,
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
        section_content = section_match.group(1)

        for match in self.ENTRY_PATTERN.finditer(section_content):
            rule_id = match.group(1).strip()
            justification = match.group(2).strip()

            # Skip entries with empty justification
            if justification:
                normalized_id = self.normalize_rule_id(rule_id)
                entries[normalized_id] = justification

        return entries

    def normalize_rule_id(self, rule_id: str) -> str:
        """Normalize rule ID for case-insensitive matching.

        Args:
            rule_id: Original rule ID string

        Returns:
            Normalized rule ID (lowercase)
        """
        return rule_id.lower().strip()

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
        # Allow leading whitespace/newlines
        stripped = code.lstrip()

        # Try double quotes first
        match = re.match(r'^"""(.*?)"""', stripped, re.DOTALL)
        if match:
            return match.group(0)

        # Try single quotes
        match = re.match(r"^'''(.*?)'''", stripped, re.DOTALL)
        if match:
            return match.group(0)

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
