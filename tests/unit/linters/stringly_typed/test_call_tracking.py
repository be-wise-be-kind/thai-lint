"""
Purpose: Tests for function call tracking in stringly-typed detection

Scope: Unit tests for FunctionCallTracker, storage, and violation generation

Overview: Comprehensive test suite for function call tracking functionality. Tests cover
    AST detection of function calls with string arguments, storage of call patterns,
    aggregation of unique values across files, and violation generation for function
    parameters that receive limited sets of string values. Includes tests for simple
    function calls, method calls, cross-file aggregation, and edge cases.

Dependencies: pytest, FunctionCallTracker, StringlyTypedStorage, StoredFunctionCall,
    PythonStringlyTypedAnalyzer

Exports: Test functions for function call tracking

Interfaces: pytest test functions

Implementation: pytest fixtures and parametrized tests for comprehensive coverage
"""

from pathlib import Path

import pytest

from src.linters.stringly_typed.config import StringlyTypedConfig
from src.linters.stringly_typed.python.analyzer import (
    FunctionCallResult,
    PythonStringlyTypedAnalyzer,
)
from src.linters.stringly_typed.python.call_tracker import FunctionCallTracker
from src.linters.stringly_typed.storage import (
    StoredFunctionCall,
    StringlyTypedStorage,
)
from src.linters.stringly_typed.violation_generator import ViolationGenerator


class TestFunctionCallTracker:
    """Tests for FunctionCallTracker class."""

    @pytest.fixture
    def tracker(self) -> FunctionCallTracker:
        """Create a tracker instance."""
        return FunctionCallTracker()

    def test_simple_function_call_with_string(self, tracker: FunctionCallTracker) -> None:
        """Test detection of simple function call with string argument."""
        import ast

        code = 'process("active")'
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].function_name == "process"
        assert patterns[0].param_index == 0
        assert patterns[0].string_value == "active"

    def test_method_call_with_string(self, tracker: FunctionCallTracker) -> None:
        """Test detection of method call with string argument."""
        import ast

        code = 'obj.set_status("pending")'
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].function_name == "obj.set_status"
        assert patterns[0].param_index == 0
        assert patterns[0].string_value == "pending"

    def test_multiple_string_arguments(self, tracker: FunctionCallTracker) -> None:
        """Test detection of function with multiple string arguments."""
        import ast

        code = 'configure("debug", "verbose")'
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 2
        assert patterns[0].param_index == 0
        assert patterns[0].string_value == "debug"
        assert patterns[1].param_index == 1
        assert patterns[1].string_value == "verbose"

    def test_mixed_arguments(self, tracker: FunctionCallTracker) -> None:
        """Test function with mixed argument types."""
        import ast

        code = 'process(123, "active", True)'
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].param_index == 1
        assert patterns[0].string_value == "active"

    def test_no_string_arguments(self, tracker: FunctionCallTracker) -> None:
        """Test function with no string arguments."""
        import ast

        code = "calculate(1, 2, 3)"
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 0

    def test_nested_method_call(self, tracker: FunctionCallTracker) -> None:
        """Test nested method call detection."""
        import ast

        code = 'a.b.c.process("value")'
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        assert patterns[0].function_name == "a.b.c.process"

    def test_call_result_method(self, tracker: FunctionCallTracker) -> None:
        """Test method call on function result."""
        import ast

        code = 'get_client().send("message")'
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 1
        # Uses placeholder for call result
        assert "send" in patterns[0].function_name

    def test_multiple_calls_in_code(self, tracker: FunctionCallTracker) -> None:
        """Test detection of multiple function calls in code."""
        import ast

        code = """
process("active")
handler.set_mode("debug")
validate("input")
"""
        tree = ast.parse(code)
        patterns = tracker.find_patterns(tree)

        assert len(patterns) == 3
        function_names = {p.function_name for p in patterns}
        assert "process" in function_names
        assert "handler.set_mode" in function_names
        assert "validate" in function_names


