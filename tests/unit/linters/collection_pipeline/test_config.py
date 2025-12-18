"""
Purpose: Test suite for collection-pipeline linter configuration loading

Scope: Configuration loading from .thailint.yaml for collection-pipeline linter

Overview: TDD test suite for collection-pipeline linter configuration covering
    config loading from .thailint.yaml, enabled flag, min_continues threshold,
    and ignore patterns list. Tests define expected behavior following
    Red-Green-Refactor methodology to verify full config support.

Dependencies: pytest for testing framework, src.linters.collection_pipeline,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestConfigLoading, TestConfigDataclass test classes

Interfaces: Tests CollectionPipelineRule and CollectionPipelineConfig

Implementation: TDD approach with mock contexts simulating config loaded from YAML
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestConfigLoading:
    """Test configuration loading from .thailint.yaml."""

    def test_loads_enabled_flag_from_config(self) -> None:
        """Should respect enabled: false in config to disable linter."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"collection_pipeline": {"enabled": False}}

        violations = rule.check(context)
        assert len(violations) == 0, "Linter should be disabled when enabled=False"

    def test_loads_min_continues_threshold_from_config(self) -> None:
        """Should respect min_continues threshold from config."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        # Default min_continues is 1, but set to 2 so this single-continue pattern passes
        context.config = {"collection_pipeline": {"min_continues": 2}}

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag pattern when below min_continues threshold"

    def test_default_config_when_not_provided(self) -> None:
        """Should use default config when no config provided."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None  # No config

        violations = rule.check(context)
        assert len(violations) == 1, "Should use defaults and detect violation"


class TestIgnorePatterns:
    """Test linter-specific ignore patterns from config."""

    def test_ignores_file_matching_pattern(self) -> None:
        """Should ignore files matching ignore patterns in config."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("tests/test_helpers.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"collection_pipeline": {"ignore": ["tests/"]}}

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore files in tests/ directory"

    def test_ignores_file_matching_glob_pattern(self) -> None:
        """Should support glob patterns in ignore list."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("src/utils/helpers.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"collection_pipeline": {"ignore": ["**/helpers.py"]}}

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore files matching glob pattern"

    def test_does_not_ignore_non_matching_file(self) -> None:
        """Should not ignore files that don't match any pattern."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("src/core/main.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"collection_pipeline": {"ignore": ["tests/", "**/helpers.py"]}}

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect violation in non-ignored file"


class TestConfigDataclass:
    """Test CollectionPipelineConfig dataclass."""

    def test_config_dataclass_defaults(self) -> None:
        """Config should have sensible defaults."""
        from src.linters.collection_pipeline.config import CollectionPipelineConfig

        config = CollectionPipelineConfig()
        assert config.enabled is True, "Default enabled should be True"
        assert config.min_continues == 1, "Default min_continues should be 1"
        assert config.ignore == [], "Default ignore should be empty list"

    def test_config_from_dict_full(self) -> None:
        """Config should load all fields from dictionary."""
        from src.linters.collection_pipeline.config import CollectionPipelineConfig

        config = CollectionPipelineConfig.from_dict(
            {
                "enabled": False,
                "min_continues": 2,
                "ignore": ["tests/", "**/helpers.py"],
            }
        )
        assert config.enabled is False
        assert config.min_continues == 2
        assert config.ignore == ["tests/", "**/helpers.py"]

    def test_config_from_dict_partial(self) -> None:
        """Config should use defaults for missing fields."""
        from src.linters.collection_pipeline.config import CollectionPipelineConfig

        config = CollectionPipelineConfig.from_dict({"min_continues": 3})
        assert config.enabled is True  # default
        assert config.min_continues == 3
        assert config.ignore == []  # default

    def test_config_validates_min_continues(self) -> None:
        """Config should validate min_continues >= 1."""
        from src.linters.collection_pipeline.config import CollectionPipelineConfig

        with pytest.raises(ValueError):
            CollectionPipelineConfig(min_continues=0)
