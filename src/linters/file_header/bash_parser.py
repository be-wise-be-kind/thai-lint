"""
Purpose: Bash shell script comment header extraction and parsing

Scope: Bash and shell script file header parsing

Overview: Extracts hash comment headers from Bash shell scripts. Handles shebang lines
    (#!/bin/bash, #!/usr/bin/env bash, etc.) by skipping them and extracting the
    comment block that follows. Parses structured header fields from comment content.
    Extracts contiguous comment blocks from the start of the file and processes them
    into structured fields for validation.

Dependencies: base_parser.BaseHeaderParser for common field parsing functionality

Exports: BashHeaderParser class

Interfaces: extract_header(code) -> str | None for comment extraction, parse_fields(header) inherited from base

Implementation: Skips shebang and preamble, then extracts contiguous hash comment block
"""

from src.linters.file_header.base_parser import BaseHeaderParser


class BashHeaderParser(BaseHeaderParser):
    """Extracts and parses Bash file headers from comment blocks."""

    def __init__(self) -> None:
        """Initialize the Bash header parser."""
        pass  # BaseHeaderParser has no __init__, but we need this for stateless-class

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
