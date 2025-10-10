"""
Purpose: Test SRP violation message formatting and content

Scope: Violation message structure, formatting, and helpful suggestions for SRP violations

Overview: Validates violation message formatting for SRP linter including class name
    inclusion in messages, metric value reporting (method counts, LOC values), helpful
    refactoring suggestions (extract class, split responsibilities), message consistency
    across violation types, multiple violation reporting for single class, and actionable
    guidance for developers. Ensures violation messages provide clear, informative feedback
    that helps developers understand and fix SRP violations effectively.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestViolationMessageFormat (8 tests) covering message content and suggestions

Interfaces: Tests Violation.message and Violation.suggestion fields from SRPRule.check()

Implementation: Validates message strings contain expected information, verifies
    suggestion quality and actionability
"""


class TestViolationMessageFormat:
    """Test SRP violation message formatting and content."""

    # Message should mention LOC violation

    # Suggestion should mention extracting or splitting

    # Message should mention multiple issues (methods, LOC, keyword)

    # Message should follow pattern: "Class 'Name' may violate SRP: ..."

    # Message should mention responsibility keyword issue

    # Suggestion should mention extracting or splitting classes
