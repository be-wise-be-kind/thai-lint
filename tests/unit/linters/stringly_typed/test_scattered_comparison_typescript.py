"""
Purpose: Tests for scattered string comparison detection in TypeScript

Scope: Unit tests for TypeScript comparison_tracker using tree-sitter

Overview: Comprehensive test suite for detecting scattered string comparisons in TypeScript
    like `if (env === "production")` across multiple files. Tests cover tree-sitter detection
    of strict equality (===), loose equality (==), strict inequality (!==), and loose
    inequality (!=) operators with string literals. Includes tests for exclusion patterns
    like template literals and configurable thresholds.

Dependencies: pytest, TypeScriptComparisonTracker (to be created), StringlyTypedStorage

Exports: Test classes for TypeScript comparison tracking functionality

Interfaces: pytest test functions with fixtures

Implementation: TDD approach - tests written before implementation to define expected behavior
"""

from pathlib import Path

import pytest

from src.linters.stringly_typed.config import StringlyTypedConfig
from src.linters.stringly_typed.storage import StringlyTypedStorage


class TestTypeScriptComparisonTrackerBasic:
    """Tests for basic TypeScript comparison detection."""

    @pytest.fixture
    def tracker(self):
        """Create a TypeScript tracker instance."""
        from src.linters.stringly_typed.typescript.comparison_tracker import (
            TypeScriptComparisonTracker,
        )

        return TypeScriptComparisonTracker()

    def test_detects_strict_equality(self, tracker) -> None:
        """Test detection of strict equality (===) with string."""
        code = """
if (status === "active") {
    process();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "active"
        assert patterns[0].operator == "==="

    def test_detects_loose_equality(self, tracker) -> None:
        """Test detection of loose equality (==) with string."""
        code = """
