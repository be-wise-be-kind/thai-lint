"""
Purpose: Regression tests for SRP private method exclusion

Scope: Unit tests for issue #142 fix - excluding private methods from count

Overview: Tests that the SRP linter only counts public methods, not private
    methods (those starting with underscore). Classes with clean public
    interfaces but complex private implementations should not be penalized.
"""

import ast

from src.linters.srp.heuristics import count_methods


class TestPrivateMethodExclusion:
    """Test that private methods are excluded from SRP count (issue #142)."""

    def test_counts_only_public_methods(self) -> None:
        """Test that only public methods are counted."""
        code = """
class MyClass:
    def public_one(self): pass
    def public_two(self): pass
    def _private_one(self): pass
    def _private_two(self): pass
    def __init__(self): pass
    def __str__(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)

        count = count_methods(class_node)

        # Only public_one and public_two should be counted
        # _private_one, _private_two, __init__, __str__ are all private
        assert count == 2

    def test_class_with_only_private_methods_has_zero_count(self) -> None:
        """Test that a class with only private methods has count 0."""
        code = """
class PrivateHelper:
    def _helper_one(self): pass
    def _helper_two(self): pass
    def __init__(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)

        count = count_methods(class_node)

        assert count == 0

    def test_class_with_many_privates_few_public_passes(self) -> None:
        """Test that class with many private but few public methods passes."""
        code = """
class ComplexImplementation:
    def process(self): pass
    def get_result(self): pass
    def _step_one(self): pass
    def _step_two(self): pass
    def _step_three(self): pass
    def _step_four(self): pass
    def _step_five(self): pass
    def _validate(self): pass
    def _transform(self): pass
    def _finalize(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)

        count = count_methods(class_node)

        # Only 2 public methods (process, get_result)
        # 8 private methods are excluded
        assert count == 2

    def test_properties_still_excluded(self) -> None:
        """Test that @property decorated methods are still excluded."""
        code = """
class MyClass:
    def public_method(self): pass

    @property
    def value(self): return self._value

    def _private_method(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)

        count = count_methods(class_node)

        # Only public_method is counted
        # @property value is excluded (property decorator)
        # _private_method is excluded (underscore prefix)
        assert count == 1

    def test_async_methods_handled_correctly(self) -> None:
        """Test that async methods are counted/excluded correctly."""
        code = """
class AsyncService:
    async def public_fetch(self): pass
    async def public_save(self): pass
    async def _private_fetch(self): pass
    async def __aenter__(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)

        count = count_methods(class_node)

        # Only public_fetch and public_save should be counted
        assert count == 2
