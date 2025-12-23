"""
Purpose: Tests for TypeScript function call tracking in stringly-typed detection

Scope: Unit tests for TypeScriptCallTracker and TypeScriptStringlyTypedAnalyzer

Overview: Comprehensive test suite for TypeScript function call tracking functionality. Tests cover
    tree-sitter detection of function calls with string arguments, method calls, chained method
    calls, and integration with the TypeScript analyzer. Includes tests for simple function calls,
    member expression calls, multiple arguments, and edge cases.

Dependencies: pytest, TypeScriptCallTracker, TypeScriptStringlyTypedAnalyzer,
    tree-sitter-typescript

Exports: Test functions for TypeScript function call tracking

Interfaces: pytest test functions

Implementation: pytest fixtures and parametrized tests for comprehensive coverage
"""

from pathlib import Path

import pytest

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE
from src.linters.stringly_typed.python.analyzer import FunctionCallResult
from src.linters.stringly_typed.typescript.analyzer import TypeScriptStringlyTypedAnalyzer
from src.linters.stringly_typed.typescript.call_tracker import (
    TypeScriptCallTracker,
)

pytestmark = pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not available")


class TestTypeScriptCallTracker:
    """Tests for TypeScriptCallTracker class."""

    @pytest.fixture
    def tracker(self) -> TypeScriptCallTracker:
        """Create a tracker instance."""
        return TypeScriptCallTracker()

    def test_simple_function_call_with_string(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection of simple function call with string argument."""
        code = 'process("active");'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].function_name == "process"
        assert patterns[0].param_index == 0
        assert patterns[0].string_value == "active"

    def test_function_call_with_double_quotes(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection with double quotes."""
        code = 'setMode("debug");'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].string_value == "debug"

    def test_function_call_with_single_quotes(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection with single quotes."""
        code = "setMode('debug');"
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].string_value == "debug"

    def test_method_call_with_string(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection of method call with string argument."""
        code = 'obj.setStatus("pending");'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].function_name == "obj.setStatus"
        assert patterns[0].param_index == 0
        assert patterns[0].string_value == "pending"

    def test_multiple_string_arguments(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection of function with multiple string arguments."""
        code = 'configure("debug", "verbose");'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 2
        assert patterns[0].param_index == 0
        assert patterns[0].string_value == "debug"
        assert patterns[1].param_index == 1
        assert patterns[1].string_value == "verbose"

    def test_mixed_arguments(self, tracker: TypeScriptCallTracker) -> None:
        """Test function with mixed argument types."""
        code = 'process(123, "active", true);'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].param_index == 1
        assert patterns[0].string_value == "active"

    def test_no_string_arguments(self, tracker: TypeScriptCallTracker) -> None:
        """Test function with no string arguments."""
        code = "calculate(1, 2, 3);"
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 0

    def test_nested_method_call(self, tracker: TypeScriptCallTracker) -> None:
        """Test nested method call detection."""
        code = 'a.b.c.process("value");'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].function_name == "a.b.c.process"

    def test_call_result_method(self, tracker: TypeScriptCallTracker) -> None:
        """Test method call on function result."""
        code = 'getClient().send("message");'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        # Uses placeholder for call result
        assert "send" in patterns[0].function_name

    def test_multiple_calls_in_code(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection of multiple function calls in code."""
        code = """
process("active");
handler.setMode("debug");
validate("input");
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 3
        function_names = {p.function_name for p in patterns}
        assert "process" in function_names
        assert "handler.setMode" in function_names
        assert "validate" in function_names

    def test_arrow_function_call(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection in arrow function context."""
        code = """
const handler = (x: string) => {
    process("active");
};
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].string_value == "active"

    def test_async_function_call(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection in async function context."""
        code = """
async function handle() {
    await process("pending");
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].string_value == "pending"

    def test_callback_with_string(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection in callback argument."""
        code = 'items.forEach(item => process("active"));'
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].string_value == "active"

    def test_template_literal_not_detected(self, tracker: TypeScriptCallTracker) -> None:
        """Test that template literals with expressions are not detected as plain strings."""
        code = "process(`value-${x}`);"
        patterns = tracker.find_patterns(code)

        # Template literals with expressions should not be detected as plain strings
        # The pattern detection only looks for "string" nodes, not template_string
        assert len(patterns) == 0

    def test_class_method_call(self, tracker: TypeScriptCallTracker) -> None:
        """Test detection in class method."""
        code = """
class Handler {
    handle() {
        this.process("active");
    }
}
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert "process" in patterns[0].function_name

    def test_line_number_tracking(self, tracker: TypeScriptCallTracker) -> None:
        """Test that line numbers are correctly tracked."""
        code = """
