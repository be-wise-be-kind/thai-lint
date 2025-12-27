"""
Purpose: Tests for scattered string comparison detection in Python

Scope: Unit tests for Python comparison_tracker and cross-file comparison aggregation

Overview: Comprehensive test suite for detecting scattered string comparisons like
    `if env == "production"` across multiple files. Tests cover AST detection of
    equality and inequality comparisons with string literals, storage of comparison
    patterns, aggregation by variable name, cross-file detection, and violation
    generation. Includes tests for exclusion patterns like `__name__ == "__main__"`,
    dictionary contexts, and configurable thresholds.

Dependencies: pytest, ComparisonTracker (to be created), StringlyTypedStorage,
    ViolationGenerator

Exports: Test classes for comparison tracking functionality

Interfaces: pytest test functions with fixtures

Implementation: TDD approach - tests written before implementation to define expected behavior
"""

import ast
from pathlib import Path

import pytest

from src.linters.stringly_typed.config import StringlyTypedConfig
from src.linters.stringly_typed.storage import StringlyTypedStorage


class TestComparisonTrackerBasic:
    """Tests for basic ComparisonTracker detection functionality."""

    @pytest.fixture
    def tracker(self):
        """Create a tracker instance."""
        from src.linters.stringly_typed.python.comparison_tracker import ComparisonTracker

        return ComparisonTracker()

    def test_detects_equality_with_string(self, tracker) -> None:
        """Test detection of simple equality comparison with string."""
        code = """
if status == "active":
    pass
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "active"
        assert patterns[0].operator == "=="

    def test_detects_inequality_with_string(self, tracker) -> None:
        """Test detection of inequality comparison with string."""
        code = """
if status != "deleted":
    pass
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "deleted"
        assert patterns[0].operator == "!="

    def test_detects_string_on_left_side(self, tracker) -> None:
        """Test detection when string is on left side of comparison."""
        code = """
if "active" == status:
    pass
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "active"

    def test_detects_multiple_comparisons(self, tracker) -> None:
        """Test detection of multiple comparisons in code."""
        code = """
if env == "production":
    deploy()
if env == "staging":
    test()
if mode != "debug":
    optimize()
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 3
        variables = {p.variable_name for p in patterns}
        assert variables == {"env", "mode"}
        values = {p.compared_value for p in patterns}
        assert values == {"production", "staging", "debug"}

    def test_captures_line_number(self, tracker) -> None:
        """Test that line numbers are captured correctly."""
        code = """
if status == "active":
    pass
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].line_number == 2

    def test_captures_column(self, tracker) -> None:
        """Test that column numbers are captured correctly."""
        code = 'if status == "active": pass'
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].column >= 0


class TestComparisonTrackerExclusions:
    """Tests for patterns that should be excluded from detection."""

    @pytest.fixture
    def tracker(self):
        """Create a tracker instance."""
        from src.linters.stringly_typed.python.comparison_tracker import ComparisonTracker

        return ComparisonTracker()

    def test_excludes_name_main_check(self, tracker) -> None:
        """Test that __name__ == "__main__" is excluded."""
        code = """
if __name__ == "__main__":
    main()
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 0

    def test_excludes_type_name_checks(self, tracker) -> None:
        """Test that __class__.__name__ comparisons are excluded."""
        code = """
if obj.__class__.__name__ == "MyClass":
    handle()
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 0

    def test_excludes_non_string_comparisons(self, tracker) -> None:
        """Test that non-string comparisons are not detected."""
        code = """
if count == 5:
    pass
if flag == True:
    pass
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 0


class TestComparisonTrackerAttributes:
    """Tests for attribute access in comparisons."""

    @pytest.fixture
    def tracker(self):
        """Create a tracker instance."""
        from src.linters.stringly_typed.python.comparison_tracker import ComparisonTracker

        return ComparisonTracker()

    def test_detects_attribute_comparison(self, tracker) -> None:
        """Test detection of attribute comparison."""
        code = """
if self.status == "active":
    process()
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "self.status"
        assert patterns[0].compared_value == "active"

    def test_detects_nested_attribute(self, tracker) -> None:
        """Test detection of nested attribute comparison."""
        code = """
