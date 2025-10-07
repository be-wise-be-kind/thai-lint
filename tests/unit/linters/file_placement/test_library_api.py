"""
Purpose: Test suite for library/programmatic API of file placement linter

Scope: Validation of importable library interface for programmatic linter usage

Overview: Validates the library API that allows importing and using file placement linter
    directly from Python code without CLI. Tests verify module importability, function call
    interface with path and config parameters, and structured violation return format.
    Ensures the linter can be embedded in other tools, editors, and automation scripts
    with clean, Pythonic API design.

Dependencies: pytest for testing framework, pathlib for Path objects

Exports: TestLibraryAPI test class with 3 tests

Interfaces: Tests importable module and lint(path, config) function signature

Implementation: 3 tests covering module import, function call interface, and violation structure
"""
import pytest
from pathlib import Path


class TestLibraryAPI:
    """Test using linter as importable library."""

    def test_import_linter(self):
        """Can import file_placement_linter."""
        from src.linters import file_placement
        assert file_placement is not None

    def test_function_call_interface(self):
        """Call linter.lint(path, config)."""
        from src.linters import file_placement

        config = {'allow': [r'.*\.py$']}
        violations = file_placement.lint(Path('.'), config)

        assert isinstance(violations, list)

    def test_return_structured_violations(self):
        """Violations returned as structured data."""
        from src.linters import file_placement

        violations = file_placement.lint(Path('.'))

        if violations:
            v = violations[0]
            assert hasattr(v, 'rule_id')
            assert hasattr(v, 'file_path')
            assert hasattr(v, 'to_dict')
