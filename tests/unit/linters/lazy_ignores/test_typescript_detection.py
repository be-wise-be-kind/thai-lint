"""
Purpose: Tests for TypeScript/JavaScript ignore pattern detection

Scope: Unit tests for detecting @ts-ignore, @ts-nocheck, @ts-expect-error, eslint-disable

Overview: TDD test suite for TypeScript and JavaScript ignore directive detection. Tests
    detection of TypeScript-specific patterns (@ts-ignore, @ts-nocheck, @ts-expect-error)
    and ESLint disable patterns (eslint-disable-next-line, eslint-disable block comments).
    All tests are marked as skip pending implementation.

Dependencies: pytest, src.linters.lazy_ignores

Exports: Test classes for TypeScript/JavaScript ignore detection

Interfaces: pytest test discovery and execution

Implementation: TDD tests marked as skip until implementation is complete
"""

import pytest


class TestTsIgnoreDetection:
    """Tests for @ts-ignore detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ts_ignore(self) -> None:
        """Detects // @ts-ignore."""
        _code = """  # noqa: F841
// @ts-ignore
const x: number = "string";
"""
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert directives[0].ignore_type == IgnoreType.TS_IGNORE

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ts_ignore_with_comment(self) -> None:
        """Detects // @ts-ignore with trailing comment."""
        _code = "// @ts-ignore - Legacy API compatibility"  # noqa: F841
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1


class TestTsNocheckDetection:
    """Tests for @ts-nocheck detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ts_nocheck(self) -> None:
        """Detects // @ts-nocheck at file level."""
        _code = """// @ts-nocheck  # noqa: F841
const x = "untyped";
"""
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert directives[0].ignore_type == IgnoreType.TS_NOCHECK


class TestTsExpectErrorDetection:
    """Tests for @ts-expect-error detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ts_expect_error(self) -> None:
        """Detects // @ts-expect-error."""
        _code = """  # noqa: F841
// @ts-expect-error - Testing error case
const x: number = "string";
"""
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert directives[0].ignore_type == IgnoreType.TS_EXPECT_ERROR


class TestEslintDisableDetection:
    """Tests for eslint-disable detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_eslint_disable_next_line(self) -> None:
        """Detects // eslint-disable-next-line."""
        _code = """  # noqa: F841
// eslint-disable-next-line no-console
console.log("debug");
"""
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "no-console" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_eslint_disable_block(self) -> None:
        """Detects /* eslint-disable */ block comment."""
        _code = """  # noqa: F841
/* eslint-disable no-console */
console.log("debug");
/* eslint-enable no-console */
"""
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) >= 1

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_eslint_disable_multiple_rules(self) -> None:
        """Detects // eslint-disable-next-line rule1, rule2."""
        _code = "// eslint-disable-next-line no-console, no-debugger"  # noqa: F841
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "no-console" in directives[0].rule_ids
        # assert "no-debugger" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_eslint_disable_inline(self) -> None:
        """Detects inline // eslint-disable-line."""
        _code = 'console.log("debug"); // eslint-disable-line no-console'  # noqa: F841
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1


class TestJavaScriptPatterns:
    """Tests for JavaScript-specific patterns."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_patterns_in_js_file(self) -> None:
        """Detects ESLint patterns in .js files."""
        _code = "// eslint-disable-next-line no-unused-vars"  # noqa: F841
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code, file_path="test.js")
        # assert len(directives) == 1

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_patterns_in_jsx_file(self) -> None:
        """Detects patterns in .jsx files."""
        _code = "// eslint-disable-next-line react/prop-types"  # noqa: F841
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code, file_path="Component.jsx")
        # assert len(directives) == 1


class TestMultiplePatterns:
    """Tests for multiple TypeScript/JavaScript patterns."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_mixed_patterns(self) -> None:
        """Detects multiple different ignore patterns in one file."""
        _code = """  # noqa: F841
// @ts-ignore
const x: number = "string";

// eslint-disable-next-line no-console
console.log(x);

// @ts-expect-error
const y: string = 123;
"""
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 3

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_correct_line_numbers(self) -> None:
        """Returns correct line numbers for each pattern."""
        _code = """// line 1  # noqa: F841
// @ts-ignore
const x = 1;
// line 4
// eslint-disable-next-line no-console
console.log(x);
"""
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # ts_ignore = [d for d in directives if d.ignore_type == IgnoreType.TS_IGNORE][0]
        # assert ts_ignore.line == 2
