"""
Purpose: Tests for thai-lint ignore directive detection

Scope: Unit tests for detecting thailint:ignore, ignore-file, ignore-start/end, ignore-next-line

Overview: Test suite for thai-lint's own ignore directive detection. Tests inline ignores
    (thailint: ignore[rule]), file-level ignores (thailint: ignore-file[rule]), block ignores
    (thailint: ignore-start/ignore-end), and next-line ignores (thailint: ignore-next-line).

Dependencies: pytest, src.linters.lazy_ignores

Exports: Test classes for thai-lint ignore detection

Interfaces: pytest test discovery and execution

Implementation: Tests verify regex patterns correctly detect thai-lint ignore directives
"""

from pathlib import Path

from src.linters.lazy_ignores.python_analyzer import PythonIgnoreDetector
from src.linters.lazy_ignores.types import IgnoreType
from src.linters.lazy_ignores.typescript_analyzer import TypeScriptIgnoreDetector


class TestThailintInlineIgnore:
    """Tests for # thailint: ignore[rule] detection."""

    def test_detects_inline_ignore_with_rule(self) -> None:
        """Detects # thailint: ignore[magic-numbers]."""
        code = "timeout = 3600  # thailint: ignore[magic-numbers]"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE
        assert "magic-numbers" in directives[0].rule_ids

    def test_detects_inline_ignore_multiple_rules(self) -> None:
        """Detects # thailint: ignore[srp,dry]."""
        code = "class Handler:  # thailint: ignore[srp,dry]"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1
        assert "srp" in directives[0].rule_ids
        assert "dry" in directives[0].rule_ids

    def test_detects_inline_ignore_with_comment(self) -> None:
        """Detects # thailint: ignore[magic-numbers] - with trailing comment."""
        code = "timeout = 3600  # thailint: ignore[magic-numbers] - Industry standard"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1


class TestThailintFileIgnore:
    """Tests for # thailint: ignore-file[rule] detection."""

    def test_detects_file_level_ignore(self) -> None:
        """Detects # thailint: ignore-file[magic-numbers]."""
        code = "# thailint: ignore-file[magic-numbers]\n\nPORT = 8080"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE_FILE

    def test_detects_file_ignore_multiple_rules(self) -> None:
        """Detects # thailint: ignore-file[rule1,rule2]."""
        code = "# thailint: ignore-file[magic-numbers,file-header]"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1
        assert "magic-numbers" in directives[0].rule_ids
        assert "file-header" in directives[0].rule_ids


class TestThailintBlockIgnore:
    """Tests for # thailint: ignore-start/ignore-end detection."""

    def test_detects_ignore_start(self) -> None:
        """Detects # thailint: ignore-start."""
        code = """# thailint: ignore-start
x = 1
y = 2
# thailint: ignore-end
"""
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        # Only detects ignore-start (ignore-end is not a pattern we track)
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE_BLOCK

    def test_detects_ignore_start_with_rule(self) -> None:
        """Detects # thailint: ignore-start[magic-numbers]."""
        code = "# thailint: ignore-start[magic-numbers]"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1
        assert "magic-numbers" in directives[0].rule_ids


class TestThailintNextLineIgnore:
    """Tests for # thailint: ignore-next-line detection."""

    def test_detects_ignore_next_line(self) -> None:
        """Detects # thailint: ignore-next-line."""
        code = """# thailint: ignore-next-line
x = 3600
"""
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE_NEXT

    def test_detects_ignore_next_line_with_rule(self) -> None:
        """Detects # thailint: ignore-next-line[magic-numbers]."""
        code = """# thailint: ignore-next-line[magic-numbers]
PORT = 8080
"""
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.py"))
        assert len(directives) == 1
        assert "magic-numbers" in directives[0].rule_ids


class TestThailintIgnoreInTypeScript:
    """Tests for thai-lint ignore detection in TypeScript files."""

    def test_detects_inline_ignore_in_ts(self) -> None:
        """Detects // thailint: ignore[rule] in TypeScript."""
        code = "const timeout = 3600;  // thailint: ignore[magic-numbers]"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.ts"))
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE

    def test_detects_file_ignore_in_ts(self) -> None:
        """Detects // thailint: ignore-file[rule] in TypeScript."""
        code = "// thailint: ignore-file[magic-numbers]"
        detector = TypeScriptIgnoreDetector()
        directives = detector.find_ignores(code, Path("test.ts"))
        assert len(directives) == 1
        assert directives[0].ignore_type == IgnoreType.THAILINT_IGNORE_FILE
