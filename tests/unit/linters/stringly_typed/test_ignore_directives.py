"""
Purpose: Tests for stringly-typed linter ignore directive support

Scope: Unit tests for IgnoreChecker class and ignore directive integration

Overview: Comprehensive test suite for ignore directive functionality in the stringly-typed
    linter. Tests line-level, block-level, file-level, and next-line ignore directives for
    both Python and TypeScript syntax. Verifies rule-specific vs general ignores, caching
    behavior, and integration with violation filtering. Uses temporary files and mock
    violations to test all ignore directive scenarios.

Dependencies: pytest, pathlib, tempfile, IgnoreChecker, Violation, Severity

Exports: Test functions for ignore directive functionality

Interfaces: pytest test discovery and execution

Implementation: pytest test functions with temporary file fixtures and assertion checks
"""

import tempfile
from pathlib import Path

import pytest

from src.core.types import Severity, Violation
from src.linters.stringly_typed.ignore_checker import IgnoreChecker


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def checker(temp_dir):
    """Create an IgnoreChecker with temp dir as project root."""
    return IgnoreChecker(project_root=temp_dir)


def _make_violation(
    file_path: str, line: int, rule_id: str = "stringly-typed.repeated-validation"
) -> Violation:
    """Create a test violation."""
    return Violation(
        rule_id=rule_id,
        file_path=file_path,
        line=line,
        column=0,
        message="Test violation message",
        severity=Severity.ERROR,
        suggestion="Test suggestion",
    )


class TestLineIgnore:
    """Tests for line-level ignore directives."""

    def test_line_ignore_filters_violation(self, temp_dir, checker):
        """Line-level ignore should filter the violation."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore[stringly-typed]
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=2)
        result = checker.filter_violations([violation])

        assert len(result) == 0

    def test_line_ignore_with_specific_rule(self, temp_dir, checker):
        """Line-level ignore with specific rule should filter matching violation."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore[stringly-typed.repeated-validation]
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=2)
        result = checker.filter_violations([violation])

        assert len(result) == 0

    def test_line_ignore_wrong_rule_keeps_violation(self, temp_dir, checker):
        """Line-level ignore with different rule should keep the violation."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore[other-rule]
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=2)
        result = checker.filter_violations([violation])

        assert len(result) == 1

    def test_line_ignore_without_brackets_filters_all(self, temp_dir, checker):
        """Line-level ignore without brackets should filter all rules."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore-all
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=2)
        result = checker.filter_violations([violation])

        assert len(result) == 0


class TestNextLineIgnore:
    """Tests for ignore-next-line directives."""

    def test_next_line_ignore_filters_violation(self, temp_dir, checker):
        """Ignore-next-line should filter the next line's violation."""
        code = """def check_status(s):
    # thailint: ignore-next-line
    if s in ("a", "b"):
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=3)
        result = checker.filter_violations([violation])

        assert len(result) == 0

    def test_next_line_ignore_with_rule(self, temp_dir, checker):
        """Ignore-next-line with specific rule should filter matching violation."""
        code = """def check_status(s):
    # thailint: ignore-next-line[stringly-typed]
    if s in ("a", "b"):
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=3)
        result = checker.filter_violations([violation])

        assert len(result) == 0

    def test_next_line_ignore_wrong_rule_keeps_violation(self, temp_dir, checker):
        """Ignore-next-line with different rule should keep the violation."""
        code = """def check_status(s):
    # thailint: ignore-next-line[other-rule]
    if s in ("a", "b"):
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=3)
        result = checker.filter_violations([violation])

        assert len(result) == 1


class TestFileIgnore:
    """Tests for file-level ignore directives."""

    def test_file_ignore_filters_all_violations(self, temp_dir, checker):
        """File-level ignore should filter all violations in the file."""
        code = """# thailint: ignore-file[stringly-typed]
def check_status(s):
    if s in ("a", "b"):
        return True

def check_env(e):
    if e in ("prod", "dev"):
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violations = [
            _make_violation(str(file_path), line=3),
            _make_violation(str(file_path), line=7),
        ]
        result = checker.filter_violations(violations)

        assert len(result) == 0

    def test_file_ignore_wildcard_filters_all_rules(self, temp_dir, checker):
        """File-level ignore with wildcard should filter all stringly-typed rules."""
        code = """# thailint: ignore-file[stringly-typed.*]
def check_status(s):
    if s in ("a", "b"):
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violations = [
            _make_violation(str(file_path), line=3, rule_id="stringly-typed.repeated-validation"),
            _make_violation(str(file_path), line=3, rule_id="stringly-typed.limited-values"),
        ]
        result = checker.filter_violations(violations)

        assert len(result) == 0

    def test_file_ignore_wrong_rule_keeps_violations(self, temp_dir, checker):
        """File-level ignore with different rule should keep violations."""
        code = """# thailint: ignore-file[other-rule]
def check_status(s):
    if s in ("a", "b"):
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=3)
        result = checker.filter_violations([violation])

        assert len(result) == 1


class TestBlockIgnore:
    """Tests for block-level ignore directives (ignore-start/ignore-end)."""

    def test_block_ignore_filters_violations_in_block(self, temp_dir, checker):
        """Block-level ignore should filter violations within the block."""
        code = """def check_status(s):
    # thailint: ignore-start stringly-typed
    if s in ("a", "b"):
        return True
    if s in ("c", "d"):
        return False
    # thailint: ignore-end
    pass
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violations = [
            _make_violation(str(file_path), line=3),
            _make_violation(str(file_path), line=5),
        ]
        result = checker.filter_violations(violations)

        assert len(result) == 0

    def test_block_ignore_keeps_violations_after_block(self, temp_dir, checker):
        """Block-level ignore should keep violations after the block ends."""
        code = """def check_status(s):
    # thailint: ignore-start stringly-typed
    if s in ("a", "b"):  # Line 3 - in block
        return True
    # thailint: ignore-end

