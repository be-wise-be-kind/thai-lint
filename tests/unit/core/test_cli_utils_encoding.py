"""
Purpose: Test encoding handling in CLI output utilities

Scope: Tests for _sanitize_string and encoding-safe violation output

Overview: Verifies that violations containing surrogate characters (from invalid
    UTF-8 file paths or content) are handled gracefully without crashing during
    text or JSON output formatting.

Dependencies: pytest, src.core.cli_utils, src.core.types

Exports: None (test module)

Interfaces: pytest test functions

Implementation: Creates violations with surrogate characters and verifies output
    functions handle them without UnicodeEncodeError
"""

import pytest

from src.core.cli_utils import _sanitize_string, format_violations
from src.core.types import Severity, Violation


class TestSanitizeString:
    """Tests for _sanitize_string function."""

    def test_normal_string_unchanged(self) -> None:
        """Normal strings pass through unchanged."""
        text = "Normal ASCII text"
        assert _sanitize_string(text) == text

    def test_unicode_string_unchanged(self) -> None:
        """Unicode strings without surrogates pass through unchanged."""
        text = "Unicode: café résumé 日本語"
        assert _sanitize_string(text) == text

    def test_surrogate_replaced_with_replacement_char(self) -> None:
        """Surrogate characters are replaced with replacement character."""
        text = "Has surrogate: \udce2"
        result = _sanitize_string(text)
        assert "\udce2" not in result
        assert "\ufffd" in result  # Unicode replacement character

    def test_multiple_surrogates_all_replaced(self) -> None:
        """Multiple surrogate characters are all replaced."""
        text = "\udc80\udc81\udc82"
        result = _sanitize_string(text)
        assert "\udc80" not in result
        assert "\udc81" not in result
        assert "\udc82" not in result


class TestFormatViolationsEncoding:
    """Tests for encoding handling in format_violations."""

    @pytest.fixture
    def violation_with_surrogate_message(self) -> Violation:
        """Create violation with surrogate in message."""
        return Violation(
            rule_id="test.rule",
            file_path="/test/path.py",
            line=10,
            column=1,
            message="Code has surrogate: \udce2",
            severity=Severity.ERROR,
        )

    @pytest.fixture
    def violation_with_surrogate_path(self) -> Violation:
        """Create violation with surrogate in file path."""
        return Violation(
            rule_id="test.rule",
            file_path="/test/path\udce2.py",
            line=10,
            column=1,
            message="Normal message",
            severity=Severity.ERROR,
        )

    def test_text_output_handles_surrogate_in_message(
        self, violation_with_surrogate_message: Violation, capsys: pytest.CaptureFixture
    ) -> None:
        """Text output handles surrogate in message without crashing."""
        # Should not raise UnicodeEncodeError
        format_violations([violation_with_surrogate_message], "text")
        captured = capsys.readouterr()
        assert "test.rule" in captured.out

    def test_text_output_handles_surrogate_in_path(
        self, violation_with_surrogate_path: Violation, capsys: pytest.CaptureFixture
    ) -> None:
        """Text output handles surrogate in path without crashing."""
        format_violations([violation_with_surrogate_path], "text")
        captured = capsys.readouterr()
        assert "test.rule" in captured.out

    def test_json_output_handles_surrogate_in_message(
        self, violation_with_surrogate_message: Violation, capsys: pytest.CaptureFixture
    ) -> None:
        """JSON output handles surrogate in message without crashing."""
        format_violations([violation_with_surrogate_message], "json")
        captured = capsys.readouterr()
        assert '"rule_id": "test.rule"' in captured.out

    def test_json_output_handles_surrogate_in_path(
        self, violation_with_surrogate_path: Violation, capsys: pytest.CaptureFixture
    ) -> None:
        """JSON output handles surrogate in path without crashing."""
        format_violations([violation_with_surrogate_path], "json")
        captured = capsys.readouterr()
        assert '"rule_id": "test.rule"' in captured.out
