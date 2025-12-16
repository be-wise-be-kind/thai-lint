"""
Purpose: Unit tests for method-should-be-property edge cases and error handling

Scope: Testing edge cases, error handling, and special scenarios

Overview: Comprehensive test suite for edge cases in method-should-be-property detection covering
    empty files, syntax errors, Unicode content, files without classes, nested classes, multiple
    classes, and other boundary conditions. Validates that the linter handles unusual inputs
    gracefully without crashing and produces appropriate results. Ensures robustness and
    stability across diverse file contents and structures.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock,
    src.linters.method_property.linter.MethodPropertyRule

Exports: TestEdgeCases, TestFileStructureEdgeCases test classes

Interfaces: test methods validating graceful handling of edge cases

Implementation: Uses Mock objects for context creation, various edge case code samples,
    validates proper handling without crashes or exceptions
"""

from pathlib import Path
from unittest.mock import Mock


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_empty_file(self):
        """Should handle empty file gracefully."""
        code = ""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("empty.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_handles_whitespace_only_file(self):
        """Should handle file with only whitespace."""
        code = "   \n\n   \t\t\n   "
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("whitespace.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_handles_syntax_error(self):
        """Should handle files with syntax errors gracefully."""
        code = "def broken(:\n    return self._value"
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("broken.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should not crash, should return empty or skip
        assert len(violations) == 0

    def test_handles_unicode_content(self):
        """Should handle files with Unicode content."""
        code = """
class Benutzer:
    def __init__(self, name):
        self._name = name

    def bezeichnung(self):
        return self._name

    def grüße(self):
        return f"Hallo {self._name}!"
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("benutzer.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should detect both methods as candidates
        assert len(violations) == 2

    def test_handles_unicode_in_strings(self):
        """Should handle Unicode strings in return values."""
        code = """
class Greeting:
    def __init__(self):
        self._emoji = "😀"

    def emoji(self):
        return self._emoji
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("greeting.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_handles_no_classes(self):
        """Should handle file with no classes."""
        code = """
def standalone_function():
    return "value"

x = 42
y = "string"
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("module.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_handles_only_imports(self):
        """Should handle file with only imports."""
        code = """
import os
import sys
from pathlib import Path
from typing import Optional, List
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("imports.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_handles_comments_only(self):
        """Should handle file with only comments."""
        code = """
# This is a comment
# Another comment

# More comments
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("comments.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestFileStructureEdgeCases:
    """Test edge cases related to file structure."""

    def test_handles_nested_classes(self):
        """Should handle nested class definitions."""
        code = """
class Outer:
    def __init__(self):
        self._outer_value = 1

    def outer_value(self):
        return self._outer_value

    class Inner:
        def __init__(self):
            self._inner_value = 2

        def inner_value(self):
            return self._inner_value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("nested.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should detect methods in both outer and inner classes
        assert len(violations) == 2

    def test_handles_multiple_classes(self):
        """Should handle multiple class definitions."""
        code = """
class First:
    def __init__(self):
        self._a = 1

    def a(self):
        return self._a

class Second:
    def __init__(self):
        self._b = 2

    def b(self):
        return self._b

class Third:
    def __init__(self):
        self._c = 3

    def c(self):
        return self._c
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("multiple.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 3

    def test_handles_class_with_no_methods(self):
        """Should handle class with no methods."""
        code = """
class Empty:
    pass

class OnlyInit:
    def __init__(self):
        self._value = 42
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("empty_class.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_handles_class_inheriting_from_builtin(self):
        """Should handle class inheriting from builtin types."""
        code = """
class MyList(list):
    def __init__(self):
        super().__init__()
        self._custom = 42

    def custom(self):
        return self._custom
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("custom_list.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_handles_dataclass(self):
        """Should handle dataclass definitions."""
        code = """
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str

    def get_display_name(self):
        return self.name.upper()
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should still detect method in dataclass
        assert len(violations) == 1


class TestMethodDefinitionEdgeCases:
    """Test edge cases in method definitions."""

    def test_handles_method_with_type_hints(self):
        """Should handle method with type hints."""
        code = """
class User:
    def __init__(self, name: str) -> None:
        self._name: str = name

    def name(self) -> str:
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("typed.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_handles_method_with_complex_return_type(self):
        """Should handle method with complex return type hints."""
        code = """
from typing import Optional, List

class Container:
    def __init__(self):
        self._items: List[str] = []

    def items(self) -> Optional[List[str]]:
        return self._items
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("container.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_handles_method_with_docstring(self):
        """Should handle method with docstring."""
        code = '''
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        """Return the user's name."""
        return self._name
'''
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Docstring + return is still simple enough
        assert len(violations) == 1

    def test_handles_method_with_multiline_docstring(self):
        """Should handle method with multi-line docstring."""
        code = '''
class User:
    def __init__(self, name):
        self._name = name

    def name(self):
        """Return the user's name.

        Returns:
            str: The name of the user.
        """
        return self._name
'''
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Multi-line docstring + return should still be detected
        assert len(violations) == 1


class TestLanguageHandling:
    """Test handling of different languages."""

    def test_ignores_non_python_files(self):
        """Should not process non-Python files."""
        code = """
class User {
    constructor(name) {
        this._name = name;
    }

    getName() {
        return this._name;
    }
}
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.js")
        context.file_content = code
        context.language = "javascript"

        violations = rule.check(context)
        # Should not flag JavaScript code
        assert len(violations) == 0

    def test_ignores_typescript_files(self):
        """Should not process TypeScript files."""
        code = """
class User {
    private _name: string;

    constructor(name: string) {
        this._name = name;
    }

    getName(): string {
        return this._name;
    }
}
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        # Should not flag TypeScript code
        assert len(violations) == 0
