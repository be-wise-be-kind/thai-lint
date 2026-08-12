"""
Purpose: Storage initialization for DRY linter

Scope: Initializes DuplicateStorage with SQLite storage

Overview: Handles storage initialization based on DRY configuration. Creates SQLite storage in
    either memory or tempfile mode based on config.storage_mode. Separates initialization logic
    from main linter rule to maintain SRP compliance.

Dependencies: DRYConfig, DRYCache, DuplicateStorage

Exports: StorageInitializer class

Interfaces: StorageInitializer.initialize(config) -> DuplicateStorage

Implementation: Creates DRYCache with storage_mode, delegates to DuplicateStorage for management
"""

from pathlib import Path

from .cache import DRYCache
from .config import DRYConfig
from .duplicate_storage import DuplicateStorage


class StorageInitializer:
    """Initializes storage for duplicate detection."""

    def initialize(self, config: DRYConfig) -> DuplicateStorage:
        """Initialize storage based on configuration.

        Args:
            config: DRY configuration

        Returns:
            DuplicateStorage instance with SQLite storage
        """
        # Create SQLite storage (in-memory or tempfile based on config). When
        # config.shared_db_path is set (parallel execution), every worker plus the
        # main process connect to the same on-disk file for this one run.
        db_path = Path(config.shared_db_path) if config.shared_db_path else None
        cache = DRYCache(storage_mode=config.storage_mode, db_path=db_path)

        return DuplicateStorage(cache)
