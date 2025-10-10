"""
Purpose: Test suite for TypeScript Single Responsibility Principle violation detection

Scope: TypeScript/JavaScript class-level SRP analysis using tree-sitter parsing

Overview: Comprehensive tests for TypeScript SRP violation detection covering method count
    violations in TypeScript classes, lines of code violations, responsibility keyword
    detection in class names, interface method count analysis, constructor parameter count
    detection (dependency injection smell), combined violations across multiple heuristics,
    and ES6 class syntax support. Validates heuristic-based approach works equivalently
    for TypeScript as Python implementation.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestTypeScriptMethodCount (5 tests), TestTypeScriptLinesOfCode (5 tests),
    TestTypeScriptKeywords (5 tests), TestTypeScriptSpecific (5 tests) - total 20 tests

Interfaces: Tests SRPRule.check(context) -> list[Violation] with TypeScript code samples

Implementation: Uses inline TypeScript code strings as test fixtures, sets language="typescript",
    verifies cross-language SRP detection consistency
"""

from pathlib import Path
from unittest.mock import Mock


class TestTypeScriptMethodCount:
    """Test SRP violations based on method count in TypeScript classes."""


class TestTypeScriptLinesOfCode:
    """Test SRP violations based on LOC in TypeScript classes."""

    # Validates LOC calculation works for TypeScript

    # May violate on method count

    def test_typescript_class_with_500_loc_violates(self):
        """TypeScript class with 500 LOC should violate."""
        methods = "\n".join([f"    method{i}() {{}}" for i in range(245)])
        code = f"""
class MassiveClass {{
{methods}
}}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with 500 LOC should violate"


class TestTypeScriptKeywords:
    """Test SRP violations based on TypeScript class name keywords."""

    # Should pass keyword check


class TestTypeScriptSpecific:
    """Test TypeScript-specific SRP violation patterns."""

    # Interface with 8 methods should violate

    # Many constructor params indicate coupling/multiple responsibilities

    def test_multiple_typescript_classes_in_file(self):
        """Multiple TypeScript classes analyzed independently."""
        code = """
class FirstClass {
    m1() {}
    m2() {}
}

class SecondManager {
    method1() {}
    method2() {}
    method3() {}
    method4() {}
    method5() {}
    method6() {}
    method7() {}
    method8() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "SecondManager should violate"
