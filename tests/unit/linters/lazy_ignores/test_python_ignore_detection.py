"""
Purpose: Tests for Python ignore pattern detection

Scope: Unit tests for detecting noqa, type:ignore, pylint:disable, nosec patterns

Overview: TDD test suite for Python ignore directive detection. Tests detection of bare
    and rule-specific noqa patterns, type:ignore with and without codes, pylint:disable
    directives, and nosec security suppressions. All tests are marked as skip pending
    implementation of PythonIgnoreDetector.

Dependencies: pytest, src.linters.lazy_ignores

Exports: Test classes for Python ignore detection

Interfaces: pytest test discovery and execution

Implementation: TDD tests marked as skip until implementation is complete
"""

import pytest


class TestNoqaDetection:
    """Tests for # noqa pattern detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_bare_noqa(self) -> None:
        """Detects # noqa without rule IDs."""
        _code = "x = 1  # noqa"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert directives[0].rule_ids == ()

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_noqa_with_single_rule(self) -> None:
        """Detects # noqa: PLR0912."""
        _code = "def complex():  # noqa: PLR0912"
        del _code  # TDD: will be used when implemented
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "PLR0912" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_noqa_with_multiple_rules(self) -> None:
        """Detects # noqa: PLR0912, PLR0915."""
        _code = "def complex():  # noqa: PLR0912, PLR0915"
        del _code  # TDD: will be used when implemented
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "PLR0912" in directives[0].rule_ids
        # assert "PLR0915" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_noqa_case_insensitive(self) -> None:
        """Detects # NOQA (uppercase)."""
        _code = "x = 1  # NOQA"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number."""
        _code = "\n\nx = 1  # noqa"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert directives[0].line == 3


class TestTypeIgnoreDetection:
    """Tests for # type: ignore detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_bare_type_ignore(self) -> None:
        """Detects # type: ignore."""
        _code = "x: int = 'string'  # type: ignore"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_type_ignore_with_code(self) -> None:
        """Detects # type: ignore[arg-type]."""
        _code = "foo(x)  # type: ignore[arg-type]"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "arg-type" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_type_ignore_with_multiple_codes(self) -> None:
        """Detects # type: ignore[arg-type, return-value]."""
        _code = "foo(x)  # type: ignore[arg-type, return-value]"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "arg-type" in directives[0].rule_ids
        # assert "return-value" in directives[0].rule_ids


class TestPylintDisableDetection:
    """Tests for # pylint: disable detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_pylint_disable(self) -> None:
        """Detects # pylint: disable=no-member."""
        _code = "obj.method()  # pylint: disable=no-member"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "no-member" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_pylint_disable_multiple_rules(self) -> None:
        """Detects # pylint: disable=no-member,unused-import."""
        _code = "import foo  # pylint: disable=no-member,unused-import"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "no-member" in directives[0].rule_ids
        # assert "unused-import" in directives[0].rule_ids


class TestNosecDetection:
    """Tests for # nosec detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_nosec_with_rule(self) -> None:
        """Detects # nosec B602."""
        _code = "subprocess.run(cmd, shell=True)  # nosec B602"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "B602" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_bare_nosec(self) -> None:
        """Detects # nosec without rule ID."""
        _code = "eval(code)  # nosec"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert directives[0].rule_ids == ()


class TestMultipleIgnoresPerFile:
    """Tests for detecting multiple ignores in a single file."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_multiple_ignores(self) -> None:
        """Detects multiple ignore patterns in one file."""
        _code = """  # noqa: F841
x = 1  # noqa
y: int = "str"  # type: ignore
z.method()  # pylint: disable=no-member
"""
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 3

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_ignores_comments_in_strings(self) -> None:
        """Does not detect ignores inside string literals."""
        _code = '''  # noqa: F841
docstring = """
This has # noqa in the string
"""
'''
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 0
