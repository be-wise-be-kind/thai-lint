"""
Purpose: Regression tests for IgnoreDirectiveParser block-ignore scaling and behavior preservation

Scope: IgnoreDirectiveParser.should_ignore_violation block-ignore scanning and per-file caching

Overview: Guards against an O(violations x filesize) blowup discovered while benchmarking the DRY
    linter against a real multi-thousand-file monorepo: should_ignore_violation re-read the whole
    file from disk (has_file_ignore) and re-scanned every line of the file (_check_block_ignore)
    from scratch for every single violation, instead of once per file. A file with thousands of
    duplicate-code violations - plausible for repetitive generated/migration code - paid that
    disk-read-plus-full-scan cost thousands of times over. Verifies the parser builds its
    block-ignore index once per distinct file content and answers each violation in near-constant
    time, by counting disk reads and timing many violations against one large file. Also pins
    behavior: because the scan being optimized is an order-dependent state machine that returns as
    it reaches the violation's own line inside an open block (never considering blocks further
    down the file for that violation), a naive independent-per-block rewrite could silently change
    results. An inline brute-force reference reproducing the original line-by-line algorithm is
    compared against the parser's real (optimized) result across randomized block/violation inputs
    to confirm the rewrite is behavior-preserving.

Dependencies: pytest, random, pathlib.Path, unittest.mock, src.core.types.Violation,
    src.linter_config.ignore

Exports: TestBlockIgnorePerformance, TestBlockIgnoreEquivalence test classes

Interfaces: Tests IgnoreDirectiveParser.should_ignore_violation(violation, file_content) -> bool

Implementation: Wraps Path.read_text with a call counter for the disk-read regression; times many
    violations against one large synthetic file for the rescan regression; runs an inline
    brute-force reference implementation of the original algorithm against randomized inputs and
    compares results to the real parser for the equivalence check
"""

import random
import re
import time
from pathlib import Path
from unittest.mock import patch

from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

MANY_VIOLATIONS = 2000
LARGE_FILE_LINES = 3000


def _make_violation(file_path: str, line: int, rule_id: str = "dry.duplicate-code") -> Violation:
    """Build a minimal Violation for a given file/line/rule."""
    return Violation(rule_id=rule_id, file_path=file_path, line=line, column=1, message="dup")


class TestBlockIgnorePerformance:
    """should_ignore_violation must not re-read from disk or re-scan per violation."""

    def test_does_not_read_file_from_disk_when_content_provided(self, tmp_path) -> None:
        """A violation with file_content already available must not trigger a disk read."""
        target = tmp_path / "big.py"
        content = "\n".join(f"x_{i} = {i}" for i in range(LARGE_FILE_LINES))
        target.write_text(content)

        parser = IgnoreDirectiveParser(project_root=tmp_path)
        violations = [_make_violation(str(target), i) for i in range(1, MANY_VIOLATIONS + 1)]

        original_read_text = Path.read_text
        read_calls = 0

        def counting(self, *args, **kwargs):
            nonlocal read_calls
            read_calls += 1
            return original_read_text(self, *args, **kwargs)

        with patch.object(Path, "read_text", counting):
            for v in violations:
                parser.should_ignore_violation(v, content)

        # The previous implementation read the file from disk once per violation
        # (2000 times here) even though the content was already available.
        assert read_calls == 0, f"expected 0 disk reads, got {read_calls}"

    def test_many_violations_against_one_file_is_fast(self, tmp_path) -> None:
        """Many violations against one large file must not each rescan the whole file."""
        target = tmp_path / "big.py"
        content = "\n".join(f"x_{i} = {i}" for i in range(LARGE_FILE_LINES))
        target.write_text(content)

        parser = IgnoreDirectiveParser(project_root=tmp_path)
        violations = [_make_violation(str(target), i) for i in range(1, MANY_VIOLATIONS + 1)]

        start = time.perf_counter()
        for v in violations:
            parser.should_ignore_violation(v, content)
        elapsed = time.perf_counter() - start

        # The previous implementation took over 1.5s for this exact input
        # (O(violations x lines)). A per-file-cached implementation should be
        # at least an order of magnitude faster.
        assert elapsed < 0.5, f"expected well under 0.5s, took {elapsed:.3f}s"


# ---------------------------------------------------------------------------
# Equivalence check: brute-force reference vs. the real (optimized) parser
# ---------------------------------------------------------------------------


def _reference_check_block_ignore(lines: list[str], violation_line: int, rule_id: str) -> bool:
    """Brute-force reference reproducing the original per-violation line scan exactly.

    Mirrors the pre-optimization _check_block_ignore/_process_block_line/_handle_block_end
    state machine: a single left-to-right pass that terminates the instant it reaches the
    violation's own line while inside an open block (regardless of whether the rules match),
    and otherwise only reconsiders the violation retroactively when a later ignore-end marker
    is reached.
    """
    if not (0 < violation_line <= len(lines)):
        return False

    in_block = False
    rules: set[str] = set()
    for i, line in enumerate(lines, 1):
        if _has_start(line):
            rules = _parse_rules(line)
            in_block = True
            continue
        if _has_end(line):
            if in_block and i > violation_line and _rules_match(rules, rule_id):
                return True
            in_block = False
            rules = set()
            continue
        if i == violation_line and in_block:
            return _rules_match(rules, rule_id)
    return False


def _has_start(line: str) -> bool:
    return "ignore-start" in line


def _has_end(line: str) -> bool:
    return "ignore-end" in line


