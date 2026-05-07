"""
Purpose: Test safe-terminal filter for Law of Demeter classifier

Scope: Filtering chains ending with known safe terminal methods

Overview: Validates the safe-terminal filter that allows chains ending with commonly used
    terminal methods like items(), keys(), values(), exists(), encode(), to_dict(), etc.
    These methods are ubiquitous endpoints that provide standard conversions or lookups
    and rarely indicate encapsulation violations even when the chain is deep.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestTerminalFilter (5 tests)

Interfaces: Tests classify_chain() returning "safe-terminal:*" for chains ending with
    known terminal methods

Implementation: Calls classify_chain() with chains ending in safe terminals,
    verifies safe-terminal filter fires
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestTerminalFilter:
    """Test safe-terminal method filter."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_ends_with_items(self) -> None:
        """registry.store.data.items() should be safe-terminal."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["registry", "store", "data", "items()"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result.startswith("safe-terminal")

    def test_ends_with_exists(self) -> None:
        """project.root.config_path.exists() should be safe-terminal."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["project", "root", "config_path", "exists()"]
        result = classify_chain(parts, self._empty_imports(), "setup.py")
        assert result.startswith("safe-terminal")

    def test_ends_with_encode(self) -> None:
        """record.payload.body.encode() should be safe-terminal."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["record", "payload", "body", "encode()"]
        result = classify_chain(parts, self._empty_imports(), "serializer.py")
        assert result.startswith("safe-terminal")

    def test_ends_with_to_dict(self) -> None:
        """model.instance.data.to_dict() should be safe-terminal."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["model", "instance", "data", "to_dict()"]
        result = classify_chain(parts, self._empty_imports(), "api.py")
        assert result.startswith("safe-terminal")

    def test_non_terminal_not_filtered(self) -> None:
        """Chain ending with non-terminal should not be caught."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert not result.startswith("safe-terminal")
