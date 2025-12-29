"""
Purpose: Fuzzy matching for constant names across files

Scope: Constant name matching with word-set and edit distance algorithms

Overview: Implements fuzzy matching strategies to identify related constants across files. Uses
    two matching strategies: word-set matching (same words in different order, e.g., API_TIMEOUT
    and TIMEOUT_API) and edit distance matching (typos within Levenshtein distance <= 2, e.g.,
    MAX_RETRYS and MAX_RETRIES). Single-word constants (e.g., MAX, TIMEOUT) only use exact
    matching to avoid false positives. Groups related constants into ConstantGroup instances
    for violation reporting.

Dependencies: ConstantInfo, ConstantLocation, ConstantGroup from constant module

Exports: find_constant_groups function

Interfaces: find_constant_groups(constants) -> list[ConstantGroup]

Implementation: Union-Find algorithm for grouping, word-set hashing, Levenshtein distance calculation

Suppressions:
    - arguments-out-of-order: Named arguments used for clarity in ConstantLocation
"""

from collections.abc import Callable
from itertools import combinations
from pathlib import Path

from .constant import ConstantGroup, ConstantInfo, ConstantLocation

# Maximum edit distance for fuzzy matching
MAX_EDIT_DISTANCE = 2

# Antonym pairs that should not be fuzzy-matched
# If one name contains a word from the left side and the other contains the right side,
# they represent different concepts and should not be grouped together
ANTONYM_PAIRS = frozenset(
    (
        frozenset(("max", "min")),
        frozenset(("start", "end")),
        frozenset(("first", "last")),
        frozenset(("before", "after")),
        frozenset(("open", "close")),
        frozenset(("read", "write")),
        frozenset(("get", "set")),
        frozenset(("push", "pop")),
        frozenset(("add", "remove")),
        frozenset(("create", "delete")),
        frozenset(("enable", "disable")),
        frozenset(("show", "hide")),
        frozenset(("up", "down")),
        frozenset(("left", "right")),
        frozenset(("top", "bottom")),
        frozenset(("prev", "next")),
        frozenset(("success", "failure")),
        frozenset(("true", "false")),
        frozenset(("on", "off")),
        frozenset(("in", "out")),
    )
)

# Minimum length for constant names (exclude single-letter type params like P, T, K, V)
MIN_CONSTANT_NAME_LENGTH = 2


class UnionFind:
    """Union-Find data structure for grouping."""

    def __init__(self, items: list[str]) -> None:
        """Initialize with list of items."""
        self._parent = {item: item for item in items}

    def find(self, x: str) -> str:
        """Find root with path compression."""
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: str, y: str) -> None:
        """Merge two sets."""
        px, py = self.find(x), self.find(y)
        if px != py:
            self._parent[px] = py


def find_constant_groups(constants: list[tuple[Path, ConstantInfo]]) -> list[ConstantGroup]:
    """Find groups of related constants.

    Args:
        constants: List of (file_path, ConstantInfo) tuples

    Returns:
        List of ConstantGroup instances representing related constants
    """
    if not constants:
        return []
    locations = _build_locations(constants)
    exact_groups = _group_by_exact_name(locations)
    return _merge_fuzzy_groups(exact_groups)


def _merge_fuzzy_groups(groups: dict[str, ConstantGroup]) -> list[ConstantGroup]:
    """Merge groups that match via fuzzy matching."""
    names = list(groups.keys())
    uf = UnionFind(names)
    _union_matching_pairs(names, uf, _is_fuzzy_match)
    return _build_merged_groups(names, groups, uf)


def _is_fuzzy_match(name1: str, name2: str) -> bool:
    """Check if two constant names should be considered a match."""
    if name1 == name2:
        return True
    return _is_fuzzy_similar(name1, name2)


def _build_locations(constants: list[tuple[Path, ConstantInfo]]) -> list[ConstantLocation]:
    """Build location list from constants."""
    return [
        ConstantLocation(
            file_path=file_path, line_number=info.line_number, name=info.name, value=info.value
        )
        for file_path, info in constants
    ]


def _group_by_exact_name(locations: list[ConstantLocation]) -> dict[str, ConstantGroup]:
    """Group locations by exact constant name."""
    groups: dict[str, ConstantGroup] = {}
    for loc in locations:
        if loc.name not in groups:
            groups[loc.name] = ConstantGroup(
                canonical_name=loc.name, locations=[], all_names=set(), is_fuzzy_match=False
            )
        groups[loc.name].add_location(loc)
    return groups


def _union_matching_pairs(
    names: list[str], uf: UnionFind, is_match: Callable[[str, str], bool]
) -> None:
    """Union all pairs of names that match."""
    for name1, name2 in combinations(names, 2):
        if is_match(name1, name2):
            uf.union(name1, name2)


def _build_merged_groups(
    names: list[str], groups: dict[str, ConstantGroup], uf: UnionFind
) -> list[ConstantGroup]:
    """Build merged groups from union-find structure."""
    merged: dict[str, ConstantGroup] = {}
    for name in names:
        root = uf.find(name)
        if root not in merged:
            merged[root] = ConstantGroup(
                canonical_name=root, locations=[], all_names=set(), is_fuzzy_match=False
            )
        for loc in groups[name].locations:
            merged[root].add_location(loc)
        if name != root:
            merged[root].is_fuzzy_match = True
    return list(merged.values())


def _get_words(name: str) -> list[str]:
    """Split constant name into lowercase words."""
    return [w.lower() for w in name.split("_") if w]


def _is_fuzzy_similar(name1: str, name2: str) -> bool:
    """Check if two names are fuzzy similar (word-set or edit distance)."""
    words1, words2 = _get_words(name1), _get_words(name2)
    if not _has_enough_words(words1, words2):
        return False
    if _has_antonym_conflict(set(words1), set(words2)):
        return False
    return _word_set_match(words1, words2) or _edit_distance_match(name1, name2)


def _has_enough_words(words1: list[str], words2: list[str]) -> bool:
    """Check if both word lists have at least 2 words for fuzzy matching."""
    return len(words1) >= 2 and len(words2) >= 2


def _word_set_match(words1: list[str], words2: list[str]) -> bool:
    """Check if two word lists contain the same words."""
    return set(words1) == set(words2)


def _has_antonym_conflict(set1: set[str], set2: set[str]) -> bool:
    """Check if word sets contain conflicting antonyms (e.g., MAX vs MIN)."""
    return any(_is_antonym_split(pair, set1, set2) for pair in ANTONYM_PAIRS)


def _is_antonym_split(pair: frozenset[str], set1: set[str], set2: set[str]) -> bool:
    """Check if one set has one word of the pair and the other has the opposite."""
    pair_list = tuple(pair)
    word_a, word_b = pair_list[0], pair_list[1]
    return (word_a in set1 and word_b in set2) or (word_b in set1 and word_a in set2)


def _edit_distance_match(name1: str, name2: str) -> bool:
    """Check if names match within edit distance threshold."""
    return _levenshtein_distance(name1.lower(), name2.lower()) <= MAX_EDIT_DISTANCE


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)  # pylint: disable=arguments-out-of-order
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
