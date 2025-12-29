"""
Purpose: Tests for violation message formatting

Scope: Unit tests for AI agent guidance and error message content

Overview: TDD test suite for violation message formatting. Tests that error messages include
    proper guidance for AI agents including instructions to add Suppressions section entries,
    explicit human approval requirements, and proper rule ID inclusion. All tests are marked
    as skip pending implementation of violation builder.

Dependencies: pytest, src.linters.lazy_ignores

Exports: Test classes for violation message validation

Interfaces: pytest test discovery and execution

Implementation: TDD tests marked as skip until implementation is complete
"""

import pytest


class TestAgentGuidance:
    """Tests for AI agent guidance in violation messages."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_violation_includes_header_instruction(self) -> None:
        """Error message tells agent to add header entry."""
        # violation = build_unjustified_violation(
        #     file_path="src/routes.py",
        #     line=45,
        #     column=20,
        #     rule_id="PLR0912",
        #     raw_text="# noqa: PLR0912",
        # )
        # assert "Suppressions:" in violation.suggestion
        # assert "PLR0912" in violation.suggestion

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_violation_requires_human_approval(self) -> None:
        """Error message emphasizes human approval requirement."""
        # violation = build_unjustified_violation(
        #     file_path="src/routes.py",
        #     line=45,
        #     column=20,
        #     rule_id="PLR0912",
        #     raw_text="# noqa: PLR0912",
        # )
        # assert "human" in violation.suggestion.lower()
        # assert "approval" in violation.suggestion.lower() or "permission" in violation.suggestion.lower()

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_violation_shows_example_format(self) -> None:
        """Error message shows example Suppressions entry format."""
        # violation = build_unjustified_violation(
        #     file_path="src/routes.py",
        #     line=45,
        #     column=20,
        #     rule_id="PLR0912",
        #     raw_text="# noqa: PLR0912",
        # )
        # Example format should show: PLR0912: [justification]
        # assert "PLR0912:" in violation.suggestion


class TestViolationContent:
    """Tests for violation content and metadata."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_violation_includes_file_path(self) -> None:
        """Violation includes correct file path."""
        # violation = build_unjustified_violation(
        #     file_path="src/routes.py",
        #     line=45,
        #     column=20,
        #     rule_id="PLR0912",
        #     raw_text="# noqa: PLR0912",
        # )
        # assert violation.file_path == "src/routes.py"

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_violation_includes_line_number(self) -> None:
        """Violation includes correct line number."""
        # violation = build_unjustified_violation(
        #     file_path="src/routes.py",
        #     line=45,
        #     column=20,
        #     rule_id="PLR0912",
        #     raw_text="# noqa: PLR0912",
        # )
        # assert violation.line == 45

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_violation_includes_raw_ignore_text(self) -> None:
        """Violation message includes the actual ignore text found."""
        # violation = build_unjustified_violation(
        #     file_path="src/routes.py",
        #     line=45,
        #     column=20,
        #     rule_id="PLR0912",
        #     raw_text="# noqa: PLR0912",
        # )
        # assert "# noqa: PLR0912" in violation.message


class TestRuleIdFormatting:
    """Tests for rule ID formatting in violations."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_rule_id_follows_pattern(self) -> None:
        """Rule ID follows lazy-ignores.* pattern."""
        # violation = build_unjustified_violation(
        #     file_path="test.py",
        #     line=1,
        #     column=0,
        #     rule_id="PLR0912",
        #     raw_text="# noqa: PLR0912",
        # )
        # assert violation.rule_id.startswith("lazy-ignores.")

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_unjustified_rule_id(self) -> None:
        """Unjustified suppression uses correct rule ID."""
        # violation = build_unjustified_violation(...)
        # assert violation.rule_id == "lazy-ignores.unjustified"

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_orphaned_rule_id(self) -> None:
        """Orphaned suppression uses correct rule ID."""
        # violation = build_orphaned_violation(...)
        # assert violation.rule_id == "lazy-ignores.orphaned"


class TestMultiRuleViolations:
    """Tests for violations involving multiple rules."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_multiple_rules_in_message(self) -> None:
        """Message includes all rules when multiple are suppressed."""
        # violation = build_unjustified_violation(
        #     file_path="test.py",
        #     line=1,
        #     column=0,
        #     rule_id="PLR0912, PLR0915",
        #     raw_text="# noqa: PLR0912, PLR0915",
        # )
        # assert "PLR0912" in violation.message
        # assert "PLR0915" in violation.message

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_suggestion_for_each_rule(self) -> None:
        """Suggestion includes entry format for each rule."""
        # violation = build_unjustified_violation(
        #     file_path="test.py",
        #     line=1,
        #     column=0,
        #     rule_id="PLR0912, PLR0915",
        #     raw_text="# noqa: PLR0912, PLR0915",
        # )
        # assert "PLR0912:" in violation.suggestion
        # assert "PLR0915:" in violation.suggestion


class TestThailintIgnoreViolations:
    """Tests for thai-lint ignore specific violation messages."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_thailint_ignore_message(self) -> None:
        """Violation message for thailint ignore directive."""
        # violation = build_unjustified_violation(
        #     file_path="test.py",
        #     line=1,
        #     column=0,
        #     rule_id="magic-numbers",
        #     raw_text="# thailint: ignore[magic-numbers]",
        # )
        # assert "magic-numbers" in violation.message

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_thailint_ignore_file_message(self) -> None:
        """Violation message for thailint ignore-file directive."""
        # violation = build_unjustified_violation(
        #     file_path="test.py",
        #     line=1,
        #     column=0,
        #     rule_id="magic-numbers",
        #     raw_text="# thailint: ignore-file[magic-numbers]",
        # )
        # assert "ignore-file" in violation.message or "file-level" in violation.message.lower()
