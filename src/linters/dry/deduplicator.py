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

        When rolling hash creates overlapping windows, keep only the first block
        per file to avoid duplicate violations.

        Args:
            blocks: List of code blocks (may have overlaps from rolling hash)

        Returns:
            Deduplicated list of blocks (one per file)
        """
        if not blocks:
            return []

        grouped = self._grouper.group_blocks_by_file(blocks)
        deduplicated = []

        for file_blocks in grouped.values():
            # Sort by start_line and keep only the first one per file
            sorted_blocks = sorted(file_blocks, key=lambda b: b.start_line)
            deduplicated.append(sorted_blocks[0])

        return deduplicated

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
