"""
Purpose: Integration tests for cross-file stringly-typed pattern detection

Scope: Multi-file pattern detection using StringlyTypedRule

Overview: Comprehensive test suite for cross-file stringly-typed pattern detection covering
    scenarios with patterns spanning multiple files, different pattern types, and configuration
    options. Validates proper cross-referencing in violation messages and threshold behavior.

Dependencies: pytest, pathlib, StringlyTypedRule, FileLintContext

Exports: Test functions for cross-file detection scenarios

Interfaces: Tests use StringlyTypedRule directly with FileLintContext

Implementation: Uses tmp_path for isolated file fixtures, tests rule directly
"""

from pathlib import Path

import pytest

from src.linters.stringly_typed import StringlyTypedRule
from src.orchestrator.core import FileLintContext


@pytest.fixture
def rule() -> StringlyTypedRule:
    """Create a fresh rule instance for each test."""
    return StringlyTypedRule()


def create_context(
    file_path: Path, language: str = "python", config: dict | None = None
) -> FileLintContext:
    """Create a FileLintContext for testing.

    Args:
        file_path: Path to the file
        language: Programming language
        config: Optional stringly_typed config dict

    Returns:
        FileLintContext instance
    """
    content = file_path.read_text() if file_path.exists() else ""
    metadata = {"stringly_typed": config or {}}
    return FileLintContext(file_path, language, content, metadata)


