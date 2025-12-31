"""
Tests for string concatenation in loop detection.

Purpose: TDD test suite for the string-concat-loop performance rule

Scope: Python and TypeScript detection of O(n²) string building patterns

Overview: Comprehensive test suite defining expected behavior for the string-concat-loop
    linter rule. Tests are written before implementation (TDD). Covers detection of
    string += in for/while loops, ignoring numeric/list operations, edge cases,
    and TypeScript support.

Dependencies: pytest

Exports: Test classes for string concat detection

Related: src/linters/performance/string_concat_analyzer.py (to be implemented)

Implementation: pytest test classes with skip markers until implementation exists
"""

import pytest

# Will be implemented in PR2
# from src.linters.performance import lint as perf_lint
# from src.linters.performance.config import PerformanceConfig


def analyze_python_code(code: str) -> list:
    """
    Analyze Python code for string concat in loop violations.

    This is a placeholder that will call the actual linter once implemented.
    For now, returns empty list so tests can be structured.
    """
    # TODO: Replace with actual implementation in PR2
    # return perf_lint(code, language="python", rules=["string-concat-loop"])
    pytest.skip("Implementation pending - PR2")
    return []


def analyze_typescript_code(code: str) -> list:
    """
    Analyze TypeScript code for string concat in loop violations.

    This is a placeholder that will call the actual linter once implemented.
    """
    # TODO: Replace with actual implementation in PR2
    pytest.skip("Implementation pending - PR2")
    return []


class TestPythonStringConcatDetection:
    """Test detection of string += in Python loops."""

    def test_detects_string_concat_in_for_loop(self):
        """Detect result += in for loop."""
        code = """
def build_message(items):
    result = ""
    for item in items:
        result += str(item)
    return result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert "result" in violations[0].message
        assert "join" in violations[0].suggestion.lower()

    def test_detects_string_concat_in_while_loop(self):
        """Detect string += in while loop."""
        code = """
def read_chunks(stream):
    content = ""
    while chunk := stream.read(1024):
        content += chunk
    return content
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert "content" in violations[0].message

    def test_detects_message_variable_concat(self):
        """Detect message += pattern (common in error building)."""
        code = """
def format_errors(errors):
    message = "Errors found:\\n"
    for err in errors:
        message += f"  {err}\\n"
    return message
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert "message" in violations[0].message

    def test_detects_html_building(self):
        """Detect html += pattern (common in template building)."""
        code = """
def build_html(items):
    html = "<ul>"
    for item in items:
        html += f"<li>{item}</li>"
    html += "</ul>"
    return html
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        # Only the one inside the loop should be flagged

    def test_detects_output_variable_concat(self):
        """Detect output += pattern."""
        code = """
def generate_report(data):
    output = ""
    for row in data:
        output += format_row(row)
    return output
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_detects_multiple_concats_in_loop_as_single_violation(self):
        """Multiple += in same loop = one violation by default."""
        code = """
def format_items(items):
    output = ""
    for item in items:
        output += item.name
        output += ": "
        output += item.value
        output += "\\n"
    return output
"""
        violations = analyze_python_code(code)
        # Default: one violation per loop, not per +=
        assert len(violations) == 1

    def test_detects_nested_loop_concat(self):
        """Detect concat in nested loop (both loops flagged)."""
        code = """
def build_table(rows):
    result = ""
    for row in rows:
        for cell in row:
            result += str(cell)
        result += "\\n"
    return result
"""
        violations = analyze_python_code(code)
        # Inner loop and outer loop both have concat
        assert len(violations) >= 1

    def test_detects_fstring_concat_in_loop(self):
        """Detect f-string concat in loop."""
        code = """
def build_list(items):
    text = ""
    for i, item in enumerate(items):
        text += f"{i}. {item}\\n"
    return text
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_ignores_numeric_addition(self):
        """Do not flag numeric += (counters)."""
        code = """
def count_items(items):
    total = 0
    for item in items:
        total += item.value
    return total
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_counter_variable(self):
        """Do not flag count/counter variables."""
        code = """
def count_valid(items):
    count = 0
    for item in items:
        if item.is_valid():
            count += 1
    return count
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_sum_variable(self):
        """Do not flag sum/total variables."""
        code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_list_extend(self):
        """Do not flag list +=."""
        code = """
def collect_items(groups):
    result = []
    for group in groups:
        result += group.items
    return result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_list_append_equivalent(self):
        """Do not flag list operations."""
        code = """
def gather_all(sources):
    items = []
    for source in sources:
        items += [source.get()]
    return items
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_concat_outside_loop(self):
        """Do not flag string += outside loops."""
        code = """
def build_greeting(name, title):
    greeting = "Hello, "
    greeting += title
    greeting += " "
    greeting += name
    return greeting
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_concat_after_loop(self):
        """Do not flag string += after loop ends."""
        code = """
def process(items):
    result = ""
    for item in items:
        print(item)
    result += "Done"
    return result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_suggests_join_alternative(self):
        """Violation message suggests join() as fix."""
        code = """
def concat_names(names):
    result = ""
    for name in names:
        result += name
    return result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        suggestion = violations[0].suggestion.lower()
        assert "join" in suggestion or "'.join(" in suggestion


class TestTypeScriptStringConcatDetection:
    """Test detection of string += in TypeScript loops."""

    def test_detects_string_concat_in_for_of_loop(self):
        """Detect string += in TypeScript for...of loop."""
        code = """
