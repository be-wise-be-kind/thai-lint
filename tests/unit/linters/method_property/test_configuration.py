"""
Purpose: Unit tests for method-should-be-property configuration handling

Scope: Testing configuration loading, defaults, and option overrides

Overview: Comprehensive test suite for method-should-be-property configuration covering default
    values, configuration loading from various sources (context config, metadata, YAML files),
    and configuration option overrides. Validates that the linter respects custom thresholds
    for max body statements, ignore patterns, and enabled/disabled states. Ensures configuration
    is properly merged and applied during linting operations.

Dependencies: pytest (including parametrize), pathlib.Path, unittest.mock.Mock,
    src.linters.method_property.linter.MethodPropertyRule,
    src.linters.method_property.config.MethodPropertyConfig

Exports: TestConfigurationDefaults, TestConfigurationLoading, TestConfigurationOverrides,
    TestProductionConfigLoading test classes

Interfaces: test methods validating configuration behavior and defaults

Implementation: Uses Mock objects for context creation, tests configuration dataclass
    instantiation and from_dict loading
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestConfigurationDefaults:
    """Test default configuration values."""

    def test_default_enabled_true(self):
        """Should have enabled=True by default."""
        from src.linters.method_property.config import MethodPropertyConfig

        config = MethodPropertyConfig()
        assert config.enabled is True

    def test_default_max_body_statements(self):
        """Should have max_body_statements=3 by default."""
        from src.linters.method_property.config import MethodPropertyConfig

        config = MethodPropertyConfig()
        assert config.max_body_statements == 3

    def test_default_ignore_patterns(self):
        """Should have empty ignore patterns by default."""
        from src.linters.method_property.config import MethodPropertyConfig

        config = MethodPropertyConfig()
        assert config.ignore == []


class TestConfigurationLoading:
    """Test configuration loading from various sources."""

    def test_loads_from_dict(self):
        """Should load configuration from dictionary."""
        from src.linters.method_property.config import MethodPropertyConfig

        config_dict = {
            "enabled": True,
            "max_body_statements": 5,
            "ignore": ["tests/*"],
        }

        config = MethodPropertyConfig.from_dict(config_dict)
        assert config.enabled is True
        assert config.max_body_statements == 5
        assert config.ignore == ["tests/*"]

    def test_loads_partial_config(self):
        """Should use defaults for missing keys in config dict."""
        from src.linters.method_property.config import MethodPropertyConfig

        config_dict = {"max_body_statements": 5}

        config = MethodPropertyConfig.from_dict(config_dict)
        assert config.enabled is True  # Default
        assert config.max_body_statements == 5  # From dict
        assert config.ignore == []  # Default

    def test_loads_empty_config(self):
        """Should use all defaults for empty config dict."""
        from src.linters.method_property.config import MethodPropertyConfig

        config = MethodPropertyConfig.from_dict({})
        assert config.enabled is True
        assert config.max_body_statements == 3
        assert config.ignore == []

    def test_loads_from_none(self):
        """Should handle None config gracefully."""
        from src.linters.method_property.config import MethodPropertyConfig

        config = MethodPropertyConfig.from_dict(None)
        assert config.enabled is True
        assert config.max_body_statements == 3
        assert config.ignore == []


class TestConfigurationOverrides:
    """Test configuration option overrides."""

    def test_custom_max_body_statements(self):
        """Should respect custom max_body_statements in detection."""
        code = """