def _parse_rules(line: str) -> set[str]:
    match = re.search(r"ignore-start\s+([^\s#]+(?:\s+[^\s#]+)*)", line)
    if match:
        return {r.strip() for r in re.split(r"[,\s]+", match.group(1).strip()) if r.strip()}
    return {"*"}


def _rules_match(rules: set[str], rule_id: str) -> bool:
    if "*" in rules:
        return True
    return rule_id in rules


def _build_random_content(num_lines: int, rng: random.Random) -> str:
    """Build synthetic file content with randomly scattered ignore-start/end markers."""
    lines = []
    open_rule_pool = ["dry.duplicate-code", "other-rule", "*"]
    for _ in range(num_lines):
        roll = rng.random()
        if roll < 0.08:
            lines.append(f"# thailint: ignore-start {rng.choice(open_rule_pool)}")
        elif roll < 0.16:
            lines.append("# thailint: ignore-end")
        else:
            lines.append(f"code_line_{len(lines)} = {len(lines)}")
    return "\n".join(lines)


class TestBlockIgnoreEquivalence:
    """The optimized block-ignore check must match the original algorithm exactly."""

    def test_matches_reference_across_randomized_inputs(self) -> None:
        """Randomized blocks/violations must produce identical block-ignore decisions."""
        rng = random.Random(1234)
        parser = IgnoreDirectiveParser()

        for trial in range(20):
            content = _build_random_content(80, rng)
            lines = content.splitlines()

            for _ in range(50):
                violation_line = rng.randint(1, len(lines))
                rule_id = rng.choice(["dry.duplicate-code", "other-rule"])
                violation = _make_violation("random.py", violation_line, rule_id)

                expected = _reference_check_block_ignore(lines, violation_line, rule_id)
                actual = parser._check_block_ignore(violation, lines)  # noqa: SLF001
                assert actual == expected, (
                    f"trial {trial}: block-ignore mismatch at line {violation_line} "
                    f"rule={rule_id}: reference={expected} actual={actual}"
                )


class TestCacheIdentityCollisionSafety:
    """A bare id() cache key must never serve another object's cached data.

    CPython's own id() contract states that "two objects with non-overlapping lifetimes
    may have the same id() value." Under --parallel, one long-lived worker process handles
    many files in sequence: each file's content string is created, used briefly, and then
    freed once that file's task returns - exactly the short-lived-object pattern where an
    address gets recycled for a later, unrelated file's content. _lines_cache and
    _block_index_cache are keyed by id() alone with no stored reference to verify the key
    still refers to the same object, so a collision silently serves a previous file's
    cached lines/block-index for the new file's violation checks. These tests force the
    exact collision an id()-reuse race would produce (by writing directly into the cache
    dict rather than relying on GC/allocator timing, which would make the test itself
    flaky) and assert the parser recomputes instead of trusting the stale entry.
    """

    def test_get_cached_lines_recomputes_on_id_collision(self) -> None:
        """A stale entry at a colliding id() must not be returned for different content."""
        parser = IgnoreDirectiveParser(project_root=Path("/tmp"))
        content_a = "line1\nline2 from file A\nline3\n"
        lines_a = parser._get_cached_lines(content_a)  # noqa: SLF001

        content_b = "totally different content from file B\n"
        # Simulate content_a's address having been recycled for content_b: the stale
        # entry is the real (content_a, lines_a) tuple the cache would still hold, now
        # sitting at the id content_b happens to occupy.
        parser._lines_cache[id(content_b)] = (content_a, lines_a)  # noqa: SLF001

        result = parser._get_cached_lines(content_b)  # noqa: SLF001

        assert result == content_b.splitlines(), "cache served file A's stale lines for file B"

    def test_get_block_index_recomputes_on_id_collision(self) -> None:
        """A stale block index at a colliding id(lines) must not be returned for other lines."""
        parser = IgnoreDirectiveParser(project_root=Path("/tmp"))
        lines_a = ["# thailint: ignore-start foo", "violate()", "# thailint: ignore-end"]
        index_a = parser._get_block_index(lines_a)  # noqa: SLF001

        lines_b = ["no", "ignore", "directives", "here"]
        # Simulate lines_a's address having been recycled for lines_b: the stale cache
        # entry is the real (lines_a, index_a) tuple the cache would still hold, now
        # sitting at the id lines_b happens to occupy.
        parser._block_index_cache[id(lines_b)] = (lines_a, index_a)  # noqa: SLF001

        index_b = parser._get_block_index(lines_b)  # noqa: SLF001

        assert not index_b.is_ignored(2, "foo"), "cache served file A's stale block index"

    def test_should_ignore_violation_unaffected_by_colliding_cache_entry(self) -> None:
        """End-to-end: a colliding stale entry must not suppress an unrelated violation."""
        parser = IgnoreDirectiveParser(project_root=Path("/tmp"))

        content_a = "x = 1  # thailint: ignore[foo]\n"
        v_a = _make_violation("/tmp/a.py", 1, "foo")
        assert parser.should_ignore_violation(v_a, content_a) is True

        stale_lines = parser._get_cached_lines(content_a)  # noqa: SLF001
        content_b = "y = 2  # no ignore directive here\n"
        # Simulate content_a's address having been recycled for content_b: the stale
        # entry is the real (content_a, stale_lines) tuple the cache would still hold.
        parser._lines_cache[id(content_b)] = (content_a, stale_lines)  # noqa: SLF001

        v_b = _make_violation("/tmp/b.py", 1, "foo")
        assert parser.should_ignore_violation(v_b, content_b) is False, (
            "file B's violation was incorrectly suppressed via a stale cache collision"
        )