function buildMessage(items: string[]): string {
    let result = "";
    for (const item of items) {
        result += item;
    }
    return result;
}
"""
        violations = analyze_typescript_code(code)
        assert len(violations) == 1

    def test_detects_string_concat_in_for_loop(self):
        """Detect string += in TypeScript traditional for loop."""
        code = """
function buildIndexed(items: string[]): string {
    let output = "";
    for (let i = 0; i < items.length; i++) {
        output += items[i];
    }
    return output;
}
"""
        violations = analyze_typescript_code(code)
        assert len(violations) == 1

    def test_detects_string_concat_in_while_loop(self):
        """Detect string += in TypeScript while loop."""
        code = """
function readAll(reader: Reader): string {
    let content = "";
    while (reader.hasMore()) {
        content += reader.read();
    }
    return content;
}
"""
        violations = analyze_typescript_code(code)
        assert len(violations) == 1

    def test_detects_template_literal_concat(self):
        """Detect template literal concat in loop."""
        code = """
function buildHtml(items: Item[]): string {
    let html = "";
    for (const item of items) {
        html += `<li>${item.name}</li>`;
    }
    return html;
}
"""
        violations = analyze_typescript_code(code)
        assert len(violations) == 1

    def test_ignores_number_addition(self):
        """Do not flag numeric += in TypeScript."""
        code = """
function sumValues(items: number[]): number {
    let total = 0;
    for (const item of items) {
        total += item;
    }
    return total;
}
"""
        violations = analyze_typescript_code(code)
        assert len(violations) == 0

    def test_ignores_array_push(self):
        """Do not flag array operations."""
        code = """
function collectAll(groups: Item[][]): Item[] {
    const result: Item[] = [];
    for (const group of groups) {
        result.push(...group);
    }
    return result;
}
"""
        violations = analyze_typescript_code(code)
        assert len(violations) == 0

    def test_detects_in_arrow_function(self):
        """Detect concat in arrow function loop."""
        code = """
const buildList = (items: string[]): string => {
    let result = "";
    for (const item of items) {
        result += item + "\\n";
    }
    return result;
};
"""
        violations = analyze_typescript_code(code)
        assert len(violations) == 1


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_handles_empty_file(self):
        """Handle empty file gracefully."""
        code = ""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_handles_file_with_only_comments(self):
        """Handle file with only comments."""
        code = """
# This is a comment
# Another comment
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_handles_syntax_error_gracefully(self):
        """Handle syntax errors gracefully (report error, don't crash)."""
        code = "def broken(:"
        # Should not raise exception
        try:
            analyze_python_code(code)
            # Either returns empty or returns syntax error violation
        except Exception:
            pytest.fail("Should handle syntax errors gracefully")

    def test_handles_nested_functions(self):
        """Detect concat in nested function's loop."""
        code = """
def outer():
    def inner(items):
        result = ""
        for item in items:
            result += item
        return result
    return inner
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_handles_class_method(self):
        """Detect concat in class method loop."""
        code = """
class Builder:
    def build(self, items):
        result = ""
        for item in items:
            result += str(item)
        return result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_handles_static_method(self):
        """Detect concat in static method loop."""
        code = """
class Formatter:
    @staticmethod
    def format(items):
        output = ""
        for item in items:
            output += item.format()
        return output
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_handles_async_function(self):
        """Detect concat in async function loop."""
        code = """
async def fetch_all(urls):
    content = ""
    for url in urls:
        content += await fetch(url)
    return content
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_handles_comprehension_not_flagged(self):
        """List comprehension with join is the solution, not a violation."""
        code = """
def build_message(items):
    return "".join(str(item) for item in items)
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_handles_walrus_operator(self):
        """Handle walrus operator in while loop."""
        code = """
def read_file(f):
    content = ""
    while (line := f.readline()):
        content += line
    return content
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1


class TestViolationMessages:
    """Test that violation messages are helpful."""

    def test_message_includes_variable_name(self):
        """Violation message includes the variable being concatenated."""
        code = """
def example(items):
    my_result = ""
    for item in items:
        my_result += item
    return my_result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert "my_result" in violations[0].message

    def test_message_includes_line_number(self):
        """Violation includes correct line number."""
        code = """
def example(items):
    result = ""
    for item in items:
        result += item
    return result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        # The += is on line 5 (1-indexed)
        assert violations[0].line_number == 5

    def test_suggestion_is_actionable(self):
        """Suggestion provides actionable fix."""
        code = """
def example(items):
    result = ""
    for item in items:
        result += str(item)
    return result
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        suggestion = violations[0].suggestion
        # Should mention join or list comprehension
        assert "join" in suggestion.lower() or "comprehension" in suggestion.lower()


class TestRealWorldPatterns:
    """Test patterns found in real codebases (FastAPI)."""

    def test_fastapi_exceptions_pattern(self):
        """Pattern from FastAPI exceptions.py:197."""
        code = """
def format_errors(errors):
    message = f"{len(errors)} validation error{'s' if len(errors) != 1 else ''}:\\n"
    for err in errors:
        message += f"  {err}\\n"
    return message.rstrip()
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_fastapi_docs_pattern(self):
        """Pattern from FastAPI openapi/docs.py."""
        code = """
def build_swagger_ui(params):
    html = "<script>"
    for key, value in params.items():
        html += f"{key}: {value},\\n"
    html += "</script>"
    return html
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_deploy_status_message_pattern(self):
        """Pattern from FastAPI scripts/deploy_docs_status.py."""
        code = """
def build_status_message(files, deploy_url):
    message = "### Modified Pages\\n\\n"
    for f in files:
        message += f"- [{f.name}]({deploy_url}/{f.path})\\n"
    message += "\\n"
    return message
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
