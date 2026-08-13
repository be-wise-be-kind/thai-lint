"""
Purpose: Query service for DRY cache database

Scope: Handles SQL queries for duplicate hash detection

Overview: Provides query methods for finding duplicate code blocks in the SQLite cache. Extracts
    query logic from DRYCache to maintain SRP compliance. Handles queries for duplicate hashes
    and blocks by hash value, including a batched multi-hash lookup that avoids running one query
    per duplicate hash (an N+1 pattern that dominates query time on large duplicate sets).

Dependencies: sqlite3.Connection

Exports: CacheQueryService class

Interfaces: CacheQueryService.get_duplicate_hashes(db), find_blocks_by_hash(db, hash_value),
    find_blocks_by_hashes(db, hash_values)

Implementation: SQL queries for duplicate detection, returns hash values and block data
"""

import sqlite3


class CacheQueryService:
    """Handles cache database queries."""

    def __init__(self) -> None:
        """Initialize the cache query service."""
        pass  # Stateless query service for database operations

    def get_duplicate_hashes(self, db: sqlite3.Connection) -> list[int]:
        """Get all hash values that appear 2+ times.

        Args:
            db: Database connection

        Returns:
            List of hash values with 2 or more occurrences
        """
        cursor = db.execute(
            """SELECT hash_value
               FROM code_blocks
               GROUP BY hash_value
               HAVING COUNT(*) >= 2"""
        )

        return [row[0] for row in cursor]

    def find_blocks_by_hash(self, db: sqlite3.Connection, hash_value: int) -> list[tuple]:
        """Find all blocks with given hash value.

        Args:
            db: Database connection
            hash_value: Hash to search for

        Returns:
            List of tuples (file_path, start_line, end_line, snippet, hash_value)
        """
        cursor = db.execute(
            """SELECT file_path, start_line, end_line, snippet, hash_value
               FROM code_blocks
               WHERE hash_value = ?
               ORDER BY file_path, start_line""",
            (hash_value,),
        )

        return cursor.fetchall()

    def find_blocks_by_hashes(self, db: sqlite3.Connection, hash_values: list[int]) -> list[tuple]:
        """Find all blocks for a batch of hash values in a single query.

        Args:
            db: Database connection
            hash_values: Hashes to search for

        Returns:
            List of tuples (file_path, start_line, end_line, snippet, hash_value),
            for every hash in hash_values, ordered so each hash's rows are contiguous
        """
        if not hash_values:
            return []
        placeholders = ",".join("?" for _ in hash_values)
        cursor = db.execute(
            f"""SELECT file_path, start_line, end_line, snippet, hash_value
               FROM code_blocks
               WHERE hash_value IN ({placeholders})
               ORDER BY hash_value, file_path, start_line""",  # nosec B608 - placeholders only
            hash_values,
        )

        return cursor.fetchall()