if (status == "active") {
    process();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "active"
        assert patterns[0].operator == "=="

    def test_detects_strict_inequality(self, tracker) -> None:
        """Test detection of strict inequality (!==) with string."""
        code = """
if (status !== "deleted") {
    show();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "deleted"
        assert patterns[0].operator == "!=="

    def test_detects_loose_inequality(self, tracker) -> None:
        """Test detection of loose inequality (!=) with string."""
        code = """
if (status != "deleted") {
    show();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "deleted"
        assert patterns[0].operator == "!="

    def test_detects_string_on_left_side(self, tracker) -> None:
        """Test detection when string literal is on left side."""
        code = """
if ("active" === status) {
    process();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "status"
        assert patterns[0].compared_value == "active"

    def test_detects_multiple_comparisons(self, tracker) -> None:
        """Test detection of multiple comparisons in code."""
        code = """
if (env === "production") {
    deploy();
}
if (env === "staging") {
    test();
}
if (mode !== "debug") {
    optimize();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 3
        variables = {p.variable_name for p in patterns}
        assert variables == {"env", "mode"}
        values = {p.compared_value for p in patterns}
        assert values == {"production", "staging", "debug"}

    def test_detects_single_quoted_strings(self, tracker) -> None:
        """Test detection with single-quoted strings."""
        code = """
if (mode === 'debug') {
    enableLogging();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].compared_value == "debug"


class TestTypeScriptComparisonTrackerAttributes:
    """Tests for member expression comparisons in TypeScript."""

    @pytest.fixture
    def tracker(self):
        """Create a TypeScript tracker instance."""
        from src.linters.stringly_typed.typescript.comparison_tracker import (
            TypeScriptComparisonTracker,
        )

        return TypeScriptComparisonTracker()

    def test_detects_member_expression(self, tracker) -> None:
        """Test detection of member expression comparison."""
        code = """
if (this.status === "active") {
    process();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "this.status"
        assert patterns[0].compared_value == "active"

    def test_detects_nested_member_expression(self, tracker) -> None:
        """Test detection of nested member expression."""
        code = """
if (user.config.mode === "advanced") {
    enableFeatures();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].variable_name == "user.config.mode"


class TestTypeScriptComparisonTrackerExclusions:
    """Tests for patterns that should be excluded in TypeScript."""

    @pytest.fixture
    def tracker(self):
        """Create a TypeScript tracker instance."""
        from src.linters.stringly_typed.typescript.comparison_tracker import (
            TypeScriptComparisonTracker,
        )

        return TypeScriptComparisonTracker()

    def test_excludes_template_literals(self, tracker) -> None:
        """Test that template literal comparisons are excluded."""
        code = """
if (message === `Hello ${name}`) {
    respond();
}
"""
        patterns = tracker.find_patterns(code)

        # Template literals should be excluded
        assert len(patterns) == 0

    def test_excludes_non_string_comparisons(self, tracker) -> None:
        """Test that non-string comparisons are not detected."""
        code = """
if (count === 5) {
    process();
}
if (flag === true) {
    enable();
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 0

    def test_excludes_typeof_comparisons(self, tracker) -> None:
        """Test that typeof comparisons are excluded."""
        code = """
if (typeof value === "string") {
    processString(value);
}
"""
        patterns = tracker.find_patterns(code)

        # typeof checks are standard JS patterns, not stringly-typed code
        assert len(patterns) == 0


class TestTypeScriptComparisonStorage:
    """Tests for TypeScript comparison storage integration."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    def test_stores_typescript_comparisons(self, storage: StringlyTypedStorage) -> None:
        """Test that TypeScript comparisons can be stored."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparison = StoredComparison(
            file_path=Path("app.ts"),
            line_number=10,
            column=4,
            variable_name="status",
            compared_value="active",
            operator="===",
        )
        storage.add_comparison(comparison)

        all_comparisons = storage.get_all_comparisons()
        assert len(all_comparisons) == 1
        assert all_comparisons[0].operator == "==="


class TestTypeScriptCrossFileDetection:
    """Tests for cross-file TypeScript comparison detection."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    def test_detects_pattern_across_ts_files(self, storage: StringlyTypedStorage) -> None:
        """Test detection of same pattern across TypeScript files."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("service.ts"),
                line_number=10,
                column=4,
                variable_name="env",
                compared_value="production",
                operator="===",
            ),
            StoredComparison(
                file_path=Path("handler.ts"),
                line_number=20,
                column=4,
                variable_name="env",
                compared_value="staging",
                operator="===",
            ),
        ]
        storage.add_comparisons(comparisons)

        variables = storage.get_variables_with_multiple_values(min_values=2)
        assert len(variables) == 1
        var_name, unique_values = variables[0]
        assert var_name == "env"
        assert unique_values == {"production", "staging"}

    def test_handles_mixed_operators(self, storage: StringlyTypedStorage) -> None:
        """Test that mixed operators are still aggregated by variable."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("file1.ts"),
                line_number=10,
                column=4,
                variable_name="status",
                compared_value="active",
                operator="===",
            ),
            StoredComparison(
                file_path=Path("file2.ts"),
                line_number=20,
                column=4,
                variable_name="status",
                compared_value="inactive",
                operator="!==",  # Different operator
            ),
        ]
        storage.add_comparisons(comparisons)

        # Should still aggregate by variable name
        variables = storage.get_variables_with_multiple_values(min_values=2)
        assert len(variables) == 1


class TestTypeScriptViolationGeneration:
    """Tests for violation generation from TypeScript comparison patterns."""

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

    def test_generates_violation_for_typescript_comparisons(
        self,
        storage: StringlyTypedStorage,
        generator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test violation generation for TypeScript comparisons."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("service.ts"),
                line_number=10,
                column=4,
                variable_name="env",
                compared_value="production",
                operator="===",
            ),
            StoredComparison(
                file_path=Path("handler.ts"),
                line_number=20,
                column=4,
                variable_name="env",
                compared_value="staging",
                operator="===",
            ),
        ]
        storage.add_comparisons(comparisons)

        violations = generator.generate_violations(
            storage, "stringly-typed.scattered-comparison", config
        )

        # Should have violations for the scattered comparisons
        comparison_violations = [
            v for v in violations if "env" in v.message.lower() or "comparison" in v.message.lower()
        ]
        assert len(comparison_violations) >= 1

    def test_violation_includes_typescript_file_refs(
        self,
        storage: StringlyTypedStorage,
        generator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test that violation includes TypeScript file references."""
        from src.linters.stringly_typed.storage import StoredComparison

        comparisons = [
            StoredComparison(
                file_path=Path("api/routes.ts"),
                line_number=10,
                column=4,
                variable_name="status",
                compared_value="active",
                operator="===",
            ),
            StoredComparison(
                file_path=Path("api/handlers.ts"),
                line_number=20,
                column=4,
                variable_name="status",
                compared_value="pending",
                operator="===",
            ),
        ]
        storage.add_comparisons(comparisons)

        violations = generator.generate_violations(
            storage, "stringly-typed.scattered-comparison", config
        )

        # Should have violations with file references
        assert len(violations) == 2
        all_messages = " ".join(v.message for v in violations)
        assert "routes.ts" in all_messages or "handlers.ts" in all_messages
