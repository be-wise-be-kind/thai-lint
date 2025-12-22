"""
Purpose: SQLite storage manager for stringly-typed pattern detection

Scope: String validation pattern storage and cross-file duplicate detection queries

Overview: Implements in-memory or temporary-file SQLite storage for stringly-typed pattern
    detection. Stores string validation patterns with hash values computed from the string
    values, enabling cross-file duplicate detection during a single linter run. Supports both
    :memory: mode (fast, RAM-only) and tempfile mode (disk-backed for large projects). No
    persistence between runs - storage is cleared when linter completes. Includes indexes
    for fast hash lookups enabling efficient cross-file detection.

Dependencies: Python sqlite3 module (stdlib), tempfile module (stdlib), pathlib.Path,
    dataclasses, json module (stdlib)

Exports: StoredPattern dataclass, StringlyTypedStorage class

Interfaces: StringlyTypedStorage.__init__(storage_mode), add_pattern(pattern),
    add_patterns(patterns), get_duplicate_hashes(min_files), get_patterns_by_hash(hash_value),
    clear(), close()

Implementation: SQLite with string_validations table, indexed on string_set_hash for
    performance, storage_mode determines :memory: vs tempfile location
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path

# Row index constants for SQLite query results
_COL_FILE_PATH = 0
_COL_LINE_NUMBER = 1
_COL_COLUMN = 2
_COL_VARIABLE_NAME = 3
_COL_STRING_SET_HASH = 4
_COL_STRING_VALUES = 5
_COL_PATTERN_TYPE = 6
_COL_DETAILS = 7

# Schema SQL for table creation
_CREATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS string_validations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    column_number INTEGER NOT NULL,
    variable_name TEXT,
    string_set_hash INTEGER NOT NULL,
    string_values TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    details TEXT NOT NULL,
    UNIQUE(file_path, line_number, column_number)
)"""

_CREATE_HASH_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_string_hash ON string_validations(string_set_hash)"
)

_CREATE_FILE_INDEX_SQL = "CREATE INDEX IF NOT EXISTS idx_file_path ON string_validations(file_path)"


def _row_to_pattern(row: tuple) -> StoredPattern:
    """Convert a database row tuple to StoredPattern.

    Args:
        row: Tuple from SQLite query result

    Returns:
        StoredPattern instance
    """
    return StoredPattern(
        file_path=Path(row[_COL_FILE_PATH]),
        line_number=row[_COL_LINE_NUMBER],
        column=row[_COL_COLUMN],
        variable_name=row[_COL_VARIABLE_NAME],
        string_set_hash=row[_COL_STRING_SET_HASH],
        string_values=json.loads(row[_COL_STRING_VALUES]),
        pattern_type=row[_COL_PATTERN_TYPE],
        details=row[_COL_DETAILS],
    )


# pylint: disable=too-many-instance-attributes
# Justification: StoredPattern is a pure data transfer object for SQLite storage.
# All 8 fields are necessary: file location (3), variable info (1), hash/values (3), pattern type (1).
@dataclass
class StoredPattern:
    """Represents a stringly-typed pattern stored in SQLite.

    Captures all information needed to detect cross-file duplicates and generate
    violations with meaningful context.
    """

    file_path: Path
    """Path to the file containing the pattern."""

    line_number: int
    """Line number where the pattern occurs (1-indexed)."""

    column: int
    """Column number where the pattern starts (0-indexed)."""

    variable_name: str | None
    """Variable name involved in the pattern, if identifiable."""

    string_set_hash: int
    """Hash of the normalized string values for cross-file matching."""

    string_values: list[str]
    """Sorted list of string values in the pattern."""

    pattern_type: str
    """Type of pattern: membership_validation, equality_chain, etc."""

    details: str
    """Human-readable description of the detected pattern."""


class StringlyTypedStorage:
    """SQLite-backed storage for stringly-typed pattern detection.

    Stores patterns from analyzed files and provides queries to find patterns
    that appear across multiple files, enabling cross-file duplicate detection.
    """

    def __init__(self, storage_mode: str = "memory") -> None:
        """Initialize storage with SQLite database.

        Args:
            storage_mode: Storage mode - "memory" (default) or "tempfile"
        """
        self._storage_mode = storage_mode
        self._tempfile = None

        # Create SQLite connection based on storage mode
        if storage_mode == "memory":
            self._db = sqlite3.connect(":memory:")
        elif storage_mode == "tempfile":
            # pylint: disable=consider-using-with
            # Justification: tempfile must remain open for SQLite connection lifetime.
            # It is explicitly closed in close() method when storage is finalized.
            self._tempfile = tempfile.NamedTemporaryFile(suffix=".db", delete=True)
            self._db = sqlite3.connect(self._tempfile.name)
        else:
            raise ValueError(f"Invalid storage_mode: {storage_mode}")

        # Create schema inline
        self._db.execute(_CREATE_TABLE_SQL)
        self._db.execute(_CREATE_HASH_INDEX_SQL)
        self._db.execute(_CREATE_FILE_INDEX_SQL)
        self._db.commit()

    def add_pattern(self, pattern: StoredPattern) -> None:
        """Add a single pattern to storage.

        Args:
            pattern: StoredPattern instance to store
        """
        self.add_patterns([pattern])

    def add_patterns(self, patterns: list[StoredPattern]) -> None:
        """Add multiple patterns to storage in a batch.

        Args:
            patterns: List of StoredPattern instances to store
        """
        if not patterns:
            return

        for pattern in patterns:
            self._db.execute(
                """INSERT OR REPLACE INTO string_validations
                   (file_path, line_number, column_number, variable_name,
                    string_set_hash, string_values, pattern_type, details)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(pattern.file_path),
                    pattern.line_number,
                    pattern.column,
                    pattern.variable_name,
                    pattern.string_set_hash,
                    json.dumps(pattern.string_values),
                    pattern.pattern_type,
                    pattern.details,
                ),
            )

        self._db.commit()

    def get_duplicate_hashes(self, min_files: int = 2) -> list[int]:
        """Get hash values that appear in min_files or more files.

        Args:
            min_files: Minimum number of distinct files (default: 2)

        Returns:
            List of hash values appearing in at least min_files files
        """
        cursor = self._db.execute(
            """SELECT string_set_hash FROM string_validations
               GROUP BY string_set_hash
               HAVING COUNT(DISTINCT file_path) >= ?""",
            (min_files,),
        )
        return [row[0] for row in cursor.fetchall()]

    def get_patterns_by_hash(self, hash_value: int) -> list[StoredPattern]:
        """Get all patterns with the given hash value.

        Args:
            hash_value: Hash value to search for

        Returns:
            List of StoredPattern instances with this hash
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, variable_name,
                      string_set_hash, string_values, pattern_type, details
               FROM string_validations
               WHERE string_set_hash = ?
               ORDER BY file_path, line_number""",
            (hash_value,),
        )

        return [_row_to_pattern(row) for row in cursor.fetchall()]

    def get_all_patterns(self) -> list[StoredPattern]:
        """Get all stored patterns.

        Returns:
            List of all StoredPattern instances in storage
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, variable_name,
                      string_set_hash, string_values, pattern_type, details
               FROM string_validations
               ORDER BY file_path, line_number"""
        )

        return [_row_to_pattern(row) for row in cursor.fetchall()]

    def clear(self) -> None:
        """Clear all stored patterns."""
        self._db.execute("DELETE FROM string_validations")
        self._db.commit()

    def close(self) -> None:
        """Close database connection and cleanup tempfile if used."""
        self._db.close()
        if self._tempfile:
            self._tempfile.close()
