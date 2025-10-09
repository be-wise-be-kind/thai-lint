"""
Purpose: Deduplication utility for overlapping code block violations

Scope: Handles filtering of overlapping duplicate code violations

Overview: Provides utilities to remove overlapping violations from duplicate code detection results.
    Delegates grouping to BlockGrouper and filtering to ViolationFilter. Handles both block-level
    deduplication (one block per file) and violation-level deduplication (removing overlaps).

Dependencies: CodeBlock, Violation, BlockGrouper, ViolationFilter

Exports: ViolationDeduplicator class

Interfaces: ViolationDeduplicator.deduplicate_blocks(blocks), deduplicate_violations(violations)

Implementation: Delegates to BlockGrouper and ViolationFilter for SRP compliance
"""

from src.core.types import Violation

from .block_grouper import BlockGrouper
from .cache import CodeBlock
from .violation_filter import ViolationFilter


class ViolationDeduplicator:
    """Removes overlapping duplicate code violations."""

    def __init__(self) -> None:
        """Initialize with helper components."""
        self._grouper = BlockGrouper()
        self._filter = ViolationFilter()

    def deduplicate_blocks(self, blocks: list[CodeBlock]) -> list[CodeBlock]:
        """Remove overlapping blocks from same file.

        When rolling hash creates overlapping windows, keep non-overlapping blocks.
        Blocks are overlapping if they share any line numbers in the same file.

        Args:
            blocks: List of code blocks (may have overlaps from rolling hash)

        Returns:
            Deduplicated list of blocks (non-overlapping blocks preserved)
        """
        if not blocks:
            return []

        grouped = self._grouper.group_blocks_by_file(blocks)
        deduplicated = []

        for file_blocks in grouped.values():
            kept = self._remove_overlaps_from_file(file_blocks)
            deduplicated.extend(kept)

        return deduplicated

    def _remove_overlaps_from_file(self, file_blocks: list[CodeBlock]) -> list[CodeBlock]:
        """Remove overlapping blocks from single file.

        Args:
            file_blocks: Blocks from same file

        Returns:
            Non-overlapping blocks
        """
        sorted_blocks = sorted(file_blocks, key=lambda b: b.start_line)
        kept_blocks: list[CodeBlock] = []

        for block in sorted_blocks:
            if not self._overlaps_any_kept(block, kept_blocks):
                kept_blocks.append(block)

        return kept_blocks

    def _overlaps_any_kept(self, block: CodeBlock, kept_blocks: list[CodeBlock]) -> bool:
        """Check if block overlaps with any kept blocks.

        Args:
            block: Block to check
            kept_blocks: Previously kept blocks

        Returns:
            True if block overlaps with any kept block
        """
        return any(self._blocks_overlap(block, kept) for kept in kept_blocks)

    def _blocks_overlap(self, block1: CodeBlock, block2: CodeBlock) -> bool:
        """Check if two blocks overlap (share any lines).

        Args:
            block1: First code block
            block2: Second code block

        Returns:
            True if blocks overlap
        """
        return block1.start_line <= block2.end_line and block2.start_line <= block1.end_line

    def deduplicate_violations(self, violations: list[Violation]) -> list[Violation]:
        """Remove overlapping violations from same file.

        Args:
            violations: List of violations (may overlap)

        Returns:
            Deduplicated list of violations
        """
        if not violations:
            return []

        grouped = self._grouper.group_violations_by_file(violations)
        deduplicated = []

        for file_violations in grouped.values():
            sorted_violations = sorted(file_violations, key=lambda v: v.line or 0)
            kept = self._filter.filter_overlapping(sorted_violations)
            deduplicated.extend(kept)

        return deduplicated
