"""
Purpose: Main DRY linter rule implementation with stateful caching

Scope: DRYRule class implementing BaseLintRule interface for duplicate code detection

Overview: Implements DRY linter rule following BaseLintRule interface with stateful caching design.
    Orchestrates duplicate detection by delegating to specialized classes: ConfigLoader for config,
    StorageInitializer for storage setup, FileAnalyzer for file analysis, and ViolationGenerator
    for violation creation. Maintains minimal orchestration logic to comply with SRP (8 methods total).

Dependencies: BaseLintRule, BaseLintContext, ConfigLoader, StorageInitializer, FileAnalyzer,
    DuplicateStorage, ViolationGenerator

Exports: DRYRule class

Interfaces: DRYRule.check(context) -> list[Violation], finalize() -> list[Violation]

Implementation: Delegates all logic to helper classes, maintains only orchestration and state
"""

from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Violation

from .config_loader import ConfigLoader
from .duplicate_storage import DuplicateStorage
from .file_analyzer import FileAnalyzer
from .storage_initializer import StorageInitializer
from .violation_generator import ViolationGenerator


class DRYRule(BaseLintRule):
    """Detects duplicate code across project files."""

    def __init__(self) -> None:
        """Initialize the DRY rule with helper components."""
        self._storage: DuplicateStorage | None = None
        self._initialized = False

        # Helper components
        self._config_loader = ConfigLoader()
        self._storage_initializer = StorageInitializer()
        self._file_analyzer = FileAnalyzer()
        self._violation_generator = ViolationGenerator()

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

        Args:
            context: Lint context with file information

        Returns:
            Empty list (violations returned in finalize())
        """
        if not self._should_process_file(context):
            return []

        config = self._config_loader.load_config(context)
        if not config.enabled:
            return []

        self._ensure_storage_initialized(context, config)
        self._analyze_and_store(context, config)

        return []

    def _should_process_file(self, context: BaseLintContext) -> bool:
        """Check if file should be processed."""
        return context.file_content is not None and context.file_path is not None

    def _ensure_storage_initialized(self, context: BaseLintContext, config) -> None:
        """Initialize storage on first call."""
        if not self._initialized:
            self._storage = self._storage_initializer.initialize(context, config)
            self._initialized = True

    def _analyze_and_store(self, context: BaseLintContext, config) -> None:
        """Analyze file and store blocks."""
        file_path = Path(context.file_path)  # type: ignore[arg-type]
        cache = self._storage._cache if self._storage else None  # pylint: disable=protected-access
        blocks = self._file_analyzer.analyze_or_load(
            file_path, context.file_content, context.language, config, cache
        )

        if blocks and self._storage:
            self._storage.add_blocks(file_path, blocks)

    def finalize(self) -> list[Violation]:
        """Generate violations after all files processed.

        Returns:
            List of all violations found across all files
        """
        if not self._storage:
            return []

        return self._violation_generator.generate_violations(self._storage, self.rule_id)
