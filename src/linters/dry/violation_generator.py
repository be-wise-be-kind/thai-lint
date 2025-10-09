"""
Purpose: Violation generation from duplicate code blocks

Scope: Generates violations from duplicate hashes

Overview: Handles violation generation for duplicate code blocks. Queries storage for duplicate
    hashes, retrieves blocks for each hash, deduplicates overlapping blocks, and builds violations
    using ViolationBuilder. Separates violation generation logic from main linter rule to maintain
    SRP compliance.

Dependencies: DuplicateStorage, ViolationDeduplicator, DRYViolationBuilder, Violation

Exports: ViolationGenerator class

Interfaces: ViolationGenerator.generate_violations(storage, rule_id) -> list[Violation]

Implementation: Queries storage, deduplicates blocks, builds violations for each block
"""

from src.core.types import Violation

from .deduplicator import ViolationDeduplicator
from .duplicate_storage import DuplicateStorage
from .violation_builder import DRYViolationBuilder


class ViolationGenerator:
    """Generates violations from duplicate code blocks."""

    def __init__(self) -> None:
        """Initialize with deduplicator and violation builder."""
        self._deduplicator = ViolationDeduplicator()
        self._violation_builder = DRYViolationBuilder()

    def generate_violations(self, storage: DuplicateStorage, rule_id: str) -> list[Violation]:
        """Generate violations from storage.

        Args:
            storage: Duplicate storage instance
            rule_id: Rule identifier for violations

        Returns:
            List of violations
        """
        duplicate_hashes = storage.get_duplicate_hashes()
        violations = []

        for hash_value in duplicate_hashes:
            blocks = storage.get_blocks_for_hash(hash_value)
            dedup_blocks = self._deduplicator.deduplicate_blocks(blocks)

            for block in dedup_blocks:
                violation = self._violation_builder.build_violation(block, dedup_blocks, rule_id)
                violations.append(violation)

        return self._deduplicator.deduplicate_violations(violations)
