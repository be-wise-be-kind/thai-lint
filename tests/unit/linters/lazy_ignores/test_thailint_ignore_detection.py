"""
Purpose: Tests for thai-lint ignore directive detection

Scope: Unit tests for detecting thailint:ignore, ignore-file, ignore-start/end, ignore-next-line

Overview: TDD test suite for thai-lint's own ignore directive detection. Tests inline ignores
    (thailint: ignore[rule]), file-level ignores (thailint: ignore-file[rule]), block ignores
    (thailint: ignore-start/ignore-end), and next-line ignores (thailint: ignore-next-line).
    All tests are marked as skip pending implementation.

Dependencies: pytest, src.linters.lazy_ignores

Exports: Test classes for thai-lint ignore detection

Interfaces: pytest test discovery and execution

Implementation: TDD tests marked as skip until implementation is complete
"""

import pytest


class TestThailintInlineIgnore:
    """Tests for # thailint: ignore[rule] detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_inline_ignore_with_rule(self) -> None:
        """Detects # thailint: ignore[magic-numbers]."""
        _code = "timeout = 3600  # thailint: ignore[magic-numbers]"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "magic-numbers" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_inline_ignore_multiple_rules(self) -> None:
        """Detects # thailint: ignore[srp,dry]."""
        _code = "class Handler:  # thailint: ignore[srp,dry]"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "srp" in directives[0].rule_ids
        # assert "dry" in directives[0].rule_ids

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_inline_ignore_with_comment(self) -> None:
        """Detects # thailint: ignore[magic-numbers] - with trailing comment."""
        _code = "timeout = 3600  # thailint: ignore[magic-numbers] - Industry standard"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1


class TestThailintFileIgnore:
    """Tests for # thailint: ignore-file[rule] detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_file_level_ignore(self) -> None:
        """Detects # thailint: ignore-file[magic-numbers]."""
        _code = "# thailint: ignore-file[magic-numbers]\n\nPORT = 8080"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE_FILE

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_file_ignore_multiple_rules(self) -> None:
        """Detects # thailint: ignore-file[rule1,rule2]."""
        _code = "# thailint: ignore-file[magic-numbers,file-header]"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1


class TestThailintBlockIgnore:
    """Tests for # thailint: ignore-start/ignore-end detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ignore_start(self) -> None:
        """Detects # thailint: ignore-start."""
        _code = """  # noqa: F841
# thailint: ignore-start
x = 1
y = 2
# thailint: ignore-end
"""
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 2  # start and end

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ignore_start_with_rule(self) -> None:
        """Detects # thailint: ignore-start[magic-numbers]."""
        _code = "# thailint: ignore-start[magic-numbers]"  # noqa: F841
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "magic-numbers" in directives[0].rule_ids


class TestThailintNextLineIgnore:
    """Tests for # thailint: ignore-next-line detection."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ignore_next_line(self) -> None:
        """Detects # thailint: ignore-next-line."""
        _code = """  # noqa: F841
# thailint: ignore-next-line
x = 3600
"""
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE_NEXT

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_ignore_next_line_with_rule(self) -> None:
        """Detects # thailint: ignore-next-line[magic-numbers]."""
        _code = """  # noqa: F841
# thailint: ignore-next-line[magic-numbers]
PORT = 8080
"""
        # detector = PythonIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
        # assert "magic-numbers" in directives[0].rule_ids


class TestThailintIgnoreInTypeScript:
    """Tests for thai-lint ignore detection in TypeScript files."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_inline_ignore_in_ts(self) -> None:
        """Detects // thailint: ignore[rule] in TypeScript."""
        _code = "const timeout = 3600;  // thailint: ignore[magic-numbers]"  # noqa: F841
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1

    @pytest.mark.skip(reason="TDD: Not yet implemented - lazy-ignores PR1")
    def test_detects_file_ignore_in_ts(self) -> None:
        """Detects // thailint: ignore-file[rule] in TypeScript."""
        _code = "// thailint: ignore-file[magic-numbers]"  # noqa: F841
        # detector = TypeScriptIgnoreDetector()
        # directives = detector.find_ignores(code)
        # assert len(directives) == 1
