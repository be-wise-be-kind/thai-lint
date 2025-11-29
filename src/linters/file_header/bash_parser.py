"""
File: src/linters/file_header/bash_parser.py
Purpose: Bash shell script comment header extraction and parsing
Exports: BashHeaderParser class
Depends: base_parser.BaseHeaderParser
Implements: Hash comment extraction with field parsing
Related: linter.py for parser usage, base_parser.py for common logic

Overview:
    Extracts hash comment headers from Bash shell scripts. Handles shebang lines
    (#!/bin/bash, #!/usr/bin/env bash, etc.) by skipping them and extracting the
    comment block that follows. Parses structured header fields from comment content.

Usage:
    parser = BashHeaderParser()
    header = parser.extract_header(code)
    fields = parser.parse_fields(header)

Notes: Skips shebang line if present, extracts contiguous comment block
"""

from src.linters.file_header.base_parser import BaseHeaderParser


class BashHeaderParser(BaseHeaderParser):
    """Extracts and parses Bash file headers from comment blocks."""

    def extract_header(self, code: str) -> str | None:
        """Extract comment header from Bash script."""
        if not code or not code.strip():
            return None

        lines = self._skip_preamble(code.split("\n"))
        header_lines = self._extract_comment_block(lines)

        return "\n".join(header_lines) if header_lines else None

    def _skip_preamble(self, lines: list[str]) -> list[str]:  # thailint: ignore[nesting]
        """Skip shebang and leading empty lines."""
        result = []
        skipping = True
        for line in lines:
            stripped = line.strip()
            if skipping:
                if stripped.startswith("#!") or not stripped:
                    continue
                skipping = False
            result.append(stripped)
        return result

    def _extract_comment_block(self, lines: list[str]) -> list[str]:
        """Extract contiguous comment lines from start of input."""
        result = []
        for line in lines:
            if line.startswith("#"):
                result.append(line[1:].strip())
            else:
                break
        return result