if user.config.mode == "advanced":
    enable_features()
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "user.config.mode"


class TestComparisonStorage:
    """Tests for comparison storage functionality."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    def test_add_comparison(self, storage: StringlyTypedStorage) -> None:
        """Test adding a single comparison."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparison = StoredComparison(
            file_path=Path("test.py"),
            line_number=10,
            column=4,
            variable_name="status",
            compared_value="active",
            operator="==",
        )
        storage.add_comparison(comparison)

        all_comparisons = storage.get_all_comparisons()
        assert len(all_comparisons) == 1
        assert all_comparisons[0].variable_name == "status"

    def test_add_multiple_comparisons(self, storage: StringlyTypedStorage) -> None:
        """Test adding multiple comparisons."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="env",
                compared_value="production",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                variable_name="env",
                compared_value="staging",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        all_comparisons = storage.get_all_comparisons()
        assert len(all_comparisons) == 2

    def test_get_variables_with_multiple_values(self, storage: StringlyTypedStorage) -> None:
        """Test finding variables compared to multiple string values."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="env",
                compared_value="production",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                variable_name="env",
                compared_value="staging",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file3.py"),
                line_number=30,
                column=4,
                variable_name="other",
                compared_value="value",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        # Should find 'env' with 2 unique values
        variables = storage.get_variables_with_multiple_values(min_values=2)
        assert len(variables) == 1
        var_name, unique_values = variables[0]
        assert var_name == "env"
        assert unique_values == {"production", "staging"}

    def test_get_comparisons_by_variable(self, storage: StringlyTypedStorage) -> None:
        """Test retrieving comparisons for a specific variable."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="env",
                compared_value="production",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                variable_name="env",
                compared_value="staging",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file3.py"),
                line_number=30,
                column=4,
                variable_name="other",
                compared_value="value",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        env_comparisons = storage.get_comparisons_by_variable("env")
        assert len(env_comparisons) == 2

    def test_respects_min_values_threshold(self, storage: StringlyTypedStorage) -> None:
        """Test that min_values threshold is respected."""
        from src.linters.stringly_typed.storage import StoredComparison

        # Only one unique value for 'status'
        storage.add_comparison(
            StoredComparison(
                file_path=Path("test.py"),
                line_number=10,
                column=4,
                variable_name="status",
                compared_value="active",
                operator="==",
            )
        )

        variables = storage.get_variables_with_multiple_values(min_values=2)
        assert len(variables) == 0  # Should not include status


class TestComparisonCrossFileDetection:
    """Tests for cross-file comparison detection."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    def test_detects_same_variable_across_files(self, storage: StringlyTypedStorage) -> None:
        """Test detection of same variable compared in multiple files."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="env",
                compared_value="production",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                variable_name="env",
                compared_value="staging",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        variables = storage.get_variables_with_multiple_values(min_values=2)
        assert len(variables) == 1

        comparisons_for_var = storage.get_comparisons_by_variable("env")
        files = {str(c.file_path) for c in comparisons_for_var}
        assert files == {"file1.py", "file2.py"}

    def test_same_file_multiple_values_detected(self, storage: StringlyTypedStorage) -> None:
        """Test that multiple values in same file are detected."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("same_file.py"),
                line_number=10,
                column=4,
                variable_name="mode",
                compared_value="debug",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("same_file.py"),
                line_number=20,
                column=4,
                variable_name="mode",
                compared_value="release",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        variables = storage.get_variables_with_multiple_values(min_values=2)
        assert len(variables) == 1
        var_name, unique_values = variables[0]
        assert var_name == "mode"
        assert unique_values == {"debug", "release"}


