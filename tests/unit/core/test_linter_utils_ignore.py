"""
Purpose: Regression tests for is_ignored_path glob-vs-substring matching

Scope: src.core.linter_utils.is_ignored_path pattern matching correctness

Overview: Guards against is_ignored_path() using naive Python substring containment
    instead of gitignore-style glob matching. Substring matching silently ignores files
    whose path merely contains an ignore pattern as a substring of an unrelated segment
    (e.g. pattern "vendor/" wrongly matching "not_vendor/mod.py"), and is the same class
    of bug fixed for other linters in #244. Verifies is_ignored_path() delegates to
    matches_pattern() for real segment-aware glob semantics.

Dependencies: pytest, src.core.linter_utils

Exports: TestIsIgnoredPath

Interfaces: Tests is_ignored_path(file_path, ignore_patterns) -> bool

Implementation: Direct unit tests against the function, no mocking required
"""

from src.core.linter_utils import is_ignored_path


class TestIsIgnoredPath:
    """Test glob-correctness of is_ignored_path()."""

    def test_does_not_match_similarly_named_directory(self) -> None:
        """A directory pattern must not match an unrelated directory containing it as a substring."""
        assert is_ignored_path("not_vendor/mod.py", ["vendor/"]) is False

    def test_matches_exact_directory(self) -> None:
        """A directory pattern still matches files under the real directory."""
        assert is_ignored_path("vendor/mod.py", ["vendor/"]) is True

    def test_matches_nested_directory_glob(self) -> None:
        """Double-star glob patterns still match deeply nested files."""
        assert is_ignored_path("backend/legacy/deep/module.py", ["backend/legacy/**"]) is True

    def test_no_patterns_never_ignores(self) -> None:
        """An empty pattern list ignores nothing."""
        assert is_ignored_path("anything.py", []) is False
