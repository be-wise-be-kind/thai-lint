"""
Purpose: TypeScript/JavaScript source code tokenization and duplicate block analysis

Scope: TypeScript and JavaScript file analysis for duplicate detection

Overview: Analyzes TypeScript and JavaScript source files to extract code blocks for duplicate
    detection. Uses token-based hashing approach to normalize code and generate rolling hash windows.
    Integrates TokenHasher for normalization and CodeBlock creation. Returns list of code blocks with
    hash values that can be stored in cache and queried for duplicates across the project. Implementation
    mirrors PythonDuplicateAnalyzer using TokenHasher which handles both Python (#) and TS/JS (//) comments.

Dependencies: TokenHasher, CodeBlock, DRYConfig, pathlib.Path

Exports: TypeScriptDuplicateAnalyzer class

Interfaces: TypeScriptDuplicateAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig)
    -> list[CodeBlock]

Implementation: Token-based analysis using TokenHasher, rolling hash windows, CodeBlock creation
"""

from pathlib import Path

from .cache import CodeBlock
from .config import DRYConfig
from .token_hasher import TokenHasher


class TypeScriptDuplicateAnalyzer:
    """Analyzes TypeScript/JavaScript code for duplicate blocks."""

    def __init__(self) -> None:
        """Initialize analyzer with token hasher."""
        self._hasher = TokenHasher()

    def analyze(self, file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]:
        """Analyze TypeScript/JavaScript file for code blocks.

        Args:
            file_path: Path to TypeScript/JavaScript file
            content: File content
            config: DRY configuration

        Returns:
            List of CodeBlock instances with hash values
        """
        # Tokenize code
        lines = self._hasher.tokenize(content)

        # Generate rolling hash windows
        windows = self._hasher.rolling_hash(lines, config.min_duplicate_lines)

        # Get interface/type definition ranges to filter out
        interface_ranges = self._find_interface_ranges(content)

        # Create CodeBlock instances, filtering out interface bodies
        blocks = []
        for hash_val, start_line, end_line, snippet in windows:
            # Skip blocks that overlap with interface definitions
            if self._overlaps_interface(start_line, end_line, interface_ranges):
                continue

            block = CodeBlock(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                snippet=snippet,
                hash_value=hash_val,
            )
            blocks.append(block)

        return blocks

    def _find_interface_ranges(self, content: str) -> list[tuple[int, int]]:
        """Find line ranges of interface/type definitions.

        Args:
            content: File content

        Returns:
            List of (start_line, end_line) tuples for interface blocks
        """
        ranges: list[tuple[int, int]] = []
        lines = content.split("\n")
        state = {"in_interface": False, "start_line": 0, "brace_count": 0}

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            self._process_line_for_interface(stripped, i, state, ranges)

        return ranges

    def _process_line_for_interface(
        self, stripped: str, line_num: int, state: dict, ranges: list[tuple[int, int]]
    ) -> None:
        """Process single line for interface detection.

        Args:
            stripped: Stripped line content
            line_num: Line number
            state: Tracking state (in_interface, start_line, brace_count)
            ranges: Accumulated interface ranges
        """
        if self._is_interface_start(stripped):
            self._handle_interface_start(stripped, line_num, state, ranges)
            return

        if state["in_interface"]:
            self._handle_interface_continuation(stripped, line_num, state, ranges)

    def _is_interface_start(self, stripped: str) -> bool:
        """Check if line starts interface/type definition."""
        return stripped.startswith(("interface ", "type ")) and "{" in stripped

    def _handle_interface_start(
        self, stripped: str, line_num: int, state: dict, ranges: list[tuple[int, int]]
    ) -> None:
        """Handle start of interface definition."""
        state["in_interface"] = True
        state["start_line"] = line_num
        state["brace_count"] = stripped.count("{") - stripped.count("}")

        if state["brace_count"] == 0:  # Single-line interface
            ranges.append((line_num, line_num))
            state["in_interface"] = False

    def _handle_interface_continuation(
        self, stripped: str, line_num: int, state: dict, ranges: list[tuple[int, int]]
    ) -> None:
        """Handle continuation of interface definition."""
        state["brace_count"] += stripped.count("{") - stripped.count("}")
        if state["brace_count"] == 0:
            ranges.append((state["start_line"], line_num))
            state["in_interface"] = False

    def _overlaps_interface(
        self, start: int, end: int, interface_ranges: list[tuple[int, int]]
    ) -> bool:
        """Check if block overlaps with any interface range.

        Args:
            start: Block start line
            end: Block end line
            interface_ranges: List of interface definition ranges

        Returns:
            True if block overlaps with an interface
        """
        for if_start, if_end in interface_ranges:
            if start <= if_end and end >= if_start:
                return True
        return False
