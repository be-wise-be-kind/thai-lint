"""
Purpose: Unit tests pinning every suppression scope for the comment-antecedents rule

Scope: Line, preceding-line, block, file, and configured-path ignore handling, plus rule-id specificity

Overview: Test suite covering the ignore mechanisms for the comment-antecedents rule. This is the
    identified risk area for the feature: the rule reports on prose, some legitimate prose matches, and
    suppressing a comment means writing a comment beside it, so an unreliable ignore path would make the
    rule unusable rather than merely noisy. Each supported scope gets an explicit regression test, and a
    negative test asserts that an unrelated rule id in an ignore directive does not silence this rule.
    None of these scenarios may be skipped or marked expected-failure; a failure here blocks the feature.

Dependencies: pytest, src.linters.file_header.comment_antecedent_rule, conftest.create_mock_context

Exports: TestLineScopeSuppression, TestFileScopeSuppression, TestBlockScopeSuppression,
    TestRuleIdSpecificity, TestPathSuppression

Interfaces: Exercises CommentAntecedentRule.check(context) -> list[Violation]

Implementation: Arrange/act/assert bodies mapped one-to-one onto Given/When/Then scenario steps
"""

from .conftest import create_mock_context

PY_HEADER = '"""\nPurpose: Fixture\nScope: Fixture\nOverview: Fixture module for tests\n"""\n'
PHRASE = "the flag used to be a boolean"


class TestLineScopeSuppression:
    """Test line-level and preceding-line ignore directives."""

    def test_a_line_level_ignore_suppresses_the_violation(self):
        """Should suppress when the block's first line carries an inline ignore."""
        code = (
            f"{PY_HEADER}\n\n"
            f"# {PHRASE}  # thailint: ignore[file-header.comment-antecedents]\n"
            "x = 1\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []

    def test_a_line_level_ignore_suppresses_a_multi_line_block(self):
        """Should suppress when the directive sits on a later line of the block.

        Reporting is per block and anchored to its first line, so a directive written beside
        the offending phrase lands on a different line than the violation. This is the normal
        case for wrapped prose, not an edge case.
        """
        code = (
            f"{PY_HEADER}\n\n"
            "# the lock was reworked in this area\n"
            f"# {PHRASE}  # thailint: ignore[file-header.comment-antecedents]\n"
            "x = 1\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []

    def test_a_multi_line_block_without_a_directive_still_reports(self):
        """Should still report a multi-line block carrying no directive."""
        code = f"{PY_HEADER}\n\n# the lock was reworked in this area\n# {PHRASE}\nx = 1\n"

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert len(violations) == 1

    def test_a_preceding_line_ignore_suppresses_the_violation(self):
        """Should suppress when an ignore-next-line directive precedes the block."""
        code = (
            f"{PY_HEADER}\n\n"
            "# thailint: ignore-next-line[file-header.comment-antecedents]\n"
            f"# {PHRASE}\n"
            "x = 1\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []


class TestFileScopeSuppression:
    """Test file-level ignore directives."""

    def test_a_file_level_ignore_suppresses_all_violations_in_the_file(self):
        """Should suppress every block when a file-level directive is present."""
        code = (
            "# thailint: ignore-file[file-header.comment-antecedents]\n"
            f"{PY_HEADER}\n\n"
            f"# {PHRASE}\n"
            "x = 1\n"
            f"# the guard used to be a no-op\n"
            "y = 2\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []


class TestBlockScopeSuppression:
    """Test ignore-start and ignore-end directives, the fifth ignore scope."""

    def test_a_block_scope_ignore_suppresses_violations_inside_the_region(self):
        """Should suppress a violation sitting between ignore-start and ignore-end."""
        code = (
            f"{PY_HEADER}\n\n"
            "# thailint: ignore-start[file-header.comment-antecedents]\n"
            f"# {PHRASE}\n"
            "x = 1\n"
            "# thailint: ignore-end[file-header.comment-antecedents]\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []

    def test_a_violation_outside_the_region_still_reports(self):
        """Should still report a violation after the region closes."""
        code = (
            f"{PY_HEADER}\n\n"
            "# thailint: ignore-start[file-header.comment-antecedents]\n"
            "# nothing to see here\n"
            "# thailint: ignore-end[file-header.comment-antecedents]\n"
            "\n"
            f"# {PHRASE}\n"
            "y = 2\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert len(violations) == 1


class TestRuleIdSpecificity:
    """Test that suppression is scoped to the correct rule id."""

    def test_an_unrelated_rule_id_in_the_ignore_does_not_suppress(self):
        """Should still report when the ignore names a different rule."""
        code = f"{PY_HEADER}\n\n# {PHRASE}  # thailint: ignore[nesting]\nx = 1\n"

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert len(violations) == 1


class TestPathSuppression:
    """Test configured ignore patterns."""

    def test_a_configured_ignore_pattern_excludes_a_path(self):
        """Should skip a file whose path matches a configured ignore pattern."""
        code = f"{PY_HEADER}\n\n# {PHRASE}\nx = 1\n"

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        context = create_mock_context(
            code, "vendor/lib.py", metadata={"file_header": {"ignore": ["vendor/**"]}}
        )
        violations = rule.check(context)

        assert violations == []
