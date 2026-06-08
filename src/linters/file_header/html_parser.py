"""
Purpose: Jinja and HTML template comment header extraction and parsing

Scope: Jinja and HTML template file header parsing

Overview: Extracts a leading comment block from Jinja/HTML templates and treats it as the
    file header. Recognizes both Jinja comment blocks ({# ... #}) and HTML comment blocks
    (<!-- ... -->), allowing leading whitespace before the block and permitting the block to
    appear before {% extends ... %} or markup. Parses structured header fields from the
    comment content using the shared base parser. Jinja blocks take precedence when both a
    Jinja and an HTML comment could match.

Dependencies: re module for regex pattern matching, base_parser.BaseHeaderParser for field parsing

Exports: HtmlHeaderParser class

Interfaces: extract_header(code) -> str | None for comment extraction, parse_fields(header)
    inherited from base

Implementation: Regex-based extraction of the first Jinja or HTML comment block at file start
"""

import re

from src.linters.file_header.base_parser import BaseHeaderParser


class HtmlHeaderParser(BaseHeaderParser):
    """Extracts and parses Jinja/HTML template headers from comment blocks."""

    # Leading comment block patterns: Jinja {# ... #} first, then HTML <!-- ... -->.
    # Both allow whitespace before the block so it may precede {% extends %} or markup.
    COMMENT_PATTERNS = (
        re.compile(r"^\s*\{#\s*(.*?)\s*#\}", re.DOTALL),
        re.compile(r"^\s*<!--\s*(.*?)\s*-->", re.DOTALL),
    )

    def extract_header(self, code: str) -> str | None:
        """Extract the leading Jinja or HTML comment block from template code.

        Args:
            code: Jinja/HTML template source code

        Returns:
            Comment content or None if no leading comment block is found
        """
        for pattern in self.COMMENT_PATTERNS:
            match = pattern.match(code or "")
            if match:
                return match.group(1)

        return None
