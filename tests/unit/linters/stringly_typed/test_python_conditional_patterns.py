"""
Purpose: Tests for Python equality chain pattern detection

Scope: Unit tests for detecting 'if x == "a" elif x == "b"', or-combined, and match patterns

Overview: Comprehensive test suite for ConditionalPatternDetector verifying correct
    detection of equality chain patterns in Python AST. Tests cover single comparisons,
    elif chains with value aggregation, or-combined comparisons, Python 3.10+ match
    statements, and edge cases like non-string comparisons and mixed patterns.
    Uses TDD approach - tests define expected behavior.

Dependencies: pytest, ast module

Exports: Test functions for conditional detector

Interfaces: pytest test discovery

Implementation: pytest fixtures with sample code, organized test classes by pattern type
"""

import ast

from src.linters.stringly_typed.python.conditional_detector import (
    ConditionalPatternDetector,
    EqualityChainPattern,
)


class TestEqualityChainDetectorBasic:
    """Tests for basic equality chain pattern detection."""

    def test_detects_if_elif_chain_with_two_values(self) -> None:
        """Detect if/elif chain with two string values."""
        code = """
def handle_status(status: str) -> None:
    if status == "success":
        print("Success!")
    elif status == "failure":
        print("Failed!")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.string_values == {"success", "failure"}
        assert pattern.pattern_type == "equality_chain"
        assert pattern.variable_name == "status"

    def test_detects_if_elif_chain_with_three_values(self) -> None:
        """Detect if/elif chain with three string values."""
        code = """
def handle_status(status: str) -> None:
    if status == "success":
        print("Completed successfully")
    elif status == "failure":
        print("Operation failed")
    elif status == "pending":
        print("Still waiting...")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.string_values == {"success", "failure", "pending"}
        assert pattern.variable_name == "status"

    def test_ignores_single_comparison_without_elif(self) -> None:
        """Ignore single string comparison without elif chain."""
        code = """
def check_status(status: str) -> bool:
    if status == "success":
        return True
    return False
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        # Single comparison doesn't form a chain
        assert len(patterns) == 0


class TestOrCombinedPatterns:
    """Tests for or-combined comparison detection."""

    def test_detects_or_combined_comparisons(self) -> None:
        """Detect x == 'a' or x == 'b' pattern."""
        code = """
def is_valid(mode: str) -> bool:
    if mode == "debug" or mode == "release":
        return True
    return False
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"debug", "release"}
        assert patterns[0].variable_name == "mode"

    def test_detects_three_or_combined_comparisons(self) -> None:
        """Detect three or-combined comparisons."""
        code = """
def is_primary_color(color: str) -> bool:
    if color == "red" or color == "blue" or color == "yellow":
        return True
    return False
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"red", "blue", "yellow"}


class TestMatchStatementPatterns:
    """Tests for Python 3.10+ match statement detection."""

    def test_detects_match_statement_with_string_cases(self) -> None:
        """Detect match statement with string literal cases."""
        code = """
def handle_mode(mode: str) -> None:
    match mode:
        case "debug":
            print("Debug mode")
        case "release":
            print("Release mode")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.string_values == {"debug", "release"}
        assert pattern.pattern_type == "match_statement"
        assert pattern.variable_name == "mode"

    def test_detects_match_with_multiple_cases(self) -> None:
        """Detect match statement with multiple string cases."""
        code = """
def handle_status(status: str) -> int:
    match status:
        case "pending":
            return 0
        case "running":
            return 1
        case "completed":
            return 2
        case "failed":
            return 3
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"pending", "running", "completed", "failed"}

    def test_ignores_match_with_wildcard_only(self) -> None:
        """Ignore match statement with only wildcard pattern."""
        code = """
def handle_any(value: str) -> None:
    match value:
        case _:
            print("Catch-all")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 0

    def test_ignores_match_with_single_string_case(self) -> None:
        """Ignore match statement with only one string case."""
        code = """
def handle_special(value: str) -> None:
    match value:
        case "special":
            print("Special case")
        case _:
            print("Other")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        # Single string case doesn't form an enum candidate
        assert len(patterns) == 0


class TestEdgeCases:
    """Tests for edge cases and false positive prevention."""

    def test_ignores_non_string_comparisons(self) -> None:
        """Ignore comparisons with non-string values."""
        code = """
