"""
Purpose: Unit tests proving the comment-antecedents rule and header validation never double-report

Scope: Boundary between header prose, which file-header.validation owns, and body prose, which the comment-antecedents rule owns

Overview: Test suite pinning the division of labour between the two rules in the file_header package.
    The header-scoped rule reads only the extracted header block; the comment-antecedents rule reads only
    what lies below it. These tests assert that a phrase inside a header never produces a
    comment-antecedents violation, that existing header validation behaviour is unchanged by the presence
    of the new rule, and that the established enforce_atemporal setting does not gate the body scan. That
    last assertion matters because widening an existing default-on setting would silently change what a
    user's configuration means.

Dependencies: pytest, src.linters.file_header.comment_antecedent_rule, src.linters.file_header.linter,
    conftest.create_mock_context

Exports: TestHeaderPhrasesAreNotBodyViolations, TestHeaderValidationUnaffected, TestConfigIndependence

Interfaces: Exercises CommentAntecedentRule.check(context) and FileHeaderRule.check(context)

Implementation: Arrange/act/assert bodies mapped one-to-one onto Given/When/Then scenario steps
"""

from .conftest import create_mock_context

COMMENT_RULE_ID = "file-header.comment-antecedents"
HEADER_RULE_ID = "file-header.validation"


class TestHeaderPhrasesAreNotBodyViolations:
    """Test that header prose is outside the comment-antecedents rule's scope."""

    def test_a_phrase_in_a_bash_header_is_not_reported_by_the_comment_rule(self):
        """Should not flag a matching phrase that sits inside a bash header block."""
        code = (
            "# Purpose: thing\n"
            "# Scope: thing\n"
            "# Overview: the flag used to be a boolean\n"
            "\n"
            "echo hi\n"
        )

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "run.sh", language="bash"))

        assert violations == []

    def test_a_phrase_in_a_python_module_docstring_is_not_reported_by_the_comment_rule(self):
        """Should not flag a matching phrase that sits inside a module docstring."""
        code = '"""\nPurpose: thing\nOverview: the flag used to be a boolean\n"""\n\nx = 1\n'

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert violations == []


class TestHeaderValidationUnaffected:
    """Test that the established header rule keeps its behaviour."""

    def test_header_validation_still_reports_temporal_language(self):
        """Should keep reporting temporal language in the header under the header rule id."""
        code = '''"""
Purpose: Authentication handler
Scope: Currently handles login
Overview: Handles user authentication for the application
Dependencies: bcrypt
Exports: AuthHandler
Interfaces: login()
Implementation: Standard authentication
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert any(v.rule_id == HEADER_RULE_ID for v in violations)

    def test_the_header_rule_does_not_emit_comment_antecedents_violations(self):
        """Should keep the header rule from claiming the comment-antecedents rule id."""
        code = '''"""
Purpose: Authentication handler
Scope: Currently handles login
Overview: Handles user authentication for the application
Dependencies: bcrypt
Exports: AuthHandler
Interfaces: login()
Implementation: Standard authentication
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        violations = rule.check(create_mock_context(code, "test.py"))

        assert not any(v.rule_id == COMMENT_RULE_ID for v in violations)


class TestConfigIndependence:
    """Test that the body scan has its own configuration switch."""

    def test_disabling_enforce_atemporal_does_not_disable_the_comment_rule(self):
        """Should keep scanning body comments when header temporal checking is switched off."""
        code = '"""\nPurpose: Fixture\nScope: Fixture\nOverview: Fixture module\n"""\n\n# the flag used to be a boolean\nx = 1\n'

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        context = create_mock_context(
            code, "test.py", metadata={"file_header": {"enforce_atemporal": False}}
        )
        violations = rule.check(context)

        assert len(violations) == 1

    def test_disabling_the_comment_rule_leaves_header_validation_running(self):
        """Should keep header validation active when the body scan is switched off."""
        code = '''"""
Purpose: Authentication handler
Scope: Currently handles login
Overview: Handles user authentication for the application
Dependencies: bcrypt
Exports: AuthHandler
Interfaces: login()
Implementation: Standard authentication
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code, "test.py", metadata={"file_header": {"check_comment_antecedents": False}}
        )
        violations = rule.check(context)

        assert any(v.rule_id == HEADER_RULE_ID for v in violations)

    def test_the_comment_rule_honours_its_own_disable_switch(self):
        """Should report nothing when check_comment_antecedents is false."""
        code = '"""\nPurpose: Fixture\nScope: Fixture\nOverview: Fixture module\n"""\n\n# the flag used to be a boolean\nx = 1\n'

        from src.linters.file_header.comment_antecedent_rule import CommentAntecedentRule

        rule = CommentAntecedentRule()
        context = create_mock_context(
            code, "test.py", metadata={"file_header": {"check_comment_antecedents": False}}
        )
        violations = rule.check(context)

        assert violations == []
