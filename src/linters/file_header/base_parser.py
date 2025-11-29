"""
File: src/linters/file_header/base_parser.py
Purpose: Base class for file header parsers with common field parsing logic
Exports: BaseHeaderParser class
Depends: re module, abc module
Implements: Abstract base class with shared field parsing methods
Related: typescript_parser.py, bash_parser.py, css_parser.py

Overview:
    Provides common field parsing functionality shared across all language-specific
    header parsers. Implements the parse_fields method and helper methods for
    detecting field lines and saving fields. Subclasses implement extract_header
    for language-specific header extraction.

Usage:
    class MyParser(BaseHeaderParser):
        def extract_header(self, code: str) -> str | None:
            # Language-specific extraction
            pass

Notes: Uses template method pattern for field parsing
"""

import re
from abc import ABC, abstractmethod


class BaseHeaderParser(ABC):
    """Base class for file header parsers with common field parsing logic."""

    # Pattern to match field names (word characters and /)
    FIELD_NAME_PATTERN = re.compile(r"^[\w/]+$")

    @abstractmethod
    def extract_header(self, code: str) -> str | None:
        """Extract header from source code.

        Args:
            code: Source code

        Returns:
            Header content or None if not found
        """

    def parse_fields(self, header: str) -> dict[str, str]:  # thailint: ignore[nesting]
        """Parse structured fields from header text.

        Args:
            header: Header text

        Returns:
            Dictionary mapping field_name -> field_value
        """
        fields: dict[str, str] = {}
        current_field: str | None = None
        current_value: list[str] = []

        for line in header.split("\n"):
            if self._is_field_line(line):
                self._save_field(fields, current_field, current_value)
                current_field, current_value = self._start_new_field(line)
            elif current_field:
                current_value.append(line.strip())

        self._save_field(fields, current_field, current_value)
        return fields

    def _is_field_line(self, line: str) -> bool:
        """Check if line starts a new field."""
        if ":" not in line:
            return False

        colon_pos = line.find(":")
        if colon_pos <= 0:
            return False

        field_name = line[:colon_pos].strip()
        return bool(self.FIELD_NAME_PATTERN.match(field_name))

    def _start_new_field(self, line: str) -> tuple[str, list[str]]:
        """Parse a field line and start tracking its value."""
        parts = line.split(":", 1)
        field_name = parts[0].strip()
        initial_value = parts[1].strip() if len(parts) > 1 else ""
        return field_name, [initial_value] if initial_value else []

    def _save_field(
        self, fields: dict[str, str], field_name: str | None, value_lines: list[str]
    ) -> None:
        """Save accumulated field value to fields dict."""
        if field_name:
            fields[field_name] = "\n".join(value_lines).strip()