class TestComparisonViolationGeneration:
    """Tests for violation generation from comparison patterns."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    @pytest.fixture
    def generator(self):
        """Create violation generator instance."""
        from src.linters.stringly_typed.violation_generator import ViolationGenerator

        return ViolationGenerator()

    @pytest.fixture
    def config(self) -> StringlyTypedConfig:
        """Create config with comparison detection enabled."""
        return StringlyTypedConfig(
            min_values_for_enum=2,
            max_values_for_enum=6,
            min_occurrences=1,
            require_cross_file=False,
        )

    def test_generates_violation_for_scattered_comparisons(
        self,
        storage: StringlyTypedStorage,
        generator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test violation generation for scattered comparisons."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="env",
                compared_value="production",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                variable_name="env",
                compared_value="staging",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        violations = generator.generate_violations(
            storage, "stringly-typed.scattered-comparison", config
        )

        # Should have violations for the scattered comparisons
        comparison_violations = [
            v
            for v in violations
            if "scattered" in v.rule_id.lower()
            or "comparison" in v.message.lower()
            or "env" in v.message.lower()
        ]
        assert len(comparison_violations) >= 1

    def test_violation_message_includes_variable_name(
        self,
        storage: StringlyTypedStorage,
        generator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test that violation message includes the variable name."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="environment_type",
                compared_value="production",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                variable_name="environment_type",
                compared_value="staging",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        violations = generator.generate_violations(
            storage, "stringly-typed.scattered-comparison", config
        )

        # At least one violation should mention the variable name
        messages = [v.message for v in violations]
        assert any("environment_type" in msg for msg in messages)

    def test_violation_suggests_enum(
        self,
        storage: StringlyTypedStorage,
        generator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test that violation suggests creating an enum."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="status",
                compared_value="active",
                operator="==",
            ),
            StoredComparison(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                variable_name="status",
                compared_value="inactive",
                operator="==",
            ),
        ]
        storage.add_comparisons(comparisons)

        violations = generator.generate_violations(
            storage, "stringly-typed.scattered-comparison", config
        )

        # Suggestion should mention enum
        suggestions = [v.suggestion for v in violations if v.suggestion]
        assert any("enum" in s.lower() for s in suggestions)

    def test_no_violation_for_single_value(
        self,
        storage: StringlyTypedStorage,
        generator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test no violation when variable is compared to only one value."""
        from src.linters.stringly_typed.storage import StoredComparison

        storage.add_comparison(
            StoredComparison(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                variable_name="single",
                compared_value="only_value",
                operator="==",
            )
        )

        violations = generator.generate_violations(
            storage, "stringly-typed.scattered-comparison", config
        )

        # Should not have violations for single-value comparisons
        single_violations = [v for v in violations if "single" in v.message.lower()]
        assert len(single_violations) == 0

    def test_respects_max_values_threshold(
        self,
        storage: StringlyTypedStorage,
        generator,
    ) -> None:
        """Test that max_values threshold is respected."""
        from src.linters.stringly_typed.storage import StoredComparison

        config = StringlyTypedConfig(
            min_values_for_enum=2,
            max_values_for_enum=4,  # Lower max for test
            min_occurrences=1,
            require_cross_file=False,
        )

        # Add 5 unique values - above max threshold
        for i, value in enumerate(["a", "b", "c", "d", "e"]):
            storage.add_comparison(
                StoredComparison(
                    file_path=Path(f"file{i}.py"),
                    line_number=10,
                    column=4,
                    variable_name="too_many",
                    compared_value=value,
                    operator="==",
                )
            )

        violations = generator.generate_violations(
            storage, "stringly-typed.scattered-comparison", config
        )

        # Should not flag variables with too many unique values
        too_many_violations = [v for v in violations if "too_many" in v.message.lower()]
        assert len(too_many_violations) == 0


class TestComparisonClearOperation:
    """Tests for clearing comparison data."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    def test_clear_removes_comparisons(self, storage: StringlyTypedStorage) -> None:
        """Test that clear() removes all comparisons."""
        from src.linters.stringly_typed.storage import StoredComparison

        storage.add_comparison(
            StoredComparison(
                file_path=Path("test.py"),
                line_number=10,
                column=4,
                variable_name="status",
                compared_value="active",
                operator="==",
            )
        )

        storage.clear()
        assert len(storage.get_all_comparisons()) == 0
