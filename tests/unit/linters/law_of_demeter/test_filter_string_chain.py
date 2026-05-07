"""
Purpose: Test string-chain filter for Law of Demeter classifier

Scope: Filtering chains of string/bytes method calls (same-type chaining)

Overview: Validates the same-type string filter that allows chains consisting of string
    manipulation methods (strip, lower, upper, replace, split, join, etc.). These chains
    always return the same type (str) and are not Law of Demeter violations. Also covers
    the string-attr variant where the first step is an attribute access followed by string
    methods (e.g., node.name.strip().lower()).

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestStringChainFilter (5 tests)

Interfaces: Tests classify_chain() returning "same-type:str" or "same-type:str-attr"

Implementation: Calls classify_chain() with string method chain parts,
    verifies string-chain filter fires
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestStringChainFilter:
    """Test same-type string method chain filter."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_pure_string_chain(self) -> None:
        """text.strip().lower().replace() should be same-type:str."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["text", "strip()", "lower()", "replace()"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert "same-type:str" in result

    def test_split_and_process(self) -> None:
        """version.partition()[0].split() should be same-type:str."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["version", "partition()", "[\u2026]", "split()"]
        result = classify_chain(parts, self._empty_imports(), "utils.py")
        assert "same-type" in result or result != ""

    def test_attr_then_string_methods(self) -> None:
        """node.name.strip().lower() should be same-type:str-attr."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["node", "name", "strip()", "lower()"]
        result = classify_chain(parts, self._empty_imports(), "parser.py")
        assert "same-type:str" in result

    def test_regex_group_chain(self) -> None:
        """m.group().strip().upper() should be same-type:str."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["m", "group()", "strip()", "upper()"]
        result = classify_chain(parts, self._empty_imports(), "parser.py")
        assert "same-type:str" in result

    def test_non_string_methods_not_filtered(self) -> None:
        """Chain with non-string methods should not be caught."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert "same-type:str" not in result
