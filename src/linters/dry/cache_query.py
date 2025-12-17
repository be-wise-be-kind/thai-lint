"""
Purpose: Query service for DRY cache database

Scope: Handles SQL queries for duplicate hash detection

Overview: Provides query methods for finding duplicate code blocks in the SQLite cache. Extracts
    query logic from DRYCache to maintain SRP compliance. Handles queries for duplicate hashes
    and blocks by hash value.

Dependencies: sqlite3.Connection

Exports: CacheQueryService class

Interfaces: CacheQueryService.get_duplicate_hashes(db), find_duplicates_by_hash(db, hash_value)

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