class TestStorageFunctionCalls:
    """Tests for function call storage functionality."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    def test_add_function_call(self, storage: StringlyTypedStorage) -> None:
        """Test adding a single function call."""
        call = StoredFunctionCall(
            file_path=Path("test.py"),
            line_number=10,
            column=4,
            function_name="process",
            param_index=0,
            string_value="active",
        )
        storage.add_function_call(call)

        all_calls = storage.get_all_function_calls()
        assert len(all_calls) == 1
        assert all_calls[0].function_name == "process"
        assert all_calls[0].string_value == "active"

    def test_add_multiple_function_calls(self, storage: StringlyTypedStorage) -> None:
        """Test adding multiple function calls."""
        calls = [
            StoredFunctionCall(
                file_path=Path("test.py"),
                line_number=10,
                column=4,
                function_name="process",
                param_index=0,
                string_value="active",
            ),
            StoredFunctionCall(
                file_path=Path("test.py"),
                line_number=20,
                column=4,
                function_name="process",
                param_index=0,
                string_value="inactive",
            ),
        ]
        storage.add_function_calls(calls)

        all_calls = storage.get_all_function_calls()
        assert len(all_calls) == 2

    def test_get_limited_value_functions(self, storage: StringlyTypedStorage) -> None:
        """Test finding functions with limited string values."""
        calls = [
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                function_name="process",
                param_index=0,
                string_value="active, ready",  # comma in value (issue #145)
            ),
            StoredFunctionCall(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                function_name="process",
                param_index=0,
                string_value="inactive",
            ),
        ]
        storage.add_function_calls(calls)

        # Should find process with 2 unique values (not 3 - comma shouldn't split)
        limited = storage.get_limited_value_functions(min_values=2, max_values=6, min_files=1)

        assert len(limited) == 1
        func_name, param_idx, values = limited[0]
        assert func_name == "process"
        assert param_idx == 0
        assert values == {"active, ready", "inactive"}

    def test_get_limited_value_functions_respects_thresholds(
        self, storage: StringlyTypedStorage
    ) -> None:
        """Test that thresholds are respected."""
        # Add calls with 7 unique values (above max threshold of 6)
        for i, value in enumerate(["a", "b", "c", "d", "e", "f", "g"]):
            storage.add_function_call(
                StoredFunctionCall(
                    file_path=Path(f"file{i}.py"),
                    line_number=10,
                    column=4,
                    function_name="too_many",
                    param_index=0,
                    string_value=value,
                )
            )

        limited = storage.get_limited_value_functions(min_values=2, max_values=6, min_files=1)

        # Should not include too_many because it has 7 unique values
        assert len(limited) == 0

    def test_get_calls_by_function(self, storage: StringlyTypedStorage) -> None:
        """Test retrieving calls for a specific function and parameter."""
        calls = [
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                function_name="process",
                param_index=0,
                string_value="active",
            ),
            StoredFunctionCall(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                function_name="process",
                param_index=0,
                string_value="inactive",
            ),
            StoredFunctionCall(
                file_path=Path("file3.py"),
                line_number=30,
                column=4,
                function_name="other",
                param_index=0,
                string_value="value",
            ),
        ]
        storage.add_function_calls(calls)

        process_calls = storage.get_calls_by_function("process", 0)
        assert len(process_calls) == 2

        other_calls = storage.get_calls_by_function("other", 0)
        assert len(other_calls) == 1

    def test_clear_also_clears_function_calls(self, storage: StringlyTypedStorage) -> None:
        """Test that clear() removes function calls."""
        storage.add_function_call(
            StoredFunctionCall(
                file_path=Path("test.py"),
                line_number=10,
                column=4,
                function_name="process",
                param_index=0,
                string_value="active",
            )
        )

        storage.clear()
        assert len(storage.get_all_function_calls()) == 0


class TestAnalyzerFunctionCalls:
    """Tests for function call analysis in PythonStringlyTypedAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> PythonStringlyTypedAnalyzer:
        """Create analyzer instance."""
        return PythonStringlyTypedAnalyzer()

    def test_analyze_function_calls_basic(self, analyzer: PythonStringlyTypedAnalyzer) -> None:
        """Test basic function call analysis."""
        code = """
process("active")
validate("input")
"""
        results = analyzer.analyze_function_calls(code, Path("test.py"))

        assert len(results) == 2
        assert all(isinstance(r, FunctionCallResult) for r in results)

    def test_analyze_function_calls_with_file_path(
        self, analyzer: PythonStringlyTypedAnalyzer
    ) -> None:
        """Test that file path is included in results."""
        code = 'process("active")'
        results = analyzer.analyze_function_calls(code, Path("my_module.py"))

        assert len(results) == 1
        assert results[0].file_path == Path("my_module.py")

    def test_analyze_function_calls_invalid_syntax(
        self, analyzer: PythonStringlyTypedAnalyzer
    ) -> None:
        """Test handling of invalid Python syntax."""
        code = "process((("  # Invalid syntax
        results = analyzer.analyze_function_calls(code, Path("test.py"))

        assert results == []


