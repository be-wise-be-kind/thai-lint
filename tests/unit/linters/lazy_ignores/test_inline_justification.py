"""
Purpose: Tests for inline justification support in lazy-ignores linter

Scope: Unit tests for inline justification extraction, validation, and precedence

Overview: Test suite for inline justification feature (Issue #147). Tests extraction of
    justification text after ` - ` delimiter, minimum length validation, precedence rules
    (inline justification takes precedence over header), and support across all ignore types.

Dependencies: pytest, src.linters.lazy_ignores modules

Exports: Test classes for inline justification functionality

Interfaces: pytest test discovery and execution

Implementation: TDD-style tests written before implementation
"""

from pathlib import Path

import pytest

from src.linters.lazy_ignores.config import LazyIgnoresConfig
from src.linters.lazy_ignores.directive_utils import (
    extract_inline_justification,
)
from src.linters.lazy_ignores.header_parser import SuppressionsParser
from src.linters.lazy_ignores.matcher import IgnoreSuppressionMatcher
from src.linters.lazy_ignores.python_analyzer import PythonIgnoreDetector
from src.linters.lazy_ignores.types import IgnoreDirective, IgnoreType


class TestExtractInlineJustification:
    """Tests for extract_inline_justification utility function."""

    def test_extracts_justification_after_delimiter(self) -> None:
        """Should extract justification text after ` - ` delimiter."""
        raw_text = "# noqa: PLR0912 - state machine inherently complex"
        result = extract_inline_justification(raw_text)
        assert result == "state machine inherently complex"

    def test_returns_none_when_no_delimiter(self) -> None:
        """Should return None when no ` - ` delimiter present."""
        raw_text = "# noqa: PLR0912"
        result = extract_inline_justification(raw_text)
        assert result is None

    def test_handles_multiple_dashes(self) -> None:
        """Should use first ` - ` delimiter when multiple present."""
        raw_text = "# type: ignore[arg-type] - library typing bug - known issue"
        result = extract_inline_justification(raw_text)
        assert result == "library typing bug - known issue"

    def test_handles_dash_without_spaces(self) -> None:
        """Should NOT match dashes without spaces (like arg-type)."""
        raw_text = "# type: ignore[arg-type]"
        result = extract_inline_justification(raw_text)
        assert result is None

    def test_strips_whitespace_from_justification(self) -> None:
        """Should strip leading/trailing whitespace from justification."""
        raw_text = "# noqa: PLR0912 -   extra spaces around   "
        result = extract_inline_justification(raw_text)
        assert result == "extra spaces around"

    def test_handles_empty_justification_after_delimiter(self) -> None:
        """Should return empty string when only whitespace after delimiter."""
        raw_text = "# noqa: PLR0912 -   "
        result = extract_inline_justification(raw_text)
        # Could be None or empty string - implementation decides
        assert result is None or result == ""


class TestIgnoreDirectiveWithInlineJustification:
    """Tests for IgnoreDirective inline_justification field."""

    def test_directive_has_inline_justification_field(self) -> None:
        """IgnoreDirective should have inline_justification field."""
        directive = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912 - test justification",
            file_path=Path("test.py"),
            inline_justification="test justification",
        )
        assert directive.inline_justification == "test justification"

    def test_directive_inline_justification_defaults_to_none(self) -> None:
        """IgnoreDirective inline_justification should default to None."""
        directive = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912",
            file_path=Path("test.py"),
        )
        assert directive.inline_justification is None


class TestPythonDetectorInlineJustification:
    """Tests for Python detector extracting inline justifications."""

    def test_detects_noqa_with_inline_justification(self) -> None:
        """Detector should extract inline justification from noqa comment."""
        code = "def complex():  # noqa: PLR0912 - state machine inherently complex"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].inline_justification == "state machine inherently complex"

    def test_detects_type_ignore_with_inline_justification(self) -> None:
        """Detector should extract inline justification from type:ignore comment."""
        code = "foo(x)  # type: ignore[arg-type] - library has typing bug"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].inline_justification == "library has typing bug"

    def test_detects_pylint_disable_with_inline_justification(self) -> None:
        """Detector should extract inline justification from pylint:disable comment."""
        code = "obj.method()  # pylint: disable=no-member - dynamically added attribute"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].inline_justification == "dynamically added attribute"

    def test_detects_nosec_with_inline_justification(self) -> None:
        """Detector should extract inline justification from nosec comment."""
        code = "subprocess.run(cmd, shell=True)  # nosec B602 - command from trusted config"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].inline_justification == "command from trusted config"

    def test_no_inline_justification_when_absent(self) -> None:
        """Detector should return None when no inline justification present."""
        code = "def complex():  # noqa: PLR0912"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].inline_justification is None


