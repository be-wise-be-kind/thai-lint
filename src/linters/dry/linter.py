"""
Purpose: Main DRY linter rule implementation with stateful caching

Scope: DRYRule class implementing BaseLintRule interface for duplicate code and constant detection

Overview: Implements DRY linter rule following BaseLintRule interface with stateful caching design.
    Orchestrates duplicate detection by delegating to specialized classes and functions:
    ConfigLoader for config, initialize_storage() for storage setup, FileAnalyzer for file
    analysis, ViolationGenerator for violation creation, and reconcile_stale_matches() for
    persistent-mode freshness verification. Also supports duplicate constant detection (opt-in)
    to identify when the same constant is defined in multiple files. Maintains minimal
    orchestration logic to comply with SRP.

Dependencies: BaseLintRule, BaseLintContext, ConfigLoader, initialize_storage, FileAnalyzer,
    DuplicateStorage, ViolationGenerator, reconcile_stale_matches, extract_python_constants,
    TypeScriptConstantExtractor, find_constant_groups, ConstantViolationBuilder

Exports: DRYRule class

Interfaces: DRYRule.check(context) -> list[Violation], finalize() -> list[Violation]

Implementation: Delegates all logic to helper classes, maintains only orchestration and state

Suppressions:
    - too-many-instance-attributes: DRYComponents groups helper dependencies; DRYRule has 8
        attributes due to stateful caching requirements (storage, config, constants, file contents
        for ignore directive processing)
    - B101: Type narrowing assertions after guards (storage initialized, file_path/content set)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import should_process_file
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .cache import DRYCache
from .config import DRYConfig
from .config_loader import ConfigLoader
from .constant import ConstantInfo
from .constant_matcher import find_constant_groups
from .constant_violation_builder import ConstantViolationBuilder
from .content_hash import compute_content_hash
from .duplicate_storage import DuplicateStorage
from .file_analyzer import FileAnalyzer
from .inline_ignore import InlineIgnoreParser
from .python_constant_extractor import extract_python_constants
from .stale_match_reconciler import reconcile_stale_matches
from .storage_initializer import initialize_storage
from .typescript_constant_extractor import TypeScriptConstantExtractor
from .violation_generator import IgnoreContext, ViolationGenerator


@dataclass
class DRYComponents:  # pylint: disable=too-many-instance-attributes
    """Component dependencies for DRY linter."""

    config_loader: ConfigLoader
    file_analyzer: FileAnalyzer
    violation_generator: ViolationGenerator
    inline_ignore: InlineIgnoreParser
    typescript_extractor: TypeScriptConstantExtractor
    constant_violation_builder: ConstantViolationBuilder


class DRYRule(BaseLintRule):  # pylint: disable=too-many-instance-attributes
    """Detects duplicate code across project files."""

    def __init__(self) -> None:
        """Initialize the DRY rule with helper components."""
        self._storage: DuplicateStorage | None = None
        self._initialized = False
        self._config: DRYConfig | None = None
        self._file_analyzer: FileAnalyzer | None = None
        self._project_root: Path | None = None

        # Collected constants for cross-file detection: list of (file_path, ConstantInfo)
        self._constants: list[tuple[Path, ConstantInfo]] = []

        # Cache file contents for ignore directive checking during finalize
        self._file_contents: dict[str, str] = {}

        # Files actually analyzed and upserted this run (persistent mode only): lets
        # finalize() tell which matched-against files were freshly scanned versus
        # indexed by a prior run and needing a freshness check before being trusted.
        self._processed_files: set[str] = set()

        # Helper components grouped to reduce instance attributes
        self._helpers = DRYComponents(
            config_loader=ConfigLoader(),
            file_analyzer=FileAnalyzer(),  # Placeholder, will be replaced with configured one
            violation_generator=ViolationGenerator(),
            inline_ignore=InlineIgnoreParser(),
            typescript_extractor=TypeScriptConstantExtractor(),
            constant_violation_builder=ConstantViolationBuilder(),
        )

    @property
    def _active_storage(self) -> DuplicateStorage:
        """Get storage, asserting it has been initialized."""
        assert self._storage is not None, "Storage not initialized"  # nosec B101
        return self._storage

    @property
    def _active_file_analyzer(self) -> FileAnalyzer:
        """Get file analyzer, asserting it has been initialized."""
        assert self._file_analyzer is not None, "File analyzer not initialized"  # nosec B101
        return self._file_analyzer

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
        """Analyze file and store blocks (collection phase)."""
        if not should_process_file(context):
            return []

        config = self._helpers.config_loader.load_config(context)
        if not config.enabled:
            return []

        self._config = self._config or config
        self._process_file(context, config)
        return []

    def _process_file(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Process a single file for duplicates and constants."""
        # should_process_file ensures file_path and file_content are set
        assert context.file_path is not None  # nosec B101
        assert context.file_content is not None  # nosec B101

        file_path = context.file_path
        # Cache file content for ignore directive checking in finalize
        self._file_contents[str(file_path)] = context.file_content
        # Get project root from context metadata if available
        if self._project_root is None:
            self._project_root = self._get_project_root(context)

        self._helpers.inline_ignore.parse_file(file_path, context.file_content)
        self._ensure_storage_initialized(config)
        self._analyze_if_not_ignored(context, config, file_path)
        if config.detect_duplicate_constants:
            self._extract_and_store_constants(context)

    def _analyze_if_not_ignored(
        self, context: BaseLintContext, config: DRYConfig, file_path: Path
    ) -> None:
        """Analyze and store blocks, unless the file matches a dry.ignore pattern."""
        if not self._is_ignored_path(file_path, config.ignore_patterns):
            self._analyze_and_store(context, config)

    @staticmethod
    def _is_ignored_path(file_path: Path, ignore_patterns: list[str]) -> bool:
        """Check whether a file matches a dry.ignore pattern.

        Mirrors ViolationGenerator._is_ignored so a matched file skips analysis
        entirely instead of paying full analysis cost only to be filtered later.
        """
        if not ignore_patterns:
            return False
        path_str = str(Path(file_path))
        return any(pattern in path_str for pattern in ignore_patterns)

    def _ensure_storage_initialized(self, config: DRYConfig) -> None:
        """Initialize storage and file analyzer on first call."""
        if not self._initialized:
            self._storage = initialize_storage(config, self._project_root)
            # Create file analyzer with config for filter configuration
            self._file_analyzer = FileAnalyzer(config)
            self._initialized = True

    def _analyze_and_store(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Analyze file and store blocks."""
        if not self._can_analyze(context):
            return
        # _can_analyze ensures file_path and file_content are set
        assert context.file_path is not None  # nosec B101
        assert context.file_content is not None  # nosec B101

        blocks = self._active_file_analyzer.analyze(
            context.file_path,
            context.file_content,
            context.language,
            config,
        )
        # Always upsert (even with zero blocks) so a file edited to remove its last
        # duplicated block still has its stale blocks deleted - the #35 regression fix.
        self._active_storage.upsert_file(
            context.file_path, compute_content_hash(context.file_content), blocks
        )
        self._processed_files.add(str(context.file_path))

    def _can_analyze(self, context: BaseLintContext) -> bool:
        """Check if context is ready for analysis."""
        return (
            context.file_path is not None
            and context.file_content is not None
            and self._file_analyzer is not None
            and self._storage is not None
        )

    def _extract_and_store_constants(self, context: BaseLintContext) -> None:
        """Extract constants from file and store for cross-file detection."""
        if context.file_path is None or context.file_content is None:
            return
        file_path = Path(context.file_path)
        extract_fn = _get_extractor_for_language(context.language, self._helpers)
        if extract_fn:
            self._constants.extend((file_path, c) for c in extract_fn(context.file_content))

    def _get_project_root(self, context: BaseLintContext) -> Path | None:
        """Get project root from context if available.

        Args:
            context: Lint context

        Returns:
            Project root path or None if not available
        """
        # Try to get from metadata (orchestrator sets this as "_project_root",
        # see Orchestrator.lint_file)
        if hasattr(context, "metadata") and isinstance(context.metadata, dict):
            project_root = context.metadata.get("_project_root")
            if project_root:
                return Path(project_root)

        # Fallback: derive from file path
        if context.file_path:
            return Path(context.file_path).parent

        return None

    def finalize(self) -> list[Violation]:
        """Generate violations after all files processed."""
        if not self._storage or not self._config:
            return []

        self._reconcile_stale_matches_if_persistent()

        # Create ignore context for violation filtering
        ignore_parser = IgnoreDirectiveParser(self._project_root)
        ignore_ctx = IgnoreContext(
            inline_ignore=self._helpers.inline_ignore,
            shared_parser=ignore_parser,
            file_contents=self._file_contents,
        )

        violations = self._helpers.violation_generator.generate_violations(
            self._storage, self.rule_id, self._config, ignore_ctx, self._processed_files
        )
        if self._config.detect_duplicate_constants and self._constants:
            constant_violations = _generate_constant_violations(
                self._constants, self._config, self._helpers, self.rule_id
            )
            # Filter constant violations through shared ignore parser
            constant_violations = _filter_ignored_violations(
                constant_violations, ignore_parser, self._file_contents
            )
            violations.extend(constant_violations)

        self._helpers.inline_ignore.clear()
        self._constants = []
        self._file_contents = {}
        self._processed_files = set()
        return violations

    def _reconcile_stale_matches_if_persistent(self) -> None:
        """Verify freshness of files matched against but not scanned this run.

        Only relevant in persistent mode: those files were indexed by a prior
        invocation and may have changed or been deleted since. Ephemeral modes never
        need this - every row in their table was written by this same run, so nothing
        external can be stale.
        """
        assert self._config is not None  # nosec B101
        if self._config.storage_mode != "persistent":
            return
        reconcile_stale_matches(
            self._active_storage, self._active_file_analyzer, self._config, self._processed_files
        )

    def get_parallel_shared_config(self, shared_dir: Path) -> dict[str, Any] | None:
        """Force a shared, on-disk store for the duration of one --parallel run.

        In-memory SQLite (":memory:") is fundamentally per-process/per-connection and can
        never be shared across worker processes, so parallel execution must use a real
        file on disk regardless of the configured storage_mode.
        """
        db_path = shared_dir / "dry_parallel.db"
        # Pre-create the file, schema, and WAL mode here in the main process (a single
        # connection, no contention) so worker processes never race each other to
        # initialize the same brand-new on-disk file - concurrent first-connections
        # attempting CREATE TABLE/PRAGMA journal_mode=WAL on the same not-yet-existing
        # file can raise "database is locked" even under a busy_timeout.
        DRYCache(storage_mode="tempfile", db_path=db_path).close()
        return {"dry": {"storage_mode": "tempfile", "shared_db_path": str(db_path)}}

    def finalize_after_parallel(self, raw_config: dict[str, Any]) -> list[Violation]:
        """Reconnect to the shared store workers wrote to, then finalize normally.

        check() never ran on this instance under --parallel (every file was processed by
        an isolated worker process); this points this instance at the same on-disk store
        those workers wrote to before delegating to the normal finalize() logic.
        """
        dry_config = raw_config.get("dry", {})
        self._config = self._config or DRYConfig.from_dict(dry_config)
        self._ensure_storage_initialized(self._config)
        # self._processed_files is empty on this instance (check() ran on workers, not
        # here). The shared store is a fresh, per-run file (see
        # get_parallel_shared_config), so every file in it belongs to this run - treat
        # all of it as in scope for report filtering, rather than filtering everything
        # out.
        self._processed_files = self._active_storage.all_file_paths
        return self.finalize()


ConstantExtractorFn = Callable[[str], list[ConstantInfo]]


def _get_extractor_for_language(
    language: str | None, helpers: DRYComponents
) -> ConstantExtractorFn | None:
    """Get the appropriate constant extractor function for a language."""
    extractors: dict[str, ConstantExtractorFn] = {
        "python": extract_python_constants,
        "typescript": helpers.typescript_extractor.extract,
        "javascript": helpers.typescript_extractor.extract,
    }
    return extractors.get(language or "")


def _generate_constant_violations(
    constants: list[tuple[Path, ConstantInfo]],
    config: DRYConfig,
    helpers: DRYComponents,
    rule_id: str,
) -> list[Violation]:
    """Generate violations for duplicate constants."""
    groups = find_constant_groups(constants)
    helpers.constant_violation_builder.min_occurrences = config.min_constant_occurrences
    return helpers.constant_violation_builder.build_violations(groups, rule_id)


def _filter_ignored_violations(
    violations: list[Violation],
    ignore_parser: IgnoreDirectiveParser,
    file_contents: dict[str, str],
) -> list[Violation]:
    """Filter violations through the shared ignore directive parser.

    Args:
        violations: List of violations to filter
        ignore_parser: Shared ignore directive parser
        file_contents: Cached file contents for checking ignore directives

    Returns:
        Filtered list of violations not matching ignore directives
    """
    filtered = []
    for violation in violations:
        file_content = file_contents.get(violation.file_path, "")
        if not ignore_parser.should_ignore_violation(violation, file_content):
            filtered.append(violation)
    return filtered
