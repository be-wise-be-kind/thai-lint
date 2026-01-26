"""
Purpose: Test suite for elif chain depth calculation fix

Scope: Verify that if/elif/elif chains are correctly counted as depth 1, not depth 3

Overview: Tests the fix for a false positive where if/elif/elif chains were incorrectly
    counted as nested depth. An elif is syntactically an If node in the parent's orelse
    list, but semantically it's at the same nesting level. These tests verify that:
    1. Simple if/elif/elif/else chains = depth 1
    2. Nested if inside elif = correctly increases depth
    3. Long elif chains (like legacy_windows_render with 14 branches) = depth 1
    4. Mixed elif and nested structures are calculated correctly

Dependencies: pytest, src.linters.nesting.python_analyzer.PythonNestingAnalyzer

Exports: TestElifDepthCalculation class with test cases for elif handling

Interfaces: Tests PythonNestingAnalyzer.calculate_max_depth(func_node) -> tuple[int, int]

Implementation: Uses ast.parse to create function nodes, then verifies depth calculation
"""

import ast

from src.linters.nesting.python_analyzer import PythonNestingAnalyzer


class TestElifDepthCalculation:
    """Test that elif chains are counted correctly (not as nested depth)."""

    def test_simple_if_elif_else_is_depth_one(self) -> None:
        """Simple if/elif/else chain should be depth 1, not depth 2."""
        code = """
def check_value(x):
    if x > 10:
        return "big"
    elif x > 5:
        return "medium"
    else:
        return "small"
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 1, f"if/elif/else should be depth 1, got {depth}"

    def test_multiple_elif_is_depth_one(self) -> None:
        """if/elif/elif/elif/else chain should still be depth 1."""
        code = """
def classify(value):
    if value == 1:
        return "one"
    elif value == 2:
        return "two"
    elif value == 3:
        return "three"
    elif value == 4:
        return "four"
    else:
        return "other"
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 1, f"Multiple elif chain should be depth 1, got {depth}"

    def test_nested_if_inside_elif_increases_depth(self) -> None:
        """Nested if inside elif body should correctly increase depth."""
        code = """
def complex_check(x, y):
    if x > 10:
        return "x big"
    elif x > 5:
        if y > 10:  # This is nested - depth 2
            return "x medium, y big"
        return "x medium"
    else:
        return "x small"
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 2, f"Nested if in elif should be depth 2, got {depth}"

    def test_long_elif_chain_like_legacy_windows_render(self) -> None:
        """14-branch elif chain (like legacy_windows_render) should be depth 1."""
        code = """
def legacy_windows_render(key):
    if key == "F1":
        return handle_f1()
    elif key == "F2":
        return handle_f2()
    elif key == "F3":
        return handle_f3()
    elif key == "F4":
        return handle_f4()
    elif key == "F5":
        return handle_f5()
    elif key == "F6":
        return handle_f6()
    elif key == "F7":
        return handle_f7()
    elif key == "F8":
        return handle_f8()
    elif key == "F9":
        return handle_f9()
    elif key == "F10":
        return handle_f10()
    elif key == "F11":
        return handle_f11()
    elif key == "F12":
        return handle_f12()
    elif key == "ESC":
        return handle_escape()
    else:
        return handle_default()
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 1, f"14-branch elif chain should be depth 1, got {depth}"

    def test_elif_with_for_loop_inside(self) -> None:
        """For loop inside elif body should be depth 2."""
        code = """
def process(items, mode):
    if mode == "skip":
        return []
    elif mode == "process":
        for item in items:  # depth 2
            print(item)
        return items
    else:
        return None
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 2, f"For loop in elif should be depth 2, got {depth}"

    def test_if_in_else_block_is_nested(self) -> None:
        """If inside else block (not elif) should increase depth."""
        code = """
def check(x, y):
    if x > 10:
        return "x big"
    else:
        if y > 10:  # This is in else, not elif - depth 2
            return "y big"
        return "both small"
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 2, f"If in else block should be depth 2, got {depth}"

    def test_mixed_elif_and_else_with_nested_if(self) -> None:
        """Complex mix of elif and nested structures."""
        code = """
def complex(a, b, c):
    if a == 1:
        return "a1"
    elif a == 2:
        return "a2"
    elif a == 3:
        if b == 1:  # depth 2
            return "a3b1"
        elif b == 2:  # still depth 2 (elif of nested if)
            if c == 1:  # depth 3
                return "a3b2c1"
            return "a3b2"
        return "a3"
    else:
        return "other"
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 3, f"Deeply nested structure should be depth 3, got {depth}"


class TestElifWithOtherConstructs:
    """Test elif handling with other nesting constructs."""

    def test_elif_with_try_except(self) -> None:
        """Try/except inside elif should be depth 2."""
        code = """
def safe_process(mode, data):
    if mode == "skip":
        return None
    elif mode == "process":
        try:  # depth 2
            return process(data)
        except ValueError:
            return "error"
    else:
        return data
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 2, f"Try in elif should be depth 2, got {depth}"

    def test_elif_with_with_statement(self) -> None:
        """With statement inside elif should be depth 2."""
        code = """
def file_handler(mode, path):
    if mode == "read":
        with open(path) as f:  # depth 2
            return f.read()
    elif mode == "write":
        with open(path, "w") as f:  # depth 2
            f.write("data")
    else:
        return None
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 2, f"With in if/elif should be depth 2, got {depth}"

    def test_elif_without_else(self) -> None:
        """elif chain without final else should still be depth 1."""
        code = """
def partial_check(x):
    if x == 1:
        return "one"
    elif x == 2:
        return "two"
    elif x == 3:
        return "three"
"""
        analyzer = PythonNestingAnalyzer()
        tree = ast.parse(code)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)

        depth, _ = analyzer.calculate_max_depth(func)
        assert depth == 1, f"elif chain without else should be depth 1, got {depth}"
