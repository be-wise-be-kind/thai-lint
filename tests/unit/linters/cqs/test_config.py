"""
Purpose: Tests for CQS linter configuration

Scope: Unit tests for CQSConfig dataclass defaults, validation, and loading

Overview: Test suite for CQS configuration. Tests default values for all configuration
    options, from_dict() loading from YAML configuration, and validation of config
    options. Verifies that constructors (__init__, __new__) are ignored by default
    and property decorators are excluded. Config tests are NOT skipped as config.py
    is implemented in PR1.

Dependencies: pytest, src.linters.cqs.config

Exports: Test classes for configuration

Interfaces: pytest test discovery and execution

Implementation: Tests for configuration validation following TDD
"""

from src.linters.cqs.config import CQSConfig


class TestConfigDataclassDefaults:
    """Tests for CQSConfig dataclass default values."""

    def test_enabled_by_default(self) -> None:
        """Config is enabled by default."""
        config = CQSConfig()
        assert config.enabled is True

    def test_min_operations_default(self) -> None:
        """Min operations defaults to 1."""
        config = CQSConfig()
        assert config.min_operations == 1

    def test_ignore_methods_default(self) -> None:
        """Constructor methods are ignored by default."""
        config = CQSConfig()
        assert "__init__" in config.ignore_methods
        assert "__new__" in config.ignore_methods

    def test_ignore_decorators_default(self) -> None:
        """Property decorators are ignored by default."""
        config = CQSConfig()
        assert "property" in config.ignore_decorators
        assert "cached_property" in config.ignore_decorators

    def test_ignore_patterns_empty_by_default(self) -> None:
        """Ignore patterns list is empty by default."""
        config = CQSConfig()
        assert config.ignore_patterns == []

    def test_detect_fluent_interface_default(self) -> None:
        """Fluent interface detection is enabled by default."""
        config = CQSConfig()
        assert config.detect_fluent_interface is True


class TestConfigFromDict:
    """Tests for CQSConfig.from_dict() loading."""

    def test_loads_empty_dict(self) -> None:
        """Empty dict uses all defaults."""
        config = CQSConfig.from_dict({})
        assert config.enabled is True
        assert config.min_operations == 1
        assert "__init__" in config.ignore_methods

    def test_loads_enabled_false(self) -> None:
        """Loads enabled: false from dict."""
        config = CQSConfig.from_dict({"enabled": False})
        assert config.enabled is False

    def test_loads_min_operations(self) -> None:
        """Loads min_operations override."""
        config = CQSConfig.from_dict({"min_operations": 2})
        assert config.min_operations == 2

    def test_loads_custom_ignore_methods(self) -> None:
        """Loads custom ignore_methods list."""
        config = CQSConfig.from_dict({"ignore_methods": ["__init__", "__new__", "setup"]})
        assert "setup" in config.ignore_methods
        assert "__init__" in config.ignore_methods

    def test_loads_custom_ignore_decorators(self) -> None:
        """Loads custom ignore_decorators list."""
        config = CQSConfig.from_dict({"ignore_decorators": ["property", "staticmethod"]})
        assert "property" in config.ignore_decorators
        assert "staticmethod" in config.ignore_decorators

    def test_loads_ignore_patterns(self) -> None:
        """Loads ignore patterns from dict."""
        config = CQSConfig.from_dict({"ignore_patterns": ["tests/**", "**/*_test.py"]})
        assert "tests/**" in config.ignore_patterns
        assert "**/*_test.py" in config.ignore_patterns

    def test_loads_detect_fluent_interface_false(self) -> None:
        """Loads detect_fluent_interface: false from dict."""
        config = CQSConfig.from_dict({"detect_fluent_interface": False})
        assert config.detect_fluent_interface is False

    def test_ignores_unknown_keys(self) -> None:
        """Unknown keys in dict are ignored."""
        config = CQSConfig.from_dict(
            {
                "unknown_key": "value",
                "another_unknown": 123,
            }
        )
        assert config.enabled is True  # Still uses defaults

    def test_language_parameter_accepted(self) -> None:
        """Language parameter is accepted but reserved for future use."""
        config = CQSConfig.from_dict({}, language="python")
        assert config.enabled is True

    def test_partial_override(self) -> None:
        """Partial dict uses defaults for missing keys."""
        config = CQSConfig.from_dict({"min_operations": 3})
        assert config.min_operations == 3
        assert config.enabled is True
        assert "__init__" in config.ignore_methods


class TestConfigDataclassInstantiation:
    """Tests for CQSConfig direct instantiation."""

    def test_custom_instantiation(self) -> None:
        """Config can be instantiated with custom values."""
        config = CQSConfig(
            enabled=False,
            min_operations=5,
            ignore_methods=["custom_method"],
            ignore_decorators=["custom_decorator"],
            ignore_patterns=["**/generated/**"],
            detect_fluent_interface=False,
        )
        assert config.enabled is False
        assert config.min_operations == 5
        assert config.ignore_methods == ["custom_method"]
        assert config.ignore_decorators == ["custom_decorator"]
        assert config.ignore_patterns == ["**/generated/**"]
        assert config.detect_fluent_interface is False

    def test_ignore_methods_not_shared(self) -> None:
        """Default ignore_methods lists are not shared between instances."""
        config1 = CQSConfig()
        config2 = CQSConfig()
        config1.ignore_methods.append("custom")
        assert "custom" not in config2.ignore_methods

    def test_ignore_decorators_not_shared(self) -> None:
        """Default ignore_decorators lists are not shared between instances."""
        config1 = CQSConfig()
        config2 = CQSConfig()
        config1.ignore_decorators.append("custom")
        assert "custom" not in config2.ignore_decorators
