"""
Purpose: Storage initialization for stringly-typed linter

Scope: Initializes StringlyTypedStorage with SQLite storage

Overview: Handles storage initialization for stringly-typed pattern detection. Creates SQLite
    storage in either memory or tempfile mode based on config.storage_mode. Separates
    initialization logic from main linter rule to maintain SRP compliance.

Dependencies: StringlyTypedConfig, StringlyTypedStorage

Exports: StorageInitializer class

Interfaces: StorageInitializer.initialize(config) -> StringlyTypedStorage

Implementation: Creates StringlyTypedStorage with storage_mode, and an explicit shared db_path
    when config.shared_db_path is set (parallel execution)
"""

from pathlib import Path

from .config import StringlyTypedConfig
from .storage import StringlyTypedStorage


class StorageInitializer:
    """Initializes storage for stringly-typed pattern detection."""

    def initialize(self, config: StringlyTypedConfig) -> StringlyTypedStorage:
        """Initialize storage based on configuration.

        Args:
            config: Stringly-typed configuration

        Returns:
            StringlyTypedStorage instance with SQLite storage
        """
        # When config.shared_db_path is set (parallel execution), every worker plus the
        # main process connect to the same on-disk file for this one run.
        db_path = Path(config.shared_db_path) if config.shared_db_path else None
        return StringlyTypedStorage(storage_mode=config.storage_mode, db_path=db_path)
