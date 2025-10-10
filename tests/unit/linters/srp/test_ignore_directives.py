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


class TestIgnoreDirectives:
    """Test ignore directive handling for SRP violations."""

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

        # Should suppress method count violation but not others

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
