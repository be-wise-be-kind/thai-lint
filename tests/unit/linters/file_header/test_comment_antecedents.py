"""
Purpose: Unit tests for comment-antecedents detection of unresolvable referents in mid-file comments

Scope: Former-state and pre-change-state detection, rejected-pattern regression guards, and file selection

Overview: Test suite for the two default-on detectors of the comment-antecedents rule. Former-state
    detection covers comments describing a code state the tree no longer holds; pre-change-state detection
    covers comments anchored to a point before the change that produced the file. A dedicated regression
    class asserts that measured-and-rejected phrases stay silent, so a later contributor cannot reintroduce
    a pattern that failed open-source validation without the test suite objecting. File selection tests pin
    the rule's self-gating on file suffix, which is what allows the rule to read Terraform, YAML, and HCL
    without any change to the orchestrator's extension map.

Dependencies: pytest, src.linters.file_header.comment_antecedent_rule, conftest.create_mock_context

Exports: TestFormerStateDetection, TestPreChangeStateDetection, TestRejectedPatterns, TestFileSelection

Interfaces: Exercises CommentAntecedentRule.check(context) -> list[Violation]

Implementation: Arrange/act/assert bodies mapped one-to-one onto Given/When/Then scenario steps,
    parametrized where the specification uses a Scenario Outline
"""

import pytest

from .conftest import create_mock_context

RULE_ID = "file-header.comment-antecedents"

PY_HEADER = '"""\nPurpose: Fixture\nScope: Fixture\nOverview: Fixture module for tests\n"""\n'


def _py_source(comment: str) -> str:
    """Build a Python source string carrying one mid-file comment."""
    return f"{PY_HEADER}\n\ndef f():\n    # {comment}\n    return 1\n"


class TestFormerStateDetection:
    """Test detection of comments describing a former code state."""

    def test_a_comment_stating_a_former_state_is_flagged(self):
        """Should flag a comment describing what the code used to be."""
        code = _py_source("The lock used to be held across the status flip")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert len(violations) == 1

    def test_the_violation_carries_the_comment_antecedents_rule_id(self):
        """Should report under the comment-antecedents rule id."""
        code = _py_source("The lock used to be held across the status flip")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations[0].rule_id == RULE_ID

    def test_the_violation_line_is_the_first_line_of_the_comment_block(self):
        """Should anchor the violation to the block's first line."""
        code = _py_source("The lock used to be held across the status flip")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations[0].line == 8

    def test_the_violation_message_names_the_offending_phrase(self):
        """Should name the matched phrase in the message."""
        code = _py_source("overlap used to be bool and is now enum")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert "used to be" in violations[0].message

    def test_two_matches_in_one_block_report_once(self):
        """Should report one violation for a block containing the phrase twice."""
        code = (
            f"{PY_HEADER}\n\n"
            "def f():\n"
            "    # The lock used to be held here, and the flag used to be a boolean\n"
            "    # so both halves changed together.\n"
            "    return 1\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert len(violations) == 1

    @pytest.mark.parametrize(
        ("filename", "marker", "language"),
        [
            ("test.py", "#", "python"),
            ("test.sh", "#", "bash"),
            ("test.yaml", "#", "unknown"),
            ("test.tf", "#", "unknown"),
            ("test.hcl", "#", "unknown"),
            ("test.ts", "//", "typescript"),
            ("test.go", "//", "unknown"),
            ("test.rs", "//", "rust"),
        ],
    )
    def test_former_state_detection_spans_comment_syntaxes(self, filename, marker, language):
        """Should detect the phrase across hash and slash comment languages."""
        code = (
            f"{marker} Purpose: header\n\ncode_line = 1\n{marker} the flag used to be a boolean\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, filename, language=language))

        assert len(violations) == 1

    def test_a_purpose_description_is_not_flagged(self):
        """Should not flag the purposive sense of 'used to'."""
        code = _py_source("Flow object used to authenticate with the server")

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []


class TestPreChangeStateDetection:
    """Test detection of comments anchored before the change that produced the code."""

    @pytest.mark.parametrize(
        "phrase",
        [
            "the list every tenant had before this filtering existed",
            "exactly as before this feature existed",
            "before this deprecation was instituted",
            "before this exception was introduced",
            "main() before this change",
        ],
    )
    def test_a_pre_change_anchor_with_an_existence_verb_is_flagged(self, phrase):
        """Should flag a pre-change anchor paired with an existence verb."""
        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(_py_source(phrase), "test.py"))

        assert len(violations) == 1

    @pytest.mark.parametrize(
        "phrase",
        [
            "the SERVER span was created before this hook ran",
            "there is a newline before this position",
            "the customer can submit before this dialog is sent",
            "a bare enabled-check would pass before this arrived",
        ],
    )
    def test_a_runtime_ordering_reference_is_not_flagged(self, phrase):
        """Should not flag 'before this' used for runtime ordering."""
        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(_py_source(phrase), "test.py"))

        assert violations == []


class TestRejectedPatterns:
    """Regression guards for phrases measured and rejected during validation."""

    @pytest.mark.parametrize(
        "comment",
        [
            "ECS never replaces the task when the target stays healthy",
            "This file replaces the single generic reviewer",
            "the withheld-save source this branch sets",
            "without this patch is_settings_enabled returns False",
            "We previously failed to make sense of file as a path",
            "formerly defined here, reexposed for backward compatibility",
            "stand up the new cert before the old one leaves",
            "THREE dots, not two",
        ],
    )
    def test_a_rejected_phrase_produces_no_violation(self, comment):
        """Should stay silent on phrases that failed open-source validation."""
        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(_py_source(comment), "test.py"))

        assert violations == []


class TestFileSelection:
    """Test the rule's self-gating on file suffix."""

    @pytest.mark.parametrize("filename", ["a.tf", "a.yaml", "a.yml", "a.hcl", "a.just"])
    def test_supported_suffixes_are_analysed(self, filename):
        """Should analyse suffixes the orchestrator maps to an unknown language."""
        code = "# Purpose: header\n\nkey = 1\n# the flag used to be a boolean\n"

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, filename, language="unknown"))

        assert len(violations) == 1

    def test_an_unsupported_suffix_is_skipped(self):
        """Should skip a Markdown file even when the phrase is present."""
        code = "# Heading\n\nThe flag used to be a boolean.\n"

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "notes.md", language="markdown"))

        assert violations == []

    def test_vendored_paths_are_excluded_by_default_configuration(self):
        """Should skip vendored trees without any user configuration."""
        code = "// Purpose: header\n\nconst a = 1;\n// the flag used to be a boolean\n"

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        context = create_mock_context(code, "node_modules/pkg/index.js", language="javascript")
        violations = rule.check(context)

        assert violations == []
