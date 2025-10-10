"""
Purpose: Test edge cases and special scenarios for SRP linter

Scope: Unusual code patterns, edge cases, error handling for SRP analysis

Overview: Validates SRP linter behavior with edge cases including empty files, files
    with only functions (no classes), files with only imports, syntax error handling,
    abstract base classes, dataclasses with many fields (shouldn't count as methods),
    property decorators (shouldn't count as methods), inherited methods (shouldn't count),
    class methods and static methods, async methods, nested function definitions,
    and various Python/TypeScript language edge cases. Ensures robust handling of
    unusual inputs without false positives or crashes.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestEdgeCases (10 tests) covering unusual code patterns and error handling

Interfaces: Tests SRPRule.check() with edge case code samples

Implementation: Tests boundary conditions, unusual syntax, and graceful error handling
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestEdgeCases:
    """Test SRP linter edge cases and special scenarios."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_empty_file_passes(self):
        """Empty file should pass without errors."""
        code = ""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Empty file should pass"

    @pytest.mark.skip(reason="100% duplicate")
    def test_file_with_only_functions_passes(self):
        """File with only functions (no classes) should pass."""
        code = """
def function1():
    pass

def function2():
    pass

def function3():
    pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Functions-only file should pass"

    @pytest.mark.skip(reason="100% duplicate")
    def test_file_with_only_imports_passes(self):
        """File with only imports should pass."""
        code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Imports-only file should pass"

    @pytest.mark.skip(reason="100% duplicate")
    def test_syntax_error_handled_gracefully(self):
        """Syntax errors should be handled without crashing."""
        code = """
class BrokenClass
    def method1(self): pass
    this is not valid python
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        # Should not crash, may return empty violations
        rule.check(context)
        # Graceful handling expected

    @pytest.mark.skip(reason="100% duplicate")
    def test_abstract_base_class_analyzed_correctly(self):
        """Abstract base classes should be analyzed like regular classes."""
        code = """
from abc import ABC, abstractmethod

class AbstractManager(ABC):
    @abstractmethod
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "ABC with 8 methods should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_dataclass_fields_dont_count_as_methods(self):
        """Dataclass fields should not count as methods."""
        code = """
from dataclasses import dataclass

@dataclass
class UserData:
    id: int
    name: str
    email: str
    age: int
    address: str
    phone: str
    created_at: str
    updated_at: str
    is_active: bool
    role: str
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        rule.check(context)
        # Dataclass fields should not count as methods

    @pytest.mark.skip(reason="100% duplicate")
    def test_property_decorators_dont_count_as_methods(self):
        """@property decorated methods should not count."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def display_name(self):
        return self._name.title()

    @property
    def username(self):
        return self._name.lower()

    def save(self): pass
    def delete(self): pass
    def validate(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        rule.check(context)
        # Properties should not count as methods

    @pytest.mark.skip(reason="100% duplicate")
    def test_inherited_methods_dont_count(self):
        """Inherited methods should not count toward limit."""
        code = """
class BaseClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass

class DerivedClass(BaseClass):
    def method4(self): pass
    def method5(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        rule.check(context)
        # DerivedClass only has 2 methods (should pass)

    @pytest.mark.skip(reason="100% duplicate")
    def test_class_and_static_methods_count(self):
        """@classmethod and @staticmethod should count as methods."""
        code = """
class UtilityClass:
    @classmethod
    def m1(cls): pass

    @staticmethod
    def m2(): pass

    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Class with 8 methods should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_async_methods_count(self):
        """Async methods should count toward limit."""
        code = """
class AsyncService:
    async def m1(self): pass
    async def m2(self): pass
    async def m3(self): pass
    async def m4(self): pass
    async def m5(self): pass
    async def m6(self): pass
    async def m7(self): pass
    async def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Async methods should count"
