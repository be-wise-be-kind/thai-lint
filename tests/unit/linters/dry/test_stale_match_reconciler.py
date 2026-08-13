"""
Purpose: Unit tests for reconcile_stale_matches, the persistent-cache freshness/rescan path

Scope: reconcile_stale_matches against a real DuplicateStorage/FileAnalyzer

Overview: Verifies the plan's "stale matched-against file" scenarios directly against
    reconcile_stale_matches in isolation, using real DRYCache/DuplicateStorage/FileAnalyzer
    instances (not mocks) on tmp_path fixtures. A file only participates in reconciliation when
    it appears in a duplicate-hash group but was NOT part of this run's processed_files set -
    i.e. it's a previously-indexed file being matched against, not one this run scanned itself.

Dependencies: pytest, pathlib.Path, DuplicateStorage, DRYCache, FileAnalyzer, DRYConfig,
    reconcile_stale_matches

Exports: Test classes covering fresh/stale/deleted/already-processed matched files

Interfaces: Exercises reconcile_stale_matches(storage, file_analyzer, config, processed_files)

Implementation: Seeds a real on-disk DRYCache with blocks for two files sharing a duplicate,
    then mutates one file's on-disk content or existence and reconciles
"""

from pathlib import Path

from src.linters.dry.cache import DRYCache
from src.linters.dry.config import DRYConfig
from src.linters.dry.content_hash import compute_content_hash
from src.linters.dry.duplicate_storage import DuplicateStorage
from src.linters.dry.file_analyzer import FileAnalyzer
from src.linters.dry.stale_match_reconciler import reconcile_stale_matches

_DUPLICATE_BODY = "\n".join(f"    value_{i} = compute({i})" for i in range(6))


def _write_and_seed(
    storage: DuplicateStorage,
    file_analyzer: FileAnalyzer,
    config: DRYConfig,
    path: Path,
    content: str,
) -> None:
    """Write file content to disk and index it into storage, as a prior run would."""
    path.write_text(content)
    blocks = file_analyzer.analyze(path, content, "python", config)
    storage.upsert_file(path, compute_content_hash(content), blocks)


def _make_storage(tmp_path: Path) -> DuplicateStorage:
    cache = DRYCache(storage_mode="tempfile", db_path=tmp_path / "dry.db")
    return DuplicateStorage(cache)


class TestReconcileFreshFile:
    """A matched-against file whose content hasn't changed is left untouched."""

    def test_fresh_file_is_not_rescanned(self, tmp_path: Path) -> None:
        """A file whose content_hash is already current must not be touched."""
        config = DRYConfig(enabled=True, min_duplicate_lines=3)
        file_analyzer = FileAnalyzer(config)
        storage = _make_storage(tmp_path)

        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content = f"def handler():\n{_DUPLICATE_BODY}\n"
        _write_and_seed(storage, file_analyzer, config, file_a, content)
        _write_and_seed(storage, file_analyzer, config, file_b, content)

        before = storage.get_blocks_for_hashes(storage.duplicate_hashes)

        reconcile_stale_matches(storage, file_analyzer, config, processed_files={str(file_a)})

        after = storage.get_blocks_for_hashes(storage.duplicate_hashes)
        assert before == after


class TestReconcileStaleFile:
    """A matched-against file whose on-disk content changed since indexing is rescanned."""

    def test_stale_file_is_rescanned_and_reindexed(self, tmp_path: Path) -> None:
        """A file whose content_hash drifted must be rescanned and re-upserted."""
        config = DRYConfig(enabled=True, min_duplicate_lines=3)
        file_analyzer = FileAnalyzer(config)
        storage = _make_storage(tmp_path)

        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        old_content = f"def handler():\n{_DUPLICATE_BODY}\n"
        _write_and_seed(storage, file_analyzer, config, file_a, old_content)
        _write_and_seed(storage, file_analyzer, config, file_b, old_content)

        # file_b changes on disk (duplicate removed) without being re-indexed - it's
        # stale relative to what's stored, and file_b is NOT in this run's processed set.
        new_content = "def handler():\n    return 'no duplicate anymore'\n"
        file_b.write_text(new_content)

        reconcile_stale_matches(storage, file_analyzer, config, processed_files={str(file_a)})

        assert storage.needs_rescan(file_b, compute_content_hash(new_content)) is False
        remaining = storage.get_blocks_for_hashes(storage.duplicate_hashes)
        remaining_files = {str(b.file_path) for blocks in remaining.values() for b in blocks}
        assert str(file_b) not in remaining_files


class TestReconcileDeletedFile:
    """A matched-against file that no longer exists on disk is purged from the index."""

    def test_deleted_file_is_purged(self, tmp_path: Path) -> None:
        """A file removed from disk must be purged from the index entirely."""
        config = DRYConfig(enabled=True, min_duplicate_lines=3)
        file_analyzer = FileAnalyzer(config)
        storage = _make_storage(tmp_path)

        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content = f"def handler():\n{_DUPLICATE_BODY}\n"
        _write_and_seed(storage, file_analyzer, config, file_a, content)
        _write_and_seed(storage, file_analyzer, config, file_b, content)

        file_b.unlink()

        reconcile_stale_matches(storage, file_analyzer, config, processed_files={str(file_a)})

        remaining = storage.get_blocks_for_hashes(storage.duplicate_hashes)
        remaining_files = {str(b.file_path) for blocks in remaining.values() for b in blocks}
        assert str(file_b) not in remaining_files
        assert storage.needs_rescan(file_b, "anything") is True


class TestReconcileSkipsProcessedFiles:
    """A file already scanned in this run is never touched by reconciliation."""

    def test_processed_file_is_skipped_even_if_changed_on_disk(self, tmp_path: Path) -> None:
        """A file already scanned this run must never be reconciled, even if it changed."""
        config = DRYConfig(enabled=True, min_duplicate_lines=3)
        file_analyzer = FileAnalyzer(config)
        storage = _make_storage(tmp_path)

        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content = f"def handler():\n{_DUPLICATE_BODY}\n"
        _write_and_seed(storage, file_analyzer, config, file_a, content)
        _write_and_seed(storage, file_analyzer, config, file_b, content)

        # file_a is "stale" on disk relative to what was indexed above, but it's in
        # processed_files (this run already scanned it directly via check()) so
        # reconciliation must not touch it.
        file_a.write_text("def handler():\n    return 'changed after indexing'\n")

        before = storage.get_blocks_for_hashes(storage.duplicate_hashes)
        reconcile_stale_matches(
            storage, file_analyzer, config, processed_files={str(file_a), str(file_b)}
        )
        after = storage.get_blocks_for_hashes(storage.duplicate_hashes)

        assert before == after