class TestViolationGeneratorFunctionCalls:
    """Tests for function call violation generation."""

    @pytest.fixture
    def storage(self) -> StringlyTypedStorage:
        """Create storage instance."""
        return StringlyTypedStorage(storage_mode="memory")

    @pytest.fixture
    def generator(self) -> ViolationGenerator:
        """Create violation generator instance."""
        return ViolationGenerator()

    @pytest.fixture
    def config(self) -> StringlyTypedConfig:
        """Create default config."""
        return StringlyTypedConfig(
            min_values_for_enum=2,
            max_values_for_enum=6,
            min_occurrences=1,
            require_cross_file=False,
        )

    def test_generates_violation_for_limited_values(
        self,
        storage: StringlyTypedStorage,
        generator: ViolationGenerator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test violation generation for function with limited values."""
        calls = [
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                function_name="process",
                param_index=0,
                string_value="active",
            ),
            StoredFunctionCall(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                function_name="process",
                param_index=0,
                string_value="inactive",
            ),
        ]
        storage.add_function_calls(calls)

        violations = generator.generate_violations(
            storage, "stringly-typed.repeated-validation", config
        )

        # Should have 2 violations (one per call site)
        assert len(violations) == 2
        assert all(v.rule_id == "stringly-typed.limited-values" for v in violations)

    def test_no_violation_below_threshold(
        self,
        storage: StringlyTypedStorage,
        generator: ViolationGenerator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test no violation when below min_values threshold."""
        storage.add_function_call(
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                function_name="single_value",
                param_index=0,
                string_value="only_one",
            )
        )

        violations = generator.generate_violations(
            storage, "stringly-typed.repeated-validation", config
        )

        # Should not generate violations for single-value case
        assert len(violations) == 0

    def test_no_violation_above_threshold(
        self,
        storage: StringlyTypedStorage,
        generator: ViolationGenerator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test no violation when above max_values threshold."""
        for i, value in enumerate(["a", "b", "c", "d", "e", "f", "g"]):
            storage.add_function_call(
                StoredFunctionCall(
                    file_path=Path(f"file{i}.py"),
                    line_number=10,
                    column=4,
                    function_name="too_many_values",
                    param_index=0,
                    string_value=value,
                )
            )

        violations = generator.generate_violations(
            storage, "stringly-typed.repeated-validation", config
        )

        # Should not generate violations for too many unique values
        assert len(violations) == 0

    def test_allowed_string_sets_not_flagged(
        self,
        storage: StringlyTypedStorage,
        generator: ViolationGenerator,
    ) -> None:
        """Test that allowed string sets are not flagged."""
        config = StringlyTypedConfig(
            min_values_for_enum=2,
            max_values_for_enum=6,
            min_occurrences=1,
            require_cross_file=False,
            allowed_string_sets=[["active", "inactive"]],
        )

        calls = [
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                function_name="process",
                param_index=0,
                string_value="active",
            ),
            StoredFunctionCall(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                function_name="process",
                param_index=0,
                string_value="inactive",
            ),
        ]
        storage.add_function_calls(calls)

        violations = generator.generate_violations(
            storage, "stringly-typed.repeated-validation", config
        )

        # Should not generate violations for allowed string sets
        assert len(violations) == 0

    def test_violation_message_contains_function_name(
        self,
        storage: StringlyTypedStorage,
        generator: ViolationGenerator,
        config: StringlyTypedConfig,
    ) -> None:
        """Test that violation message includes function name."""
        calls = [
            StoredFunctionCall(
                file_path=Path("file1.py"),
                line_number=10,
                column=4,
                function_name="set_status",
                param_index=0,
                string_value="active",
            ),
            StoredFunctionCall(
                file_path=Path("file2.py"),
                line_number=20,
                column=4,
                function_name="set_status",
                param_index=0,
                string_value="inactive",
            ),
        ]
        storage.add_function_calls(calls)

        violations = generator.generate_violations(
            storage, "stringly-typed.repeated-validation", config
        )

        assert any("set_status" in v.message for v in violations)

    def test_cross_file_requirement(
        self,
        storage: StringlyTypedStorage,
        generator: ViolationGenerator,
    ) -> None:
        """Test require_cross_file config option."""
        config = StringlyTypedConfig(
            min_values_for_enum=2,
            max_values_for_enum=6,
            min_occurrences=2,
            require_cross_file=True,
        )

        # Both calls in same file
        calls = [
            StoredFunctionCall(
                file_path=Path("same_file.py"),
                line_number=10,
                column=4,
                function_name="process",
                param_index=0,
                string_value="active",
            ),
            StoredFunctionCall(
                file_path=Path("same_file.py"),
                line_number=20,
                column=4,
                function_name="process",
                param_index=0,
                string_value="inactive",
            ),
        ]
        storage.add_function_calls(calls)

        violations = generator.generate_violations(
            storage, "stringly-typed.repeated-validation", config
        )

        # Should not flag since require_cross_file=True and both calls in same file
        assert len(violations) == 0
