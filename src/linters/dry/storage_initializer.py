"""
Purpose: Storage initialization for DRY linter

Scope: Initializes DuplicateStorage with cache or in-memory fallback

Overview: Handles storage initialization based on DRY configuration. Creates SQLite cache when
    cache_enabled is true, or triggers in-memory fallback when false (Decision 6). Separates
    initialization logic from main linter rule to maintain SRP compliance.

Dependencies: BaseLintContext, DRYConfig, DRYCache, DuplicateStorage, Path

Exports: StorageInitializer class

Interfaces: StorageInitializer.initialize(context, config) -> DuplicateStorage

Implementation: Creates cache if enabled, delegates to DuplicateStorage for storage management
"""

from pathlib import Path

from src.core.base import BaseLintContext

from .cache import DRYCache
from .config import DRYConfig
from .duplicate_storage import DuplicateStorage


class StorageInitializer:
    """Initializes storage for duplicate detection."""

    def initialize(self, context: BaseLintContext, config: DRYConfig) -> DuplicateStorage:
        """Initialize storage based on configuration.

        Args:
            context: Lint context
            config: DRY configuration

        Returns:
            DuplicateStorage instance
        """
        cache = None
        if config.cache_enabled:
            # Use SQLite cache
            metadata = getattr(context, "metadata", {})
            project_root = metadata.get("_project_root", Path.cwd())
            cache_path = project_root / config.cache_path
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache = DRYCache(cache_path)
        # else: cache = None triggers in-memory fallback in DuplicateStorage

        return DuplicateStorage(cache)
