"""
Purpose: Regression tests for centralized per-linter ignore enforcement

Scope: MultiLanguageLintRule.check() and PythonOnlyLintRule.check() ignore handling

Overview: Verifies that the two shared template-method base classes consult a config's
    ignore/ignore_patterns list before dispatching to language-specific analysis, so every
    linter built on top of them gets correct, glob-based, config-driven file exclusion
    without reimplementing it. Uses minimal fake Rule/Config/Context doubles rather than a
    real linter, so these tests exercise the base-class contract in isolation from any
    specific linter's behavior.

Dependencies: pytest, pathlib, src.core.base, src.core.python_lint_rule

Exports: TestMultiLanguageLintRuleIgnore, TestPythonOnlyLintRuleIgnore

Interfaces: Tests check(context) -> list[Violation] on both base classes

Implementation: Fake subclasses record whether language-specific analysis was invoked,
    so tests assert on dispatch behavior rather than violation content
"""

from pathlib import Path

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.python_lint_rule import PythonOnlyLintRule


class _FakeConfig:
    """Minimal config double with the attributes the base classes read."""

    def __init__(self, ignore: list[str] | None = None, enabled: bool = True) -> None:
        self.ignore = ignore or []
        self.enabled = enabled


class _FakeContext(BaseLintContext):
    """Minimal context double."""

    def __init__(self, file_path: Path, language: str = "python") -> None:
        self._file_path = file_path
        self._language = language

    @property
    def file_path(self) -> Path | None:
        return self._file_path

    @property
    def file_content(self) -> str | None:
        return "x = 1"

    @property
    def language(self) -> str:
        return self._language


class _FakeMultiLanguageRule(MultiLanguageLintRule):
    """Records whether language dispatch happened."""

    def __init__(self, config: _FakeConfig) -> None:
        super().__init__()
        self._config = config
        self.dispatched = False

    @property
    def rule_id(self) -> str:
        return "fake.rule"

    @property
    def rule_name(self) -> str:
        return "Fake Rule"

    @property
    def description(self) -> str:
        return "Fake rule for testing base-class ignore handling"

    def _load_config(self, context: BaseLintContext) -> _FakeConfig:
        return self._config

    def _check_python(self, context: BaseLintContext, config: _FakeConfig) -> list:
        self.dispatched = True
        return ["violation"]

    def _check_typescript(self, context: BaseLintContext, config: _FakeConfig) -> list:
        self.dispatched = True
        return ["violation"]


class _FakePythonOnlyRule(PythonOnlyLintRule[_FakeConfig]):
    """Records whether analysis happened."""

    def __init__(self, config: _FakeConfig) -> None:
        super().__init__(config)
        self.analyzed = False

    @property
    def rule_id(self) -> str:
        return "fake.python-only-rule"

    @property
    def rule_name(self) -> str:
        return "Fake Python-Only Rule"

    @property
    def description(self) -> str:
        return "Fake rule for testing base-class ignore handling"

    @property
    def _config_key(self) -> str:
        return "fake"

    @property
    def _config_class(self) -> type[_FakeConfig]:
        return _FakeConfig

    def _analyze(self, code: str, file_path: str, config: _FakeConfig) -> list:
        self.analyzed = True
        return ["violation"]


class TestMultiLanguageLintRuleIgnore:
    """Test ignore enforcement in MultiLanguageLintRule.check()."""

    def test_ignored_file_returns_empty_without_dispatch(self) -> None:
        """A file matching config.ignore must short-circuit before language dispatch."""
        rule = _FakeMultiLanguageRule(_FakeConfig(ignore=["**/legacy/**"]))
        context = _FakeContext(Path("app/legacy/x.py"))

        violations = rule.check(context)

        assert violations == []
        assert rule.dispatched is False

    def test_non_ignored_file_dispatches_normally(self) -> None:
        """A file not matching config.ignore must still dispatch to analysis."""
        rule = _FakeMultiLanguageRule(_FakeConfig(ignore=[]))
        context = _FakeContext(Path("app/x.py"))

        violations = rule.check(context)

        assert violations == ["violation"]
        assert rule.dispatched is True


class TestPythonOnlyLintRuleIgnore:
    """Test ignore enforcement in PythonOnlyLintRule.check()."""

    def test_ignored_file_returns_empty_without_analysis(self) -> None:
        """A file matching config.ignore must short-circuit before analysis."""
        rule = _FakePythonOnlyRule(_FakeConfig(ignore=["**/legacy/**"]))
        context = _FakeContext(Path("app/legacy/x.py"))

        violations = rule.check(context)

        assert violations == []
        assert rule.analyzed is False

    def test_non_ignored_file_analyzes_normally(self) -> None:
        """A file not matching config.ignore must still be analyzed."""
        rule = _FakePythonOnlyRule(_FakeConfig(ignore=[]))
        context = _FakeContext(Path("app/x.py"))

        violations = rule.check(context)

        assert violations == ["violation"]
        assert rule.analyzed is True
