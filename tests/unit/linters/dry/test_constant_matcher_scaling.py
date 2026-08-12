"""
Purpose: Regression test for find_constant_groups all-pairs fuzzy matching blowup

Scope: constant_matcher.find_constant_groups edit-distance comparison scaling

Overview: Guards against an O(N^2) blowup discovered while benchmarking the DRY linter against
    a real multi-thousand-file monorepo: find_constant_groups ran combinations(names, 2) over
    every distinct constant name collected across the whole scan, calling the Levenshtein-based
    edit-distance check on every pair regardless of whether the pair could possibly match. Since
    edit distance can never be smaller than the difference in string length, two names whose
    lengths differ by more than MAX_EDIT_DISTANCE can never match, so comparing them at all is
    wasted work that becomes catastrophic as the number of distinct constant names grows into the
    thousands (real monorepos easily have tens of thousands). Verifies the edit-distance check is
    skipped entirely for length-incompatible pairs by counting calls to the Levenshtein distance
    function on an input engineered so no two names are within the matching window.

Dependencies: pytest, unittest.mock, pathlib.Path, src.linters.dry.constant,
    src.linters.dry.constant_matcher

Exports: TestConstantMatcherScaling test class

Interfaces: Tests find_constant_groups(constants: list[tuple[Path, ConstantInfo]])
    -> list[ConstantGroup]

Implementation: Builds names whose lengths are spaced further apart than MAX_EDIT_DISTANCE so no
    pair can ever match, wraps the Levenshtein distance function with a call counter, and asserts
    it is never invoked
"""

from pathlib import Path
from unittest.mock import patch

from src.linters.dry import constant_matcher
from src.linters.dry.constant import ConstantInfo

# Enough distinct names to make an all-pairs blowup obvious (N*(N-1)/2 pairs).
MANY_NAMES = 200

# Length step between consecutive names, chosen to exceed MAX_EDIT_DISTANCE (2)
# so no two generated names can ever be within the fuzzy-match length window.
LENGTH_STEP = 3


def _build_length_separated_names(n: int) -> list[tuple[Path, ConstantInfo]]:
    """Build constants whose names have pairwise length differences > MAX_EDIT_DISTANCE.

    Each name has 3 underscore-separated words (satisfying the >= 2 word minimum for
    fuzzy matching) and a distinct word-set (so word-set matching never short-circuits
    before the edit-distance check would otherwise run).
    """
    constants = []
    for i in range(n):
        name = f"WORD_{'X' * (i * LENGTH_STEP)}_TAIL{i}"
        constants.append((Path(f"file_{i}.py"), ConstantInfo(name=name, value="x", line_number=1)))
    return constants


class TestConstantMatcherScaling:
    """find_constant_groups must not compare every pair of distinct constant names."""

    def test_length_incompatible_pairs_never_reach_edit_distance(self) -> None:
        """Names whose lengths differ by more than MAX_EDIT_DISTANCE must skip Levenshtein."""
        constants = _build_length_separated_names(MANY_NAMES)

        original_distance = constant_matcher._levenshtein_distance
        distance_calls = 0

        def counting(*args, **kwargs):
            nonlocal distance_calls
            distance_calls += 1
            return original_distance(*args, **kwargs)

        with patch.object(constant_matcher, "_levenshtein_distance", counting):
            constant_matcher.find_constant_groups(constants)

        # Every one of the MANY_NAMES*(MANY_NAMES-1)/2 pairs is length-incompatible by
        # construction, so a correct implementation calls Levenshtein zero times. The
        # previous all-pairs implementation called it for every single pair (19,900 times
        # at MANY_NAMES=200).
        assert distance_calls == 0, f"expected 0 Levenshtein calls, got {distance_calls}"
