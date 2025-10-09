"""
Purpose: TypeScript/JavaScript source code tokenization and duplicate block analysis

Scope: TypeScript and JavaScript file analysis for duplicate detection

Overview: Analyzes TypeScript and JavaScript source files to extract code blocks for duplicate
    detection. Inherits from BaseTokenAnalyzer for common token-based hashing and rolling hash
    window logic. Adds TypeScript-specific filtering to exclude interface/type definition bodies
    from duplicate detection since these often have intentional structural similarity. Returns list
    of code blocks with hash values that can be stored in cache and queried for duplicates.

Dependencies: BaseTokenAnalyzer, CodeBlock, DRYConfig, pathlib.Path

Exports: TypeScriptDuplicateAnalyzer class

Interfaces: TypeScriptDuplicateAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig)
    -> list[CodeBlock]

Implementation: Inherits analyze() workflow from BaseTokenAnalyzer, adds interface filtering logic
"""

from .base_token_analyzer import BaseTokenAnalyzer


class TypeScriptDuplicateAnalyzer(BaseTokenAnalyzer):
    """Analyzes TypeScript/JavaScript code for duplicate blocks."""

    def _should_include_block(self, content: str, start_line: int, end_line: int) -> bool:
        """Filter out blocks that overlap with interface/type definitions.

        Args:
            content: File content
            start_line: Block start line
            end_line: Block end line

        Returns:
            False if block overlaps interface definition, True otherwise
        """
        interface_ranges = self._find_interface_ranges(content)
        return not self._overlaps_interface(start_line, end_line, interface_ranges)

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
