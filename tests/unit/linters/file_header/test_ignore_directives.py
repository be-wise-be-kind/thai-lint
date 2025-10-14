"""
File: tests/unit/linters/file_header/test_ignore_directives.py

Purpose: Test suite for ignore directive support in file header linter

Exports: TestIgnoreDirectives test class with ~6 tests

Depends: pytest, unittest.mock, src.linters.file_header.linter.FileHeaderRule

Implements: TDD RED phase tests for ignore pattern support

Related: conftest.py for fixtures and mock context creation

Overview: Tests ignore directive functionality including pattern-based ignores in
    configuration. Validates that files matching ignore patterns are skipped during
    validation. Tests follow TDD approach with all tests initially failing.

Usage: Run via pytest: `pytest tests/unit/linters/file_header/test_ignore_directives.py`

Notes: All tests FAIL initially (TDD RED phase) until FileHeaderRule implementation
"""

from pathlib import Path
from unittest.mock import Mock


class TestIgnoreDirectives:
    """Tests for ignore directive support."""

    def test_ignores_test_files_pattern(self):
        """Should ignore files matching test/** pattern."""
        code = '''"""
No proper header here at all
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test/test_module.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": {"ignore": ["test/**"]}}

        violations = rule.check(context)
        # Should be ignored due to test/** pattern
        assert len(violations) == 0

    def test_ignores_init_files(self):
        """Should ignore __init__.py files by default."""
        code = '''"""
No proper header
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("src/__init__.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": {"ignore": ["**/__init__.py"]}}

        violations = rule.check(context)
        # Should be ignored
        assert len(violations) == 0

    def test_ignores_migrations_pattern(self):
        """Should ignore migration files."""
        code = '''"""
No header
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("db/migrations/0001_initial.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": {"ignore": ["**/migrations/**"]}}

        violations = rule.check(context)
        # Should be ignored
        assert len(violations) == 0

    def test_does_not_ignore_non_matching_files(self):
        """Should not ignore files that don't match patterns."""
        code = '''"""
No proper header
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("src/main.py")  # Does not match any ignore pattern
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": {"ignore": ["test/**", "**/__init__.py"]}}

        violations = rule.check(context)
        # Should NOT be ignored, should have violations
        assert len(violations) >= 1

    def test_supports_multiple_ignore_patterns(self):
        """Should support multiple ignore patterns."""
        code = '''"""
No header
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test/conftest.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": {"ignore": ["test/**", "**/conftest.py", "docs/**"]}}

        violations = rule.check(context)
        # Should match test/** pattern
        assert len(violations) == 0

    def test_glob_pattern_matching(self):
        """Should support glob-style pattern matching."""
        code = '''"""
No header
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("src/linters/magic_numbers/__init__.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": {"ignore": ["**/__init__.py"]}}

        violations = rule.check(context)
        # Should match **/__init__.py pattern regardless of depth
        assert len(violations) == 0
