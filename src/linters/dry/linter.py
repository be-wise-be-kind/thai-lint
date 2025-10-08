"""
Purpose: Main DRY linter rule implementation with stateful caching

Scope: DRYRule class implementing BaseLintRule interface for duplicate code detection

Overview: Implements DRY linter rule following BaseLintRule interface with stateful caching design.
    Orchestrates configuration loading, cache management, language-specific analysis, and violation
    building. Maintains persistent cache across all check() calls for cross-file duplicate detection.
    Implements Decision 6 with in-memory fallback when cache disabled. Supports Python and TypeScript
    through analyzer delegation. Uses single-pass streaming algorithm where each file is analyzed
    or loaded from cache, queried for duplicates, and violations reported immediately.

Dependencies: BaseLintRule, BaseLintContext, DRYConfig, DRYCache, PythonDuplicateAnalyzer,
    TypeScriptDuplicateAnalyzer, DRYViolationBuilder, CodeBlock

Exports: DRYRule class

Interfaces: DRYRule.check(context) -> list[Violation], properties for rule metadata

Implementation: Stateful design with lazy cache initialization, in-memory fallback for cache_enabled
    false, single-pass streaming with per-file violation reporting, language-specific analyzers
"""

from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Violation

from .cache import CodeBlock, DRYCache
from .config import DRYConfig
from .python_analyzer import PythonDuplicateAnalyzer
from .typescript_analyzer import TypeScriptDuplicateAnalyzer
from .violation_builder import DRYViolationBuilder


