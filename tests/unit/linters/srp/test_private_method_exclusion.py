"""
Purpose: Test private method exclusion from SRP method count

Scope: Validates that private methods (starting with _) are excluded from method count

Overview: Regression tests for GitHub Issue #142 - private method exclusion in SRP linter.
    Tests Python and TypeScript classes with mixed public/private methods, dunder methods,
    and name-mangled methods. Verifies that classes with clean public interfaces but many
    private helpers do not violate method count thresholds. Validates TDD approach where
    these tests fail before implementation and pass after.

Dependencies: pytest for testing framework, ast module for Python parsing,
    src.linters.srp.heuristics for count_methods, src.linters.srp.linter for SRPRule

Exports: TestPythonPrivateMethodExclusion (5 tests), TestTypeScriptPrivateMethodExclusion (2 tests)

Interfaces: Tests count_methods() and SRPRule.check() with private method scenarios

Implementation: Uses inline code strings as test fixtures, Mock contexts for SRPRule
"""

import ast
from pathlib import Path
from unittest.mock import Mock

from src.linters.srp.heuristics import count_methods
from src.linters.srp.linter import SRPRule


class TestPythonPrivateMethodExclusion:
    """Test private method exclusion in Python classes."""

    def test_class_with_only_public_methods_counted(self):
        """Public methods should be counted in method count."""
        code = """
class MyClass:
    def public1(self): pass
    def public2(self): pass
    def public3(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]

        method_count = count_methods(class_node)
        assert method_count == 3, "All 3 public methods should be counted"

    def test_private_methods_excluded_from_count(self):
        """Private methods (starting with _) should NOT be counted."""
        code = """
class MyClass:
    def public1(self): pass
    def _private1(self): pass
    def _private2(self): pass
    def public2(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]

        method_count = count_methods(class_node)
        assert method_count == 2, "Only 2 public methods should be counted, not 4"

    def test_dunder_methods_excluded(self):
        """Dunder methods (__init__, __str__, etc.) should be excluded."""
        code = """
class MyClass:
    def __init__(self): pass
    def __str__(self): return ""
    def __repr__(self): return ""
    def _private(self): pass
    def public(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]

        method_count = count_methods(class_node)
        # Only public = 1 method
        # __init__, __str__, __repr__, _private are all excluded (start with _)
        assert method_count == 1, "Only public method counted, dunders and private excluded"

    def test_double_underscore_private_excluded(self):
        """Name-mangled methods (__private without trailing __) should be excluded."""
        code = """
class MyClass:
    def __mangled(self): pass
    def __also_mangled_helper(self): pass
    def public(self): pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]

        method_count = count_methods(class_node)
        assert method_count == 1, "Only public method counted, name-mangled methods excluded"

    def test_class_under_threshold_with_many_private_methods(self):
        """Class with many private methods but few public ones should pass threshold."""
        code = """
class ComplexButCleanClass:
    def process(self): pass
    def validate(self): pass
    def _helper1(self): pass
    def _helper2(self): pass
    def _helper3(self): pass
    def _helper4(self): pass
    def _helper5(self): pass
    def _helper6(self): pass
    def _helper7(self): pass
    def _helper8(self): pass
"""
        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # 2 public methods is under default threshold of 7
        method_violations = [v for v in violations if "methods" in str(v.message)]
        assert len(method_violations) == 0, "Class with 2 public methods should not violate"

    def test_class_over_threshold_with_public_methods_only(self):
        """Class with many public methods should still violate."""
        code = """
class OverloadedPublicInterface:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
"""
        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # 8 public methods exceeds default threshold of 7
        assert len(violations) > 0, "Class with 8 public methods should violate"


class TestTypeScriptPrivateMethodExclusion:
    """Test private method exclusion in TypeScript classes."""

    def test_typescript_underscore_methods_excluded(self):
        """TypeScript methods starting with _ should be excluded."""
        code = """
class MyClass {
    method1() {}
    method2() {}
    _privateHelper() {}
    _anotherHelper() {}
}
"""
        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        # Only 2 non-underscore methods counted
        method_violations = [v for v in violations if "methods" in str(v.message)]
        assert len(method_violations) == 0, "Class with 2 public methods should not violate"

    def test_typescript_many_private_no_violation(self):
        """TypeScript class with many private methods should not violate if public count is low."""
        code = """
class DataProcessor {
    process() {}
    validate() {}
    _parseJson() {}
    _validateSchema() {}
    _transformData() {}
    _logDebug() {}
    _handleError() {}
    _retryOperation() {}
    _cacheResult() {}
    _cleanupResources() {}
}
"""
        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        # Only 2 public methods, should not violate
        method_violations = [v for v in violations if "methods" in str(v.message)]
        assert len(method_violations) == 0, "TypeScript class with 2 public methods should pass"
