"""
Purpose: Violation generation from duplicate code blocks

Scope: Generates violations from duplicate hashes

Overview: Handles violation generation for duplicate code blocks. Queries storage for duplicate
    hashes, retrieves blocks for each hash, deduplicates overlapping blocks, builds violations
    using ViolationBuilder, and filters violations based on ignore patterns. A duplicate group is
    only reported if at least one of its occurrences is a file the current invocation actually
    processed - the query itself still scans the whole persisted index (needed to find matches
    against files outside the invocation), but a group where every occurrence is outside the
    invocation's scope is skipped entirely, so a diff-scoped run's report stays proportional to
    what was passed in rather than reprinting the whole backlog every time (issue #238). For a
    full-tree scan, every file is "processed", so this filter is a no-op. Separates violation
    generation logic from main linter rule to maintain SRP compliance.

Dependencies: DuplicateStorage, ViolationDeduplicator, DRYViolationBuilder, Violation, DRYConfig

Exports: ViolationGenerator class, IgnoreContext dataclass

Interfaces: ViolationGenerator.generate_violations(storage, rule_id, config, ignore_ctx,
    processed_files) -> list[Violation]

Implementation: Queries storage, deduplicates blocks, drops groups with no occurrence in
    processed_files, builds violations, filters by ignore patterns

Suppressions:
    - too-many-arguments,too-many-positional-arguments: generate_violations takes five
        independent, equally-necessary inputs (storage, rule_id, config, ignore_ctx,
        processed_files); bundling them into a params object would add indirection
        without reducing the actual number of concerns the caller has to supply
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from src.core.linter_utils import is_ignored_path
from src.core.types import Violation
from src.orchestrator.language_detector import detect_language

from .config import DRYConfig
from .deduplicator import ViolationDeduplicator
from .duplicate_storage import DuplicateStorage
from .inline_ignore import InlineIgnoreParser
from .violation_builder import DRYViolationBuilder

if TYPE_CHECKING:
    from src.linter_config.ignore import IgnoreDirectiveParser


@dataclass
class IgnoreContext:
    """Context for ignore directive filtering."""

    inline_ignore: InlineIgnoreParser
    shared_parser: "IgnoreDirectiveParser | None" = None
    file_contents: dict[str, str] | None = None


class ViolationGenerator:
    """Generates violations from duplicate code blocks."""

    def __init__(self) -> None:
        """Initialize with deduplicator and violation builder."""
        self._deduplicator = ViolationDeduplicator()
        self._violation_builder = DRYViolationBuilder()

    def generate_violations(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        storage: DuplicateStorage,
        rule_id: str,
        config: DRYConfig,
        ignore_ctx: IgnoreContext,
        processed_files: set[str],
    ) -> list[Violation]:
        """Generate violations from storage.

        Args:
            storage: Duplicate storage instance
            rule_id: Rule identifier for violations
            config: DRY configuration with ignore patterns
            ignore_ctx: Context containing ignore parsers and file contents
            processed_files: Absolute-path strings of files this invocation processed.
                A duplicate group with no occurrence in this set is dropped entirely -
                see module docstring.

        Returns:
            List of violations filtered by ignore patterns and inline directives
        """
        raw_violations = self._collect_violations(storage, rule_id, config, processed_files)
        deduplicated = self._deduplicator.deduplicate_violations(raw_violations)
        pattern_filtered = self._filter_ignored(deduplicated, config.ignore_patterns)
        inline_filtered = self._filter_inline_ignored(pattern_filtered, ignore_ctx.inline_ignore)

        # Apply shared ignore directive filtering for block and line directives
        if ignore_ctx.shared_parser and ignore_ctx.file_contents:
            return self._filter_shared_ignored(
                inline_filtered, ignore_ctx.shared_parser, ignore_ctx.file_contents
            )

        return inline_filtered

    def _collect_violations(
        self,
        storage: DuplicateStorage,
        rule_id: str,
        config: DRYConfig,
        processed_files: set[str],
    ) -> list[Violation]:
        """Collect raw violations from storage duplicate hashes.

        Args:
            storage: Duplicate storage instance
            rule_id: Rule identifier for violations
            config: DRY configuration
            processed_files: Absolute-path strings of files this invocation processed

        Returns:
            List of raw violations before filtering
        """
        violations = []
        blocks_by_hash = storage.get_blocks_for_hashes(storage.duplicate_hashes)
        for blocks in blocks_by_hash.values():
            dedup_blocks = self._deduplicator.deduplicate_blocks(blocks)

            if not self._meets_min_occurrences(dedup_blocks, config):
                continue

            if not self._touches_invocation(dedup_blocks, processed_files):
                continue

            for block in dedup_blocks:
                violation = self._violation_builder.build_violation(block, dedup_blocks, rule_id)
                violations.append(violation)

        return violations

    def _touches_invocation(self, blocks: list, processed_files: set[str]) -> bool:
        """Check whether any occurrence in a duplicate group is a file this run processed.

        Args:
            blocks: Deduplicated occurrences of one duplicate-hash group
            processed_files: Absolute-path strings of files this invocation processed

        Returns:
            True if at least one occurrence's file is in processed_files
        """
        return any(str(block.file_path) in processed_files for block in blocks)

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
            if not is_ignored_path(str(Path(violation.file_path)), ignore_patterns):
                filtered.append(violation)
        return filtered

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

    def _filter_shared_ignored(
        self,
        violations: list[Violation],
        ignore_parser: "IgnoreDirectiveParser",
        file_contents: dict[str, str],
    ) -> list[Violation]:
        """Filter violations using the shared ignore directive parser.

        This enables standard # thailint: ignore-start/end directives for DRY linter.

        Args:
            violations: List of violations to filter
            ignore_parser: Shared ignore directive parser
            file_contents: Cached file contents for ignore checking

        Returns:
            Filtered list of violations
        """
        filtered = []
        for violation in violations:
            file_content = file_contents.get(violation.file_path, "")
            if not ignore_parser.should_ignore_violation(violation, file_content):
                filtered.append(violation)
        return filtered
