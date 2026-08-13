"""
Purpose: SQLite storage manager for DRY linter duplicate detection

Scope: Code block storage and duplicate-hash detection queries

Overview: Implements in-memory, temporary-file, or persistent SQLite storage for duplicate code
    detection. Stores code blocks with hash values, enabling cross-file duplicate detection.
    "memory" and "tempfile" modes are cleared when the linter completes; "persistent" mode (and
    any mode given an explicit db_path) survives between runs, so upsert_file always explicitly
    deletes a file's old code_blocks rows before inserting new ones - never relying on ON DELETE
    CASCADE, which requires PRAGMA foreign_keys=ON and was never enabled here (the exact bug,
    #35, that caused stale duplicate-code violations to persist after the underlying duplicate
    was already fixed, in this feature's earlier, removed incarnation). Includes indexes for
    fast hash lookups enabling efficient cross-file detection. Duplicate-constant detection uses
    a separate, in-memory, non-SQLite path (DRYRule._constants + find_constant_groups) and has no
    presence here.

Dependencies: Python sqlite3 module (stdlib), tempfile module (stdlib), pathlib.Path, dataclasses

Exports: CodeBlock dataclass, DRYCache class

Interfaces: DRYCache.__init__(storage_mode, db_path), upsert_file(file_path, content_hash,
    blocks), needs_rescan(file_path, content_hash), purge_file(file_path),
    find_duplicates_by_hash(hash_value), find_duplicates_by_hashes(hash_values),
    duplicate_hashes, close()

Implementation: SQLite with three tables (files, code_blocks, schema_meta), indexed for
    performance, storage_mode determines :memory:/tempfile/persistent location, ACID transactions
    for reliability, schema_meta enables self-healing rebuild on an incompatible on-disk schema

Suppressions:
    - consider-using-with: Tempfile managed by class lifecycle, not context manager
"""

from __future__ import annotations

