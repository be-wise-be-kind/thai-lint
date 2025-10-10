"""
Purpose: Test library API for programmatic SRP linter usage

Scope: Python library interface, programmatic access, direct API usage for SRP linter

Overview: Validates programmatic library API for SRP linter including srp_lint convenience
    function import and usage, orchestrator integration with rules=['srp'] parameter,
    direct SRPRule class instantiation and invocation, programmatic result parsing and
    violation access, configuration passing via API parameters, and integration with
    the core linting framework. Ensures SRP linter is accessible as a Python library
    for programmatic use cases and custom integrations.

Dependencies: pytest for testing framework, src package for library API, pathlib for Path,
    src.linters.srp for SRPRule

Exports: TestLibraryAPI (6 tests) covering import, instantiation, and programmatic usage

Interfaces: Tests from src import srp_lint, SRPRule class, orchestrator rules parameter

Implementation: Tests library imports, function invocations, and result parsing
"""

import tempfile
from pathlib import Path


class TestLibraryAPI:
    """Test SRP linter library/programmatic API."""

    def test_import_srp_lint_function(self):
        """Should be able to import srp_lint convenience function."""
        from src import srp_lint

        assert callable(srp_lint), "srp_lint should be a callable function"

    def test_import_srp_rule_class(self):
        """Should be able to import SRPRule class."""
        from src import SRPRule

        assert SRPRule is not None, "SRPRule should be importable"

    def test_srp_lint_convenience_function_works(self):
        """srp_lint function should analyze code and return results."""
        from src import srp_lint

        # Create test file
        test_code = """
class DataManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            result = srp_lint(temp_path)
            assert isinstance(result, list), "Should return list of violations"
        finally:
            Path(temp_path).unlink()

    def test_orchestrator_with_srp_rule(self):
        """Linter API should support rules=['srp.violation'] parameter."""
        # Test Linter API integration
        from src import Linter

        test_code = """
class UserManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            linter = Linter()
            violations = linter.lint(temp_path, rules=["srp.violation"])
            assert isinstance(violations, list), "Should return list"
        finally:
            Path(temp_path).unlink()
