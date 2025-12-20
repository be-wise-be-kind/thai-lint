"""
Purpose: Tests for Python membership validation pattern detection

Scope: Unit tests for detecting 'x in ("a", "b")' and 'x not in (...)' patterns

Overview: Comprehensive test suite for MembershipValidationDetector verifying correct
    detection of membership validation patterns in Python AST. Tests cover various
    collection types (tuple, set, list), operators (in, not in), and edge cases
    like non-string collections, empty collections, and single-element collections.
    Uses TDD approach - tests written before implementation.

Dependencies: pytest, ast module

Exports: Test functions for validation detector

Interfaces: pytest test discovery

Implementation: pytest fixtures with sample code, parametrized tests for coverage
"""

import ast

from src.linters.stringly_typed.python.validation_detector import (
    MembershipPattern,
    MembershipValidationDetector,
)


class TestMembershipValidationDetectorBasic:
    """Tests for basic membership validation pattern detection."""

    def test_detects_in_operator_with_tuple(self) -> None:
        """Detect x in ('a', 'b') pattern with tuple."""
        code = """
def validate(x: str) -> bool:
    if x in ("staging", "production"):
        return True
    return False
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.string_values == {"staging", "production"}
        assert pattern.operator == "in"
        assert pattern.line_number > 0

    def test_detects_not_in_operator_with_set(self) -> None:
        """Detect x not in {'a', 'b'} pattern with set."""
        code = """
def check_env(env: str) -> None:
    if env not in {"dev", "staging", "prod"}:
        raise ValueError("Invalid environment")
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.string_values == {"dev", "staging", "prod"}
        assert pattern.operator == "not in"

    def test_detects_in_operator_with_list(self) -> None:
        """Detect x in ['a', 'b'] pattern with list."""
        code = """
def is_valid_status(status: str) -> bool:
    return status in ["pending", "completed", "failed"]
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"pending", "completed", "failed"}


class TestMembershipValidationDetectorEdgeCases:
    """Tests for edge cases and false positive prevention."""

    def test_ignores_non_string_collections(self) -> None:
        """Ignore membership tests with non-string values."""
        code = """
def check_range(x: int) -> bool:
    return x in (1, 2, 3)
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 0

    def test_ignores_mixed_type_collections(self) -> None:
        """Ignore collections with mixed types (strings and non-strings)."""
        code = """
def mixed_check(x: str) -> bool:
    return x in ("a", 1, "b")
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 0

    def test_ignores_single_element_collections(self) -> None:
        """Ignore single-element collections (not enum candidates)."""
        code = """
def single_check(x: str) -> bool:
    return x in ("only_one",)
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 0

    def test_ignores_empty_collections(self) -> None:
        """Ignore empty collections."""
        code = """
def empty_check(x: str) -> bool:
    return x in ()
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 0

    def test_ignores_variable_membership(self) -> None:
        """Ignore membership tests against variables (not literals)."""
        code = """
VALID_ENVS = ("staging", "production")
def check_env(x: str) -> bool:
    return x in VALID_ENVS
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        # Should not detect because VALID_ENVS is a Name, not a literal collection
        assert len(patterns) == 0


class TestMembershipValidationDetectorComplexCases:
    """Tests for complex patterns and real-world scenarios."""

    def test_detects_method_call_in_collection(self) -> None:
        """Detect pattern with method call on left side."""
        code = """
def check_lower(x: str) -> bool:
    return x.lower() in ("staging", "production")
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].string_values == {"staging", "production"}

    def test_detects_multiple_patterns_in_same_file(self) -> None:
        """Detect multiple membership patterns in same file."""
        code = """
def validate_all(env: str, status: str) -> bool:
    if env not in ("dev", "prod"):
        return False
    if status in {"pending", "completed"}:
        return True
    return False
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 2
        string_sets = {frozenset(p.string_values) for p in patterns}
        assert frozenset({"dev", "prod"}) in string_sets
        assert frozenset({"pending", "completed"}) in string_sets

    def test_captures_variable_name_when_simple(self) -> None:
        """Capture variable name when left side is simple Name node."""
        code = """
def check_status(status: str) -> bool:
    return status in ("pending", "completed")
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"

    def test_captures_attribute_access_as_variable(self) -> None:
        """Capture attribute access (e.g., self.status) as variable name."""
        code = """
class Handler:
    def check(self) -> bool:
        return self.status in ("pending", "completed")
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        # Variable name should capture attribute chain
        assert "status" in patterns[0].variable_name

    def test_returns_none_variable_for_complex_expressions(self) -> None:
        """Return None for variable when expression is complex."""
        code = """
def check(x: str) -> bool:
    return get_value().lower() in ("a", "b")
"""
        tree = ast.parse(code)
        detector = MembershipValidationDetector()
        patterns = detector.find_patterns(tree)

        assert len(patterns) == 1
        # Complex expression shouldn't have a simple variable name
        assert patterns[0].variable_name is None or "get_value" in patterns[0].variable_name


class TestMembershipPatternDataclass:
    """Tests for MembershipPattern dataclass."""

    def test_pattern_has_required_fields(self) -> None:
        """Verify MembershipPattern has all required fields."""
        pattern = MembershipPattern(
            string_values={"a", "b"},
            operator="in",
            line_number=10,
            column=4,
            variable_name="status",
        )

        assert pattern.string_values == {"a", "b"}
        assert pattern.operator == "in"
        assert pattern.line_number == 10
        assert pattern.column == 4
        assert pattern.variable_name == "status"

    def test_pattern_variable_name_optional(self) -> None:
        """Verify variable_name is optional."""
        pattern = MembershipPattern(
            string_values={"a", "b"},
            operator="in",
            line_number=10,
            column=4,
            variable_name=None,
        )

        assert pattern.variable_name is None
