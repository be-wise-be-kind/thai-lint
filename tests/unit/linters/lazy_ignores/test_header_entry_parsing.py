"""
Purpose: Regression tests for Suppressions entry parsing edge cases

Scope: Unit tests for SuppressionsParser entry splitting and end-to-end justification matching

Overview: Test suite covering header Suppressions entries whose justification prose does not
    begin with a plain word character, entries whose justification contains a colon, and
    entries whose justification wraps across multiple lines. Each shape previously caused the
    entry to be dropped or mis-keyed, which surfaced as spurious unjustified and orphaned
    violations on suppressions that were genuinely documented. Also covers em dash and en dash
    inline justification separators alongside the ASCII hyphen form.

Dependencies: pytest, src.linters.lazy_ignores modules

Exports: Test classes for header entry parsing regressions

Interfaces: pytest test discovery and execution

Implementation: Parser-level unit tests paired with end-to-end LazyIgnoresRule assertions
"""

import pytest

from src.linters.lazy_ignores import LazyIgnoresRule
from src.linters.lazy_ignores.directive_utils import extract_inline_justification
from src.linters.lazy_ignores.header_parser import SuppressionsParser

JUSTIFICATION_PREFIXES = [
    pytest.param("`git` is off PATH; the argv is literal.", id="backtick"),
    pytest.param('"trusted" subprocess input only.', id="double-quote"),
    pytest.param("'trusted' subprocess input only.", id="single-quote"),
    pytest.param("12 branches are inherent to the state machine.", id="digit"),
    pytest.param("(intentional) the argv is literal.", id="paren"),
    pytest.param("[see module docs] the argv is literal.", id="bracket"),
]


def _header_with(justification: str) -> str:
    """Build a Python header whose S607 entry carries the given justification."""
    return f'''"""
Purpose: Test file

Suppressions:
    - S607: {justification}
"""'''


class TestJustificationLeadingCharacter:
    """Entries are parsed regardless of the justification's first character."""

    @pytest.mark.parametrize("justification", JUSTIFICATION_PREFIXES)
    def test_parses_entry_with_non_word_leading_character(self, justification: str) -> None:
        """Parses entries whose justification starts with punctuation or a digit."""
        entries = SuppressionsParser().parse(_header_with(justification))
        assert entries["s607"] == justification

    def test_non_word_justification_justifies_the_ignore(self) -> None:
        """Regression test for GitHub issue #249.

        Issue: https://github.com/be-wise-be-kind/thai-lint/issues/249
        Problem: A Suppressions entry whose justification started with a backtick was
            dropped by the entry regex, so the documented ignore reported as unjustified.
        """
        code = '''"""
Purpose: Test file

Suppressions:
    - S607: `git` is spelled without an absolute path; the argv is otherwise literal.
"""

import subprocess


def run():
    return subprocess.run(["git", "ls-files"], capture_output=True)  # noqa: S607
'''
        violations = LazyIgnoresRule().check_content(code, "test.py")
        assert violations == []


class TestJustificationContainingColon:
    """The rule ID is taken from the first colon, not the last."""

    def test_parses_entry_when_justification_contains_colon(self) -> None:
        """Keys the entry on S607 even though the justification has its own colon."""
        entries = SuppressionsParser().parse(_header_with("note: git is off PATH here."))
        assert entries == {"s607": "note: git is off PATH here."}

    def test_colon_in_justification_justifies_the_ignore(self) -> None:
        """No unjustified or orphaned violation when the justification contains a colon."""
        code = '''"""
Purpose: Test file

Suppressions:
    - S607: reason: the argv is literal and no shell is used.
"""

import subprocess


def run():
    return subprocess.run(["git", "ls-files"], capture_output=True)  # noqa: S607
'''
        violations = LazyIgnoresRule().check_content(code, "test.py")
        assert violations == []


