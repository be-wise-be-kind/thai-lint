"""
Purpose: Tests for test skip pattern detection in the lazy-ignores linter

Scope: pytest.mark.skip, pytest.skip(), it.skip(), describe.skip() detection

Overview: Comprehensive tests for TestSkipDetector covering Python pytest patterns and
    JavaScript/TypeScript test framework skip patterns. Tests validate that unjustified
    skips are detected while properly justified skips with reason arguments are allowed.
    Includes tests for edge cases like multi-line decorators and various skip styles.

Dependencies: pytest, TestSkipDetector, IgnoreType

Exports: Test classes for pytest and JavaScript skip detection

Interfaces: Standard pytest test methods

Implementation: Unit tests with parametrized inputs for comprehensive coverage
"""

from pathlib import Path

import pytest

from src.linters.lazy_ignores.skip_detector import TestSkipDetector
from src.linters.lazy_ignores.types import IgnoreType


class TestPytestSkipDetection:
    """Tests for Python pytest skip pattern detection."""

    @pytest.fixture
    def detector(self) -> TestSkipDetector:
        """Create a TestSkipDetector instance."""
        return TestSkipDetector()

    def test_detects_bare_pytest_mark_skip(self, detector: TestSkipDetector) -> None:
        """Detects @pytest.mark.skip without any arguments."""
        code = """
@pytest.mark.skip
def test_something():
    pass
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.PYTEST_SKIP

    def test_detects_pytest_mark_skip_empty_parens(self, detector: TestSkipDetector) -> None:
        """Detects @pytest.mark.skip() with empty parentheses."""
        code = """
@pytest.mark.skip()
def test_something():
    pass
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.PYTEST_SKIP

    def test_detects_bare_pytest_skip_call(self, detector: TestSkipDetector) -> None:
        """Detects pytest.skip() without any arguments."""
        code = """
def test_something():
    pytest.skip()
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.PYTEST_SKIP

    def test_allows_pytest_mark_skip_with_reason(self, detector: TestSkipDetector) -> None:
        """Allows @pytest.mark.skip(reason='...') - properly justified."""
        code = """
@pytest.mark.skip(reason="Not implemented yet")
def test_something():
    pass
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 0

    def test_allows_pytest_mark_skipif_with_reason(self, detector: TestSkipDetector) -> None:
        """Allows @pytest.mark.skipif(..., reason='...') - properly justified."""
        code = """
@pytest.mark.skipif(sys.platform == "win32", reason="Windows not supported")
def test_something():
    pass
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 0

    def test_allows_pytest_skip_with_message(self, detector: TestSkipDetector) -> None:
        """Allows pytest.skip('message') - properly justified."""
        code = """
def test_something():
    pytest.skip("Feature not available")
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 0

    def test_allows_pytest_skip_with_reason_kwarg(self, detector: TestSkipDetector) -> None:
        """Allows pytest.skip(reason='...') - properly justified."""
        code = """
def test_something():
    pytest.skip(reason="Skipping for now")
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 0

    def test_returns_correct_line_number(self, detector: TestSkipDetector) -> None:
        """Reports correct line number for detected skip."""
        code = """# line 1
# line 2
@pytest.mark.skip
def test_something():
    pass
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 1
        assert directives[0].line == 3

    def test_returns_correct_column(self, detector: TestSkipDetector) -> None:
        """Reports correct column for detected skip."""
        code = "@pytest.mark.skip\ndef test(): pass"
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 1
        assert directives[0].column == 1

    def test_handles_indented_decorator(self, detector: TestSkipDetector) -> None:
        """Detects skip decorator with indentation."""
        code = """
class TestClass:
    @pytest.mark.skip
    def test_method(self):
        pass
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 1

    def test_multiple_skips_in_file(self, detector: TestSkipDetector) -> None:
        """Detects multiple skip patterns in same file."""
        code = """
@pytest.mark.skip
def test_one():
    pass

@pytest.mark.skip()
def test_two():
    pass

def test_three():
    pytest.skip()
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 3


