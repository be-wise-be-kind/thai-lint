"""
Purpose: Storage management for duplicate code blocks in SQLite

Scope: Manages storage of code blocks in SQLite for duplicate detection

Overview: Provides storage interface for code blocks using SQLite (in-memory or tempfile mode).
    Handles block insertion and duplicate hash queries. Delegates all storage operations to
    DRYCache SQLite layer. Separates storage concerns from linting logic to maintain SRP compliance.

Dependencies: DRYCache, CodeBlock, Path

Exports: DuplicateStorage class

Interfaces: DuplicateStorage.add_blocks(file_path, blocks), duplicate_hashes property,
    get_blocks_for_hash(hash_value)

Implementation: Delegates to SQLite cache for all storage operations
"""

from pathlib import Path

from .cache import CodeBlock, DRYCache


class DuplicateStorage:
    """Manages storage of code blocks in SQLite."""

    def __init__(self, cache: DRYCache) -> None:
        """Initialize storage with SQLite cache.

        Args:
            cache: SQLite cache instance (in-memory or tempfile mode)
        """
        self._cache = cache

    def add_blocks(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Add code blocks to SQLite storage.

        Args:
            file_path: Path to source file
            blocks: List of code blocks to store
        """
        if blocks:
            self._cache.add_blocks(file_path, blocks)

    @property
    def duplicate_hashes(self) -> list[int]:
        """Hash values with 2+ occurrences from SQLite.

        Returns:
            List of hash values that appear in multiple blocks
        """
        return self._cache.duplicate_hashes

    def get_blocks_for_hash(self, hash_value: int) -> list[CodeBlock]:
        """Get all blocks with given hash value from SQLite.

        Args:
            hash_value: Hash to search for

        Returns:
            List of code blocks with this hash
        """
        return self._cache.find_duplicates_by_hash(hash_value)
