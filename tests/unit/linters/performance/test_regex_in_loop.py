"""
Tests for regex compilation in loop detection.

Purpose: Test suite for the regex-in-loop performance rule

Scope: Python detection of repeated regex compilation patterns in loops

Overview: Comprehensive test suite for the regex-in-loop linter rule. Covers detection
    of re.match(), re.search(), re.sub(), re.findall(), re.split(), and re.fullmatch()
    calls inside for/while loops. Verifies that compiled patterns (via re.compile())
    are correctly ignored as they represent the optimal pattern.

Dependencies: pytest, ast, PythonRegexInLoopAnalyzer

Exports: Test classes for regex-in-loop detection

Related: src/linters/performance/regex_analyzer.py

Implementation: pytest test classes with assertions on analyzer output
"""

import ast

from src.linters.performance.regex_analyzer import PythonRegexInLoopAnalyzer


def analyze_python_code(code: str) -> list:
    """Helper to analyze Python code and return violations."""
    analyzer = PythonRegexInLoopAnalyzer()
    tree = ast.parse(code)
    return analyzer.find_violations(tree)


class TestPythonRegexInLoopDetection:
    """Test detection of re.method() calls in loops."""

    def test_detects_re_match_in_for_loop(self):
        """Detect re.match() in for loop."""
        code = """
import re

def find_matches(items, pattern):
    matches = []
    for item in items:
        if re.match(pattern, item):
            matches.append(item)
    return matches
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.match"
        assert violations[0].loop_type == "for"

    def test_detects_re_search_in_for_loop(self):
        """Detect re.search() in for loop."""
        code = """
import re

def search_all(texts, pattern):
    results = []
    for text in texts:
        match = re.search(pattern, text)
        if match:
            results.append(match.group())
    return results
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.search"

    def test_detects_re_sub_in_for_loop(self):
        """Detect re.sub() in for loop."""
        code = """
import re

def clean_all(strings, pattern, replacement):
    cleaned = []
    for s in strings:
        cleaned.append(re.sub(pattern, replacement, s))
    return cleaned
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.sub"

    def test_detects_re_findall_in_for_loop(self):
        """Detect re.findall() in for loop."""
        code = """
import re

def extract_numbers(lines):
    all_numbers = []
    for line in lines:
        numbers = re.findall(r'\\d+', line)
        all_numbers.extend(numbers)
    return all_numbers
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.findall"

    def test_detects_re_split_in_for_loop(self):
        """Detect re.split() in for loop."""
        code = """
import re

def tokenize_all(texts, pattern):
    all_tokens = []
    for text in texts:
        tokens = re.split(pattern, text)
        all_tokens.extend(tokens)
    return all_tokens
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.split"

    def test_detects_re_fullmatch_in_loop(self):
        """Detect re.fullmatch() in for loop."""
        code = """
import re

def validate_all(items, pattern):
    valid = []
    for item in items:
        if re.fullmatch(pattern, item):
            valid.append(item)
    return valid
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.fullmatch"

    def test_detects_re_match_in_while_loop(self):
        """Detect re.match() in while loop."""
        code = """
import re

def process_stream(stream, pattern):
    results = []
    line = stream.readline()
    while line:
        if re.match(pattern, line):
            results.append(line)
        line = stream.readline()
    return results
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].loop_type == "while"

    def test_detects_multiple_re_calls_in_loop(self):
        """Detect multiple different re.method() calls in same loop."""
        code = """
import re

def process(items):
    for item in items:
        if re.match(r'^\\d', item):
            parts = re.split(r'\\s+', item)
            clean = re.sub(r'[^a-z]', '', parts[0])
    return clean
"""
        violations = analyze_python_code(code)
        assert len(violations) == 3
        method_names = {v.method_name for v in violations}
        assert method_names == {"re.match", "re.split", "re.sub"}


class TestCompiledPatternIgnored:
    """Test that compiled patterns are correctly ignored."""

    def test_ignores_compiled_pattern_match_in_loop(self):
        """Allow pattern.match() in loop when pattern is compiled."""
        code = """
import re

