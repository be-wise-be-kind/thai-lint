"""
Purpose: Block grouping utilities for duplicate detection

Scope: Groups code blocks by file path

Overview: Provides grouping utilities for organizing code blocks by file. Used by ViolationDeduplicator
    to process blocks on a per-file basis for overlap detection. Separates grouping logic to maintain
    SRP compliance.

Dependencies: CodeBlock, Violation

Exports: BlockGrouper class

Interfaces: BlockGrouper.group_blocks_by_file(blocks), group_violations_by_file(violations)

Implementation: Simple dictionary-based grouping by file path
"""

from pathlib import Path

from src.core.types import Violation

from .cache import CodeBlock


class BlockGrouper:
    """Groups blocks and violations by file path."""

    def __init__(self) -> None:
        """Initialize the block grouper."""
        pass  # Stateless grouper for code blocks

    def group_blocks_by_file(self, blocks: list[CodeBlock]) -> dict[Path, list[CodeBlock]]:
        """Group blocks by file path.

        Args:
            blocks: List of code blocks

        Returns:
            Dictionary mapping file paths to lists of blocks
        """
        grouped: dict[Path, list[CodeBlock]] = {}
        for block in blocks:
            if block.file_path not in grouped:
                grouped[block.file_path] = []
            grouped[block.file_path].append(block)
        return grouped

    def group_violations_by_file(self, violations: list[Violation]) -> dict[str, list[Violation]]:
        """Group violations by file path.

        Args:
            violations: List of violations

        Returns:
            Dictionary mapping file paths to lists of violations
        """
        grouped: dict[str, list[Violation]] = {}
        for violation in violations:
            if violation.file_path not in grouped:
                grouped[violation.file_path] = []
            grouped[violation.file_path].append(violation)
        return grouped
