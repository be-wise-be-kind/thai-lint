"""
File: tests/unit/linters/file_header/test_ignore_directives.py
Purpose: Test suite for ignore directive support in file header linter
Exports: TestLineIgnoreDirectives, TestFileIgnoreDirectives, TestPatternIgnoreConfiguration
Depends: pytest, conftest.create_mock_context, src.linters.file_header.linter.FileHeaderRule
Related: test_configuration.py, test_python_header_validation.py

Overview:
    Tests for ignore directive support allowing developers to suppress file header
    validation. Covers line-level ignore directives, file-level ignore directives,
    and pattern-based ignore configuration. All tests initially fail (TDD RED phase)
    since FileHeaderRule does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_ignore_directives.py -v
"""

from tests.unit.linters.file_header.conftest import create_mock_context


class TestLineIgnoreDirectives:
    """Test line-level ignore directives."""

    def test_respects_line_ignore_directive(self):
        """Should respect line-level ignore directive for specific violations."""
        code = '''"""
Purpose: Test module
Scope: Created 2025-01-15  # thailint-ignore-line: file-header
Overview: Test overview
Dependencies: None
Exports: None
Interfaces: None
Implementation: Test
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should not flag the line with ignore directive
        # (Date "2025-01-15" would normally be flagged)
        # May still have other violations, but not for that specific line
        line_2_violations = [v for v in violations if v.line == 2]
        assert len(line_2_violations) == 0


class TestFileIgnoreDirectives:
    """Test file-level ignore directives."""

    def test_respects_file_ignore_directive(self):
        """Should respect file-level ignore directive."""
        code = '''"""
# thailint-ignore-file: file-header

Purpose: Missing many fields
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should ignore entire file
        assert len(violations) == 0

    def test_file_ignore_at_top_of_file(self):
        """Should detect file-level ignore at top of file."""
        code = '''# thailint-ignore-file: file-header
"""
Purpose: Test only
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should ignore entire file
        assert len(violations) == 0


class TestPatternIgnoreConfiguration:
    """Test pattern-based ignore in configuration."""

    def test_respects_test_file_ignore_pattern(self):
        """Should ignore test files based on configuration pattern."""
        code = '''"""
Purpose: Test purpose only
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code,
            "test_my_module.py",  # Test file pattern
            metadata={"file_header": {"ignore": ["test_*.py", "**/tests/**"]}},
        )
        violations = rule.check(context)

        # Should ignore test files
        assert len(violations) == 0

    def test_respects_init_file_ignore_pattern(self):
        """Should ignore __init__.py files based on configuration."""
        code = '"""Purpose: Init file"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code, "__init__.py", metadata={"file_header": {"ignore": ["**/__init__.py"]}}
        )
        violations = rule.check(context)

        # Should ignore __init__.py files
        assert len(violations) == 0

    def test_respects_directory_ignore_pattern(self):
        """Should ignore files in specific directories."""
        code = '"""Purpose: Migration file"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code,
            "migrations/0001_initial.py",
            metadata={"file_header": {"ignore": ["**/migrations/**"]}},
        )
        violations = rule.check(context)

        # Should ignore migration files
        assert len(violations) == 0

    def test_generic_ignore_directive(self):
        """Should support generic ignore directive without specific rule."""
        code = '''"""
# thailint-ignore

Purpose: Test only
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Generic ignore should work for file-header rule
        assert len(violations) == 0