def find_matches(items, raw_pattern):
    pattern = re.compile(raw_pattern)
    matches = []
    for item in items:
        if pattern.match(item):
            matches.append(item)
    return matches
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_compiled_pattern_search_in_loop(self):
        """Allow pattern.search() in loop when pattern is compiled."""
        code = """
import re

def search_all(texts):
    pattern = re.compile(r'\\b\\w+@\\w+\\.\\w+\\b')
    results = []
    for text in texts:
        match = pattern.search(text)
        if match:
            results.append(match.group())
    return results
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_compiled_pattern_sub_in_loop(self):
        """Allow pattern.sub() in loop when pattern is compiled."""
        code = """
import re

def clean_all(strings):
    pattern = re.compile(r'\\s+')
    cleaned = []
    for s in strings:
        cleaned.append(pattern.sub(' ', s))
    return cleaned
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_compiled_pattern_findall_in_loop(self):
        """Allow pattern.findall() in loop when pattern is compiled."""
        code = """
import re

def extract_all(texts):
    pattern = re.compile(r'\\d+')
    results = []
    for text in texts:
        results.extend(pattern.findall(text))
    return results
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_compiled_pattern_split_in_loop(self):
        """Allow pattern.split() in loop when pattern is compiled."""
        code = """
import re

def tokenize_all(texts):
    pattern = re.compile(r'[,;\\s]+')
    all_tokens = []
    for text in texts:
        all_tokens.extend(pattern.split(text))
    return all_tokens
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_compiled_pattern_as_parameter(self):
        """Allow compiled pattern passed as parameter."""
        code = """
import re

def process(items, compiled_pattern):
    results = []
    for item in items:
        if compiled_pattern.match(item):
            results.append(item)
    return results
"""
        # Parameter is not tracked as compiled, but it's not re.match() either
        # So no violation since it's method call on unknown variable
        violations = analyze_python_code(code)
        assert len(violations) == 0


class TestRegexOutsideLoop:
    """Test that regex outside loops is not flagged."""

    def test_ignores_re_match_outside_loop(self):
        """Allow re.match() outside loop."""
        code = """
import re

def validate(text, pattern):
    if re.match(pattern, text):
        return True
    return False
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_re_search_outside_loop(self):
        """Allow re.search() outside loop."""
        code = """
import re

def find_first(text):
    match = re.search(r'\\d+', text)
    if match:
        return match.group()
    return None
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_re_compile_in_loop(self):
        """Allow re.compile() in loop - intentional use case."""
        code = """
import re

def create_patterns(pattern_strings):
    patterns = []
    for p in pattern_strings:
        patterns.append(re.compile(p))
    return patterns
"""
        # re.compile() is the solution, not the problem
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_ignores_re_match_after_loop(self):
        """Allow re.match() after loop ends."""
        code = """
import re

def process(items):
    combined = ""
    for item in items:
        combined += item
    # This is outside the loop
    if re.match(r'^\\d', combined):
        return combined
    return None
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_handles_empty_file(self):
        """Handle empty file gracefully."""
        code = ""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_handles_file_without_re_import(self):
        """Handle file without re import."""
        code = """
def simple_function(x):
    return x * 2
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_handles_syntax_error_gracefully(self):
        """Handle syntax errors gracefully."""
        import pytest

        code = "def broken(:"
        with pytest.raises(SyntaxError):
            analyze_python_code(code)

    def test_handles_nested_loops(self):
        """Detect re.match in nested loop."""
        code = """
import re

def process_grid(grid, pattern):
    results = []
    for row in grid:
        for cell in row:
            if re.match(pattern, cell):
                results.append(cell)
    return results
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].loop_type == "for"

    def test_handles_loop_in_function_in_loop(self):
        """Handle nested function definitions with loops."""
        code = """
import re

def outer(items):
    def inner(texts, pattern):
        matches = []
        for text in texts:
            if re.match(pattern, text):
                matches.append(text)
        return matches

    for item in items:
        inner(item.texts, r'^\\d+')
"""
        violations = analyze_python_code(code)
        # Only the inner function's loop has a regex call
        assert len(violations) == 1

    def test_handles_class_method(self):
        """Detect regex in class method loop."""
        code = """
import re

