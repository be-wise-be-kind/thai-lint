"""
Purpose: Test AST traversal filter for Law of Demeter classifier

Scope: Filtering chains that navigate AST/compiler node attributes

Overview: Validates the AST traversal filter that allows chains consisting primarily of
    AST node attribute names (func, value, attr, args, body, targets, etc.). These chains
    navigate data structures (like compiler ASTs) rather than violating encapsulation.
    The filter fires when >= 60% of intermediate parts are known AST node attributes.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestAstTraversalFilter (4 tests)

Interfaces: Tests classify_chain() returning "ast-traversal" for AST navigation chains

Implementation: Calls classify_chain() with AST node attribute parts,
    verifies ast-traversal filter fires when threshold met
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestAstTraversalFilter:
    """Test AST/compiler node traversal filter."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_ast_node_chain(self) -> None:
        """node.func.value.attr should be ast-traversal."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["node", "func", "value", "attr"]
        result = classify_chain(parts, self._empty_imports(), "analyzer.py")
        assert result == "ast-traversal"

    def test_ast_target_chain(self) -> None:
        """node.targets[0].value.id should be ast-traversal."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["node", "targets", "[\u2026]", "value", "id"]
        result = classify_chain(parts, self._empty_imports(), "compiler.py")
        assert result == "ast-traversal"

    def test_mypy_node_access(self) -> None:
        """node.callee.node.fullname should be ast-traversal."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["node", "callee", "node", "fullname"]
        result = classify_chain(parts, self._empty_imports(), "type_checker.py")
        assert result == "ast-traversal"

    def test_non_ast_chain_not_filtered(self) -> None:
        """Chain with non-AST attributes should not be caught."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result != "ast-traversal"
