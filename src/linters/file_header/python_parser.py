"""
File: src/linters/file_header/python_parser.py
Purpose: Python docstring extraction and parsing for file headers
Exports: PythonHeaderParser class
Depends: Python ast module
Implements: AST-based docstring extraction with field parsing
Related: linter.py for parser usage, field_validator.py for field validation

Overview:
    Extracts module-level docstrings from Python files using AST parsing.
    Parses structured header fields from docstring content and handles both
    well-formed and malformed headers. Provides field extraction and validation
    support for FileHeaderRule.

Usage:
    parser = PythonHeaderParser()
    header = parser.extract_header(code)
    fields = parser.parse_fields(header)

Notes: Uses ast.get_docstring() for reliable module-level docstring extraction
"""

import ast


class PythonHeaderParser:
    """Extracts and parses Python file headers from docstrings."""

    def extract_header(self, code: str) -> str | None:
        """Extract module-level docstring from Python code.

        Args:
            code: Python source code

        Returns:
            Module docstring or None if not found or parse error
        """
        try:
            tree = ast.parse(code)
            return ast.get_docstring(tree)
        except SyntaxError:
            return None

    def parse_fields(self, header: str) -> dict[str, str]:  # thailint: ignore[nesting]
        """Parse structured fields from header text.

        Args:
            header: Header docstring text

        Returns:
            Dictionary mapping field_name -> field_value
        """
        fields: dict[str, str] = {}
        current_field: str | None = None
        current_value: list[str] = []

        for line in header.split("\n"):
            if self._is_new_field_line(line):
                current_field = self._save_and_start_new_field(
                    fields, current_field, current_value, line
                )
                current_value = [line.split(":", 1)[1].strip()]
            elif current_field:
                current_value.append(line.strip())

        self._save_current_field(fields, current_field, current_value)
        return fields

    def _is_new_field_line(self, line: str) -> bool:
        """Check if line starts a new field."""
        return ":" in line and not line.startswith(" ")

    def _save_and_start_new_field(
        self, fields: dict[str, str], current_field: str | None, current_value: list[str], line: str
    ) -> str:
        """Save current field and start new one."""
        if current_field:
            fields[current_field] = "\n".join(current_value).strip()
        return line.split(":", 1)[0].strip()

    def _save_current_field(
        self, fields: dict[str, str], current_field: str | None, current_value: list[str]
    ) -> None:
        """Save the last field."""
        if current_field:
            fields[current_field] = "\n".join(current_value).strip()
