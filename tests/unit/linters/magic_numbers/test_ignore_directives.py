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


class TestIgnoreDirectiveFormats:
    """Test various ignore directive formats."""

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
