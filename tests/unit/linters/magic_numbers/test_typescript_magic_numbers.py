"""
Purpose: Test suite for TypeScript magic number detection

Scope: TypeScript numeric literal detection and violation reporting

Overview: Comprehensive tests for TypeScript magic number detection covering basic numeric literal
    identification in TypeScript/JavaScript code, TypeScript-specific acceptable contexts (const
    assertions, enum definitions, type definitions), ignore directive support with TypeScript
    comment styles, and various TypeScript patterns (arrow functions, async/await, class methods).
    Validates that the linter correctly distinguishes between magic numbers requiring extraction
    to constants and legitimate numeric literals in acceptable TypeScript contexts. Tests follow
    TDD approach with all tests initially failing before implementation.

Dependencies: pytest for testing framework, pathlib for Path handling, unittest.mock for context
    mocking, src.linters.magic_numbers.linter for MagicNumberRule (TypeScript support)

Exports: TestBasicTypeScriptDetection (5 tests), TestTypeScriptAcceptableContexts (6 tests),
    TestTypeScriptSpecificPatterns (5 tests), TestTypeScriptIgnoreDirectives (3 tests) - total
    19 test cases

Interfaces: Tests MagicNumberRule.check(context) -> list[Violation] with TypeScript code samples

Implementation: Uses Mock objects for context creation, inline TypeScript code strings as test
    fixtures, validates violation detection with descriptive assertions
"""

from pathlib import Path
from unittest.mock import Mock


class TestBasicTypeScriptDetection:
    """Test basic magic number detection in TypeScript code."""

    def test_detects_integer_in_const_variable(self):
        """Should detect integer magic number in const variable."""
        code = """
const timeout = 3600;
function useTimeout() {
    return timeout;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 3600 in const"
        assert "3600" in str(violations[0].message), "Violation should mention the number"

    def test_detects_float_in_calculation(self):
        """Should detect float magic number in calculation."""
        code = """
