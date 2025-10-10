"""
Purpose: Storage initialization for DRY linter

Scope: Initializes DuplicateStorage with SQLite storage

Overview: Handles storage initialization based on DRY configuration. Creates SQLite storage in
    either memory or tempfile mode based on config.storage_mode. Separates initialization logic
    from main linter rule to maintain SRP compliance.

Dependencies: BaseLintContext, DRYConfig, DRYCache, DuplicateStorage

Exports: StorageInitializer class

Interfaces: StorageInitializer.initialize(context, config) -> DuplicateStorage

Implementation: Creates DRYCache with storage_mode, delegates to DuplicateStorage for management
"""

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
            DuplicateStorage instance with SQLite storage
        """
        # Create SQLite storage (in-memory or tempfile based on config)
        cache = DRYCache(storage_mode=config.storage_mode)

        return DuplicateStorage(cache)
