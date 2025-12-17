"""
Purpose: Test suite for stateless class detection in Python code

Scope: Python class-level stateless detection using AST-based analysis

Overview: Comprehensive TDD test suite for stateless class detection covering core
    detection scenarios (classes without __init__ or instance state), exception cases
    (ABC, Protocol, decorated classes, dataclasses), edge cases (empty classes, single
    method classes), and real-world patterns like TokenHasher. Tests define expected
    behavior before implementation following Red-Green-Refactor methodology.

Dependencies: pytest for testing framework, src.linters.stateless_class for detector,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestStatelessClassDetection (11 tests) covering all detection scenarios

Interfaces: Tests StatelessClassRule.check(context) -> list[Violation] with Python samples

Implementation: TDD approach - all tests written to fail initially, then implementation
    makes them pass. Uses inline Python code strings as test fixtures with mock contexts.
"""

from pathlib import Path
from unittest.mock import Mock


class TestStatelessClassDetection:
    """Test cases for detecting stateless classes that should be functions."""

    def test_detects_class_without_init_two_plus_methods(self) -> None:
        """Should flag class with 2+ methods but no __init__ as violation."""
        code = """
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect one stateless class violation"
        assert "StatelessHelper" in violations[0].message

    def test_ignores_class_with_init(self) -> None:
        """Should not flag class with __init__ (has constructor)."""
        code = """
class WithInit:
    def __init__(self):
        pass

    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class with __init__ should not be flagged"

    def test_ignores_class_with_instance_attributes(self) -> None:
        """Should not flag class that uses self.attr assignments."""
        code = """
class WithState:
    def method1(self, x):
        self.data = x
        return self.data * 2

    def method2(self, y):
        return self.data + y
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class with instance attributes should not be flagged"

    def test_ignores_abc_class(self) -> None:
        """Should not flag abstract base classes (legitimate pattern)."""
        code = """
from abc import ABC, abstractmethod

class AbstractHelper(ABC):
    @abstractmethod
    def method1(self, x):
        pass

    @abstractmethod
    def method2(self, y):
        pass
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "ABC classes should not be flagged"

    def test_ignores_protocol_class(self) -> None:
        """Should not flag Protocol classes (legitimate typing pattern)."""
        code = """
from typing import Protocol

class Callable(Protocol):
    def __call__(self, x: int) -> int:
        ...

    def validate(self, x: int) -> bool:
        ...
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Protocol classes should not be flagged"

    def test_ignores_decorated_class(self) -> None:
        """Should not flag classes with decorators (framework usage)."""
        code = """
@dataclass
class DataHolder:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Decorated classes should not be flagged"

    def test_ignores_class_with_class_attributes(self) -> None:
        """Should not flag class with class-level attributes (has state)."""
        code = """
class WithClassAttrs:
    DEFAULT_VALUE = 42
    CONFIG = {"key": "value"}

    def method1(self, x):
        return x * self.DEFAULT_VALUE

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class with class attributes should not be flagged"

    def test_ignores_class_with_new(self) -> None:
        """Should not flag class with __new__ method (custom constructor)."""
        code = """
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class with __new__ should not be flagged"

    def test_ignores_empty_class(self) -> None:
        """Should not flag empty class (placeholder)."""
        code = """
class PlaceholderClass:
    pass
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Empty class should not be flagged"

    def test_ignores_class_with_single_method(self) -> None:
        """Should not flag class with only one method (too few to matter)."""
        code = """
class SingleMethod:
    def only_method(self, x):
        return x * 2
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Single method class should not be flagged"

    def test_detects_real_world_tokenhasher_pattern(self) -> None:
        """Should detect TokenHasher-style stateless classes from real codebase."""
        code = '''
class TokenHasher:
    """Hashes code tokens for duplicate detection."""

    def tokenize(self, code: str) -> list[str]:
        """Tokenize code into meaningful chunks."""
        return self._strip_comments(code).split()

    def _strip_comments(self, code: str) -> str:
        """Remove comments from code."""
        lines = []
        for line in code.split("\\n"):
            if "#" in line:
                line = line.split("#")[0]
            lines.append(line)
        return "\\n".join(lines)

    def compute_hash(self, tokens: list[str]) -> str:
        """Compute hash of tokens."""
        import hashlib
        return hashlib.md5("".join(tokens).encode()).hexdigest()
'''
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1, "TokenHasher pattern should be flagged"
        assert "TokenHasher" in violations[0].message


class TestMultipleClasses:
    """Test detection across multiple classes in a single file."""

    def test_detects_only_stateless_classes(self) -> None:
        """Should detect only stateless classes, not classes with state."""
        code = """
class StatelessOne:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1


class WithState:
    def __init__(self):
        self.data = []

    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1


class StatelessTwo:
    def helper1(self, a):
        return a.upper()

    def helper2(self, b):
        return b.lower()
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 2, "Should detect exactly 2 stateless classes"
        class_names = [v.message for v in violations]
        assert any("StatelessOne" in msg for msg in class_names)
        assert any("StatelessTwo" in msg for msg in class_names)
        assert not any("WithState" in msg for msg in class_names)


class TestViolationDetails:
    """Test violation message content and line numbers."""

    def test_violation_includes_class_name(self) -> None:
        """Violation message should include the class name."""
        code = """
class UtilityClass:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1
        assert "UtilityClass" in violations[0].message

    def test_violation_includes_correct_line_number(self) -> None:
        """Violation should point to correct line where class is defined."""
        code = """# Comment line
# Another comment

class MyStatelessClass:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1
        assert violations[0].line == 4, "Should point to line 4 where class is defined"

    def test_violation_includes_suggestion(self) -> None:
        """Violation message should include refactoring suggestion."""
        code = """
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1
        message = violations[0].message.lower()
        assert "function" in message or "module" in message, (
            "Should suggest converting to functions"
        )
