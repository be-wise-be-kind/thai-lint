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

Exports: TestSelfBaseline, TestExternalCorpusBaselines, MAX_HIT_RATE_PER_1K

Interfaces: Reads THAILINT_CORPUS_QBENCH and THAILINT_CORPUS_OSS environment variables for optional corpora

Implementation: Directory walk applying the shipped extractor and detector, counting comment blocks and
    default-tier hits, asserted as a ceiling on both absolute count and firing rate
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

# Ceiling on firing density, per 1,000 comment blocks. The labelled corpora measured 0.35
# (OSS) and 0.79 (qbench); this leaves headroom for corpus churn while still failing if the
# rule starts firing several times more often than it was measured doing.
MAX_HIT_RATE_PER_1K = 1.5


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
        ("env_var", "baseline_hits", "min_blocks"),
        [
            # Hand-labelled at the revision measured: 19/19 true, 0 false positives.
            ("THAILINT_CORPUS_QBENCH", 19, 20000),
            # Hand-labelled at the revision measured: 57/57 true, 0 false positives.
            ("THAILINT_CORPUS_OSS", 57, 150000),
        ],
    )
    def test_external_corpus_does_not_exceed_its_baseline(self, env_var, baseline_hits, min_blocks):
        """Should not report more than the labelled baseline, by count or by rate.

        Asserted as a ceiling rather than an equality. These corpora are live checkouts that
        nobody pins: qbench landed 55 commits in the day after the baseline was taken, one of
        which deleted a comment the baseline counted. An equality assertion reads that as a
        failure identical to the rule widening, which is the thing the gate exists to catch.
        A ceiling separates them — deleting a comment cannot trip it, and adding a pattern
        that widens the rule still does.
        """
        root = os.environ.get(env_var)
        if not root:
            pytest.skip(f"{env_var} not set")

        blocks, hits = scan_corpus(root)
        rate = len(hits) / blocks * 1000

        assert blocks > min_blocks, f"{root} yielded only {blocks} comment blocks"
        assert len(hits) <= baseline_hits, (
            f"{env_var} reports {len(hits)} hits against a labelled baseline of "
            f"{baseline_hits}. Every hit below the baseline was hand-checked as a true "
            "positive; anything beyond it is unlabelled and must be read before the "
            "baseline moves:\n" + "\n".join(sorted(hits))
        )
        assert rate <= MAX_HIT_RATE_PER_1K, (
            f"{env_var} hit rate {rate:.2f} per 1k blocks exceeds {MAX_HIT_RATE_PER_1K}. "
            "The rule is firing more densely than the labelled measurement, which a "
            "shrinking corpus alone cannot cause."
        )