function calculateArea(radius: number): number {
    return 3.14159 * radius * radius;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 3.14159 (PI)"
        assert "3.14159" in str(violations[0].message), "Violation should mention PI value"

    def test_detects_integer_in_comparison(self):
        """Should detect integer magic number in comparison."""
        code = """
function isValidAge(age: number): boolean {
    return age >= 18;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 18 in comparison"

    def test_detects_multiple_magic_numbers(self):
        """Should detect all magic numbers in a function."""
        code = """
function complexCalculation(x: number): number {
    const result = x * 42 + 365 - 7;
    return result;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) >= 3, "Should detect at least 3 magic numbers (42, 365, 7)"

    def test_detects_magic_number_in_array_access(self):
        """Should detect magic numbers in array access."""
        code = """
function getThirdElement(arr: number[]): number {
    return arr[2];
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 2 in array access"


class TestTypeScriptAcceptableContexts:
    """Test contexts where numbers are acceptable in TypeScript."""

    def test_ignores_constant_definitions(self):
        """Should not flag numbers in UPPERCASE constant definitions."""
        code = """
const TIMEOUT_SECONDS = 3600;
const MAX_RETRIES = 5;
const PI_VALUE = 3.14159;

function useConstants(): number {
    return TIMEOUT_SECONDS;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag constant definitions"

    def test_ignores_enum_values(self):
        """Should not flag numbers in enum definitions."""
        code = """
enum Status {
    ACTIVE = 1,
    INACTIVE = 0,
    PENDING = 2,
    ERROR = 500
}

function checkStatus(status: Status): boolean {
    return status === Status.ACTIVE;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag enum values"

    def test_ignores_allowed_numbers_from_config(self):
        """Should not flag numbers in default allowed_numbers."""
        code = """
function checkValue(x: number): boolean {
    if (x === -1) return false;
    if (x === 0) return true;
    if (x === 100) return true;
    return false;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # -1, 0, 100 are in default allowed_numbers
        assert len(violations) == 0, "Should not flag allowed numbers"

    def test_ignores_numbers_in_test_files(self):
        """Should not flag numbers in test files."""
        code = """
describe('calculation', () => {
    it('should calculate correctly', () => {
        expect(calculate(5)).toBe(42);
        expect(getTimeout()).toBe(3600);
    });
});
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test_my_module.test.ts")  # Test file
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag numbers in test files"

    def test_ignores_numbers_in_spec_files(self):
        """Should not flag numbers in .spec.ts files."""
        code = """
describe('service', () => {
    it('should handle timeout', () => {
        const result = service.timeout(3600);
        expect(result).toBe(true);
    });
});
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("my_service.spec.ts")  # Spec file
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag numbers in spec files"

    def test_detects_magic_numbers_in_readonly_properties(self):
        """Should flag magic numbers in readonly property initialization."""
        code = """
class Config {
    readonly timeout = 5000;
    readonly maxRetries = 3;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("config.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # Should flag 5000 and 3 (not in allowed list, not UPPERCASE constants)
        assert len(violations) >= 1, "Should flag magic numbers in readonly properties"


class TestTypeScriptSpecificPatterns:
    """Test TypeScript-specific code patterns."""

    def test_detects_magic_numbers_in_arrow_functions(self):
        """Should detect magic numbers in arrow functions."""
        code = """
const multiply = (x: number) => x * 42;
const timeout = () => 3600;
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) >= 2, "Should detect magic numbers in arrow functions"

    def test_detects_magic_numbers_in_async_functions(self):
        """Should detect magic numbers in async functions."""
        code = """
async function fetchWithTimeout(url: string): Promise<Response> {
    const timeout = 5000;
    return await fetch(url, { timeout });
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 5000 in async function"

    def test_detects_magic_numbers_in_class_methods(self):
        """Should detect magic numbers in class methods."""
        code = """
class Calculator {
    calculate(x: number): number {
        return x * 3.14159;
    }

    getTimeout(): number {
        return 3600;
    }
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("calculator.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) >= 2, "Should detect magic numbers in class methods"

    def test_detects_magic_numbers_in_ternary_expressions(self):
        """Should detect magic numbers in ternary expressions."""
        code = """
function getStatus(x: number): string {
    return x > 100 ? 'high' : 'low';
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 100 in ternary"

    def test_detects_magic_numbers_in_object_literals(self):
        """Should detect magic numbers in object literals."""
        code = """
const config = {
    timeout: 5000,
    maxRetries: 3,
    port: 8080
};
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("config.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) >= 2, "Should detect magic numbers in object literals"


class TestTypeScriptIgnoreDirectives:
    """Test ignore directives in TypeScript comments."""

    def test_respects_single_line_comment_ignore(self):
        """Should ignore violations with // thailint: ignore directive."""
        code = """
function getTimeout(): number {
    return 3600; // thailint: ignore[magic-numbers]
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0, "Should respect single-line ignore directive"

    def test_respects_noqa_style_ignore(self):
        """Should ignore violations with // noqa style directive."""
        code = """
function calculate(x: number): number {
    return x * 3.14159; // noqa
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0, "Should respect noqa style directive"

    def test_only_ignores_specific_line(self):
        """Ignore directive should only affect the specific line."""
        code = """
function multipleNumbers(): number {
    const a = 42; // thailint: ignore[magic-numbers]
    const b = 365;
    return a + b;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # Should detect 365 but not 42
        assert len(violations) == 1, "Should only ignore the specific line with directive"
        assert "365" in str(violations[0].message), "Should detect 365 without ignore directive"


class TestTypeScriptViolationDetails:
    """Test that violations contain appropriate details for TypeScript."""

    def test_violation_contains_line_number(self):
        """Should include line number in violation."""
        code = """
function getValue(): number {
    return 42;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        assert violations[0].line is not None, "Violation should have line number"

    def test_violation_contains_rule_id(self):
        """Should include magic-numbers rule ID."""
        code = """
function getValue(): number {
    return 999;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        assert "magic-numbers" in violations[0].rule_id, "Should have magic-numbers rule ID"

    def test_violation_contains_helpful_message(self):
        """Should provide helpful message for TypeScript code."""
        code = """
const TIMEOUT = 3600;
function getTimeout(): number {
    return TIMEOUT;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # Should not violate - TIMEOUT is uppercase constant
        assert len(violations) == 0, "Should not flag UPPERCASE constant in TypeScript"


class TestTypeScriptJavaScriptCompatibility:
    """Test JavaScript (.js) file detection with same rules."""

    def test_detects_magic_numbers_in_javascript(self):
        """Should detect magic numbers in .js files."""
        code = """
function getTimeout() {
    return 3600;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.js")
        context.file_content = code
        context.language = "javascript"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic numbers in JavaScript files"

    def test_ignores_constants_in_javascript(self):
        """Should ignore UPPERCASE constants in JavaScript."""
        code = """
const TIMEOUT_SECONDS = 3600;
const MAX_RETRIES = 5;

function useConstants() {
    return TIMEOUT_SECONDS;
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.js")
        context.file_content = code
        context.language = "javascript"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag constants in JavaScript"
