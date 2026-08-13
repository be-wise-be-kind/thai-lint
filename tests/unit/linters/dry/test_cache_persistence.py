"""
Purpose: Unit tests for DRYCache's persistent cross-run storage primitives

Scope: DRYCache.upsert_file, needs_rescan, purge_file, and on-disk schema durability

Overview: Tests the low-level SQLite primitives a persistent, cross-run duplicate index is built
    on, in isolation from the rest of the DRY linter (per the project plan's own instruction to
    unit-test this directly rather than through the whole linter). Covers the exact regression
    that killed the original persistent-cache feature (#35): relying on an unenforced
    ON DELETE CASCADE left stale code_blocks rows behind after a file was edited to remove a
    duplicate, so the violation reappeared on every subsequent run even after the underlying
    duplicate was fixed. upsert_file's explicit delete-before-insert (never dependent on any
    PRAGMA) is the direct fix, verified here as "fix then rescan, old block gone."

Dependencies: pytest, pathlib.Path, sqlite3, src.linters.dry.cache.DRYCache, CodeBlock

Exports: Test classes for upsert_file, needs_rescan, purge_file, and reconnect-durability

Interfaces: Exercises DRYCache(storage_mode="tempfile", db_path=...) directly

Implementation: Uses tmp_path for a real on-disk file, opening and closing DRYCache instances to
    simulate separate process invocations reconnecting to the same persistent store
"""

from pathlib import Path

from src.linters.dry.cache import CodeBlock, DRYCache


def _block(file_path: Path, hash_value: int, start: int = 1, end: int = 3) -> CodeBlock:
    return CodeBlock(
        file_path=file_path,
        start_line=start,
        end_line=end,
        snippet=f"snippet-{hash_value}",
        hash_value=hash_value,
    )


class TestUpsertFile:
    """upsert_file stores blocks queryable by hash, and replaces old blocks on rescan."""

    def test_upsert_file_stores_blocks_queryable_by_hash(self, tmp_path: Path) -> None:
        """A block stored via upsert_file must be findable by its hash."""
        db_path = tmp_path / "dry.db"
        cache = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            file_a = tmp_path / "file_a.py"
            cache.upsert_file(file_a, content_hash="hash-v1", blocks=[_block(file_a, 111)])

            found = cache.find_duplicates_by_hash(111)
            assert len(found) == 1
            assert found[0].file_path == file_a
        finally:
            cache.close()

    def test_upsert_file_replaces_old_blocks_on_rescan(self, tmp_path: Path) -> None:
        """The #35 regression: fixing a duplicate and rescanning must not leave stale blocks."""
        db_path = tmp_path / "dry.db"
        cache = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            file_a = tmp_path / "file_a.py"
            cache.upsert_file(file_a, content_hash="hash-v1", blocks=[_block(file_a, 111)])
            assert len(cache.find_duplicates_by_hash(111)) == 1

            # File is edited to remove the duplicate and rescanned: no blocks this time.
            cache.upsert_file(file_a, content_hash="hash-v2", blocks=[])

            assert cache.find_duplicates_by_hash(111) == []
        finally:
            cache.close()

    def test_upsert_file_records_content_hash_even_with_no_blocks(self, tmp_path: Path) -> None:
        """A file with zero blocks must still be recorded, so needs_rescan can find it later."""
        db_path = tmp_path / "dry.db"
        cache = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            file_a = tmp_path / "file_a.py"
            cache.upsert_file(file_a, content_hash="hash-v1", blocks=[])
            assert cache.needs_rescan(file_a, "hash-v1") is False
        finally:
            cache.close()


class TestNeedsRescan:
    """needs_rescan reports whether a file's on-disk content has drifted from the index."""

    def test_needs_rescan_true_for_unknown_file(self, tmp_path: Path) -> None:
        """A file never indexed always needs a scan."""
        db_path = tmp_path / "dry.db"
        cache = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            assert cache.needs_rescan(tmp_path / "never_indexed.py", "any-hash") is True
        finally:
            cache.close()

    def test_needs_rescan_false_when_content_hash_matches(self, tmp_path: Path) -> None:
        """A file whose indexed content_hash matches the current one needs no rescan."""
        db_path = tmp_path / "dry.db"
        cache = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            file_a = tmp_path / "file_a.py"
            cache.upsert_file(file_a, content_hash="hash-v1", blocks=[_block(file_a, 111)])
            assert cache.needs_rescan(file_a, "hash-v1") is False
        finally:
            cache.close()

    def test_needs_rescan_true_when_content_hash_differs(self, tmp_path: Path) -> None:
        """A file whose current content_hash differs from what's indexed needs a rescan."""
        db_path = tmp_path / "dry.db"
        cache = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            file_a = tmp_path / "file_a.py"
            cache.upsert_file(file_a, content_hash="hash-v1", blocks=[_block(file_a, 111)])
            assert cache.needs_rescan(file_a, "hash-v2") is True
        finally:
            cache.close()


class TestPurgeFile:
    """purge_file removes a file's entries entirely (e.g. it was deleted from disk)."""

    def test_purge_file_removes_blocks_and_index_entry(self, tmp_path: Path) -> None:
        """purge_file must remove both the file's code_blocks and its files-table entry."""
        db_path = tmp_path / "dry.db"
        cache = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            file_a = tmp_path / "file_a.py"
            cache.upsert_file(file_a, content_hash="hash-v1", blocks=[_block(file_a, 111)])

            cache.purge_file(file_a)

            assert cache.find_duplicates_by_hash(111) == []
            assert cache.needs_rescan(file_a, "hash-v1") is True
        finally:
            cache.close()


class TestPersistsAcrossReconnect:
    """A real on-disk file must survive being closed and reopened by a fresh DRYCache instance.

    The literal proof that this store is not tied to one process's lifetime.
    """

    def test_blocks_survive_close_and_reopen(self, tmp_path: Path) -> None:
        """A block written by one DRYCache instance must be readable by a later one."""
        db_path = tmp_path / "dry.db"
        file_a = tmp_path / "file_a.py"

        first = DRYCache(storage_mode="tempfile", db_path=db_path)
        first.upsert_file(file_a, content_hash="hash-v1", blocks=[_block(file_a, 111)])
        first.close()

        second = DRYCache(storage_mode="tempfile", db_path=db_path)
        try:
            found = second.find_duplicates_by_hash(111)
            assert len(found) == 1
            assert second.needs_rescan(file_a, "hash-v1") is False
        finally:
            second.close()