// Comment line 1
// Comment line 2
process("value");
"""
        patterns = tracker.find_patterns(code)

        assert len(patterns) == 1
        assert patterns[0].line_number == 4


class TestTypeScriptStringlyTypedAnalyzer:
    """Tests for TypeScriptStringlyTypedAnalyzer class."""

    @pytest.fixture
    def analyzer(self) -> TypeScriptStringlyTypedAnalyzer:
        """Create analyzer instance."""
        return TypeScriptStringlyTypedAnalyzer()

    def test_analyze_function_calls_basic(self, analyzer: TypeScriptStringlyTypedAnalyzer) -> None:
        """Test basic function call analysis."""
        code = """
process("active");
validate("input");
"""
        results = analyzer.analyze_function_calls(code, Path("test.ts"))

        assert len(results) == 2
        assert all(isinstance(r, FunctionCallResult) for r in results)

    def test_analyze_function_calls_with_file_path(
        self, analyzer: TypeScriptStringlyTypedAnalyzer
    ) -> None:
        """Test that file path is included in results."""
        code = 'process("active");'
        results = analyzer.analyze_function_calls(code, Path("my_module.ts"))

        assert len(results) == 1
        assert results[0].file_path == Path("my_module.ts")

    def test_analyze_function_calls_returns_function_call_result(
        self, analyzer: TypeScriptStringlyTypedAnalyzer
    ) -> None:
        """Test that results are FunctionCallResult instances."""
        code = 'setStatus("active");'
        results = analyzer.analyze_function_calls(code, Path("test.ts"))

        assert len(results) == 1
        result = results[0]
        assert isinstance(result, FunctionCallResult)
        assert result.function_name == "setStatus"
        assert result.param_index == 0
        assert result.string_value == "active"
        assert result.file_path == Path("test.ts")

    def test_analyze_empty_code(self, analyzer: TypeScriptStringlyTypedAnalyzer) -> None:
        """Test analysis of empty code."""
        results = analyzer.analyze_function_calls("", Path("test.ts"))

        assert results == []

    def test_analyze_code_without_function_calls(
        self, analyzer: TypeScriptStringlyTypedAnalyzer
    ) -> None:
        """Test analysis of code without function calls."""
        code = """
const x = 1;
const y = 2;
"""
        results = analyzer.analyze_function_calls(code, Path("test.ts"))

        assert results == []

    def test_analyze_javascript_file(self, analyzer: TypeScriptStringlyTypedAnalyzer) -> None:
        """Test analysis works for JavaScript too."""
        code = 'process("active");'
        results = analyzer.analyze_function_calls(code, Path("test.js"))

        assert len(results) == 1
        assert results[0].string_value == "active"


class TestTypeScriptIntegration:
    """Integration tests for TypeScript call tracking."""

    @pytest.fixture
    def analyzer(self) -> TypeScriptStringlyTypedAnalyzer:
        """Create analyzer instance."""
        return TypeScriptStringlyTypedAnalyzer()

    def test_realistic_react_component(self, analyzer: TypeScriptStringlyTypedAnalyzer) -> None:
        """Test detection in realistic React component."""
        code = """
import React from 'react';

interface ButtonProps {
    variant: string;
}

export function Button({ variant }: ButtonProps) {
    const handleClick = () => {
        analytics.track("button_click");
        setStatus("clicked");
    };

    return <button className={getClass("primary")} />;
}
"""
        results = analyzer.analyze_function_calls(code, Path("Button.tsx"))

        # Should detect the string arguments
        string_values = {r.string_value for r in results}
        assert (
            "button_click" in string_values
            or "clicked" in string_values
            or "primary" in string_values
        )

    def test_api_service_calls(self, analyzer: TypeScriptStringlyTypedAnalyzer) -> None:
        """Test detection in API service pattern."""
        code = """
class ApiService {
    async fetchData() {
        const response = await this.request("GET");
        return response;
    }

    async submitData(data: any) {
        await this.request("POST");
    }

    async deleteItem(id: string) {
        await this.request("DELETE");
    }
}
"""
        results = analyzer.analyze_function_calls(code, Path("api.ts"))

        # Should detect HTTP method strings
        method_values = [r.string_value for r in results if r.function_name.endswith("request")]
        assert set(method_values) == {"GET", "POST", "DELETE"}
