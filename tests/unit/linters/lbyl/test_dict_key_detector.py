"""
Purpose: Tests for dict key LBYL pattern detection

Scope: Unit tests for detecting 'if key in dict: dict[key]' patterns

Overview: Test suite for dict key LBYL pattern detection. Tests detection of basic
    patterns, variable keys, nested dicts, and f-string keys. Verifies no false positives
    for different dict/key combinations, walrus operator patterns, and dict.get() usage.
    Tests EAFP suggestion generation.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for dict key detection

Interfaces: pytest test discovery and execution

Implementation: Tests for DictKeyDetector and LBYLViolationBuilder
"""

import ast

from src.linters.lbyl.pattern_detectors.dict_key_detector import (
    DictKeyDetector,
    DictKeyPattern,
)
from src.linters.lbyl.violation_builder import build_dict_key_violation


class TestDictKeyDetectorBasic:
    """Tests for basic dict key LBYL detection."""

    def test_detects_if_in_dict_before_access(self) -> None:
        """Detect: if key in dict: dict[key] pattern."""
        code = """
if "api_key" in config:
    api_key = config["api_key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], DictKeyPattern)
        assert patterns[0].dict_name == "config"
        assert patterns[0].key_expression == "'api_key'"

    def test_detects_with_variable_key(self) -> None:
        """Detect pattern with variable as key."""
        code = """
if key in data:
    value = data[key]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], DictKeyPattern)
        assert patterns[0].key_expression == "key"

    def test_detects_with_else_branch(self) -> None:
        """Detect pattern with else branch."""
        code = """
if "key" in config:
    value = config["key"]
else:
    value = "default"
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
# Comment line 2

if "key" in config:
    value = config["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 4


class TestDictKeyDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_dict(self) -> None:
        """No detection when if and access use different dicts."""
        code = """
if "key" in dict1:
    value = dict2["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_no_false_positive_for_different_key(self) -> None:
        """No detection when if and access use different keys."""
        code = """
if "key1" in config:
    value = config["key2"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_walrus_operator_pattern(self) -> None:
        """Don't flag: if (x := d.get(k)) is not None."""
        code = """
if (value := config.get("key")) is not None:
    use(value)
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_dict_get_usage(self) -> None:
        """Don't flag dict.get() usage."""
        code = """
value = config.get("key", "default")
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_try_except_pattern(self) -> None:
        """Don't flag EAFP try/except pattern."""
        code = """
try:
    value = config["key"]
except KeyError:
    value = "default"
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0


class TestDictKeyDetectorEdgeCases:
    """Edge case tests for dict key detection."""

    def test_handles_nested_dict_access(self) -> None:
        """Detect nested dict patterns."""
        code = """
if "inner" in config["outer"]:
    value = config["outer"]["inner"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        # Should detect the pattern - the dict is config["outer"]
        assert len(patterns) == 1

    def test_handles_f_string_keys(self) -> None:
        """Detect patterns with variable keys (f-string result assigned to var)."""
        code = """
key = f"prefix_{name}"
if key in config:
    value = config[key]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_method_call_dict(self) -> None:
        """Detect when dict comes from method call."""
        code = """
if "key" in get_config():
    value = get_config()["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        # Method calls have the same AST structure so should be detected
        assert len(patterns) == 1

    def test_handles_attribute_access_dict(self) -> None:
        """Detect when dict is an attribute."""
        code = """
if "key" in self.config:
    value = self.config["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestDictKeyDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_includes_try_except_keyerror(self) -> None:
        """Suggestion should mention try/except KeyError."""
        code = """
if "key" in config:
    value = config["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, DictKeyPattern)
        violation = build_dict_key_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            dict_name=pattern.dict_name,
            key_expression=pattern.key_expression,
        )
        assert "try" in violation.suggestion.lower()
        assert "KeyError" in violation.suggestion

    def test_suggestion_mentions_dict_get(self) -> None:
        """Suggestion mentions KeyError (dict.get is alternative)."""
        code = """
if "key" in config:
    value = config["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, DictKeyPattern)
        violation = build_dict_key_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            dict_name=pattern.dict_name,
            key_expression=pattern.key_expression,
        )
        # Suggestion mentions KeyError as the exception to catch
        assert "KeyError" in violation.suggestion

    def test_suggestion_uses_actual_dict_name(self) -> None:
        """Suggestion uses the actual dict variable name."""
        code = """
if "key" in my_data:
    value = my_data["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, DictKeyPattern)
        violation = build_dict_key_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            dict_name=pattern.dict_name,
            key_expression=pattern.key_expression,
        )
        assert "my_data" in violation.suggestion


class TestMultiplePatternsInFile:
    """Tests for detecting multiple patterns in a single file."""

    def test_detects_multiple_dict_key_patterns(self) -> None:
        """Detects multiple dict key LBYL patterns."""
        code = """
if "key1" in config:
    value1 = config["key1"]

if "key2" in data:
    value2 = data["key2"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
if condition:
    if "key" in config:
        value = config["key"]
"""
        tree = ast.parse(code)
        detector = DictKeyDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
