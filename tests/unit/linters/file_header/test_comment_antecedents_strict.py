"""
Purpose: Unit tests for the opt-in strict tier of the comment-antecedents rule

Scope: Habitual-past detection gated behind the comment_antecedents_strict configuration flag

Overview: Test suite for the strict tier, which trades precision for recall by flagging the habitual-past
    sense of "used to" when a contrast word sits near it. The tier measured 86% precision on an
    open-source corpus, below the project's acceptance threshold, so it stays disabled unless a user asks
    for it. These tests pin that default-off behaviour, the grammar gating that separates habitual past
    from the passive and purposive senses, and the proximity requirement that keeps a distant contrast
    word from validating an unrelated phrase.

Dependencies: pytest, src.linters.file_header.comment_antecedent_rule, conftest.create_mock_context

Exports: TestStrictModeDefault, TestStrictModeDetection, TestStrictModeGrammarGating, TestStrictModeProximity

Interfaces: Exercises CommentAntecedentRule.check(context) -> list[Violation]

Implementation: Arrange/act/assert bodies mapped one-to-one onto Given/When/Then scenario steps,
    parametrized where the specification uses a Scenario Outline
"""

import pytest

from .conftest import create_mock_context

PY_HEADER = '"""\nPurpose: Fixture\nScope: Fixture\nOverview: Fixture module for tests\n"""\n'
STRICT_ON = {"file_header": {"comment_antecedents_strict": True}}


def _py_source(comment: str) -> str:
    """Build a Python source string carrying one mid-file comment."""
    return f"{PY_HEADER}\n\n# {comment}\nx = 1\n"


class TestStrictModeDefault:
    """Test that the strict tier stays off unless requested."""

    def test_strict_mode_is_disabled_by_default(self):
        """Should report nothing for habitual past under default configuration."""
        code = _py_source("This route used to refuse outright. It no longer does")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []


class TestStrictModeDetection:
    """Test habitual-past detection when the strict tier is enabled."""

    def test_strict_mode_flags_habitual_past_with_a_nearby_contrast_word(self):
        """Should flag habitual past paired with a nearby contrast word."""
        code = _py_source("This route used to refuse outright. It no longer does")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py", metadata=STRICT_ON))

        assert len(violations) == 1

    def test_tier_one_results_are_unchanged_when_strict_mode_is_enabled(self):
        """Should keep reporting one violation for a tier-one phrase under strict mode."""
        code = _py_source("the flag used to be a boolean")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py", metadata=STRICT_ON))

        assert len(violations) == 1


class TestStrictModeGrammarGating:
    """Test that the passive and purposive senses stay silent under strict mode."""

    @pytest.mark.parametrize(
        "comment",
        [
            "This callback is used to reload the user object, not the old one",
            "Used to iterate over part of the tree instead of the whole",
            "A structural comparison, used to spot edited fields, now buffered",
            "Can be used to overwrite the toolbar instead of replacing it",
        ],
    )
    def test_strict_mode_does_not_flag_the_passive_or_purposive_sense(self, comment):
        """Should not flag 'used to' meaning 'utilised to'."""
        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        context = create_mock_context(_py_source(comment), "test.py", metadata=STRICT_ON)
        violations = rule.check(context)

        assert violations == []


class TestStrictModeProximity:
    """Test the distance requirement between phrase and contrast word."""

    def test_strict_mode_requires_the_contrast_word_to_be_near_the_phrase(self):
        """Should not flag when the contrast word sits beyond the proximity window."""
        filler = "a" * 100
        code = _py_source(f"an id set used to tell a fresh sync from a resync {filler} instead")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py", metadata=STRICT_ON))

        assert violations == []
