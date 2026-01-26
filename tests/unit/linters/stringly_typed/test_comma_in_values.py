"""
Purpose: Regression tests for stringly-typed comma handling

Scope: Unit tests for issue #145 fix - string values containing commas

Overview: Tests that the stringly-typed linter correctly handles string values
    that contain commas (like SQL queries), without incorrectly splitting them.
"""

from pathlib import Path

import pytest

from src.linters.stringly_typed.storage import (
    StoredComparison,
    StoredFunctionCall,
    StringlyTypedStorage,
)


class TestCommaInStringValues:
    """Test proper handling of commas in string values (issue #145)."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create a fresh in-memory storage for each test."""
        return StringlyTypedStorage(storage_mode="memory")

    def test_function_call_with_comma_in_value(self, storage: StringlyTypedStorage) -> None:
        """Test that function call values with commas are not split."""
        # Add function calls with SQL-like values containing commas
        storage.add_function_call(
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=0,
                function_name="db.execute",
                param_index=0,
                string_value="SELECT id, name FROM users",
            )
        )
        storage.add_function_call(
            StoredFunctionCall(
                file_path=Path("file2.py"),
                line_number=20,
                column=0,
                function_name="db.execute",
                param_index=0,
                string_value="SELECT id, email FROM accounts",
            )
        )

        results = storage.get_limited_value_functions(min_values=2, max_values=10, min_files=1)

        # Should find the function with exactly 2 distinct values
        matching = [r for r in results if r[0] == "db.execute"]
        assert len(matching) == 1
        func_name, param_idx, values = matching[0]
        assert len(values) == 2
        assert "SELECT id, name FROM users" in values
        assert "SELECT id, email FROM accounts" in values

    def test_comparison_with_comma_in_value(self, storage: StringlyTypedStorage) -> None:
        """Test that comparison values with commas are not split."""
        # Add comparisons with values containing commas
        storage.add_comparison(
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=0,
                variable_name="query",
                compared_value="INSERT INTO users (id, name) VALUES (?, ?)",
                operator="==",
            )
        )
        storage.add_comparison(
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=0,
                variable_name="query",
                compared_value="UPDATE users SET name=?, email=? WHERE id=?",
                operator="==",
            )
        )

        results = storage.get_variables_with_multiple_values(min_values=2, min_files=1)

        # Should find the variable with exactly 2 distinct values
        matching = [r for r in results if r[0] == "query"]
        assert len(matching) == 1
        var_name, values = matching[0]
        assert len(values) == 2
        assert "INSERT INTO users (id, name) VALUES (?, ?)" in values
        assert "UPDATE users SET name=?, email=? WHERE id=?" in values

    def test_many_commas_does_not_inflate_count(self, storage: StringlyTypedStorage) -> None:
        """Test that values with many commas don't inflate the value count."""
        # This was the original bug: SQL with commas got split, inflating counts
        storage.add_function_call(
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=0,
                function_name="run_query",
                param_index=0,
                string_value="SELECT a, b, c, d, e FROM table",  # 4 commas
            )
        )

        results = storage.get_limited_value_functions(min_values=1, max_values=10, min_files=1)

        # Should find exactly 1 value, not 5 (split by commas)
        matching = [r for r in results if r[0] == "run_query"]
        assert len(matching) == 1
        func_name, param_idx, values = matching[0]
        assert len(values) == 1
        assert "SELECT a, b, c, d, e FROM table" in values
