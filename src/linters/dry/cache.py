"""
Purpose: SQLite storage manager for DRY linter duplicate detection

Scope: Code block storage and duplicate detection queries

Overview: Implements in-memory or temporary-file SQLite storage for duplicate code detection.
    Stores code blocks with hash values, file locations, and metadata during a single linter run.
    Supports both :memory: mode (fast, RAM-only) and tempfile mode (disk-backed for large projects).
    No persistence between runs - storage is cleared when linter completes. Includes indexes for
    fast hash lookups enabling cross-file duplicate detection with minimal overhead.

Dependencies: Python sqlite3 module (stdlib), tempfile module (stdlib), pathlib.Path, dataclasses

Exports: CodeBlock dataclass, DRYCache class

Interfaces: DRYCache.__init__(storage_mode), add_blocks(file_path, blocks),
    find_duplicates_by_hash(hash_value), get_duplicate_hashes(), close()

Implementation: SQLite with two tables (files, code_blocks), indexed on hash_value for performance,
    storage_mode determines :memory: vs tempfile location, ACID transactions for reliability
"""

import sqlite3
import tempfile
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
    """SQLite-backed storage for duplicate detection."""

    SCHEMA_VERSION = 1

    def __init__(self, storage_mode: str = "memory") -> None:
        """Initialize storage with SQLite database.

        Args:
            storage_mode: Storage mode - "memory" (default) or "tempfile"
        """
        self._storage_mode = storage_mode
        self._tempfile = None

        # Create SQLite connection based on storage mode
        if storage_mode == "memory":
            self.db = sqlite3.connect(":memory:")
        elif storage_mode == "tempfile":
            # Create temporary file that auto-deletes on close
            # pylint: disable=consider-using-with
            # Justification: tempfile must remain open for SQLite connection lifetime.
            # It is explicitly closed in close() method when cache is finalized.
            self._tempfile = tempfile.NamedTemporaryFile(suffix=".db", delete=True)
            self.db = sqlite3.connect(self._tempfile.name)
        else:
            raise ValueError(f"Invalid storage_mode: {storage_mode}")

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

    def add_blocks(self, file_path: Path, blocks: list[CodeBlock]) -> None:
        """Add code blocks to storage.

        Args:
            file_path: Path to source file
            blocks: List of CodeBlock instances to store
        """
        if not blocks:
            return

        # Insert file metadata
        try:
            mtime = file_path.stat().st_mtime
        except OSError:
            mtime = 0.0  # File doesn't exist, use placeholder

        self.db.execute(
            "INSERT OR REPLACE INTO files (file_path, mtime, hash_count) VALUES (?, ?, ?)",
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

    @property
    def duplicate_hashes(self) -> list[int]:
        """Hash values that appear 2+ times.

        Returns:
            List of hash values with 2 or more occurrences
        """
        return self._query_service.get_duplicate_hashes(self.db)

    def close(self) -> None:
        """Close database connection and cleanup tempfile if used."""
        self.db.close()
        if self._tempfile:
            self._tempfile.close()
