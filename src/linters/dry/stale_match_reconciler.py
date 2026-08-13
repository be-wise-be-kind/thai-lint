"""
Purpose: Freshness verification for persistent-cache duplicate matches

Scope: Reconciles matched-against files that were not part of this run's file list

Overview: A persistent, cross-run duplicate index can report a match against a file this run
    never scanned - it was indexed by a prior invocation. That file's on-disk content may have
    drifted since then (edited, or deleted entirely) without ever being re-indexed. Before
    trusting such a match, this reconciles each externally-matched file's current state: if it
    no longer exists, its stale entries are purged so it can't produce phantom violations; if its
    content hash no longer matches what's indexed, it's transparently rescanned and re-upserted
    so the match reflects current content, not stale content. Files this run already processed
    directly (via DRYRule.check()) are skipped entirely - they're already known-fresh.

Dependencies: DuplicateStorage, FileAnalyzer, DRYConfig, detect_language, compute_content_hash

Exports: reconcile_stale_matches function

Interfaces: reconcile_stale_matches(storage, file_analyzer, config, processed_files)

Implementation: Module-level functions (no state to justify a class). Queries duplicate hashes
    once, collects the file paths involved that aren't in processed_files, and rescans/purges
    each as needed before returning
"""

from pathlib import Path

from src.orchestrator.language_detector import detect_language

from .config import DRYConfig
from .content_hash import compute_content_hash
from .duplicate_storage import DuplicateStorage
from .file_analyzer import FileAnalyzer


def reconcile_stale_matches(
    storage: DuplicateStorage,
    file_analyzer: FileAnalyzer,
    config: DRYConfig,
    processed_files: set[str],
) -> None:
    """Rescan or purge stale matched-against files before violations are generated.

    Args:
        storage: Duplicate storage backed by the persistent index
        file_analyzer: Analyzer used to rescan a stale file's blocks
        config: DRY configuration, used to rescan with the same settings
        processed_files: Absolute-path strings of files this run already scanned
            directly via check() - never reconciled, since they're already fresh
    """
    for file_path in _external_file_paths(storage, processed_files):
        _reconcile_file(file_path, storage, file_analyzer, config)


def _external_file_paths(storage: DuplicateStorage, processed_files: set[str]) -> set[Path]:
    """Collect file paths in a duplicate-hash match that this run didn't itself scan."""
    blocks_by_hash = storage.get_blocks_for_hashes(storage.duplicate_hashes)
    paths: set[Path] = set()
    for blocks in blocks_by_hash.values():
        for block in blocks:
            if str(block.file_path) not in processed_files:
                paths.add(block.file_path)
    return paths


def _reconcile_file(
    file_path: Path,
    storage: DuplicateStorage,
    file_analyzer: FileAnalyzer,
    config: DRYConfig,
) -> None:
    """Purge a deleted file, or rescan one whose content hash has drifted."""
    content = _read_file(file_path)
    if content is None:
        storage.purge_file(file_path)
        return

    content_hash = compute_content_hash(content)
    if not storage.needs_rescan(file_path, content_hash):
        return

    language = detect_language(file_path)
    blocks = file_analyzer.analyze(file_path, content, language, config)
    storage.upsert_file(file_path, content_hash, blocks)


def _read_file(file_path: Path) -> str | None:
    """Read a file's content, or None if it's missing/unreadable."""
    try:
        return file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
