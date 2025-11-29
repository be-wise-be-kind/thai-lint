"""
Purpose: CSS block comment header extraction and parsing

Scope: CSS and SCSS file header parsing

Overview: Extracts JSDoc-style block comments (/** ... */) from CSS and SCSS files.
    Handles @charset declarations by allowing them before the header comment.
    Parses structured header fields from comment content and cleans formatting
    characters. Requires JSDoc-style comment (/**) not regular block comment (/*).
    Processes multi-line comments and removes leading asterisks from content.

Dependencies: re module for regex pattern matching, base_parser.BaseHeaderParser for field parsing

Exports: CssHeaderParser class

Interfaces: extract_header(code) -> str | None for JSDoc comment extraction, parse_fields(header) inherited from base

Implementation: Regex-based JSDoc comment extraction with content cleaning and formatting removal
"""

import re

from src.linters.file_header.base_parser import BaseHeaderParser


class CssHeaderParser(BaseHeaderParser):
    """Extracts and parses CSS file headers from block comments."""

    # Pattern to match JSDoc-style comment, allowing @charset before
    JSDOC_PATTERN = re.compile(r'^(?:@charset\s+"[^"]+"\s*;\s*)?\s*/\*\*\s*(.*?)\s*\*/', re.DOTALL)

    def extract_header(self, code: str) -> str | None:
        """Extract JSDoc-style comment from CSS code.

        Args:
            code: CSS/SCSS source code

        Returns:
            Comment content or None if not found
        """
        if not code or not code.strip():
            return None

        match = self.JSDOC_PATTERN.match(code)
        if not match:
            return None

        # Extract and clean the content
        comment_content = match.group(1)
        return self._clean_comment_content(comment_content)

    def _clean_comment_content(self, content: str) -> str:
        """Remove comment formatting (leading asterisks) from content.

        Args:
            content: Raw comment content

        Returns:
            Cleaned content without leading asterisks
        """
        lines = content.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("*"):
                stripped = stripped[1:].strip()
            cleaned_lines.append(stripped)

        return "\n".join(cleaned_lines)
