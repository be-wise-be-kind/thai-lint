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

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import should_process_file
from src.core.types import Violation

from .config import DRYConfig
from .config_loader import ConfigLoader
from .duplicate_storage import DuplicateStorage
from .file_analyzer import FileAnalyzer
from .inline_ignore import InlineIgnoreParser
from .storage_initializer import StorageInitializer
from .violation_generator import ViolationGenerator

if TYPE_CHECKING:
    from .cache import CodeBlock


@dataclass
class DRYComponents:
    """Component dependencies for DRY linter."""

    config_loader: ConfigLoader
    storage_initializer: StorageInitializer
    file_analyzer: FileAnalyzer
    violation_generator: ViolationGenerator
    inline_ignore: InlineIgnoreParser


class DRYRule(BaseLintRule):
    """Detects duplicate code across project files."""

    def __init__(self) -> None:
        """Initialize the DRY rule with helper components."""
        self._storage: DuplicateStorage | None = None
        self._initialized = False
        self._config: DRYConfig | None = None
        self._file_analyzer: FileAnalyzer | None = None

        # Helper components grouped to reduce instance attributes
        self._helpers = DRYComponents(
            config_loader=ConfigLoader(),
            storage_initializer=StorageInitializer(),
            file_analyzer=FileAnalyzer(),  # Placeholder, will be replaced with configured one
            violation_generator=ViolationGenerator(),
            inline_ignore=InlineIgnoreParser(),
        )

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
        if not should_process_file(context):
            return []

        config = self._helpers.config_loader.load_config(context)
        if not config.enabled:
            return []

        # Store config for finalize()
        if self._config is None:
            self._config = config

        # Parse inline ignore directives from this file
        file_path = Path(context.file_path)  # type: ignore[arg-type]
        self._helpers.inline_ignore.parse_file(file_path, context.file_content or "")

        self._ensure_storage_initialized(context, config)
        self._analyze_and_store(context, config)

        return []

    def _ensure_storage_initialized(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Initialize storage and file analyzer on first call."""
        if not self._initialized:
            self._storage = self._helpers.storage_initializer.initialize(context, config)
            # Create file analyzer with config for filter configuration
            self._file_analyzer = FileAnalyzer(config)
            self._initialized = True

    def _analyze_and_store(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Analyze file and store blocks."""
        # Guaranteed by _should_process_file check
        if context.file_path is None or context.file_content is None:
            return  # Should never happen due to should_process_file check

        if not self._file_analyzer:
            return  # Should never happen after initialization

        file_path = Path(context.file_path)
        blocks = self._file_analyzer.analyze(
            file_path, context.file_content, context.language, config
        )

        if blocks:
            self._store_blocks(file_path, blocks)

    def _store_blocks(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Store blocks in SQLite if storage available."""
        if self._storage:
            self._storage.add_blocks(file_path, blocks)

    def finalize(self) -> list[Violation]:
        """Generate violations after all files processed.

        Returns:
            List of all violations found across all files
        """
        if not self._storage or not self._config:
            return []

        violations = self._helpers.violation_generator.generate_violations(
            self._storage, self.rule_id, self._config, self._helpers.inline_ignore
        )

        # Clear inline ignore cache for next run
        self._helpers.inline_ignore.clear()

        return violations
