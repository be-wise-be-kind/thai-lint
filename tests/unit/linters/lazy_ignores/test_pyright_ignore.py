"""
Purpose: Regression tests for pyright:ignore detection

Scope: Unit tests for issue #149 fix - detecting pyright:ignore comments

Overview: Tests that the lazy-ignores linter correctly detects pyright:ignore
    comments with and without rule IDs, matching the behavior of type:ignore.
"""

from pathlib import Path

import pytest

from src.linters.lazy_ignores.python_analyzer import PythonIgnoreDetector
from src.linters.lazy_ignores.types import IgnoreType


class TestPyrightIgnoreDetection:
    """Test pyright:ignore pattern detection (issue #149)."""

    @pytest.fixture
    def detector(self) -> PythonIgnoreDetector:
        """Create a PythonIgnoreDetector for testing."""
        return PythonIgnoreDetector()

    def test_detects_pyright_ignore_without_rule(self, detector: PythonIgnoreDetector) -> None:
        """Test detection of bare pyright: ignore comment."""
        code = "from langfuse.media import LangfuseMedia  # pyright: ignore"
        ignores = detector.find_ignores(code, Path("test.py"))

        assert len(ignores) == 1
        assert ignores[0].ignore_type == IgnoreType.PYRIGHT_IGNORE
        assert ignores[0].rule_ids == ()
        assert ignores[0].line == 1

    def test_detects_pyright_ignore_with_rule(self, detector: PythonIgnoreDetector) -> None:
        """Test detection of pyright: ignore with rule ID in brackets."""
        code = "from internal import _private  # pyright: ignore[reportPrivateImportUsage]"
        ignores = detector.find_ignores(code, Path("test.py"))

        assert len(ignores) == 1
        assert ignores[0].ignore_type == IgnoreType.PYRIGHT_IGNORE
        assert ignores[0].rule_ids == ("reportPrivateImportUsage",)
        assert ignores[0].line == 1

    def test_detects_pyright_ignore_with_multiple_rules(
        self, detector: PythonIgnoreDetector
    ) -> None:
        """Test detection of pyright: ignore with multiple rule IDs."""
        code = "x = foo()  # pyright: ignore[reportUnknownVariableType, reportUnusedVariable]"
        ignores = detector.find_ignores(code, Path("test.py"))

        assert len(ignores) == 1
        assert ignores[0].ignore_type == IgnoreType.PYRIGHT_IGNORE
        assert "reportUnknownVariableType" in ignores[0].rule_ids
        assert "reportUnusedVariable" in ignores[0].rule_ids

    def test_does_not_detect_pyright_in_string(self, detector: PythonIgnoreDetector) -> None:
        """Test that pyright: ignore inside strings is not detected."""
        code = 'message = "Use # pyright: ignore to suppress"'
        ignores = detector.find_ignores(code, Path("test.py"))

        assert len(ignores) == 0

    def test_detects_both_type_and_pyright_ignore(self, detector: PythonIgnoreDetector) -> None:
        """Test that both type:ignore and pyright:ignore are detected separately."""
        code = """
value1 = call1()  # type: ignore[arg-type]
value2 = call2()  # pyright: ignore[reportPrivateImportUsage]
"""
        ignores = detector.find_ignores(code, Path("test.py"))

        assert len(ignores) == 2
        types = {i.ignore_type for i in ignores}
        assert IgnoreType.TYPE_IGNORE in types
        assert IgnoreType.PYRIGHT_IGNORE in types