class DRYRule(BaseLintRule):
    """Detects duplicate code across project files."""

    def __init__(self) -> None:
        """Initialize the DRY rule with stateful cache."""
        # Stateful components - persist across all check() calls
        self._cache: DRYCache | None = None
        self._memory_store: dict[int, list[CodeBlock]] = {}
        self._initialized = False
        self._cache_enabled = True

        # Analyzers and builders
        self._python_analyzer = PythonDuplicateAnalyzer()
        self._typescript_analyzer = TypeScriptDuplicateAnalyzer()
        self._violation_builder = DRYViolationBuilder()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "dry.duplicate-code"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Duplicate Code"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Detects duplicate code blocks across the project"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Analyze file and store blocks (collection phase).

        This method analyzes each file and stores code blocks in the cache/memory.
        Violations are NOT returned here - they are generated in finalize() after
        all files have been processed.

        Args:
            context: Lint context with file information

        Returns:
            Empty list (violations returned in finalize())
        """
        if not self._should_process(context):
            return []

        config = self._load_config(context)
        if not config.enabled:
            return []

        self._ensure_initialized(context, config)

        file_path = Path(context.file_path)  # type: ignore[arg-type]
        blocks = self._analyze_or_load(file_path, context.file_content, context.language, config)

        if blocks:
            self._add_blocks_to_storage(file_path, blocks)

        return []

    def _should_process(self, context: BaseLintContext) -> bool:
        """Check if context should be processed."""
        return context.file_content is not None and context.file_path is not None

    def _ensure_initialized(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Ensure cache is initialized on first call."""
        if not self._initialized:
            self._initialize_cache(context, config)
            self._initialized = True

    def _load_config(self, context: BaseLintContext) -> DRYConfig:
        """Load configuration from context metadata.

        Args:
            context: Lint context containing metadata

        Returns:
            DRYConfig instance
        """
        metadata = getattr(context, "metadata", None)
        if metadata is None or not isinstance(metadata, dict):
            return DRYConfig()

        config_dict = metadata.get("dry", {})
        if not isinstance(config_dict, dict):
            return DRYConfig()

        return DRYConfig.from_dict(config_dict)

    def _initialize_cache(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Initialize cache on first check() call (Decision 6).

        Args:
            context: Lint context
            config: DRY configuration
        """
        self._cache_enabled = config.cache_enabled

        if config.cache_enabled:
            # Use SQLite cache
            project_root = getattr(context, "project_root", Path.cwd())
            cache_path = project_root / config.cache_path
            self._cache = DRYCache(cache_path)
        else:
            # Use in-memory fallback (Decision 6)
            self._cache = None
            self._memory_store = {}

    def _analyze_or_load(
        self, file_path: Path, content: str, language: str, config: DRYConfig
    ) -> list[CodeBlock]:
        """Analyze file or load from cache.

        Args:
            file_path: Path to file
            content: File content
            language: File language
            config: DRY configuration

        Returns:
            List of CodeBlock instances
        """
        # Check if file is fresh in cache
        if self._cache:
            mtime = file_path.stat().st_mtime
            if self._cache.is_fresh(file_path, mtime):
                # Load from cache (already in DB, no need to re-add)
                return self._cache.load(file_path)

        # Analyze file based on language
        if language == "python":
            blocks = self._python_analyzer.analyze(file_path, content, config)
        elif language in ("typescript", "javascript"):
            blocks = self._typescript_analyzer.analyze(file_path, content, config)
        else:
            blocks = []

        return blocks

    def _add_blocks_to_storage(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Add blocks to cache or memory storage.

        Args:
            file_path: Path to file
            blocks: List of code blocks
        """
        if self._cache:
            self._add_to_cache(file_path, blocks)
        else:
            self._add_to_memory(blocks)

    def _add_to_cache(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Add blocks to SQLite cache."""
        if self._cache is None:
            return
        mtime = file_path.stat().st_mtime
        self._cache.add_blocks(file_path, mtime, blocks)

    def _add_to_memory(self, blocks: list[CodeBlock]) -> None:
        """Add blocks to in-memory store."""
        for block in blocks:
            if block.hash_value not in self._memory_store:
                self._memory_store[block.hash_value] = []
            self._memory_store[block.hash_value].append(block)

    def finalize(self) -> list[Violation]:
        """Finalize analysis and generate violations after all files processed.

        Queries database/memory for all duplicate hashes and creates violations
        for each participating code block (per-file reporting pattern).
        Deduplicates overlapping violations in the same file.

        Returns:
            List of all violations found across all files
        """
        duplicate_hashes = self._get_duplicate_hashes()
        violations = self._create_violations_for_hashes(duplicate_hashes)
        return self._deduplicate_overlapping_violations(violations)

    def _get_duplicate_hashes(self) -> list[int]:
        """Get all hash values with 2+ occurrences."""
        if self._cache:
            return self._cache.get_duplicate_hashes()
        return [hash_val for hash_val, blocks in self._memory_store.items() if len(blocks) >= 2]

    def _create_violations_for_hashes(self, hashes: list[int]) -> list[Violation]:
        """Create violations for all duplicate hashes."""
        violations = []
        for hash_value in hashes:
            blocks = self._get_blocks_for_hash(hash_value)
            dedup_blocks = self._deduplicate_overlapping_blocks(blocks)
            violations.extend(self._build_violations_for_blocks(dedup_blocks))
        return violations

    def _get_blocks_for_hash(self, hash_value: int) -> list[CodeBlock]:
        """Get all blocks for given hash."""
        if self._cache:
            return self._cache.find_duplicates_by_hash(hash_value)
        return self._memory_store[hash_value]

    def _build_violations_for_blocks(self, blocks: list[CodeBlock]) -> list[Violation]:
        """Build violations for code blocks."""
        return [
            self._violation_builder.build_violation(block, blocks, self.rule_id) for block in blocks
        ]

    def _deduplicate_overlapping_blocks(self, blocks: list[CodeBlock]) -> list[CodeBlock]:
        """Remove overlapping blocks within the same file.

        When rolling hash creates overlapping windows (e.g., lines 2-4, 3-5, 4-6),
        keep only the first block per file to avoid duplicate violations.

        Args:
            blocks: List of code blocks with same hash

        Returns:
            Deduplicated list with one block per file
        """
        # Group blocks by file
        blocks_by_file: dict[Path, list[CodeBlock]] = {}
        for block in blocks:
            if block.file_path not in blocks_by_file:
                blocks_by_file[block.file_path] = []
            blocks_by_file[block.file_path].append(block)

        # For each file, keep only the first block (earliest start_line)
        deduplicated = []
        for _file_path, file_blocks in blocks_by_file.items():
            # Sort by start_line and keep the first one
            file_blocks_sorted = sorted(file_blocks, key=lambda b: b.start_line)
            deduplicated.append(file_blocks_sorted[0])

        return deduplicated

    def _deduplicate_overlapping_violations(self, violations: list[Violation]) -> list[Violation]:
        """Remove overlapping violations from the same file."""
        violations_by_file = self._group_violations_by_file(violations)
        deduplicated = []

        for file_violations in violations_by_file.values():
            sorted_violations = sorted(file_violations, key=lambda v: v.line)
            kept = self._filter_overlapping_violations(sorted_violations)
            deduplicated.extend(kept)

        return deduplicated

    def _group_violations_by_file(self, violations: list[Violation]) -> dict[str, list[Violation]]:
        """Group violations by file path."""
        by_file: dict[str, list[Violation]] = {}
        for violation in violations:
            if violation.file_path not in by_file:
                by_file[violation.file_path] = []
            by_file[violation.file_path].append(violation)
        return by_file

    def _filter_overlapping_violations(self, sorted_violations: list[Violation]) -> list[Violation]:
        """Filter out violations that overlap with earlier ones."""
        kept: list[Violation] = []
        for violation in sorted_violations:
            if not self._overlaps_with_any(violation, kept):
                kept.append(violation)
        return kept

    def _overlaps_with_any(self, violation: Violation, kept_violations: list[Violation]) -> bool:
        """Check if violation overlaps with any kept violation."""
        for kept in kept_violations:
            if violation.line <= kept.line + 2:  # Rough 3-line estimate
                return True
        return False
