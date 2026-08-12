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