class Processor:
    def __init__(self):
        self._value = "test"

    def processed(self):
        v = self._value
        v = v.strip()
        return v
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()

        # With default max=3, this 3-statement method should be flagged
        context = Mock()
        context.file_path = Path("processor.py")
        context.file_content = code
        context.language = "python"
        context.config = {}

        violations_default = rule.check(context)

        # With max=2, this 3-statement method should NOT be flagged
        context.config = {"method-property": {"max_body_statements": 2}}
        violations_custom = rule.check(context)

        # Default should flag it, custom should not
        assert len(violations_default) == 1
        assert len(violations_custom) == 0

    def test_custom_ignore_patterns(self):
        """Should respect custom ignore patterns."""
        code = """
class Helper:
    def __init__(self):
        self._value = 42

    def get_value(self):
        return self._value
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("helpers/utils.py")
        context.file_content = code
        context.language = "python"

        # Without ignore pattern, should flag
        context.config = {}
        violations_without = rule.check(context)

        # With ignore pattern matching file, should not flag
        context.config = {"method-property": {"ignore": ["helpers/*"]}}
        violations_with = rule.check(context)

        assert len(violations_without) == 1
        assert len(violations_with) == 0

    def test_disabled_linter(self):
        """Should not flag anything when disabled."""
        code = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"
        context.config = {"method-property": {"enabled": False}}

        violations = rule.check(context)
        assert len(violations) == 0


class TestConfigurationMerging:
    """Test configuration merging behavior."""

    def test_context_config_overrides_defaults(self):
        """Should allow context config to override defaults."""
        from src.linters.method_property.config import MethodPropertyConfig

        # Default config
        default = MethodPropertyConfig()
        assert default.max_body_statements == 3

        # Override via dict
        override = {"max_body_statements": 5}
        merged = MethodPropertyConfig.from_dict(override)
        assert merged.max_body_statements == 5

    def test_multiple_ignore_patterns(self):
        """Should support multiple ignore patterns."""
        from src.linters.method_property.config import MethodPropertyConfig

        config_dict = {
            "ignore": [
                "tests/*",
                "**/test_*.py",
                "fixtures/*",
            ]
        }

        config = MethodPropertyConfig.from_dict(config_dict)
        assert len(config.ignore) == 3
        assert "tests/*" in config.ignore
        assert "**/test_*.py" in config.ignore
        assert "fixtures/*" in config.ignore


class TestProductionConfigLoading:
    """Test configuration loading from context.metadata (production path)."""

    SIMPLE_CODE = """
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name
"""

    def _make_context(self, code: str, metadata: dict | None = None) -> Mock:
        """Create a mock context with metadata and no test config."""
        context = Mock()
        context.file_path = Path("user.py")
        context.file_content = code
        context.language = "python"
        context.config = None
        context.metadata = metadata if metadata is not None else {}
        return context

    @pytest.mark.parametrize("config_key", ["method_property", "method-property"])
    def test_loads_config_from_metadata(self, config_key: str):
        """Should load config from metadata using either key format."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = self._make_context(
            self.SIMPLE_CODE,
            metadata={config_key: {"max_body_statements": 5}},
        )

        violations = rule.check(context)
        assert len(violations) == 1  # get_name still flagged with permissive threshold

    @pytest.mark.parametrize("config_key", ["method_property", "method-property"])
    def test_metadata_max_body_statements(self, config_key: str):
        """Custom max_body_statements from metadata affects detection."""
        code = """
class Processor:
    def __init__(self):
        self._value = "test"

    def processed(self):
        v = self._value
        v = v.strip()
        return v
"""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()

        # With max=2, the 3-statement method should NOT be flagged
        context = self._make_context(
            code,
            metadata={config_key: {"max_body_statements": 2}},
        )
        violations = rule.check(context)
        assert len(violations) == 0

    @pytest.mark.parametrize("config_key", ["method_property", "method-property"])
    def test_metadata_ignore_patterns(self, config_key: str):
        """Ignore patterns from metadata work correctly."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = self._make_context(
            self.SIMPLE_CODE,
            metadata={config_key: {"ignore": ["user.py"]}},
        )

        violations = rule.check(context)
        assert len(violations) == 0

    @pytest.mark.parametrize("config_key", ["method_property", "method-property"])
    def test_metadata_disabled_linter(self, config_key: str):
        """enabled: false from metadata disables linter."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = self._make_context(
            self.SIMPLE_CODE,
            metadata={config_key: {"enabled": False}},
        )

        violations = rule.check(context)
        assert len(violations) == 0

    def test_defaults_when_no_metadata(self):
        """Falls back to defaults when metadata has no relevant key."""
        from src.linters.method_property.linter import MethodPropertyRule

        rule = MethodPropertyRule()
        context = self._make_context(
            self.SIMPLE_CODE,
            metadata={"some_other_linter": {"enabled": False}},
        )

        violations = rule.check(context)
        assert len(violations) == 1  # get_name flagged with default config
