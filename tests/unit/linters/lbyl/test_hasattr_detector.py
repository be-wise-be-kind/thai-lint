"""
Purpose: Tests for hasattr LBYL pattern detection

Scope: Unit tests for detecting 'if hasattr(obj, attr): obj.attr' patterns

Overview: Test suite for hasattr LBYL pattern detection. Tests detection of basic
    patterns where hasattr check is followed by attribute access. Verifies no false
    positives for different object/attribute combinations, getattr usage, and
    try/except AttributeError patterns. Tests EAFP suggestion generation.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for hasattr detection

Interfaces: pytest test discovery and execution

Implementation: Tests for HasattrDetector and LBYLViolationBuilder
"""

import ast

from src.linters.lbyl.pattern_detectors.hasattr_detector import (
    HasattrDetector,
    HasattrPattern,
)
from src.linters.lbyl.violation_builder import build_hasattr_violation


class TestHasattrDetectorBasic:
    """Tests for basic hasattr LBYL detection."""

    def test_detects_if_hasattr_before_access(self) -> None:
        """Detect: if hasattr(obj, 'attr'): obj.attr pattern."""
        code = """
if hasattr(config, 'debug'):
    debug_mode = config.debug
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], HasattrPattern)
        assert patterns[0].object_name == "config"
        assert patterns[0].attribute_name == "debug"

    def test_detects_if_hasattr_before_method_call(self) -> None:
        """Detect: if hasattr(obj, 'method'): obj.method() pattern."""
        code = """
if hasattr(handler, 'process'):
    handler.process()
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], HasattrPattern)
        assert patterns[0].object_name == "handler"
        assert patterns[0].attribute_name == "process"

    def test_detects_with_else_branch(self) -> None:
        """Detect pattern with else branch."""
        code = """
if hasattr(obj, 'value'):
    result = obj.value
else:
    result = default
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
# Comment line 2

if hasattr(obj, 'attr'):
    value = obj.attr
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 4

    def test_detects_double_quoted_attribute(self) -> None:
        """Detect pattern with double-quoted attribute name."""
        code = """
if hasattr(obj, "method"):
    obj.method()
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].attribute_name == "method"


class TestHasattrDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_object(self) -> None:
        """No detection when if and access use different objects."""
        code = """
if hasattr(obj1, 'attr'):
    value = obj2.attr
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_no_false_positive_for_different_attribute(self) -> None:
        """No detection when if and access use different attributes."""
        code = """
if hasattr(obj, 'attr1'):
    value = obj.attr2
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_getattr_with_default(self) -> None:
        """Don't flag getattr() with default (already EAFP-like)."""
        code = """
value = getattr(obj, 'attr', default)
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_try_except_attributeerror(self) -> None:
        """Don't flag EAFP try/except AttributeError pattern."""
        code = """
try:
    value = obj.attr
except AttributeError:
    value = default
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_hasattr_without_body_access(self) -> None:
        """Don't flag hasattr when body doesn't access the attribute."""
        code = """
if hasattr(obj, 'attr'):
    print("has attribute")
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_hasattr_variable_attribute(self) -> None:
        """Don't flag when attribute name is a variable (runtime value)."""
        code = """
attr_name = 'dynamic'
if hasattr(obj, attr_name):
    value = getattr(obj, attr_name)
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        # Variable attribute can't be matched to static access
        assert len(patterns) == 0


class TestHasattrDetectorEdgeCases:
    """Edge case tests for hasattr detection."""

    def test_handles_nested_object(self) -> None:
        """Detect pattern with nested object access."""
        code = """
if hasattr(self.config, 'debug'):
    debug = self.config.debug
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].object_name == "self.config"

    def test_handles_chained_attribute_in_body(self) -> None:
        """Detect pattern where body uses attribute in chain."""
        code = """
if hasattr(obj, 'logger'):
    obj.logger.info("message")
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        # Should detect - obj.logger is accessed
        assert len(patterns) == 1

    def test_handles_assignment_and_usage(self) -> None:
        """Detect when attribute is assigned and then used."""
        code = """
if hasattr(config, 'timeout'):
    timeout = config.timeout
    use(timeout)
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_method_result_object(self) -> None:
        """Detect when object comes from method call."""
        code = """
if hasattr(get_handler(), 'process'):
    get_handler().process()
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        # Method calls have the same AST structure so should be detected
        assert len(patterns) == 1


class TestHasattrDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_includes_try_except_attributeerror(self) -> None:
        """Suggestion should mention try/except AttributeError."""
        code = """
if hasattr(config, 'debug'):
    debug = config.debug
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, HasattrPattern)
        violation = build_hasattr_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            object_name=pattern.object_name,
            attribute_name=pattern.attribute_name,
        )
        assert "try" in violation.suggestion.lower()
        assert "AttributeError" in violation.suggestion

    def test_suggestion_uses_actual_object_name(self) -> None:
        """Suggestion uses the actual object variable name."""
        code = """
if hasattr(my_handler, 'process'):
    my_handler.process()
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, HasattrPattern)
        violation = build_hasattr_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            object_name=pattern.object_name,
            attribute_name=pattern.attribute_name,
        )
        assert "my_handler" in violation.suggestion
        assert "process" in violation.suggestion


class TestMultipleHasattrPatterns:
    """Tests for detecting multiple patterns in a single file."""

    def test_detects_multiple_hasattr_patterns(self) -> None:
        """Detects multiple hasattr LBYL patterns."""
        code = """
if hasattr(obj1, 'attr1'):
    value1 = obj1.attr1

if hasattr(obj2, 'attr2'):
    value2 = obj2.attr2
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
if condition:
    if hasattr(obj, 'attr'):
        value = obj.attr
"""
        tree = ast.parse(code)
        detector = HasattrDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
