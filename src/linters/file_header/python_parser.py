"""
File: src/linters/file_header/python_parser.py
Purpose: Python docstring extraction and parsing for file headers
Exports: PythonHeaderParser class
Depends: Python ast module, base_parser.BaseHeaderParser
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

from src.linters.file_header.base_parser import BaseHeaderParser


class PythonHeaderParser(BaseHeaderParser):
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