class TestCrossFileDetection:
    """Tests for cross-file pattern detection."""

    def test_same_pattern_in_two_files_generates_violations(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Two files with same string pattern should generate violations."""
        # Create file 1 with membership validation
        file1 = tmp_path / "module1.py"
        file1.write_text("""
def check_env(env: str) -> bool:
    if env in ("staging", "production"):
        return True
    return False
""")

        # Create file 2 with same pattern
        file2 = tmp_path / "module2.py"
        file2.write_text("""
def validate_env(env: str) -> None:
    if env not in ("staging", "production"):
        raise ValueError("Invalid env")
""")

        # Process both files
        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        # Get violations
        violations = rule.finalize()

        # Should have 2 violations (one per file)
        assert len(violations) == 2
        violation_files = {Path(v.file_path).name for v in violations}
        assert "module1.py" in violation_files
        assert "module2.py" in violation_files

    def test_pattern_in_three_files_generates_violations(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Pattern appearing in 3 files should generate 3 violations."""
        pattern_values = '("active", "inactive", "pending")'

        for i in range(3):
            file = tmp_path / f"module{i}.py"
            file.write_text(f"""
def check_status_{i}(status: str) -> bool:
    return status in {pattern_values}
""")

        # Process all files
        for i in range(3):
            ctx = create_context(tmp_path / f"module{i}.py")
            rule.check(ctx)

        violations = rule.finalize()

        assert len(violations) == 3

    def test_single_file_no_violation_with_require_cross_file(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Single file should not generate violation when require_cross_file=True."""
        file1 = tmp_path / "single.py"
        file1.write_text("""
def check_mode(mode: str) -> bool:
    return mode in ("debug", "release")
""")

        ctx = create_context(file1, config={"require_cross_file": True})
        rule.check(ctx)

        violations = rule.finalize()

        assert len(violations) == 0

    def test_different_patterns_no_cross_file_match(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Different string patterns should not match across files."""
        file1 = tmp_path / "module1.py"
        file1.write_text("""
def check_env(env: str) -> bool:
    return env in ("staging", "production")
""")

        file2 = tmp_path / "module2.py"
        file2.write_text("""
def check_mode(mode: str) -> bool:
    return mode in ("debug", "release")
""")

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # Different patterns, no cross-file match
        assert len(violations) == 0

    def test_same_values_different_order_matches(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Same values in different order should match (hash normalization)."""
        file1 = tmp_path / "module1.py"
        file1.write_text("""
def check1(x: str) -> bool:
    return x in ("alpha", "beta", "gamma")
""")

        file2 = tmp_path / "module2.py"
        file2.write_text("""
def check2(x: str) -> bool:
    return x in ("gamma", "alpha", "beta")
""")

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # Same values in different order should match
        assert len(violations) == 2

    def test_case_normalized_matching(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Values should match regardless of case (lowercase normalization)."""
        file1 = tmp_path / "module1.py"
        file1.write_text("""
def check1(x: str) -> bool:
    return x in ("Active", "Inactive")
""")

        file2 = tmp_path / "module2.py"
        file2.write_text("""
def check2(x: str) -> bool:
    return x in ("active", "inactive")
""")

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # Case-insensitive matching for hash
        assert len(violations) == 2


class TestMinOccurrencesThreshold:
    """Tests for min_occurrences configuration."""

    def test_respects_min_occurrences_threshold(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Pattern in 2 files with min_occurrences=3 should not flag."""
        file1 = tmp_path / "module1.py"
        file1.write_text('x = status in ("a", "b")')

        file2 = tmp_path / "module2.py"
        file2.write_text('y = status in ("a", "b")')

        config = {"min_occurrences": 3}
        ctx1 = create_context(file1, config=config)
        ctx2 = create_context(file2, config=config)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # Only 2 files but min_occurrences is 3
        assert len(violations) == 0

    def test_meets_min_occurrences_threshold(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Pattern in 3 files with min_occurrences=3 should flag."""
        for i in range(3):
            file = tmp_path / f"module{i}.py"
            file.write_text(f'x{i} = status in ("a", "b", "c")')

        config = {"min_occurrences": 3}

        for i in range(3):
            ctx = create_context(tmp_path / f"module{i}.py", config=config)
            rule.check(ctx)

        violations = rule.finalize()

        assert len(violations) == 3


class TestEnumValueThresholds:
    """Tests for min/max_values_for_enum configuration."""

    def test_too_few_values_not_flagged(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Pattern with 1 value should not be flagged (min_values_for_enum=2)."""
        file1 = tmp_path / "module1.py"
        file1.write_text('x = status in ("single",)')

        file2 = tmp_path / "module2.py"
        file2.write_text('y = status in ("single",)')

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # Only 1 value, below min_values_for_enum=2
        assert len(violations) == 0

    def test_too_many_values_not_flagged(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Pattern with 7+ values should not be flagged (max_values_for_enum=6)."""
        values = '("a", "b", "c", "d", "e", "f", "g")'

        file1 = tmp_path / "module1.py"
        file1.write_text(f"x = status in {values}")

        file2 = tmp_path / "module2.py"
        file2.write_text(f"y = status in {values}")

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # 7 values, above max_values_for_enum=6
        assert len(violations) == 0


class TestAllowedStringSets:
    """Tests for allowed_string_sets configuration."""

    def test_allowed_string_set_not_flagged(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Patterns in allowed_string_sets should not be flagged."""
        file1 = tmp_path / "module1.py"
        file1.write_text('x = env in ("dev", "staging", "prod")')

        file2 = tmp_path / "module2.py"
        file2.write_text('y = env in ("dev", "staging", "prod")')

        config = {"allowed_string_sets": [["dev", "staging", "prod"]]}
        ctx1 = create_context(file1, config=config)
        ctx2 = create_context(file2, config=config)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        assert len(violations) == 0


class TestViolationMessages:
    """Tests for violation message content."""

    def test_violation_message_contains_values(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Violation message should contain the string values."""
        file1 = tmp_path / "module1.py"
        file1.write_text('x = mode in ("fast", "slow")')

        file2 = tmp_path / "module2.py"
        file2.write_text('y = mode in ("fast", "slow")')

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        assert len(violations) == 2
        for v in violations:
            assert "fast" in v.message
            assert "slow" in v.message

    def test_violation_message_contains_file_count(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Violation message should mention number of files."""
        for i in range(3):
            file = tmp_path / f"module{i}.py"
            file.write_text(f'x{i} = status in ("active", "inactive")')

        for i in range(3):
            ctx = create_context(tmp_path / f"module{i}.py")
            rule.check(ctx)

        violations = rule.finalize()

        assert len(violations) == 3
        for v in violations:
            assert "3 files" in v.message

    def test_violation_contains_cross_references(
        self, rule: StringlyTypedRule, tmp_path: Path
    ) -> None:
        """Violation message should reference other files with same pattern."""
        file1 = tmp_path / "first.py"
        file1.write_text('x = status in ("on", "off")')

        file2 = tmp_path / "second.py"
        file2.write_text('y = status in ("on", "off")')

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # Find violation for first.py
        first_violation = next(v for v in violations if "first.py" in v.file_path)
        assert "second.py" in first_violation.message

        # Find violation for second.py
        second_violation = next(v for v in violations if "second.py" in v.file_path)
        assert "first.py" in second_violation.message


class TestIgnorePatterns:
    """Tests for ignore pattern configuration."""

    def test_ignored_files_not_flagged(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Files matching ignore patterns should not generate violations."""
        file1 = tmp_path / "src" / "module.py"
        file1.parent.mkdir(parents=True, exist_ok=True)
        file1.write_text('x = status in ("a", "b")')

        file2 = tmp_path / "tests" / "test_module.py"
        file2.parent.mkdir(parents=True, exist_ok=True)
        file2.write_text('y = status in ("a", "b")')

        config = {"ignore": ["tests/"]}
        ctx1 = create_context(file1, config=config)
        ctx2 = create_context(file2, config=config)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        # Only src/module.py should potentially have violations
        # But since we ignore tests/, there's only 1 file, which means no cross-file match
        assert len(violations) == 0


class TestRuleReset:
    """Tests for rule state reset between runs."""

    def test_rule_reset_between_runs(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Rule should reset state between finalize() calls."""
        file1 = tmp_path / "module1.py"
        file1.write_text('x = status in ("a", "b")')

        file2 = tmp_path / "module2.py"
        file2.write_text('y = status in ("a", "b")')

        # First run
        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations1 = rule.finalize()
        assert len(violations1) == 2

        # Second run with new files
        file3 = tmp_path / "module3.py"
        file3.write_text('a = mode in ("x", "y", "z")')

        file4 = tmp_path / "module4.py"
        file4.write_text('b = mode in ("x", "y", "z")')

        ctx3 = create_context(file3)
        ctx4 = create_context(file4)

        rule.check(ctx3)
        rule.check(ctx4)

        violations2 = rule.finalize()

        # Should only contain new files, not old ones
        assert len(violations2) == 2
        violation_files = {Path(v.file_path).name for v in violations2}
        assert "module3.py" in violation_files
        assert "module4.py" in violation_files
        assert "module1.py" not in violation_files


class TestEqualityChainPatterns:
    """Tests for equality chain pattern detection."""

    def test_equality_chain_cross_file(self, rule: StringlyTypedRule, tmp_path: Path) -> None:
        """Equality chains with same values should match across files."""
        file1 = tmp_path / "module1.py"
        file1.write_text("""
def process1(status: str) -> int:
    if status == "success":
        return 1
    elif status == "failure":
        return 2
    elif status == "pending":
        return 3
    return 0
""")

        file2 = tmp_path / "module2.py"
        file2.write_text("""
def process2(status: str) -> str:
    if status == "success":
        return "ok"
    elif status == "failure":
        return "error"
    elif status == "pending":
        return "wait"
    return ""
""")

        ctx1 = create_context(file1)
        ctx2 = create_context(file2)

        rule.check(ctx1)
        rule.check(ctx2)

        violations = rule.finalize()

        assert len(violations) == 2