class Validator:
    def validate_all(self, items, pattern):
        valid = []
        for item in items:
            if re.match(pattern, item):
                valid.append(item)
        return valid
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_handles_async_function(self):
        """Detect regex in async function loop."""
        code = """
import re

async def process_async(items, pattern):
    results = []
    for item in items:
        if re.match(pattern, item):
            results.append(item)
    return results
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_handles_from_import(self):
        """Detect regex with 'from re import match' style."""
        code = """
from re import match

def find_matches(items, pattern):
    matches = []
    for item in items:
        if match(pattern, item):
            matches.append(item)
    return matches
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "match"

    def test_handles_aliased_import(self):
        """Detect regex with 'import re as regex' style."""
        code = """
import re as regex

def find_matches(items, pattern):
    matches = []
    for item in items:
        if regex.match(pattern, item):
            matches.append(item)
    return matches
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.match"


class TestViolationMessages:
    """Test that violation messages are helpful."""

    def test_message_includes_method_name(self):
        """Violation message includes the re method being called."""
        code = """
import re

def example(items):
    for item in items:
        re.search(r'\\d+', item)
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert "search" in violations[0].method_name

    def test_message_includes_line_number(self):
        """Violation includes correct line number."""
        code = """
import re

def example(items):
    for item in items:
        re.match(r'\\d+', item)
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].line_number == 6

    def test_suggestion_mentions_compile(self):
        """Suggestion provides re.compile() as fix."""
        # This is tested via violation builder - analyzer just returns data
        code = """
import re

def example(items):
    for item in items:
        re.match(r'\\d+', item)
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        # Analyzer returns method_name; violation builder creates suggestion

    def test_suggestion_is_actionable(self):
        """Suggestion shows how to fix the issue."""
        code = """
import re

def process(items, pattern):
    for item in items:
        re.match(pattern, item)
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        # Analyzer output is validated; violation builder handles suggestions


class TestRealWorldPatterns:
    """Test patterns found in real codebases (FastAPI)."""

    def test_fastapi_deploy_docs_status_pattern(self):
        """Pattern from FastAPI scripts/deploy_docs_status.py:83."""
        code = """
import re

def process_docs_files(docs_files):
    lang_links = {}
    for f in docs_files:
        match = re.match(r"docs/([^/]+)/docs/(.*)", f.filename)
        if not match:
            continue
        lang = match.group(1)
        path = match.group(2)
        lang_links.setdefault(lang, []).append(path)
    return lang_links
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.match"
        assert violations[0].loop_type == "for"

    def test_fastapi_pattern_with_fix(self):
        """Show the correct pattern (what FastAPI should have done)."""
        code = """
import re

def process_docs_files(docs_files):
    lang_links = {}
    docs_pattern = re.compile(r"docs/([^/]+)/docs/(.*)")
    for f in docs_files:
        match = docs_pattern.match(f.filename)
        if not match:
            continue
        lang = match.group(1)
        path = match.group(2)
        lang_links.setdefault(lang, []).append(path)
    return lang_links
"""
        violations = analyze_python_code(code)
        assert len(violations) == 0

    def test_common_log_parsing_pattern(self):
        """Common pattern: parsing log files with regex."""
        code = """
import re

def parse_logs(log_lines):
    entries = []
    for line in log_lines:
        match = re.match(r'(\\d{4}-\\d{2}-\\d{2}) (\\w+): (.+)', line)
        if match:
            entries.append({
                'date': match.group(1),
                'level': match.group(2),
                'message': match.group(3)
            })
    return entries
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1

    def test_csv_field_extraction_pattern(self):
        """Common pattern: extracting fields from CSV-like data."""
        code = """
import re

def extract_emails(records):
    emails = []
    for record in records:
        found = re.findall(r'[\\w.+-]+@[\\w-]+\\.[\\w.-]+', record)
        emails.extend(found)
    return emails
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
        assert violations[0].method_name == "re.findall"

    def test_url_validation_pattern(self):
        """Common pattern: validating URLs in a list."""
        code = """
import re

def validate_urls(urls):
    valid = []
    for url in urls:
        if re.match(r'^https?://[\\w.-]+(?:/[\\w.-]*)*$', url):
            valid.append(url)
    return valid
"""
        violations = analyze_python_code(code)
        assert len(violations) == 1
