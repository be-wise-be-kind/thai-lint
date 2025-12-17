"""
Purpose: Violation message formatting for duplicate code detection

Scope: Construction of detailed violation messages with cross-file references

Overview: Builds comprehensive violation messages for duplicate code blocks. Formats messages to
    include duplicate line count, occurrence count, and references to all other locations where
    the duplicate appears. Provides helpful context for developers to identify and refactor
    duplicated code. Follows established violation building pattern from nesting and SRP linters.

Dependencies: CodeBlock, Violation from core.types

Exports: DRYViolationBuilder class

Interfaces: DRYViolationBuilder.build_violation(block: CodeBlock, all_duplicates: list[CodeBlock],
    rule_id: str) -> Violation

Implementation: Message formatting with cross-references, location tracking, multi-file duplicate
    reporting
"""

from src.core.types import Severity, Violation

from .cache import CodeBlock


class DRYViolationBuilder:
    """Builds violation messages for duplicate code."""

    def __init__(self) -> None:
        """Initialize the DRY violation builder."""
        pass  # Stateless builder for duplicate code violations

    def build_violation(
        self, block: CodeBlock, all_duplicates: list[CodeBlock], rule_id: str
    ) -> Violation:
        """Build violation for duplicate code block.

        Args:
            block: The code block in current file
            all_duplicates: All blocks with same hash (including current)
            rule_id: Rule identifier

        Returns:
            Violation instance with formatted message
        """
        line_count = block.end_line - block.start_line + 1
        occurrence_count = len(all_duplicates)

        # Get other locations and format message
        location_refs = self._get_location_refs(block, all_duplicates)
        message = self._build_message(line_count, occurrence_count, location_refs)

        return Violation(
            rule_id=rule_id,
            message=message,
            file_path=str(block.file_path),
            line=block.start_line,
            column=1,
            severity=Severity.ERROR,
        )

    def _get_location_refs(self, block: CodeBlock, all_duplicates: list[CodeBlock]) -> list[str]:
        """Get formatted location strings for other duplicates."""
        other_blocks = [
            d
            for d in all_duplicates
            if d.file_path != block.file_path or d.start_line != block.start_line
        ]

        return [f"{loc.file_path}:{loc.start_line}-{loc.end_line}" for loc in other_blocks]

    def _build_message(self, line_count: int, occurrence_count: int, locations: list[str]) -> str:
        """Build violation message with location references."""
        message = f"Duplicate code ({line_count} lines, {occurrence_count} occurrences)"
        if locations:
            message += f". Also found in: {', '.join(locations)}"
        return message
