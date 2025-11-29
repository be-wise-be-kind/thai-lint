"""
File: src/linters/file_header/typescript_parser.py
Purpose: TypeScript/JavaScript JSDoc comment extraction and parsing
Exports: TypeScriptHeaderParser class
Depends: re module for regex matching, base_parser.BaseHeaderParser
Implements: Regex-based JSDoc extraction with field parsing
Related: linter.py for parser usage, base_parser.py for common logic

Overview:
    Extracts JSDoc-style comments (/** ... */) from TypeScript and JavaScript files.
    Parses structured header fields from JSDoc content and handles both single-line
    and multi-line field values. Distinguishes JSDoc comments from regular block
    comments (/* ... */).

Usage:
    parser = TypeScriptHeaderParser()
    header = parser.extract_header(code)
    fields = parser.parse_fields(header)

Notes: Only recognizes JSDoc comments starting with /** (not /*)
"""

import re

from src.linters.file_header.base_parser import BaseHeaderParser


class TypeScriptHeaderParser(BaseHeaderParser):
    """Extracts and parses TypeScript/JavaScript file headers from JSDoc comments."""

    # Pattern to match JSDoc comment at start of file (allowing whitespace before)
    JSDOC_PATTERN = re.compile(r"^\s*/\*\*\s*(.*?)\s*\*/", re.DOTALL)

    def extract_header(self, code: str) -> str | None:
        """Extract JSDoc comment from TypeScript/JavaScript code.

        Args:
            code: TypeScript/JavaScript source code

        Returns:
            JSDoc content or None if not found
        """
        if not code or not code.strip():
            return None

        match = self.JSDOC_PATTERN.match(code)
        if not match:
            return None

        # Extract the content inside the JSDoc
        jsdoc_content = match.group(1)

        # Clean up the JSDoc content - remove leading * from each line
        return self._clean_jsdoc_content(jsdoc_content)

    def _clean_jsdoc_content(self, content: str) -> str:
        """Remove JSDoc formatting (leading asterisks) from content.

        Args:
            content: Raw JSDoc content

        Returns:
            Cleaned content without leading asterisks
        """
        lines = content.split("\n")
        cleaned_lines = []

        for line in lines:
            # Remove leading whitespace and asterisk
            stripped = line.strip()
            if stripped.startswith("*"):
                stripped = stripped[1:].strip()
            cleaned_lines.append(stripped)

        return "\n".join(cleaned_lines)
