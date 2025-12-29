"""
Purpose: Tests for orphaned suppression detection

Scope: Unit tests for detecting header entries without matching ignores in code

Overview: Test suite for orphaned suppression detection. An orphaned suppression is
    one that is declared in the file header's Suppressions section but has no corresponding
    ignore directive in the code. This indicates stale documentation that should be removed.

Dependencies: pytest, src.linters.lazy_ignores

Exports: Test classes for orphaned detection

Interfaces: pytest test discovery and execution

Implementation: Unit tests validating LazyIgnoresRule orphaned detection
"""

from src.linters.lazy_ignores import LazyIgnoresRule


class TestOrphanedDetection:
    """Tests for detecting orphaned header entries."""

    def test_detects_orphaned_suppression(self) -> None:
        """Header declares PLR0912 but no such ignore in code."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: Some justification
"""

def simple_function():
    return 1
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 1

    def test_no_orphaned_when_ignore_exists(self) -> None:
        """No orphaned violation when ignore actually exists."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: State machine complexity
"""

def complex():  # noqa: PLR0912
    # ... complex code ...
    pass
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 0

    def test_detects_multiple_orphaned(self) -> None:
        """Detects multiple orphaned suppressions."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: Old complexity
    PLR0915: Old branches
    nosec B602: Old security bypass
"""

def simple():
    return 1
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 3


class TestPartialOrphaned:
    """Tests for partial orphaned detection."""

    def test_some_used_some_orphaned(self) -> None:
        """Detects only orphaned entries when some are used."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: Used below
    PLR0915: Not used - should be flagged
"""

def complex():  # noqa: PLR0912
    pass
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 1
        assert "PLR0915" in orphaned[0].message


class TestOrphanedWithNormalization:
    """Tests for orphaned detection with rule ID normalization."""

    def test_matches_case_insensitive(self) -> None:
        """Matches PLR0912 in header with plr0912 in code."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: Complexity
"""

def complex():  # noqa: plr0912
    pass
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 0

    def test_matches_type_ignore_variants(self) -> None:
        """Matches type:ignore[arg-type] variations."""
        code = '''"""
Purpose: Test

Suppressions:
    type:ignore[arg-type]: Pydantic model
"""

value = get_value()  # type: ignore[arg-type]
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 0


class TestOrphanedErrorMessages:
    """Tests for orphaned violation error messages."""

    def test_error_includes_rule_id(self) -> None:
        """Error message includes the orphaned rule ID."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: Old entry
"""

def simple():
    return 1
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert "PLR0912" in orphaned[0].message

    def test_error_suggests_removal(self) -> None:
        """Error message suggests removing the orphaned entry."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: Old entry
"""

def simple():
    return 1
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert "remove" in orphaned[0].suggestion.lower()
