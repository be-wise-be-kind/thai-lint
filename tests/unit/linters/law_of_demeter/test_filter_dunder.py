"""
Purpose: Test dunder-access filter for Law of Demeter classifier

Scope: Filtering chains containing dunder (double-underscore) protocol attributes

Overview: Validates the dunder-access filter that allows chains containing Python protocol
    attributes like __class__, __name__, __module__, etc. These access Python's object model
    internals and are framework/protocol patterns, not encapsulation violations.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestDunderFilter (4 tests)

Interfaces: Tests classify_chain() returning "dunder-access" for chains with dunder attrs

Implementation: Calls classify_chain() with dunder attribute parts,
    verifies dunder-access filter fires
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestDunderFilter:
    """Test dunder/protocol access filter."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_class_name_access(self) -> None:
        """obj.__class__.__name__.lower() should be dunder-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["obj", "__class__", "__name__", "lower()"]
        result = classify_chain(parts, self._empty_imports(), "utils.py")
        assert result == "dunder-access"

    def test_module_access(self) -> None:
        """func.__module__.__class__.__name__ should be dunder-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["func", "__module__", "__class__", "__name__"]
        result = classify_chain(parts, self._empty_imports(), "inspect.py")
        assert result == "dunder-access"

    def test_single_dunder_in_chain(self) -> None:
        """Even one dunder in chain should trigger filter."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["obj", "meta", "__class__", "name"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result == "dunder-access"

    def test_no_dunder_not_filtered(self) -> None:
        """Chain without dunder should not be caught by this filter."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result != "dunder-access"