class TestWrappedJustification:
    """Continuation lines belong to their entry, not to a new one."""

    def test_wrapped_justification_stays_with_its_entry(self) -> None:
        """Joins a continuation line onto the preceding entry."""
        header = '''"""
Purpose: Test file

Suppressions:
    - S607: git is spelled without an absolute path; the argv is otherwise literal and the
      call only reads the tracked-file list.
"""'''
        entries = SuppressionsParser().parse(header)
        assert list(entries) == ["s607"]
        assert entries["s607"].endswith("call only reads the tracked-file list.")

    def test_wrapped_line_with_colon_does_not_create_an_entry(self) -> None:
        """A wrapped line containing a colon does not become a bogus entry."""
        header = '''"""
Purpose: Test file

Suppressions:
    - S607: git is invoked bare, and the reason is simple:
      the argv is literal.
    - S603: no shell is used, and the argv is literal.
"""'''
        entries = SuppressionsParser().parse(header)
        assert sorted(entries) == ["s603", "s607"]

    def test_wrapped_entries_produce_no_violations(self) -> None:
        """Sibling entries still match when an earlier justification wraps."""
        code = '''"""
Purpose: Test file

Suppressions:
    - S607: git is invoked bare, and the reason is simple:
      the argv is literal.
    - S603: no shell is used, and the argv is literal.
"""

import subprocess


def run():
    return subprocess.run(["git", "ls-files"], capture_output=True)  # noqa: S603,S607
'''
        violations = LazyIgnoresRule().check_content(code, "test.py")
        assert violations == []

    def test_flush_indent_continuation_stays_with_its_bulleted_entry(self) -> None:
        """Joins a continuation line indented flush with the bullet it wraps."""
        header = '''"""
Purpose: Test file

Suppressions:
    - S607: git is spelled without an absolute path and the reason
    continues here: the argv is literal.
"""'''
        entries = SuppressionsParser().parse(header)
        assert list(entries) == ["s607"]
        assert entries["s607"].endswith("continues here: the argv is literal.")

    def test_unbulleted_entry_after_bulleted_entry_is_its_own_entry(self) -> None:
        """A rule ID line flush with a bullet still starts its own entry."""
        header = '''"""
Purpose: Test file

Suppressions:
    - S607: git is off PATH and the argv is literal.
    S603: no shell is used.
"""'''
        entries = SuppressionsParser().parse(header)
        assert sorted(entries) == ["s603", "s607"]

    def test_jsdoc_wrapped_justification_stays_with_its_entry(self) -> None:
        """Joins JSDoc continuation lines onto the preceding entry."""
        header = """/**
 * Purpose: Test component
 *
 * Suppressions:
 *   @ts-ignore: the upstream types are wrong, and the reason is simple:
 *     the generic is not inferred.
 */"""
        entries = SuppressionsParser().parse(header)
        assert list(entries) == ["@ts-ignore"]


class TestDashSeparators:
    """Em and en dashes work as inline justification separators."""

    @pytest.mark.parametrize("dash", ["-", "—", "–"], ids=["hyphen", "em", "en"])
    def test_extracts_justification_after_dash(self, dash: str) -> None:
        """Extracts the reason after a hyphen, em dash, or en dash."""
        result = extract_inline_justification(f"# noqa: S607 {dash} the argv is literal")
        assert result == "the argv is literal"

    def test_em_dash_justification_justifies_the_ignore(self) -> None:
        """An em dash inline reason satisfies the linter without a header entry."""
        code = '''"""
Purpose: Test file
"""

import subprocess


def run():
    return subprocess.run(["git"], capture_output=True)  # noqa: S607 — the argv is literal
'''
        violations = LazyIgnoresRule().check_content(code, "test.py")
        assert violations == []

    def test_em_dash_without_spaces_is_not_a_separator(self) -> None:
        """Does not treat an unspaced em dash inside a rule ID as a separator."""
        assert extract_inline_justification("# type: ignore[arg—type]") is None
