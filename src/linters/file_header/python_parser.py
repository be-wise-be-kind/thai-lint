"""
Purpose: Python docstring extraction and parsing for file headers

Scope: Python file header parsing from module-level docstrings

Overview: Extracts module-level docstrings from Python files using AST parsing.
    Parses structured header fields from docstring content and handles both
    well-formed and malformed headers. Provides field extraction and validation
    support for FileHeaderRule. Uses ast.get_docstring() for reliable extraction
    and gracefully handles syntax errors in source code.

Dependencies: Python ast module for AST parsing, base_parser.BaseHeaderParser for field parsing

Exports: PythonHeaderParser class

Interfaces: extract_header(code) -> str | None for docstring extraction, parse_fields(header) inherited from base

Implementation: AST-based docstring extraction with syntax error handling
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
