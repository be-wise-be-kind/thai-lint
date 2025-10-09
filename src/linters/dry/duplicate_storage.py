"""
Purpose: Storage management for duplicate code blocks with cache and memory fallback

Scope: Manages storage of code blocks in SQLite cache or in-memory dict

Overview: Provides unified storage interface for code blocks supporting both SQLite-backed caching
    and in-memory fallback when cache disabled. Handles block insertion, retrieval, and duplicate
    hash queries. Encapsulates Decision 6 (in-memory fallback) implementation. Separates storage
    concerns from linting logic to maintain SRP compliance.

Dependencies: DRYCache, CodeBlock, Path

Exports: DuplicateStorage class

Interfaces: DuplicateStorage.add_blocks(file_path, blocks), get_duplicate_hashes(),
    get_blocks_for_hash(hash_value)

Implementation: Delegates to either SQLite cache or in-memory dict based on cache_enabled setting
"""

from pathlib import Path

from .cache import CodeBlock, DRYCache


class DuplicateStorage:
    """Manages storage of code blocks in cache or memory."""

    def __init__(self, cache: DRYCache | None) -> None:
        """Initialize storage with optional cache.

        Args:
            cache: SQLite cache instance (None for in-memory mode)
        """
        self._cache = cache
        self._memory_store: dict[int, list[CodeBlock]] = {}

    def add_blocks(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Add code blocks to storage and cache.

        Args:
            file_path: Path to source file
            blocks: List of code blocks to store
        """
        # Always add to memory for duplicate detection
        self._add_to_memory(blocks)

        # Also persist to cache if available
        if self._cache:
            self._add_to_cache(file_path, blocks)

    def add_blocks_to_memory(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Add code blocks to in-memory storage only (for cache hits).

        Args:
            file_path: Path to source file (used for cache persistence check)
            blocks: List of code blocks to store
        """
        # Add to memory for duplicate detection this run
        self._add_to_memory(blocks)

        # Update cache with new blocks if needed (for fresh analysis)
        # Skip if blocks were loaded from cache (they're already persisted)
        if self._cache and blocks:
            # Check if file analysis is fresh (not from cache)
            # This is indicated by the blocks not having been persisted yet
            # We can tell by checking mtime freshness
            try:
                mtime = file_path.stat().st_mtime
                if not self._cache.is_fresh(file_path, mtime):
                    # File was analyzed (not cached), so persist
                    self._add_to_cache(file_path, blocks)
            except OSError:
                # File doesn't exist, skip cache
                pass

    def get_duplicate_hashes(self) -> list[int]:
        """Get all hash values with 2+ occurrences from memory.

        Returns:
            List of hash values that appear in multiple blocks
        """
        # Always query from in-memory store for this run's files
        return [h for h, blocks in self._memory_store.items() if len(blocks) >= 2]

    def get_blocks_for_hash(self, hash_value: int) -> list[CodeBlock]:
        """Get all blocks with given hash value from memory.

        Args:
            hash_value: Hash to search for

        Returns:
            List of code blocks with this hash
        """
        # Always query from in-memory store for this run's files
        return self._memory_store.get(hash_value, [])

    def _add_to_cache(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Add blocks to SQLite cache."""
        if not self._cache or not blocks:
            return

        mtime = file_path.stat().st_mtime
        self._cache.save(file_path, mtime, blocks)

    def _add_to_memory(self, blocks: list[CodeBlock]) -> None:
        """Add blocks to in-memory store."""
        for block in blocks:
            if block.hash_value not in self._memory_store:
                self._memory_store[block.hash_value] = []
            self._memory_store[block.hash_value].append(block)
