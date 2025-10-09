"""
Purpose: SQLite cache manager for DRY linter with mtime-based invalidation

Scope: Code block storage, cache operations, and duplicate detection queries

Overview: Implements persistent caching layer for duplicate code detection using SQLite database.
    Stores code blocks with hash values, file locations, and metadata. Provides mtime-based cache
    invalidation to detect stale entries. Serves dual purpose as both cache (avoid re-hashing) and
    hash table (query duplicates across project). Includes indexes for fast hash lookups enabling
    cross-file duplicate detection with minimal overhead.

Dependencies: Python sqlite3 module (stdlib), pathlib.Path, dataclasses

Exports: CodeBlock dataclass, DRYCache class

Interfaces: DRYCache.__init__, is_fresh, load, save, find_duplicates_by_hash, get_blocks_for_file,
    add_blocks, cleanup_stale, close

Implementation: SQLite with two tables (files, code_blocks), indexed on hash_value for performance,
    ACID transactions for reliability, foreign key constraints for data integrity
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .cache_query import CacheQueryService


@dataclass
class CodeBlock:
    """Represents a code block location with hash."""

    file_path: Path
    start_line: int
    end_line: int
    snippet: str
    hash_value: int


class DRYCache:
    """SQLite-backed cache for duplicate detection."""

    SCHEMA_VERSION = 1

    def __init__(self, cache_path: Path) -> None:
        """Initialize cache with SQLite database.

        Args:
            cache_path: Path to SQLite database file
        """
        # Ensure parent directory exists
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        self.db = sqlite3.connect(str(cache_path))
        self._query_service = CacheQueryService()

        # Create schema
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS files (
                file_path TEXT PRIMARY KEY,
                mtime REAL NOT NULL,
                hash_count INTEGER,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )

        self.db.execute(
            """CREATE TABLE IF NOT EXISTS code_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                hash_value INTEGER NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                snippet TEXT NOT NULL,
                FOREIGN KEY (file_path) REFERENCES files(file_path) ON DELETE CASCADE
            )"""
        )

        self.db.execute("CREATE INDEX IF NOT EXISTS idx_hash_value ON code_blocks(hash_value)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON code_blocks(file_path)")

        self.db.commit()

    def is_fresh(self, file_path: Path, current_mtime: float) -> bool:
        """Check if cached data is fresh (mtime matches).

        Args:
            file_path: Path to file
            current_mtime: Current modification time

        Returns:
            True if cache is fresh, False if stale or missing
        """
        cursor = self.db.execute("SELECT mtime FROM files WHERE file_path = ?", (str(file_path),))
        row = cursor.fetchone()

        if not row:
            return False  # Not in cache

        cached_mtime = row[0]
        return cached_mtime == current_mtime

    def load(self, file_path: Path) -> list[CodeBlock]:
        """Load cached code blocks for file.

        Args:
            file_path: Path to file

        Returns:
            List of CodeBlock instances from cache
        """
        cursor = self.db.execute(
            """SELECT hash_value, start_line, end_line, snippet
               FROM code_blocks
               WHERE file_path = ?""",
            (str(file_path),),
        )

        blocks = []
        for hash_val, start, end, snippet in cursor:
            block = CodeBlock(
                file_path=file_path,
                start_line=start,
                end_line=end,
                snippet=snippet,
                hash_value=hash_val,
            )
            blocks.append(block)

        return blocks

    def save(self, file_path: Path, mtime: float, blocks: list[CodeBlock]) -> None:
        """Save code blocks to cache.

        Args:
            file_path: Path to file
            mtime: File modification time
            blocks: List of CodeBlock instances to cache
        """
        # Delete old data for this file
        self.db.execute("DELETE FROM files WHERE file_path = ?", (str(file_path),))

        # Insert file metadata
        self.db.execute(
            "INSERT INTO files (file_path, mtime, hash_count) VALUES (?, ?, ?)",
            (str(file_path), mtime, len(blocks)),
        )

        # Insert code blocks
        for block in blocks:
            self.db.execute(
                """INSERT INTO code_blocks
                   (file_path, hash_value, start_line, end_line, snippet)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    str(file_path),
                    block.hash_value,
                    block.start_line,
                    block.end_line,
                    block.snippet,
                ),
            )

        self.db.commit()

    def cleanup_stale(self, max_age_days: int) -> None:
        """Remove cache entries older than max_age_days.

        Args:
            max_age_days: Maximum age in days for cache entries
        """
        # Use parameterized query to prevent SQL injection
        self.db.execute(
            """DELETE FROM files
               WHERE last_scanned < datetime('now', ? || ' days')""",
            (f"-{max_age_days}",),
        )

        # Vacuum to reclaim space
        self.db.execute("VACUUM")
        self.db.commit()

    def find_duplicates_by_hash(self, hash_value: int) -> list[CodeBlock]:
        """Find all code blocks with the given hash value.

        Args:
            hash_value: Hash value to search for

        Returns:
            List of ALL CodeBlock instances with this hash (from all files)
        """
        rows = self._query_service.find_blocks_by_hash(self.db, hash_value)

        blocks = []
        for file_path_str, start, end, snippet, hash_val in rows:
            block = CodeBlock(
                file_path=Path(file_path_str),
                start_line=start,
                end_line=end,
                snippet=snippet,
                hash_value=hash_val,
            )
            blocks.append(block)

        return blocks

    def get_duplicate_hashes(self) -> list[int]:
        """Get all hash values that appear 2+ times.

        Returns:
            List of hash values with 2 or more occurrences
        """
        return self._query_service.get_duplicate_hashes(self.db)

    def close(self) -> None:
        """Close database connection."""
        self.db.close()