import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.core.constants import StorageMode

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

    SCHEMA_VERSION = 2
    # Seconds to wait for a lock before raising "database is locked", when connecting
    # to a shared on-disk file that multiple --parallel worker processes write to.
    SHARED_DB_CONNECT_TIMEOUT = 30

    def __init__(self, storage_mode: str = "memory", db_path: Path | None = None) -> None:
        """Initialize storage with SQLite database.

        Args:
            storage_mode: Storage mode - "memory" (default), "tempfile", or "persistent"
            db_path: Explicit on-disk path to connect to instead of a random
                auto-deleting tempfile. Required for "persistent" mode. Callers also
                pass this for "tempfile" mode to share one database file across
                multiple processes (e.g. --parallel worker processes plus the main
                process) for the duration of a single run. The file is not
                managed/deleted by this class when db_path is given. Ignored for
                "memory" mode.
        """
        self._storage_mode = storage_mode
        self._tempfile: tempfile._TemporaryFileWrapper[bytes] | None = None

        # Create SQLite connection based on storage mode
        if storage_mode == StorageMode.MEMORY:
            self.db = sqlite3.connect(":memory:")
        elif storage_mode in (StorageMode.TEMPFILE, StorageMode.PERSISTENT):
            self.db = self._connect_on_disk(storage_mode, db_path)
        else:
            raise ValueError(f"Invalid storage_mode: {storage_mode}")

        self._query_service = CacheQueryService()
        self._ensure_schema()

    def _connect_on_disk(self, storage_mode: str, db_path: Path | None) -> sqlite3.Connection:
        """Connect to an explicit on-disk file, or fall back to a random tempfile."""
        if db_path is not None:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db = sqlite3.connect(str(db_path), timeout=self.SHARED_DB_CONNECT_TIMEOUT)
            # WAL mode lets multiple processes/connections read/write the same file
            # concurrently with far less lock-contention than the default rollback
            # journal - needed since this file can be shared across --parallel
            # worker processes, or reopened by a later, unrelated CLI invocation.
            db.execute("PRAGMA journal_mode=WAL")
            # NORMAL (vs the default FULL) skips fsync on every commit, only syncing at
            # WAL checkpoints - WAL mode's own crash-recovery guarantees make this safe.
            # upsert_file() commits once per file, so without this a full-tree index
            # build on a large project pays one fsync per file - the dominant cost of a
            # cold build (measured on a ~3000-file real-world repo).
            db.execute("PRAGMA synchronous=NORMAL")
            return db
        if storage_mode == StorageMode.PERSISTENT:
            raise ValueError("storage_mode='persistent' requires an explicit db_path")
        # pylint: disable=consider-using-with
        # Justification: tempfile must remain open for SQLite connection lifetime.
        # It is explicitly closed in close() method when cache is finalized.
        self._tempfile = tempfile.NamedTemporaryFile(suffix=".db", delete=True)
        return sqlite3.connect(self._tempfile.name)

    def _ensure_schema(self) -> None:
        """Create the schema, self-healing (drop and recreate) an incompatible on-disk one.

        A persistent on-disk file from an older SCHEMA_VERSION is rebuilt from scratch
        rather than erroring or silently misbehaving against a shape it doesn't expect.
        """
        self.db.execute("CREATE TABLE IF NOT EXISTS schema_meta (version INTEGER NOT NULL)")
        row = self.db.execute("SELECT version FROM schema_meta").fetchone()
        if row is not None and row[0] != self.SCHEMA_VERSION:
            self._drop_app_tables()
        self._create_tables()
        self.db.execute("DELETE FROM schema_meta")
        self.db.execute("INSERT INTO schema_meta (version) VALUES (?)", (self.SCHEMA_VERSION,))
        self.db.commit()

    def _drop_app_tables(self) -> None:
        """Drop every app table, for a schema-version mismatch rebuild."""
        for table in ("code_blocks", "files"):
            self.db.execute(f"DROP TABLE IF EXISTS {table}")  # nosec B608 - fixed table names

    def _create_tables(self) -> None:
        """Create the schema if it doesn't already exist."""
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS files (
                file_path TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
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
                snippet TEXT NOT NULL
            )"""
        )
        # Deliberately no FOREIGN KEY ... ON DELETE CASCADE here: SQLite only enforces
        # that with PRAGMA foreign_keys=ON, which this codebase never sets. Relying on
        # it was the exact root cause of #35 (stale code_blocks rows survived a file's
        # `files` row being replaced). upsert_file() deletes explicitly instead.

        self.db.execute("CREATE INDEX IF NOT EXISTS idx_hash_value ON code_blocks(hash_value)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON code_blocks(file_path)")

    def upsert_file(self, file_path: Path, content_hash: str, blocks: list[CodeBlock]) -> None:
        """Replace all stored blocks for a file with fresh ones, atomically.

        Always deletes this file's existing code_blocks first, regardless of whether
        blocks is empty - the direct fix for #35 (see class docstring). Recording
        content_hash even when blocks is empty lets needs_rescan() recognize this file
        as already up to date on a later run, and lets a later edit that reintroduces a
        duplicate be detected as a content-hash change.

        Args:
            file_path: Path to source file
            content_hash: Hash of the file's current content, for later freshness checks
            blocks: List of CodeBlock instances to store (may be empty)
        """
        self.db.execute("DELETE FROM code_blocks WHERE file_path = ?", (str(file_path),))
        self.db.execute(
            """INSERT INTO files (file_path, content_hash, last_scanned)
               VALUES (?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(file_path) DO UPDATE SET
                   content_hash = excluded.content_hash,
                   last_scanned = excluded.last_scanned""",
            (str(file_path), content_hash),
        )
        if blocks:
            self.db.executemany(
                """INSERT INTO code_blocks
                   (file_path, hash_value, start_line, end_line, snippet)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    (str(file_path), b.hash_value, b.start_line, b.end_line, b.snippet)
                    for b in blocks
                ],
            )
        self.db.commit()

    def needs_rescan(self, file_path: Path, current_content_hash: str) -> bool:
        """Check whether a file's indexed content is stale relative to current_content_hash.

        Args:
            file_path: Path to source file
            current_content_hash: Hash of the file's current on-disk content

        Returns:
            True if the file has never been indexed, or its indexed content_hash
            differs from current_content_hash
        """
        row = self.db.execute(
            "SELECT content_hash FROM files WHERE file_path = ?", (str(file_path),)
        ).fetchone()
        return row is None or row[0] != current_content_hash

    def purge_file(self, file_path: Path) -> None:
        """Remove a file's entries entirely (e.g. it was deleted from disk since indexing).

        Args:
            file_path: Path to source file
        """
        self.db.execute("DELETE FROM code_blocks WHERE file_path = ?", (str(file_path),))
        self.db.execute("DELETE FROM files WHERE file_path = ?", (str(file_path),))
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

    def find_duplicates_by_hashes(self, hash_values: list[int]) -> dict[int, list[CodeBlock]]:
        """Find all code blocks for a batch of hash values in a single query.

        Replaces calling find_duplicates_by_hash once per hash (an N+1 query pattern
        that dominates query time when a run has many duplicate hash groups).

        Args:
            hash_values: Hash values to search for

        Returns:
            Mapping of hash_value to its list of CodeBlock instances
        """
        rows = self._query_service.find_blocks_by_hashes(self.db, hash_values)

        result: dict[int, list[CodeBlock]] = {h: [] for h in hash_values}
        for file_path_str, start, end, snippet, hash_val in rows:
            result[hash_val].append(
                CodeBlock(
                    file_path=Path(file_path_str),
                    start_line=start,
                    end_line=end,
                    snippet=snippet,
                    hash_value=hash_val,
                )
            )

        return result

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
