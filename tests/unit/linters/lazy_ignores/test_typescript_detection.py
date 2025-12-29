"""
Purpose: Tests for TypeScript/JavaScript ignore pattern detection

Scope: Unit tests for detecting @ts-ignore, @ts-nocheck, @ts-expect-error, eslint-disable

Overview: Test suite for TypeScript and JavaScript ignore directive detection. Tests
    detection of TypeScript-specific patterns (@ts-ignore, @ts-nocheck, @ts-expect-error)
    and ESLint disable patterns (eslint-disable-next-line, eslint-disable block comments).

Dependencies: pytest, src.linters.lazy_ignores

Exports: Test classes for TypeScript/JavaScript ignore detection

Interfaces: pytest test discovery and execution

Implementation: Tests verify pattern detection, rule extraction, and line number accuracy
"""

from src.linters.lazy_ignores.types import IgnoreType
from src.linters.lazy_ignores.typescript_analyzer import TypeScriptIgnoreDetector


class TestTsIgnoreDetection:
    """Tests for @ts-ignore detection."""

    def test_detects_ts_ignore(self) -> None:
        """Detects // @ts-ignore."""
        code = """// @ts-ignore
const x: number = "string";
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.TS_IGNORE

    def test_detects_ts_ignore_with_comment(self) -> None:
        """Detects // @ts-ignore with trailing comment."""
        code = "// @ts-ignore - Legacy API compatibility"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.TS_IGNORE


class TestTsNocheckDetection:
    """Tests for @ts-nocheck detection."""

    def test_detects_ts_nocheck(self) -> None:
        """Detects // @ts-nocheck at file level."""
        code = """// @ts-nocheck
const x = "untyped";
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.TS_NOCHECK


class TestTsExpectErrorDetection:
    """Tests for @ts-expect-error detection."""

    def test_detects_ts_expect_error(self) -> None:
        """Detects // @ts-expect-error."""
        code = """// @ts-expect-error - Testing error case
const x: number = "string";
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.TS_EXPECT_ERROR


class TestEslintDisableDetection:
    """Tests for eslint-disable detection."""

    def test_detects_eslint_disable_next_line(self) -> None:
        """Detects // eslint-disable-next-line."""
        code = """// eslint-disable-next-line no-console
console.log("debug");
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "no-console" in directives[0].rule_ids

    def test_detects_eslint_disable_block(self) -> None:
        """Detects /* eslint-disable */ block comment."""
        code = """/* eslint-disable no-console */
console.log("debug");
/* eslint-enable no-console */
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) >= 1
        # Should detect the eslint-disable, eslint-enable is not tracked

    def test_detects_eslint_disable_multiple_rules(self) -> None:
        """Detects // eslint-disable-next-line rule1, rule2."""
        code = "// eslint-disable-next-line no-console, no-debugger"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "no-console" in directives[0].rule_ids
        assert "no-debugger" in directives[0].rule_ids

    def test_detects_eslint_disable_inline(self) -> None:
        """Detects inline // eslint-disable-line."""
        code = 'console.log("debug"); // eslint-disable-line no-console'
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.ESLINT_DISABLE


class TestJavaScriptPatterns:
    """Tests for JavaScript-specific patterns."""

    def test_detects_patterns_in_js_file(self) -> None:
        """Detects ESLint patterns in .js files."""
        code = "// eslint-disable-next-line no-unused-vars"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code, file_path="test.js")
        assert len(directives) == 1

    def test_detects_patterns_in_jsx_file(self) -> None:
        """Detects patterns in .jsx files."""
        code = "// eslint-disable-next-line react/prop-types"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code, file_path="Component.jsx")
        assert len(directives) == 1
        assert "react/prop-types" in directives[0].rule_ids


class TestMultiplePatterns:
    """Tests for multiple TypeScript/JavaScript patterns."""

    def test_detects_mixed_patterns(self) -> None:
        """Detects multiple different ignore patterns in one file."""
        code = """// @ts-ignore
const x: number = "string";

// eslint-disable-next-line no-console
console.log(x);

// @ts-expect-error
const y: string = 123;
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 3

    def test_correct_line_numbers(self) -> None:
        """Returns correct line numbers for each pattern."""
        code = """// line 1
// @ts-ignore
const x = 1;
// line 4
// eslint-disable-next-line no-console
console.log(x);
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        ts_ignore = [d for d in directives if d.ignore_type == IgnoreType.TS_IGNORE][0]
        assert ts_ignore.line == 2


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_code(self) -> None:
        """Handles empty code gracefully."""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores("")
        assert len(directives) == 0

    def test_no_patterns(self) -> None:
        """Returns empty list when no patterns found."""
        code = """const x = 1;
const y = 2;
console.log(x + y);
"""
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 0

    def test_preserves_raw_text(self) -> None:
        """Preserves the original raw text of the pattern."""
        code = "// @ts-ignore"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert "ts-ignore" in directives[0].raw_text.lower()

    def test_eslint_disable_no_rules(self) -> None:
        """Handles eslint-disable without specific rules."""
        code = "// eslint-disable-next-line"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].rule_ids == ()

    def test_block_comment_with_rules(self) -> None:
        """Handles block comment eslint-disable with rules."""
        code = "/* eslint-disable no-console, no-alert */"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "no-console" in directives[0].rule_ids
        assert "no-alert" in directives[0].rule_ids
