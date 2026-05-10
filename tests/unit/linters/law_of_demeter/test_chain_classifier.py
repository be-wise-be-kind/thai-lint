"""
Purpose: Test classify_chain() orchestration across all filters

Scope: End-to-end chain classification with filter pipeline ordering

Overview: Validates the classify_chain() function that orchestrates the 9-filter pipeline.
    Tests verify that the correct filter fires for each category, that filter ordering is
    respected (earlier filters take precedence), and that genuine violations return an
    empty string. Uses a mix of true-positive and false-positive chain patterns.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestClassifyChainOrchestration (8 tests)

Interfaces: Tests classify_chain(parts, imports, filepath) -> str

Implementation: Calls classify_chain() with various chain patterns, verifies
    correct filter identification or empty string for violations
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestClassifyChainOrchestration:
    """Test classify_chain() filter pipeline orchestration."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_violation_returns_empty_string(self) -> None:
        """Genuine violation should return empty string."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result == ""

    def test_safe_prefix_takes_precedence(self) -> None:
        """Safe prefix should be checked before module access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        # self. chains are safe prefix, not module access
        parts = ["self", "os", "path", "join()"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result.startswith("safe-prefix")

    def test_module_access_recognized(self) -> None:
        """Module-rooted chain should be identified."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        imports = FileImports()
        imports.module_names.add("httpx")
        parts = ["httpx", "Client()", "get()", "json()"]
        result = classify_chain(parts, imports, "app.py")
        assert result.startswith("module-access")

    def test_string_chain_recognized(self) -> None:
        """String method chain should be identified."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["text", "strip()", "lower()", "replace()"]
        result = classify_chain(parts, self._empty_imports(), "utils.py")
        assert "same-type:str" in result

    def test_fluent_chain_recognized(self) -> None:
        """Fluent/builder chain should be identified."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["db", "filter()", "order_by()", "limit()"]
        result = classify_chain(parts, self._empty_imports(), "views.py")
        assert result == "fluent-chain"

    def test_dunder_recognized(self) -> None:
        """Dunder access should be identified."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["obj", "__class__", "__name__", "lower()"]
        result = classify_chain(parts, self._empty_imports(), "utils.py")
        assert result == "dunder-access"

    def test_genuine_violation_not_classified(self) -> None:
        """Genuine violation chain is not classified as legitimate."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        # A chain that doesn't match any filter - genuine LoD violation
        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "test_orders.py")
        assert result == ""

    def test_frame_introspection_recognized(self) -> None:
        """Frame/code object introspection chain should be identified."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["frame", "f_back", "f_code", "co_filename"]
        result = classify_chain(parts, self._empty_imports(), "debugger.py")
        assert result == "ast-traversal"

    def test_multiple_filters_first_wins(self) -> None:
        """When multiple filters could match, first in pipeline wins."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        # self. prefix AND ends with items() - safe-prefix should win
        parts = ["self", "data", "store", "items()"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result.startswith("safe-prefix")
