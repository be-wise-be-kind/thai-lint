"""
Purpose: Storage initialization for stringly-typed linter

Scope: Initializes StringlyTypedStorage with SQLite storage

Overview: Handles storage initialization for stringly-typed pattern detection. Creates SQLite
    storage in memory mode for efficient cross-file analysis during a single linter run.
    Separates initialization logic from main linter rule to maintain SRP compliance.

Dependencies: BaseLintContext, StringlyTypedConfig, StringlyTypedStorage

Exports: StorageInitializer class

Interfaces: StorageInitializer.initialize(context, config) -> StringlyTypedStorage

Implementation: Creates StringlyTypedStorage with memory mode for fast in-memory storage
"""

from src.core.base import BaseLintContext

from .config import StringlyTypedConfig
from .storage import StringlyTypedStorage


class StorageInitializer:
    """Initializes storage for stringly-typed pattern detection."""

    def initialize(
        self, context: BaseLintContext, config: StringlyTypedConfig
    ) -> StringlyTypedStorage:
        """Initialize storage based on configuration.

        Args:
            context: Lint context (reserved for future use)
            config: Stringly-typed configuration (reserved for future storage_mode)

        Returns:
            StringlyTypedStorage instance with SQLite storage
        """
        # Context and config reserved for future storage_mode configuration
        _ = context
        _ = config

        # Create SQLite storage in memory mode
        return StringlyTypedStorage(storage_mode="memory")
