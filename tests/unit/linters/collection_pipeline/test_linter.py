"""
Purpose: Unit tests for CollectionPipelineRule integration

Scope: Tests for the main rule class integrating with thai-lint framework

Overview: Tests the CollectionPipelineRule class which implements the BaseLintRule
    interface. Verifies correct violation creation, configuration handling, and
    integration with the thai-lint orchestrator system.

Dependencies: pytest, src.linters.collection_pipeline, src.core.types

Exports: TestCollectionPipelineRule test class

Interfaces: Standard pytest test class with test methods

Implementation: Integration tests for rule class behavior
"""

from pathlib import Path

from src.core.types import Severity
from src.linters.collection_pipeline import CollectionPipelineRule
from src.linters.collection_pipeline.config import CollectionPipelineConfig


class MockContext:
    """Mock lint context for testing."""

    def __init__(
        self,
        file_content: str,
        file_path: str = "test.py",
        language: str = "python",
        metadata: dict | None = None,
    ) -> None:
        """Initialize mock context."""
        self._file_content = file_content
        self._file_path = Path(file_path)
        self._language = language
        self.metadata = metadata or {}

    @property
    def file_content(self) -> str:
        """Return file content."""
        return self._file_content

    @property
    def file_path(self) -> Path:
        """Return file path."""
        return self._file_path

    @property
    def language(self) -> str:
        """Return language."""
        return self._language


class TestCollectionPipelineRule:
    """Tests for CollectionPipelineRule class."""

    def test_rule_id(self) -> None:
        """Rule should have correct ID."""
        rule = CollectionPipelineRule()
        assert rule.rule_id == "collection-pipeline.embedded-filter"

    def test_rule_name(self) -> None:
        """Rule should have human-readable name."""
        rule = CollectionPipelineRule()
        assert len(rule.rule_name) > 0
        # Check for meaningful words in the rule name
        assert any(
            word in rule.rule_name.lower()
            for word in ["loop", "filter", "embed", "collection", "pipeline"]
        )

    def test_description(self) -> None:
        """Rule should have description."""
        rule = CollectionPipelineRule()
        assert len(rule.description) > 0

    def test_detects_violation(self) -> None:
        """Should detect embedded filtering pattern."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        context = MockContext(file_content=code)
        rule = CollectionPipelineRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert violations[0].rule_id == "collection-pipeline.embedded-filter"
        assert violations[0].severity == Severity.ERROR

    def test_no_violation_for_clean_code(self) -> None:
        """Should not flag clean code."""
        code = """
for item in items:
    process(item)
"""
        context = MockContext(file_content=code)
        rule = CollectionPipelineRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_violation_has_suggestion(self) -> None:
        """Violation should include refactoring suggestion."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        context = MockContext(file_content=code)
        rule = CollectionPipelineRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert violations[0].suggestion is not None
        assert "for item in" in violations[0].suggestion

    def test_violation_has_line_number(self) -> None:
        """Violation should have correct line number."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        context = MockContext(file_content=code)
        rule = CollectionPipelineRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert violations[0].line == 2  # for loop starts on line 2

    def test_respects_enabled_config(self) -> None:
        """Should respect enabled=False in config."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        context = MockContext(
            file_content=code,
            metadata={"collection-pipeline": {"enabled": False}},
        )
        rule = CollectionPipelineRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_respects_min_continues_config(self) -> None:
        """Should respect min_continues threshold."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        # Single continue, but min_continues is 2
        context = MockContext(
            file_content=code,
            metadata={"collection-pipeline": {"min_continues": 2}},
        )
        rule = CollectionPipelineRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_returns_empty_for_empty_content(self) -> None:
        """Should return empty for empty content."""
        context = MockContext(file_content="")
        rule = CollectionPipelineRule()
        violations = rule.check(context)

        assert len(violations) == 0


class TestCollectionPipelineConfig:
    """Tests for CollectionPipelineConfig."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        config = CollectionPipelineConfig()
        assert config.enabled is True
        assert config.min_continues == 1

    def test_from_dict(self) -> None:
        """Should load from dictionary."""
        config_dict = {
            "enabled": True,
            "min_continues": 2,
        }
        config = CollectionPipelineConfig.from_dict(config_dict)

        assert config.enabled is True
        assert config.min_continues == 2

    def test_from_dict_with_defaults(self) -> None:
        """Should use defaults for missing values."""
        config = CollectionPipelineConfig.from_dict({})

        assert config.enabled is True
        assert config.min_continues == 1
