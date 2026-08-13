"""
Purpose: Storage management for duplicate code blocks in SQLite

Scope: Manages storage of code blocks in SQLite for duplicate detection

Overview: Provides storage interface for code blocks using SQLite (memory, tempfile, or
    persistent mode). Handles block upsertion, freshness checks, and duplicate hash queries.
    Delegates all storage operations to the DRYCache SQLite layer. Separates storage concerns
    from linting logic to maintain SRP compliance.

Dependencies: DRYCache, CodeBlock, Path

Exports: DuplicateStorage class

Interfaces: DuplicateStorage.upsert_file(file_path, content_hash, blocks), needs_rescan(file_path,
    content_hash), purge_file(file_path), duplicate_hashes property,
    get_blocks_for_hash(hash_value), get_blocks_for_hashes(hash_values), all_file_paths property

Implementation: Delegates to SQLite cache for all storage operations
"""

from pathlib import Path

from .cache import CodeBlock, DRYCache


class DuplicateStorage:
    """Manages storage of code blocks in SQLite."""

    def __init__(self, cache: DRYCache) -> None:
        """Initialize storage with SQLite cache.

        Args:
            cache: SQLite cache instance (memory, tempfile, or persistent mode)
        """
        self._cache = cache

    def upsert_file(self, file_path: Path, content_hash: str, blocks: list[CodeBlock]) -> None:
        """Replace all stored blocks for a file with fresh ones.

        Runs unconditionally, even when blocks is empty - a file edited to remove its
        last duplicated block must still have its stale blocks deleted (see
        DRYCache.upsert_file).

        Args:
            file_path: Path to source file
            content_hash: Hash of the file's current content
            blocks: List of code blocks to store (may be empty)
        """
        self._cache.upsert_file(file_path, content_hash, blocks)

    def needs_rescan(self, file_path: Path, current_content_hash: str) -> bool:
        """Check whether a file's indexed content is stale.

        Args:
            file_path: Path to source file
            current_content_hash: Hash of the file's current on-disk content

        Returns:
            True if the file needs to be (re)scanned
        """
        return self._cache.needs_rescan(file_path, current_content_hash)

    def purge_file(self, file_path: Path) -> None:
        """Remove a file's entries entirely (e.g. it was deleted from disk).

        Args:
            file_path: Path to source file
        """
        self._cache.purge_file(file_path)

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

    def get_blocks_for_hashes(self, hash_values: list[int]) -> dict[int, list[CodeBlock]]:
        """Get all blocks for multiple hash values in one batched query.

        Args:
            hash_values: Hashes to search for

        Returns:
            Mapping of hash_value to its list of code blocks
        """
        return self._cache.find_duplicates_by_hashes(hash_values)

    @property
    def all_file_paths(self) -> set[str]:
        """Every file path currently indexed.

        Returns:
            Set of all file_path strings currently in storage
        """
        return self._cache.all_file_paths
