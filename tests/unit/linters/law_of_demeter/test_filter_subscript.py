"""
Purpose: Test subscript-access filter for Law of Demeter classifier

Scope: Filtering chains where most depth comes from subscript (dict/list) access

Overview: Validates the subscript-access filter that allows chains where most of the
    apparent depth comes from subscript operations (dict/list indexing) rather than
    attribute access. Chains like data["config"]["database"]["host"] navigate data
    structures, not object hierarchies, and are not LoD violations.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestSubscriptFilter (4 tests)

Interfaces: Tests classify_chain() returning "subscript-access" for subscript-heavy chains

Implementation: Calls classify_chain() with subscript marker parts,
    verifies subscript-access filter fires when threshold met
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestSubscriptFilter:
    """Test subscript-heavy chain filter."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_dict_navigation(self) -> None:
        """data["config"]["database"]["host"] should be subscript-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["data", "[\u2026]", "[\u2026]", "[\u2026]"]
        result = classify_chain(parts, self._empty_imports(), "config.py")
        assert result == "subscript-access"

    def test_list_then_attr(self) -> None:
        """data[0].field[1] should be subscript-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["data", "[\u2026]", "field", "[\u2026]"]
        result = classify_chain(parts, self._empty_imports(), "parser.py")
        assert result == "subscript-access"

    def test_single_subscript_with_short_chain(self) -> None:
        """response.headers["Content-Type"] with 1 subscript + 1 attr = subscript-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["response", "headers", "[\u2026]"]
        result = classify_chain(parts, self._empty_imports(), "http.py")
        # Short chain, but subscript filter should still recognize the pattern
        assert result == "subscript-access"

    def test_deep_attr_chain_not_filtered(self) -> None:
        """Chain without subscripts should not be caught by this filter."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result != "subscript-access"
