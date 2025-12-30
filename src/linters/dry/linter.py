"""
Purpose: Main DRY linter rule implementation with stateful caching

Scope: DRYRule class implementing BaseLintRule interface for duplicate code and constant detection

Overview: Implements DRY linter rule following BaseLintRule interface with stateful caching design.
    Orchestrates duplicate detection by delegating to specialized classes: ConfigLoader for config,
    StorageInitializer for storage setup, FileAnalyzer for file analysis, and ViolationGenerator
    for violation creation. Also supports duplicate constant detection (opt-in) to identify when
    the same constant is defined in multiple files. Maintains minimal orchestration logic to comply
    with SRP.

Dependencies: BaseLintRule, BaseLintContext, ConfigLoader, StorageInitializer, FileAnalyzer,
    DuplicateStorage, ViolationGenerator, extract_python_constants, TypeScriptConstantExtractor,
    find_constant_groups, ConstantViolationBuilder

Exports: DRYRule class

Interfaces: DRYRule.check(context) -> list[Violation], finalize() -> list[Violation]

Implementation: Delegates all logic to helper classes, maintains only orchestration and state

Suppressions:
    - too-many-instance-attributes: DRYComponents groups related helper dependencies
    - B101: Type narrowing assertions after guards (storage initialized, file_path/content set)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import should_process_file
from src.core.types import Violation

from .config import DRYConfig
from .config_loader import ConfigLoader
from .constant import ConstantInfo
from .constant_matcher import find_constant_groups
from .constant_violation_builder import ConstantViolationBuilder
from .duplicate_storage import DuplicateStorage
from .file_analyzer import FileAnalyzer
from .inline_ignore import InlineIgnoreParser
from .python_constant_extractor import extract_python_constants
from .storage_initializer import StorageInitializer
from .typescript_constant_extractor import TypeScriptConstantExtractor
from .violation_generator import ViolationGenerator


@dataclass
class DRYComponents:  # pylint: disable=too-many-instance-attributes
    """Component dependencies for DRY linter."""

    config_loader: ConfigLoader
    storage_initializer: StorageInitializer
    file_analyzer: FileAnalyzer
    violation_generator: ViolationGenerator
    inline_ignore: InlineIgnoreParser
    typescript_extractor: TypeScriptConstantExtractor
    constant_violation_builder: ConstantViolationBuilder


class DRYRule(BaseLintRule):
    """Detects duplicate code across project files."""

    def __init__(self) -> None:
        """Initialize the DRY rule with helper components."""
        self._storage: DuplicateStorage | None = None
        self._initialized = False
        self._config: DRYConfig | None = None
        self._file_analyzer: FileAnalyzer | None = None

        # Collected constants for cross-file detection: list of (file_path, ConstantInfo)
        self._constants: list[tuple[Path, ConstantInfo]] = []

        # Helper components grouped to reduce instance attributes
        self._helpers = DRYComponents(
            config_loader=ConfigLoader(),
            storage_initializer=StorageInitializer(),
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
        self._helpers.inline_ignore.parse_file(file_path, context.file_content)
        self._ensure_storage_initialized(context, config)
        self._analyze_and_store(context, config)
        if config.detect_duplicate_constants:
            self._extract_and_store_constants(context)

    def _ensure_storage_initialized(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Initialize storage and file analyzer on first call."""
        if not self._initialized:
            self._storage = self._helpers.storage_initializer.initialize(context, config)
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
        if blocks:
            self._active_storage.add_blocks(context.file_path, blocks)

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

    def finalize(self) -> list[Violation]:
        """Generate violations after all files processed."""
        if not self._storage or not self._config:
            return []
        violations = self._helpers.violation_generator.generate_violations(
            self._storage, self.rule_id, self._config, self._helpers.inline_ignore
        )
        if self._config.detect_duplicate_constants and self._constants:
            violations.extend(
                _generate_constant_violations(
                    self._constants, self._config, self._helpers, self.rule_id
                )
            )
        self._helpers.inline_ignore.clear()
        self._constants = []
        return violations


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
