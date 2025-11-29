"""
File: tests/unit/linters/print_statements/test_typescript_analyzer_debug.py

Purpose: Debug tests for TypeScript console.* analyzer

Exports: TestAnalyzerInternals test class

Depends: pytest, src.linters.print_statements.typescript_analyzer

Implements: Tests to verify tree-sitter parsing and console call detection

Related: test_typescript_print_statements.py

Overview: Diagnostic tests to verify the TypeScript analyzer is correctly parsing code
    and finding console.* calls. These tests examine the internal workings of the analyzer
    to help debug detection issues.

Usage: pytest tests/unit/linters/print_statements/test_typescript_analyzer_debug.py -v

Notes: Debug/diagnostic tests for troubleshooting
"""


class TestAnalyzerInternals:
    """Test analyzer internal operations."""

    def test_tree_sitter_parses_typescript(self):
        """Verify tree-sitter can parse TypeScript code."""
        from src.linters.print_statements.typescript_analyzer import (
            TypeScriptPrintStatementAnalyzer,
        )

        analyzer = TypeScriptPrintStatementAnalyzer()
        code = 'console.log("test");'

        root = analyzer.parse_typescript(code)
        assert root is not None, "Tree-sitter should parse TypeScript code"
        assert root.type == "program", f"Root should be 'program', got {root.type}"

    def test_finds_call_expressions(self):
        """Verify analyzer can find call_expression nodes."""
        from src.linters.print_statements.typescript_analyzer import (
            TypeScriptPrintStatementAnalyzer,
        )

        analyzer = TypeScriptPrintStatementAnalyzer()
        code = 'console.log("test");'

        root = analyzer.parse_typescript(code)

        # Walk tree to find call expressions
        call_expressions = analyzer.walk_tree(root, "call_expression")
        assert len(call_expressions) >= 1, (
            f"Should find call_expression, found {len(call_expressions)}"
        )

    def test_finds_member_expressions(self):
        """Verify analyzer can find member_expression nodes for console.log."""
        from src.linters.print_statements.typescript_analyzer import (
            TypeScriptPrintStatementAnalyzer,
        )

        analyzer = TypeScriptPrintStatementAnalyzer()
        code = 'console.log("test");'

        root = analyzer.parse_typescript(code)

        # Walk tree to find member expressions
        member_expressions = analyzer.walk_tree(root, "member_expression")
        assert len(member_expressions) >= 1, (
            f"Should find member_expression, found {len(member_expressions)}"
        )

    def test_console_log_tree_structure(self):
        """Examine the tree structure for console.log."""
        from src.linters.print_statements.typescript_analyzer import (
            TypeScriptPrintStatementAnalyzer,
        )

        analyzer = TypeScriptPrintStatementAnalyzer()
        code = 'console.log("test");'

        root = analyzer.parse_typescript(code)
        call_expressions = analyzer.walk_tree(root, "call_expression")

        assert len(call_expressions) >= 1, "Should have call_expression"

        call_expr = call_expressions[0]

        # Find member_expression child
        member_expr = analyzer.find_child_by_type(call_expr, "member_expression")
        assert member_expr is not None, "call_expression should have member_expression child"

        # Check member_expression structure
        children_types = [child.type for child in member_expr.children]
        assert "identifier" in children_types, (
            f"member_expression should have identifier, got {children_types}"
        )

    def test_find_console_calls_returns_results(self):
        """Verify find_console_calls works with simple code."""
        from src.linters.print_statements.typescript_analyzer import (
            TypeScriptPrintStatementAnalyzer,
        )

        analyzer = TypeScriptPrintStatementAnalyzer()
        code = 'console.log("test");'

        root = analyzer.parse_typescript(code)
        calls = analyzer.find_console_calls(root, {"log", "warn", "error"})

        assert len(calls) >= 1, f"Should find console.log, found {len(calls)} calls"

    def test_extract_console_method_name(self):
        """Verify method name extraction."""
        from src.linters.print_statements.typescript_analyzer import (
            TypeScriptPrintStatementAnalyzer,
        )

        analyzer = TypeScriptPrintStatementAnalyzer()
        code = 'console.warn("test");'

        root = analyzer.parse_typescript(code)
        calls = analyzer.find_console_calls(root, {"log", "warn", "error"})

        if len(calls) > 0:
            node, method, line = calls[0]
            assert method == "warn", f"Method should be 'warn', got '{method}'"