class TestJavaScriptSkipDetection:
    """Tests for JavaScript/TypeScript test skip pattern detection."""

    @pytest.fixture
    def detector(self) -> TestSkipDetector:
        """Create a TestSkipDetector instance."""
        return TestSkipDetector()

    def test_detects_it_skip(self, detector: TestSkipDetector) -> None:
        """Detects it.skip('...') pattern."""
        code = """
it.skip('should do something', () => {
    expect(true).toBe(true);
});
"""
        directives = detector.find_skips(code, language="javascript")
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.JEST_SKIP

    def test_detects_test_skip(self, detector: TestSkipDetector) -> None:
        """Detects test.skip('...') pattern."""
        code = """
test.skip('should do something', () => {
    expect(true).toBe(true);
});
"""
        directives = detector.find_skips(code, language="javascript")
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.JEST_SKIP

    def test_detects_describe_skip(self, detector: TestSkipDetector) -> None:
        """Detects describe.skip('...') pattern."""
        code = """
describe.skip('Test Suite', () => {
    it('should pass', () => {
        expect(true).toBe(true);
    });
});
"""
        directives = detector.find_skips(code, language="javascript")
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.MOCHA_SKIP

    def test_typescript_skip_detection(self, detector: TestSkipDetector) -> None:
        """Detects skip patterns in TypeScript code."""
        code = """
it.skip('typed test', (): void => {
    const result: number = 1;
    expect(result).toBe(1);
});
"""
        directives = detector.find_skips(code, language="typescript")
        assert len(directives) == 1

    def test_multiple_js_skips(self, detector: TestSkipDetector) -> None:
        """Detects multiple skip patterns in same file."""
        code = """
describe.skip('Suite 1', () => {
    it('test 1', () => {});
});

it.skip('standalone test', () => {});

test.skip('another test', () => {});
"""
        directives = detector.find_skips(code, language="javascript")
        assert len(directives) == 3

    def test_returns_correct_line_for_js(self, detector: TestSkipDetector) -> None:
        """Reports correct line number for JS skip."""
        code = """// line 1
// line 2
it.skip('test', () => {});
"""
        directives = detector.find_skips(code, language="javascript")
        assert len(directives) == 1
        assert directives[0].line == 3


class TestFilePathHandling:
    """Tests for file path handling in TestSkipDetector."""

    @pytest.fixture
    def detector(self) -> TestSkipDetector:
        """Create a TestSkipDetector instance."""
        return TestSkipDetector()

    def test_accepts_path_object(self, detector: TestSkipDetector) -> None:
        """Accepts Path object for file_path."""
        code = "@pytest.mark.skip\ndef test(): pass"
        path = Path("/some/test.py")
        directives = detector.find_skips(code, file_path=path, language="python")
        assert len(directives) == 1
        assert directives[0].file_path == path

    def test_accepts_string_path(self, detector: TestSkipDetector) -> None:
        """Accepts string for file_path."""
        code = "@pytest.mark.skip\ndef test(): pass"
        directives = detector.find_skips(code, file_path="/some/test.py", language="python")
        assert len(directives) == 1
        assert directives[0].file_path == Path("/some/test.py")

    def test_accepts_none_path(self, detector: TestSkipDetector) -> None:
        """Uses 'unknown' for None file_path."""
        code = "@pytest.mark.skip\ndef test(): pass"
        directives = detector.find_skips(code, file_path=None, language="python")
        assert len(directives) == 1
        assert directives[0].file_path == Path("unknown")


class TestEdgeCases:
    """Tests for edge cases in test skip detection."""

    @pytest.fixture
    def detector(self) -> TestSkipDetector:
        """Create a TestSkipDetector instance."""
        return TestSkipDetector()

    def test_empty_code(self, detector: TestSkipDetector) -> None:
        """Returns empty list for empty code."""
        directives = detector.find_skips("", language="python")
        assert directives == []

    def test_code_without_skips(self, detector: TestSkipDetector) -> None:
        """Returns empty list for code without skip patterns."""
        code = """
def test_something():
    assert True
"""
        directives = detector.find_skips(code, language="python")
        assert directives == []

    def test_skip_in_comment_not_detected(self, detector: TestSkipDetector) -> None:
        """Does not detect skip patterns in comments."""
        code = """
# @pytest.mark.skip
def test_something():
    pass
"""
        directives = detector.find_skips(code, language="python")
        # The comment line starts with #, so our regex won't match the @
        assert len(directives) == 0

    def test_skip_in_string_literal_not_detected(self, detector: TestSkipDetector) -> None:
        """Does NOT detect skip patterns inside string literals."""
        code = """
def test_something():
    code = "@pytest.mark.skip"
    assert True
"""
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 0

    def test_skip_in_docstring_not_detected(self, detector: TestSkipDetector) -> None:
        """Does NOT detect skip patterns mentioned in docstrings."""
        code = '''"""
Purpose: Test skip detector for pytest.skip() and @pytest.mark.skip patterns
"""
def test_something():
    pass
'''
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 0

    def test_skip_description_in_docstring_not_detected(self, detector: TestSkipDetector) -> None:
        """Does NOT detect skip pattern descriptions in docstrings."""
        code = '''"""
Scope: pytest.mark.skip, pytest.skip(), it.skip(), describe.skip() detection
"""
def test_something():
    pass
'''
        directives = detector.find_skips(code, language="python")
        assert len(directives) == 0
