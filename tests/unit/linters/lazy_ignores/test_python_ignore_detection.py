"""
Purpose: Tests for Python ignore pattern detection

Scope: Unit tests for detecting noqa, type:ignore, pylint:disable, nosec patterns

Overview: Test suite for Python ignore directive detection. Tests detection of bare
    and rule-specific noqa patterns, type:ignore with and without codes, pylint:disable
    directives, and nosec security suppressions.

Dependencies: pytest, src.linters.lazy_ignores.python_analyzer

Exports: Test classes for Python ignore detection

Interfaces: pytest test discovery and execution

Implementation: Unit tests using PythonIgnoreDetector
"""

from src.linters.lazy_ignores.python_analyzer import PythonIgnoreDetector
from src.linters.lazy_ignores.types import IgnoreType


class TestNoqaDetection:
    """Tests for # noqa pattern detection."""

    def test_detects_bare_noqa(self) -> None:
        """Detects # noqa without rule IDs."""
        code = "x = 1  # noqa"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.NOQA
        assert directives[0].rule_ids == ()

    def test_detects_noqa_with_single_rule(self) -> None:
        """Detects # noqa: PLR0912."""
        code = "def complex():  # noqa: PLR0912"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "PLR0912" in directives[0].rule_ids

    def test_detects_noqa_with_multiple_rules(self) -> None:
        """Detects # noqa: PLR0912, PLR0915."""
        code = "def complex():  # noqa: PLR0912, PLR0915"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "PLR0912" in directives[0].rule_ids
        assert "PLR0915" in directives[0].rule_ids

    def test_detects_noqa_case_insensitive(self) -> None:
        """Detects # NOQA (uppercase)."""
        code = "x = 1  # NOQA"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.NOQA

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number."""
        code = "\n\nx = 1  # noqa"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert directives[0].line == 3


class TestTypeIgnoreDetection:
    """Tests for # type: ignore detection."""

    def test_detects_bare_type_ignore(self) -> None:
        """Detects # type: ignore."""
        code = "x: int = 'string'  # type: ignore"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.TYPE_IGNORE

    def test_detects_type_ignore_with_code(self) -> None:
        """Detects # type: ignore[arg-type]."""
        code = "foo(x)  # type: ignore[arg-type]"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "arg-type" in directives[0].rule_ids

    def test_detects_type_ignore_with_multiple_codes(self) -> None:
        """Detects # type: ignore[arg-type, return-value]."""
        code = "foo(x)  # type: ignore[arg-type, return-value]"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "arg-type" in directives[0].rule_ids
        assert "return-value" in directives[0].rule_ids


class TestPylintDisableDetection:
    """Tests for # pylint: disable detection."""

    def test_detects_pylint_disable(self) -> None:
        """Detects # pylint: disable=no-member."""
        code = "obj.method()  # pylint: disable=no-member"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.PYLINT_DISABLE
        assert "no-member" in directives[0].rule_ids

    def test_detects_pylint_disable_multiple_rules(self) -> None:
        """Detects # pylint: disable=no-member,unused-import."""
        code = "import foo  # pylint: disable=no-member,unused-import"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "no-member" in directives[0].rule_ids
        assert "unused-import" in directives[0].rule_ids


class TestNosecDetection:
    """Tests for # nosec detection."""

    def test_detects_nosec_with_rule(self) -> None:
        """Detects # nosec B602."""
        code = "subprocess.run(cmd, shell=True)  # nosec B602"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.NOSEC
        assert "B602" in directives[0].rule_ids

    def test_detects_bare_nosec(self) -> None:
        """Detects # nosec without rule ID."""
        code = "eval(code)  # nosec"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].rule_ids == ()


class TestMultipleIgnoresPerFile:
    """Tests for detecting multiple ignores in a single file."""

    def test_detects_multiple_ignores(self) -> None:
        """Detects multiple ignore patterns in one file."""
        code = """
x = 1  # noqa
y: int = "str"  # type: ignore
z.method()  # pylint: disable=no-member
"""
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 3

    def test_detects_ignores_on_correct_lines(self) -> None:
        """Returns correct line numbers for each ignore."""
        code = """line1
x = 1  # noqa
line3
y = 2  # type: ignore
"""
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 2
        assert directives[0].line == 2
        assert directives[1].line == 4