def check_after(s):
    if s in ("m", "n"):  # Line 8 - after block
        pass
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violations = [
            _make_violation(str(file_path), line=3),  # Inside block
            _make_violation(str(file_path), line=8),  # After block
        ]
        result = checker.filter_violations(violations)

        assert len(result) == 1
        assert result[0].line == 8


class TestTypeScriptIgnore:
    """Tests for TypeScript-style ignore directives."""

    def test_typescript_line_ignore(self, temp_dir, checker):
        """TypeScript-style line ignore should filter violation."""
        code = """function checkEnv(env: string): boolean {
    if (!["a", "b"].includes(env)) {  // thailint: ignore[stringly-typed]
        return false;
    }
    return true;
}
"""
        file_path = temp_dir / "test.ts"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=2)
        result = checker.filter_violations([violation])

        assert len(result) == 0

    def test_typescript_file_ignore_with_hash_comment(self, temp_dir, checker):
        """File-level ignore uses # syntax even in TypeScript files."""
        # Note: The IgnoreDirectiveParser uses # for file-level ignores in all file types
        code = """# thailint: ignore-file[stringly-typed]
function checkEnv(env: string): boolean {
    if (!["a", "b"].includes(env)) {
        return false;
    }
    return true;
}
"""
        file_path = temp_dir / "test.ts"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=3)
        result = checker.filter_violations([violation])

        assert len(result) == 0


class TestWildcardRuleMatching:
    """Tests for wildcard rule matching in ignore directives."""

    def test_wildcard_matches_all_subrules(self, temp_dir, checker):
        """Wildcard pattern should match all sub-rules."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore[stringly-typed.*]
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violations = [
            _make_violation(str(file_path), line=2, rule_id="stringly-typed.repeated-validation"),
            _make_violation(str(file_path), line=2, rule_id="stringly-typed.limited-values"),
        ]
        result = checker.filter_violations(violations)

        assert len(result) == 0

    def test_prefix_matches_subrules(self, temp_dir, checker):
        """Prefix pattern should match sub-rules."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore[stringly-typed]
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(
            str(file_path), line=2, rule_id="stringly-typed.repeated-validation"
        )
        result = checker.filter_violations([violation])

        assert len(result) == 0


class TestCaching:
    """Tests for file content caching."""

    def test_cache_avoids_multiple_reads(self, temp_dir, checker):
        """Multiple checks on same file should use cache."""
        code = """def check_status(s):
    if s in ("a", "b"):
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violations = [
            _make_violation(str(file_path), line=2),
            _make_violation(str(file_path), line=2),
            _make_violation(str(file_path), line=2),
        ]

        # Should read file only once due to caching
        result = checker.filter_violations(violations)
        assert len(result) == 3

        # Cache should be populated
        assert str(file_path) in checker._file_content_cache

    def test_clear_cache(self, temp_dir, checker):
        """Cache clear should remove cached content."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore[stringly-typed]
        return True
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violation = _make_violation(str(file_path), line=2)
        checker.filter_violations([violation])

        assert str(file_path) in checker._file_content_cache

        checker.clear_cache()

        assert str(file_path) not in checker._file_content_cache


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_nonexistent_file_keeps_violation(self, temp_dir, checker):
        """Violation for non-existent file should be kept."""
        file_path = temp_dir / "nonexistent.py"

        violation = _make_violation(str(file_path), line=2)
        result = checker.filter_violations([violation])

        assert len(result) == 1

    def test_empty_violations_list(self, checker):
        """Empty violations list should return empty list."""
        result = checker.filter_violations([])
        assert result == []

    def test_file_with_encoding_error(self, temp_dir, checker):
        """File with encoding error should keep violation."""
        file_path = temp_dir / "test.py"
        # Write binary content that can't be decoded as UTF-8
        file_path.write_bytes(b"\x80\x81\x82")

        violation = _make_violation(str(file_path), line=1)
        result = checker.filter_violations([violation])

        assert len(result) == 1


class TestMultipleViolations:
    """Tests for filtering multiple violations."""

    def test_mixed_ignored_and_kept_violations(self, temp_dir, checker):
        """Mix of ignored and kept violations should filter correctly."""
        code = """def check_status(s):
    if s in ("a", "b"):  # thailint: ignore[stringly-typed]
        return True

def check_env(e):
    if e in ("prod", "dev"):  # No ignore directive
        return False
"""
        file_path = temp_dir / "test.py"
        file_path.write_text(code)

        violations = [
            _make_violation(str(file_path), line=2),  # Ignored
            _make_violation(str(file_path), line=6),  # Kept
        ]
        result = checker.filter_violations(violations)

        assert len(result) == 1
        assert result[0].line == 6

    def test_violations_from_multiple_files(self, temp_dir, checker):
        """Violations from multiple files should be filtered independently."""
        code1 = """# thailint: ignore-file[stringly-typed]
def check_status(s):
    if s in ("a", "b"):
        return True
"""
        code2 = """def check_env(e):
    if e in ("prod", "dev"):
        return False
"""
        file1 = temp_dir / "ignored.py"
        file2 = temp_dir / "not_ignored.py"
        file1.write_text(code1)
        file2.write_text(code2)

        violations = [
            _make_violation(str(file1), line=3),  # File-level ignore
            _make_violation(str(file2), line=2),  # No ignore
        ]
        result = checker.filter_violations(violations)

        assert len(result) == 1
        assert result[0].file_path == str(file2)