class TestLazyIgnoresConfigInlineOptions:
    """Tests for inline justification configuration options."""

    def test_config_has_allow_inline_justifications_option(self) -> None:
        """Config should have allow_inline_justifications option."""
        config = LazyIgnoresConfig()
        assert hasattr(config, "allow_inline_justifications")
        assert config.allow_inline_justifications is True  # Default to True

    def test_config_has_min_justification_length_option(self) -> None:
        """Config should have min_justification_length option."""
        config = LazyIgnoresConfig()
        assert hasattr(config, "min_justification_length")
        assert config.min_justification_length == 10  # Default to 10

    def test_config_from_dict_loads_inline_options(self) -> None:
        """Config.from_dict should load inline justification options."""
        config_dict = {
            "allow_inline_justifications": False,
            "min_justification_length": 20,
        }
        config = LazyIgnoresConfig.from_dict(config_dict)
        assert config.allow_inline_justifications is False
        assert config.min_justification_length == 20


class TestMatcherInlineJustificationPrecedence:
    """Tests for inline justification precedence in matcher."""

    def test_inline_justification_makes_rule_justified(self) -> None:
        """Inline justification should make rule ID justified (no violation)."""
        parser = SuppressionsParser()
        matcher = IgnoreSuppressionMatcher(parser)

        ignore = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912 - complex state machine",
            file_path=Path("test.py"),
            inline_justification="complex state machine",
        )

        # No header suppressions
        suppressions: dict[str, str] = {}
        unjustified = matcher.find_unjustified_rule_ids(ignore, suppressions)
        assert unjustified == []

    def test_inline_justification_takes_precedence_over_header(self) -> None:
        """Inline justification should take precedence over header."""
        parser = SuppressionsParser()
        matcher = IgnoreSuppressionMatcher(parser)

        ignore = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912 - different reason",
            file_path=Path("test.py"),
            inline_justification="different reason",
        )

        # Header has different justification
        suppressions = {"plr0912": "header reason"}
        unjustified = matcher.find_unjustified_rule_ids(ignore, suppressions)
        assert unjustified == []  # Inline justification is sufficient

    def test_header_still_works_without_inline(self) -> None:
        """Header suppression should still work when no inline justification."""
        parser = SuppressionsParser()
        matcher = IgnoreSuppressionMatcher(parser)

        ignore = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912",
            file_path=Path("test.py"),
            inline_justification=None,
        )

        # Header has suppression
        suppressions = {"plr0912": "header reason"}
        unjustified = matcher.find_unjustified_rule_ids(ignore, suppressions)
        assert unjustified == []

    def test_violation_when_neither_inline_nor_header(self) -> None:
        """Should report violation when neither inline nor header justification."""
        parser = SuppressionsParser()
        matcher = IgnoreSuppressionMatcher(parser)

        ignore = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912",
            file_path=Path("test.py"),
            inline_justification=None,
        )

        # No header suppressions
        suppressions: dict[str, str] = {}
        unjustified = matcher.find_unjustified_rule_ids(ignore, suppressions)
        assert unjustified == ["PLR0912"]


class TestMinimumJustificationLength:
    """Tests for minimum justification length validation."""

    def test_short_justification_not_valid(self) -> None:
        """Justification shorter than min_length should not be valid."""
        parser = SuppressionsParser()
        matcher = IgnoreSuppressionMatcher(parser, min_justification_length=10)

        ignore = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912 - ok",
            file_path=Path("test.py"),
            inline_justification="ok",  # Too short (2 chars < 10)
        )

        suppressions: dict[str, str] = {}
        unjustified = matcher.find_unjustified_rule_ids(ignore, suppressions)
        assert unjustified == ["PLR0912"]  # Not justified due to short length

    def test_long_enough_justification_is_valid(self) -> None:
        """Justification meeting min_length should be valid."""
        parser = SuppressionsParser()
        matcher = IgnoreSuppressionMatcher(parser, min_justification_length=10)

        ignore = IgnoreDirective(
            ignore_type=IgnoreType.NOQA,
            rule_ids=("PLR0912",),
            line=1,
            column=1,
            raw_text="# noqa: PLR0912 - this is long enough",
            file_path=Path("test.py"),
            inline_justification="this is long enough",  # 19 chars >= 10
        )

        suppressions: dict[str, str] = {}
        unjustified = matcher.find_unjustified_rule_ids(ignore, suppressions)
        assert unjustified == []


class TestAllIgnoreTypesSupportInlineJustification:
    """Tests that all ignore types support inline justification."""

    @pytest.mark.parametrize(
        "code,expected_type",
        [
            ("x = 1  # noqa: E501 - line length acceptable", IgnoreType.NOQA),
            (
                "x: int = 'str'  # type: ignore[assignment] - pydantic validates",
                IgnoreType.TYPE_IGNORE,
            ),
            (
                "obj.attr  # pylint: disable=no-member - dynamic attr",
                IgnoreType.PYLINT_DISABLE,
            ),
            ("eval(x)  # nosec B307 - input sanitized", IgnoreType.NOSEC),
            (
                "from mod import x  # pyright: ignore[reportMissing] - optional dep",
                IgnoreType.PYRIGHT_IGNORE,
            ),
        ],
    )
    def test_ignore_type_supports_inline_justification(
        self, code: str, expected_type: IgnoreType
    ) -> None:
        """All Python ignore types should support inline justification."""
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].ignore_type == expected_type
        assert directives[0].inline_justification is not None
