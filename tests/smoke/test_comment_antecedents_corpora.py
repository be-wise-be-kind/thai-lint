"""
Purpose: Corpus smoke-test gates pinning measured comment-antecedents precision baselines

Scope: Whole-corpus scans over this repository and, when configured, private and open-source corpora

Overview: Guards the precision of the comment-antecedents rule against silent drift. The default tier was
    selected by hand-labelling every hit across three codebases, and the resulting counts are pinned here
    so that a pattern addition which widens the rule fails the suite rather than passing unnoticed. Only
    the thai-lint baseline runs unconditionally, because the other two corpora are not committed; those
    read a path from an environment variable and skip when it is unset. The self-scan doubles as a
    dogfooding assertion: this repository is expected to hold no comment carrying an unresolvable
    antecedent.

Dependencies: pytest, src.linters.file_header.comment_block_extractor, src.linters.file_header.antecedent_detector

Exports: TestSelfBaseline, TestExternalCorpusBaselines

Interfaces: Reads THAILINT_CORPUS_QBENCH and THAILINT_CORPUS_OSS environment variables for optional corpora

Implementation: Directory walk applying the shipped extractor and detector, counting comment blocks and
    default-tier hits, compared against recorded baselines
"""

import os
from pathlib import Path

import pytest

from src.linters.file_header.antecedent_detector import detect_default_tier
from src.linters.file_header.comment_block_extractor import (
    HASH_SUFFIXES,
    SLASH_SUFFIXES,
    extract_comment_blocks,
)

SUPPORTED = HASH_SUFFIXES | SLASH_SUFFIXES

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".claude",
    ".pytest_cache",
    "dist",
    "build",
    ".terraform",
    ".tox",
    "migrations",
    "htmlcov",
    ".ruff_cache",
    ".thailint-cache",
}
SKIP_PATH_PARTS = ("/site-packages/pip/", ".min.js", "/vendor/", "/static/qbc/assets/")

REPO_ROOT = Path(__file__).resolve().parents[2]


def scan_corpus(root: str) -> tuple[int, list[str]]:
    """Count comment blocks and collect located default-tier hits under a directory tree."""
    blocks = 0
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            suffix = ".just" if filename.endswith(".just") else Path(filename).suffix
            if suffix not in SUPPORTED:
                continue
            path = Path(dirpath) / filename
            if any(part in str(path) for part in SKIP_PATH_PARTS):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for block in extract_comment_blocks(content, suffix):
                blocks += 1
                phrase = detect_default_tier(block.text)
                if phrase:
                    hits.append(f"{path}:{block.start_line} [{phrase}]")
    return blocks, hits


class TestSelfBaseline:
    """Dogfooding baseline for this repository."""

    def test_this_repository_holds_no_unresolvable_antecedents(self):
        """Should find no default-tier hit anywhere in this repository."""
        _blocks, hits = scan_corpus(str(REPO_ROOT))

        assert hits == [], "unexpected comment antecedents in this repository:\n" + "\n".join(hits)

    def test_the_self_scan_reads_a_meaningful_number_of_blocks(self):
        """Should scan a substantial corpus, so a zero result is not an empty walk."""
        blocks, _hits = scan_corpus(str(REPO_ROOT))

        assert blocks > 1500


class TestExternalCorpusBaselines:
    """Baselines for corpora that are not committed to this repository."""

    @pytest.mark.parametrize(
        ("env_var", "expected_hits", "min_blocks"),
        [
            # Hand-labelled: 19/19 true, 0 false positives.
            ("THAILINT_CORPUS_QBENCH", 19, 20000),
            # Hand-labelled: 57/57 true, 0 false positives.
            ("THAILINT_CORPUS_OSS", 57, 150000),
        ],
    )
    def test_external_corpus_reproduces_its_baseline(self, env_var, expected_hits, min_blocks):
        """Should reproduce the recorded hit count for a configured corpus."""
        root = os.environ.get(env_var)
        if not root:
            pytest.skip(f"{env_var} not set")

        blocks, hits = scan_corpus(root)

        assert blocks > min_blocks, f"{root} yielded only {blocks} comment blocks"
        assert len(hits) == expected_hits, (
            f"{env_var} baseline moved: expected {expected_hits}, found {len(hits)}. "
            "A corpus at a different revision drifts as readily as a widened rule, so "
            "compare the located hits below against the labelled set before adjusting "
            "the baseline:\n" + "\n".join(sorted(hits))
        )
