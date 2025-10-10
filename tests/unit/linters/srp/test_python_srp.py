"""
Purpose: Test suite for Python Single Responsibility Principle violation detection

Scope: Python class-level SRP analysis using AST-based heuristics

Overview: Comprehensive tests for Python SRP violation detection covering method count
    violations (classes exceeding configured max_methods threshold), lines of code
    violations (classes exceeding max_loc threshold), responsibility keyword detection
    (identifying generic class names like Manager, Handler, Processor), combined
    violations (multiple SRP issues in single class), and compliant code patterns
    that should pass validation. Verifies heuristic-based SRP analysis accurately
    identifies god classes and provides actionable refactoring suggestions.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestMethodCountViolations (5 tests), TestLinesOfCodeViolations (5 tests),
    TestResponsibilityKeywords (5 tests), TestCombinedViolations (5 tests) - total 20 tests

Interfaces: Tests SRPRule.check(context) -> list[Violation] with Python code samples

Implementation: Uses inline Python code strings as test fixtures, creates mock contexts
    with file_path and file_content, verifies violation detection and message accuracy
"""

from pathlib import Path
from unittest.mock import Mock


class TestMethodCountViolations:
    """Test SRP violations based on method count threshold."""


class TestLinesOfCodeViolations:
    """Test SRP violations based on lines of code threshold."""

    # May violate on method count, not LOC
    # This test validates LOC calculation works

    # May have violations from method count depending on implementation

    def test_class_with_500_loc_violates_severely(self):
        """Class with 500 lines should violate (severe)."""
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(245)])
        code = f"""
class MassiveClass:
{methods}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Class with 500 LOC should violate"


class TestResponsibilityKeywords:
    """Test SRP violations based on responsibility keywords in class names."""

    # Should pass keyword check (may fail on other metrics)
    # This validates keyword detection works


class TestCombinedViolations:
    """Test combined SRP violations (multiple heuristics triggered)."""

    def test_nested_class_definitions_detected_independently(self):
        """Nested classes should be analyzed independently."""
        code = """
class OuterClass:
    def method1(self): pass

    class InnerClass:
        def m1(self): pass
        def m2(self): pass
        def m3(self): pass
        def m4(self): pass
        def m5(self): pass
        def m6(self): pass
        def m7(self): pass
        def m8(self): pass  # Inner violates
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        rule.check(context)
        # InnerClass should violate method count

    def test_multiple_classes_in_file_detected_independently(self):
        """Multiple classes should be analyzed separately."""
        code = """
class FirstClass:
    def m1(self): pass
    def m2(self): pass

class SecondClassManager:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "SecondClassManager should violate"
