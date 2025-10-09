"""
Purpose: Test suite for magic numbers ignore directive support

Scope: Inline ignore directive handling for magic number violations

Overview: Tests for magic numbers linter ignore directive functionality including inline
    ignore comments, line-specific suppression, and multi-line ignore patterns. Validates
    that thailint ignore directives properly suppress magic number violations while
    maintaining detection for non-ignored cases. Tests ensure ignore directives work
    across different comment styles and line positions.

Dependencies: pytest for testing framework, pathlib for Path handling, unittest.mock for
    context mocking, src.linters.magic_numbers.linter for MagicNumberRule

Exports: TestInlineIgnoreDirectives (4 tests), TestIgnoreDirectiveFormats (3 tests) -
    total 7 test cases

Interfaces: Tests MagicNumberRule ignore directive handling through check() method

Implementation: Mock-based testing with inline comment patterns, validates selective
    suppression of violations based on ignore directives
"""

from pathlib import Path
from unittest.mock import Mock


class TestInlineIgnoreDirectives:
    """Test inline ignore directive support."""

    def test_ignores_magic_number_with_inline_comment(self):
        """Should ignore magic number with inline thailint ignore comment."""
        code = """
def get_timeout():
    return 3600  # thailint: ignore[magic-numbers]
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should not flag 3600 because of ignore directive
        assert len(violations) == 0, "Should ignore number with inline directive"

    def test_ignores_only_commented_line(self):
        """Should ignore only the line with the comment, not others."""
        code = """
def calculate():
    timeout = 3600  # thailint: ignore[magic-numbers]
    max_retries = 5  # This should still be caught
    return timeout + max_retries
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should flag 5 but not 3600
        assert len(violations) > 0, "Should still flag non-ignored numbers"
        # Verify 3600 is not in violations
        for violation in violations:
            assert "3600" not in str(violation.message), "Should not flag ignored 3600"

    def test_respects_generic_ignore_directive(self):
        """Should respect generic thailint ignore directive."""
        code = """
def get_value():
    return 999  # thailint: ignore
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Generic ignore should work too
        assert len(violations) == 0, "Should respect generic ignore directive"

    def test_multiple_numbers_one_ignored(self):
        """Should handle multiple numbers where only one is ignored."""
        code = """
def complex():
    x = 42  # thailint: ignore[magic-numbers]
    y = 365  # This should be flagged
    z = 7  # This should also be flagged
    return x + y + z
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should flag 365 and 7, but not 42
        assert len(violations) >= 2, "Should flag non-ignored numbers"
        violation_messages = [str(v.message) for v in violations]
        assert not any("42" in msg for msg in violation_messages), "Should not flag ignored 42"


class TestIgnoreDirectiveFormats:
    """Test various ignore directive formats."""

    def test_end_of_line_comment_format(self):
        """Should handle end-of-line comment format."""
        code = """
def timeout():
    return 3600  # thailint: ignore[magic-numbers] - timeout constant
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0, "Should handle comment with explanation"

    def test_ignore_with_multiple_rules(self):
        """Should handle ignore directive with multiple rules."""
        code = """
def process():
    value = 42  # thailint: ignore[magic-numbers,complexity]
    return value
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should respect ignore even with multiple rules listed
        assert len(violations) == 0, "Should handle ignore with multiple rules"

    def test_noqa_style_comment(self):
        """Should handle noqa-style ignore comments for compatibility."""
        code = """
def get_value():
    return 3600  # noqa: magic-numbers
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should support noqa style for compatibility
        assert len(violations) == 0, "Should support noqa-style comments"
