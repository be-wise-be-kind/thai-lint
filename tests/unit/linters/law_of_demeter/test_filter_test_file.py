"""
Purpose: Test test-file filter for Law of Demeter classifier

Scope: Filtering chains in test files (check_test_files=false by default)

Overview: Validates the test-file filter that allows chains in test files when
    check_test_files is false (default). Test code commonly has deep assertion
    chains and mock setup chains that aren't actionable LoD violations.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestTestFileFilter (4 tests)

Interfaces: Tests classify_chain() returning "test-file" for chains in test files

Implementation: Calls classify_chain() with test file paths,
    verifies test-file filter fires based on file path patterns
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestTestFileFilter:
    """Test test-file leniency filter."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_test_prefix_file(self) -> None:
        """Chains in test_*.py files should be filtered."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["client", "get()", "json()", "data"]
        result = classify_chain(parts, self._empty_imports(), "test_api.py")
        assert result == "test-file"

    def test_tests_directory(self) -> None:
        """Chains in tests/ directory should be filtered."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["mocker", "patch()", "return_value", "method"]
        result = classify_chain(parts, self._empty_imports(), "tests/test_service.py")
        assert result == "test-file"

    def test_conftest_file(self) -> None:
        """Chains in conftest.py should be filtered."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["fixture", "setup", "mock", "value"]
        result = classify_chain(parts, self._empty_imports(), "conftest.py")
        assert result == "test-file"

    def test_non_test_file_not_filtered(self) -> None:
        """Chains in regular files should not be caught by test filter."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result != "test-file"