def check_code(code: int) -> None:
    if code == 200:
        print("OK")
    elif code == 404:
        print("Not found")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 0

    def test_ignores_variable_comparisons(self) -> None:
        """Ignore comparisons against variables (not literals)."""
        code = """
SUCCESS = "success"
FAILURE = "failure"
def check(status: str) -> None:
    if status == SUCCESS:
        print("OK")
    elif status == FAILURE:
        print("Failed")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        # Comparisons against variables don't count as string literals
        assert len(patterns) == 0

    def test_captures_attribute_access_as_variable(self) -> None:
        """Capture attribute access (e.g., self.status) as variable name."""
        code = """
class Handler:
    def handle(self) -> None:
        if self.status == "active":
            self.process()
        elif self.status == "inactive":
            self.skip()
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"active", "inactive"}
        assert "status" in patterns[0].variable_name

    def test_detects_multiple_chains_in_same_function(self) -> None:
        """Detect multiple independent if/elif chains."""
        code = """
def validate_all(status: str, mode: str) -> bool:
    if status == "active":
        print("Active")
    elif status == "inactive":
        print("Inactive")

    if mode == "debug":
        return False
    elif mode == "release":
        return True
    return False
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 2
        string_sets = {frozenset(p.string_values) for p in patterns}
        assert frozenset({"active", "inactive"}) in string_sets
        assert frozenset({"debug", "release"}) in string_sets

    def test_ignores_mixed_and_or_conditions(self) -> None:
        """Handle mixed AND/OR conditions correctly."""
        code = """
def complex_check(status: str, active: bool) -> None:
    if status == "ready" and active:
        print("Go!")
    elif status == "waiting":
        print("Wait...")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        # Should detect the chain even with mixed conditions
        assert len(patterns) == 1
        assert patterns[0].string_values == {"ready", "waiting"}

    def test_handles_nested_if_statements(self) -> None:
        """Handle nested if statements correctly (don't double-count)."""
        code = """
def nested_check(outer: str, inner: str) -> None:
    if outer == "first":
        if inner == "a":
            print("1a")
        elif inner == "b":
            print("1b")
    elif outer == "second":
        print("2")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        # Should detect both chains independently
        assert len(patterns) == 2


class TestEqualityChainPatternDataclass:
    """Tests for EqualityChainPattern dataclass."""

    def test_pattern_has_required_fields(self) -> None:
        """Verify EqualityChainPattern has all required fields."""
        pattern = EqualityChainPattern(
            string_values={"a", "b"},
            pattern_type="equality_chain",
            line_number=10,
            column=4,
            variable_name="status",
        )

        assert pattern.string_values == {"a", "b"}
        assert pattern.pattern_type == "equality_chain"
        assert pattern.line_number == 10
        assert pattern.column == 4
        assert pattern.variable_name == "status"

    def test_pattern_variable_name_optional(self) -> None:
        """Verify variable_name is optional."""
        pattern = EqualityChainPattern(
            string_values={"a", "b"},
            pattern_type="match_statement",
            line_number=10,
            column=4,
            variable_name=None,
        )

        assert pattern.variable_name is None


class TestRealWorldScenarios:
    """Tests for real-world code patterns."""

    def test_http_status_handling(self) -> None:
        """Detect stringly-typed HTTP status handling."""
        code = """
def handle_response(status: str) -> None:
    if status == "ok":
        process_success()
    elif status == "error":
        handle_error()
    elif status == "timeout":
        retry()
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"ok", "error", "timeout"}

    def test_environment_switching(self) -> None:
        """Detect stringly-typed environment switching."""
        code = """
def get_config(env: str) -> dict:
    if env == "development":
        return DEV_CONFIG
    elif env == "staging":
        return STAGING_CONFIG
    elif env == "production":
        return PROD_CONFIG
    else:
        raise ValueError(f"Unknown env: {env}")
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"development", "staging", "production"}

    def test_state_machine_pattern(self) -> None:
        """Detect stringly-typed state machine pattern."""
        code = """
def transition(state: str, event: str) -> str:
    match state:
        case "idle":
            if event == "start":
                return "running"
        case "running":
            if event == "pause":
                return "paused"
            elif event == "stop":
                return "idle"
        case "paused":
            if event == "resume":
                return "running"
    return state
"""
        tree = ast.parse(code)
        detector = ConditionalPatternDetector()
        patterns = detector.find_patterns(tree)

        # Should detect match statement pattern
        assert any(p.pattern_type == "match_statement" for p in patterns)
        state_pattern = next(p for p in patterns if p.pattern_type == "match_statement")
        assert state_pattern.string_values == {"idle", "running", "paused"}
