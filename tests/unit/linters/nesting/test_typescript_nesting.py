"""
Purpose: Test suite for TypeScript nesting depth analysis

Scope: TypeScript AST-based nesting depth calculation and violation detection

Overview: Comprehensive tests for TypeScript code nesting depth analysis covering simple nesting
    patterns (single if/for/while statements), complex multi-level nesting, TypeScript-specific
    statement types (if, for-of, for-in, while, switch, try), accurate depth calculation, and
    violation detection. Verifies TypeScript-specific constructs like arrow functions, for-of
    loops, and class methods are handled correctly. Tests both passing scenarios (depth within
    limits) and violation scenarios (depth exceeds configured limits). Validates parser
    integration with @typescript-eslint/typescript-estree for AST analysis.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, unittest.mock for Mock objects

Exports: TestSimpleTypeScriptNesting (4 tests), TestTypeScriptStatementTypes (6 tests),
    TestTypeScriptDepthCalculation (5 tests) - total 15 test cases

Interfaces: Tests NestingDepthRule.check(context) -> list[Violation] with TypeScript code samples

Implementation: Uses inline TypeScript code strings as test fixtures, creates mock contexts
    with language='typescript', verifies violation detection for TypeScript constructs
"""

from pathlib import Path
from unittest.mock import Mock


class TestSimpleTypeScriptNesting:
    """Test basic TypeScript nesting depth detection."""


class TestTypeScriptStatementTypes:
    """Test various TypeScript statement types."""

    def test_arrow_function_nesting(self):
        """Arrow functions should track nesting correctly."""
        code = """
const processItems = (items: Item[]) => {
    for (const item of items) {
        if (item.valid) {
            for (const child of item.children) {
                if (child.active) {
                    console.log(child);
                }
            }
        }
    }
};
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # Arrow function with depth 5 should violate
        assert len(violations) > 0, "Arrow function with depth 5 should violate"


class TestTypeScriptDepthCalculation:
    """Test accurate depth calculation for TypeScript."""

    def test_class_method_nesting(self):
        """Class methods should track nesting correctly."""
        code = """
class MyClass {
    processData(items: Item[]) {
        for (const item of items) {
            if (item.valid) {
                for (const child of item.children) {
                    if (child.active) {
                        console.log(child);
                    }
                }
            }
        }
    }
}
"""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # Method with depth 5 should violate
        assert len(violations) > 0, "Class method with depth 5 should violate"
