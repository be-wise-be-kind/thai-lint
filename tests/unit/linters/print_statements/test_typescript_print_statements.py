"""
Purpose: Unit tests for TypeScript and JavaScript console statement detection

Scope: Testing console.* call detection for TypeScript and JavaScript files

Overview: Comprehensive test suite for TypeScript/JavaScript console.* statement detection covering
    basic detection of console.log, console.warn, console.error, console.debug, console.info, method
    filtering based on configuration, ignore directives, and test file handling. Validates that the
    linter correctly identifies console statements that should be replaced with proper logging while
    allowing configuration of which console methods trigger violations.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock, src.linters.print_statements.linter.PrintStatementRule

Exports: TestBasicDetection, TestMethodFiltering, TestIgnoreDirectives test classes

Interfaces: test_detects_console_log, test_filters_console_methods, test_respects_ignore_directives,
    and other test methods validating PrintStatementRule.check(context)

Implementation: Uses Mock objects for context creation, tree-sitter for TypeScript parsing,
    inline TypeScript code strings as test fixtures, validates violation detection
"""

from pathlib import Path
from unittest.mock import Mock


class TestBasicDetection:
    """Test basic console.* statement detection in TypeScript/JavaScript code."""

    def test_detects_console_log(self):
        """Should flag console.log() calls."""
        code = """
function test() {
    console.log("hello");
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "console.log()" in violations[0].message

    def test_detects_console_warn(self):
        """Should flag console.warn() calls."""
        code = """
function test() {
    console.warn("warning message");
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "console.warn()" in violations[0].message

    def test_detects_console_error(self):
        """Should flag console.error() calls."""
        code = """
function test() {
    console.error("error message");
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "console.error()" in violations[0].message

    def test_detects_multiple_console_calls(self):
        """Should flag multiple console.* calls."""
        code = """
function test() {
    console.log("start");
    console.warn("check");
    console.error("fail");
    console.debug("debug");
    console.info("info");
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 5


class TestMethodFiltering:
    """Test console method filtering based on configuration."""

    def test_only_detects_configured_methods(self):
        """Should only flag console methods in console_methods config."""
        code = """
function test() {
    console.log("should flag");
    console.table("should not flag");
    console.dir("should not flag");
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # Default methods are log, warn, error, debug, info
        # table and dir should not be flagged
        assert len(violations) == 1
        assert "console.log()" in violations[0].message

    def test_custom_console_methods_config(self):
        """Should respect custom console_methods configuration."""
        code = """
function test() {
    console.log("flagged");
    console.table("flagged with custom config");
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"
        context.config = {"console_methods": {"log", "table"}}

        violations = rule.check(context)
        assert len(violations) == 2


class TestTestFileHandling:
    """Test handling of test files."""

    def test_ignores_test_files(self):
        """Should not flag console.* in test files."""
        code = """
describe("test suite", () => {
    it("should work", () => {
        console.log("debugging test");
    });
});
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.test.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_spec_files(self):
        """Should not flag console.* in spec files."""
        code = """
describe("spec", () => {
    console.log("test output");
});
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.spec.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0


class TestIgnoreDirectives:
    """Test ignore directive support for TypeScript."""

    def test_ignores_with_thailint_ignore_comment(self):
        """Should respect // thailint: ignore directive."""
        code = """
function test() {
    console.log("flagged");
    console.log("ignored");  // thailint: ignore
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_ignores_with_noqa_comment(self):
        """Should respect // noqa directive."""
        code = """
function test() {
    console.log("flagged");
    console.log("ignored");  // noqa
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 1


class TestViolationDetails:
    """Test that violations contain appropriate details."""

    def test_violation_has_correct_rule_id(self):
        """Should set correct rule_id on violations."""
        code = 'console.log("test");'
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert violations[0].rule_id == "improper-logging.print-statement"

    def test_violation_includes_method_name(self):
        """Should include console method name in message."""
        code = 'console.warn("test");'
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert "console.warn()" in violations[0].message

    def test_violation_has_suggestion(self):
        """Should include helpful suggestion in violation."""
        code = 'console.log("test");'
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert "logging" in violations[0].suggestion.lower()


class TestJavaScriptSupport:
    """Test JavaScript file support."""

    def test_detects_in_javascript_files(self):
        """Should detect console.* in .js files."""
        code = """
function test() {
    console.log("hello from JS");
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("app.js")
        context.file_content = code
        context.language = "javascript"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_in_jsx_files(self):
        """Should detect console.* in .jsx files."""
        code = """
function Component() {
    console.log("rendering");
    return <div>Hello</div>;
}
"""
        from src.linters.print_statements.linter import PrintStatementRule

        rule = PrintStatementRule()
        context = Mock()
        context.file_path = Path("component.jsx")
        context.file_content = code
        context.language = "javascript"

        violations = rule.check(context)
        assert len(violations) == 1
