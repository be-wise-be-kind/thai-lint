"""
Purpose: Regression tests for DRY overlap-deduplication scaling and behavior preservation

Scope: ViolationFilter.filter_overlapping and ViolationDeduplicator block/violation dedup

Overview: Guards against the O(v^2) blow-up reported in issue #213, where the per-file overlap
    dedup compared each block/violation against every previously kept item, hanging for over an
    hour on files with thousands of internal duplicates. Verifies the dedup now scales linearly by
    counting how many pairwise overlap comparisons run on a pathological single-file input (each
    item compared against only the last kept item). Also pins behavior with independent brute-force
    reference implementations so the linear rewrite produces identical output to the original
    all-pairs logic across randomized inputs.

Dependencies: pytest, unittest.mock, pathlib.Path, src.core.types.Violation,
    src.linters.dry.cache.CodeBlock, ViolationFilter, ViolationDeduplicator

Exports: TestOverlapDedupScaling, TestOverlapDedupEquivalence test classes

Interfaces: Tests filter_overlapping(violations) and deduplicate_blocks/deduplicate_violations

Implementation: Comparison-count instrumentation via mock wrappers for scaling assertions;
    inline brute-force references for equivalence assertions on randomized inputs
"""

import random
from pathlib import Path
from unittest.mock import patch

from src.core.types import Violation
from src.linters.dry.cache import CodeBlock
from src.linters.dry.deduplicator import ViolationDeduplicator
from src.linters.dry.violation_filter import ViolationFilter

# Size of the pathological single-file input. Large enough that the original
# O(v^2) all-pairs scan vastly exceeds a linear comparison budget.
PATHOLOGICAL_N = 500


def make_violation(line: int, line_count: int = 4) -> Violation:
    """Build a DRY-style violation whose message encodes the duplicate line count."""
    return Violation(
        rule_id="dry.duplicate-code",
        file_path="repetitive.py",
        line=line,
        column=1,
        message=f"Duplicate code ({line_count} lines, 2 occurrences) detected",
    )


def make_block(start_line: int, line_count: int = 4) -> CodeBlock:
    """Build a CodeBlock spanning line_count lines from start_line."""
    return CodeBlock(
        file_path=Path("repetitive.py"),
        start_line=start_line,
        end_line=start_line + line_count - 1,
        snippet="x = 1\ny = 2\nz = 3\nw = 4",
        hash_value=42,
    )


def _bruteforce_filter_violations(violations: list[Violation]) -> list[Violation]:
    """Independent reference for the original all-pairs violation overlap filter."""

    def line_count(message: str) -> int:
        try:
            start = message.index("(") + 1
            end = message.index(" lines")
            return int(message[start:end])
        except (ValueError, IndexError):
            return 5

    ordered = sorted(violations, key=lambda v: v.line or 0)
    kept: list[Violation] = []
    for v in ordered:
        if not any((v.line or 0) < (k.line or 0) + line_count(v.message) for k in kept):
            kept.append(v)
    return kept


def _bruteforce_dedup_blocks(blocks: list[CodeBlock]) -> list[CodeBlock]:
    """Independent reference for the original all-pairs block overlap dedup (single file)."""
    ordered = sorted(blocks, key=lambda b: b.start_line)
    kept: list[CodeBlock] = []
    for b in ordered:
        if not any(b.start_line <= k.end_line and k.start_line <= b.end_line for k in kept):
            kept.append(b)
    return kept


class TestOverlapDedupScaling:
    """Pairwise overlap comparisons must scale linearly, not quadratically (issue #213)."""

    def test_violation_filter_runs_linear_comparison_count(self) -> None:
        """filter_overlapping must compare each violation against O(1) kept items, not all."""
        # Consecutive overlapping windows: the report's pathological repetitive-file shape.
        violations = [make_violation(line) for line in range(1, PATHOLOGICAL_N + 1)]
        vf = ViolationFilter()
        original = vf._overlaps
        calls = 0

        def counting(*args, **kwargs):
            nonlocal calls
            calls += 1
            return original(*args, **kwargs)

        with patch.object(vf, "_overlaps", side_effect=counting):
            kept = vf.filter_overlapping(violations)

        assert kept == _bruteforce_filter_violations(violations)
        assert calls <= 4 * PATHOLOGICAL_N, f"expected linear comparisons, got {calls}"

    def test_block_dedup_runs_linear_comparison_count(self) -> None:
        """deduplicate_blocks must compare each block against O(1) kept blocks, not all."""
        blocks = [make_block(line) for line in range(1, PATHOLOGICAL_N + 1)]
        dedup = ViolationDeduplicator()
        original = dedup._blocks_overlap
        calls = 0

        def counting(*args, **kwargs):
            nonlocal calls
            calls += 1
            return original(*args, **kwargs)

        with patch.object(dedup, "_blocks_overlap", side_effect=counting):
            kept = dedup.deduplicate_blocks(blocks)

        assert sorted(b.start_line for b in kept) == sorted(
            b.start_line for b in _bruteforce_dedup_blocks(blocks)
        )
        assert calls <= 4 * PATHOLOGICAL_N, f"expected linear comparisons, got {calls}"


class TestOverlapDedupEquivalence:
    """Linear rewrite must produce identical output to the original all-pairs logic."""

    def test_violation_filter_matches_bruteforce_on_random_inputs(self) -> None:
        """filter_overlapping output equals the brute-force reference across random inputs."""
        rng = random.Random(1234)
        for _ in range(50):
            lines = rng.sample(range(1, 300), rng.randint(1, 60))
            violations = [make_violation(line, rng.randint(3, 8)) for line in lines]
            expected = _bruteforce_filter_violations(violations)
            actual = ViolationFilter().filter_overlapping(
                sorted(violations, key=lambda v: v.line or 0)
            )
            assert [v.line for v in actual] == [v.line for v in expected]

    def test_block_dedup_matches_bruteforce_on_random_inputs(self) -> None:
        """deduplicate_blocks output equals the brute-force reference across random inputs."""
        rng = random.Random(5678)
        for _ in range(50):
            starts = rng.sample(range(1, 300), rng.randint(1, 60))
            blocks = [make_block(start, rng.randint(3, 8)) for start in starts]
            expected = _bruteforce_dedup_blocks(blocks)
            actual = ViolationDeduplicator().deduplicate_blocks(blocks)
            assert sorted(b.start_line for b in actual) == sorted(b.start_line for b in expected)
