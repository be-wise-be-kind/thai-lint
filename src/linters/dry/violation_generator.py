"""
Purpose: Violation generation from duplicate code blocks

Scope: Generates violations from duplicate hashes

Overview: Handles violation generation for duplicate code blocks. Queries storage for duplicate
    hashes, retrieves blocks for each hash, deduplicates overlapping blocks, builds violations
    using ViolationBuilder, and filters violations based on ignore patterns. Separates violation
    generation logic from main linter rule to maintain SRP compliance.

Dependencies: DuplicateStorage, ViolationDeduplicator, DRYViolationBuilder, Violation, DRYConfig

Exports: ViolationGenerator class

Interfaces: ViolationGenerator.generate_violations(storage, rule_id, config) -> list[Violation]

Implementation: Queries storage, deduplicates blocks, builds violations, filters by ignore patterns
"""

from pathlib import Path

from src.core.types import Violation
from src.orchestrator.language_detector import detect_language

from .config import DRYConfig
from .deduplicator import ViolationDeduplicator
from .duplicate_storage import DuplicateStorage
from .inline_ignore import InlineIgnoreParser
from .violation_builder import DRYViolationBuilder


class ViolationGenerator:
    """Generates violations from duplicate code blocks."""

    def __init__(self) -> None:
        """Initialize with deduplicator and violation builder."""
        self._deduplicator = ViolationDeduplicator()
        self._violation_builder = DRYViolationBuilder()

    def generate_violations(
        self,
        storage: DuplicateStorage,
        rule_id: str,
        config: DRYConfig,
        inline_ignore: InlineIgnoreParser,
    ) -> list[Violation]:
        """Generate violations from storage.

        Args:
            storage: Duplicate storage instance
            rule_id: Rule identifier for violations
            config: DRY configuration with ignore patterns
            inline_ignore: Parser with inline ignore directives

        Returns:
            List of violations filtered by ignore patterns and inline directives
        """
        duplicate_hashes = storage.duplicate_hashes
        violations = []

        for hash_value in duplicate_hashes:
            blocks = storage.get_blocks_for_hash(hash_value)
            dedup_blocks = self._deduplicator.deduplicate_blocks(blocks)

            # Check min_occurrences threshold (language-aware)
            if not self._meets_min_occurrences(dedup_blocks, config):
                continue

            for block in dedup_blocks:
                violation = self._violation_builder.build_violation(block, dedup_blocks, rule_id)
                violations.append(violation)

        deduplicated = self._deduplicator.deduplicate_violations(violations)
        pattern_filtered = self._filter_ignored(deduplicated, config.ignore_patterns)
        return self._filter_inline_ignored(pattern_filtered, inline_ignore)

    def _meets_min_occurrences(self, blocks: list, config: DRYConfig) -> bool:
        """Check if blocks meet minimum occurrence threshold for the language.

        Args:
            blocks: List of duplicate code blocks
            config: DRY configuration with min_occurrences settings

        Returns:
            True if blocks meet or exceed minimum occurrence threshold
        """
        if len(blocks) == 0:
            return False

        # Get language from first block's file extension
        first_block = blocks[0]
        language = detect_language(first_block.file_path)

        # Get language-specific threshold
        min_occurrences = config.get_min_occurrences_for_language(language)

        return len(blocks) >= min_occurrences

    def _filter_ignored(
        self, violations: list[Violation], ignore_patterns: list[str]
    ) -> list[Violation]:
        """Filter violations based on ignore patterns.

        Args:
            violations: List of violations to filter
            ignore_patterns: List of path patterns to ignore

        Returns:
            Filtered list of violations
        """
        if not ignore_patterns:
            return violations

        filtered = []
        for violation in violations:
            if not self._is_ignored(violation.file_path, ignore_patterns):
                filtered.append(violation)
        return filtered

    def _is_ignored(self, file_path: str, ignore_patterns: list[str]) -> bool:
        """Check if file path matches any ignore pattern.

        Args:
            file_path: Path to check
            ignore_patterns: List of patterns to match against

        Returns:
            True if file should be ignored
        """
        path_str = str(Path(file_path))
        for pattern in ignore_patterns:
            if pattern in path_str:
                return True
        return False

    def _filter_inline_ignored(
        self, violations: list[Violation], inline_ignore: InlineIgnoreParser
    ) -> list[Violation]:
        """Filter violations based on inline ignore directives.

        Args:
            violations: List of violations to filter
            inline_ignore: Parser with inline ignore directives

        Returns:
            Filtered list of violations
        """
        filtered = []
        for violation in violations:
            start_line = violation.line or 0
            # Extract line count from message to calculate end_line
            line_count = self._extract_line_count(violation.message)
            end_line = start_line + line_count - 1

            if not inline_ignore.should_ignore(violation.file_path, start_line, end_line):
                filtered.append(violation)
        return filtered

    def _extract_line_count(self, message: str) -> int:
        """Extract line count from violation message.

        Args:
            message: Violation message

        Returns:
            Number of lines (default 1)
        """
        # Message format: "Duplicate code (N lines, ...)"
        try:
            start = message.index("(") + 1
            end = message.index(" lines")
            return int(message[start:end])
        except (ValueError, IndexError):
            return 1
