"""
Purpose: Test suite for stringly-typed linter configuration loading

Scope: Configuration dataclass and loading for stringly-typed linter

Overview: TDD test suite for stringly-typed linter configuration covering
    config defaults, loading from dictionary, validation of numeric constraints,
    and language-specific config overrides. Tests define expected behavior
    following Red-Green-Refactor methodology to verify full config support.

Dependencies: pytest for testing framework, src.linters.stringly_typed.config

Exports: TestConfigDataclass, TestConfigValidation, TestLanguageOverrides test classes

Interfaces: Tests StringlyTypedConfig dataclass

Implementation: TDD approach with comprehensive test coverage for config behavior
"""

import pytest

from src.linters.stringly_typed.config import (
    DEFAULT_MAX_VALUES_FOR_ENUM,
    DEFAULT_MIN_OCCURRENCES,
    DEFAULT_MIN_VALUES_FOR_ENUM,
    StringlyTypedConfig,
)


class TestConfigDataclass:
    """Test StringlyTypedConfig dataclass defaults and loading."""

    def test_config_dataclass_defaults(self) -> None:
        """Config should have sensible defaults."""
        config = StringlyTypedConfig()
        assert config.enabled is True, "Default enabled should be True"
        assert config.min_occurrences == DEFAULT_MIN_OCCURRENCES, (
            f"Default min_occurrences should be {DEFAULT_MIN_OCCURRENCES}"
        )
        assert config.min_values_for_enum == DEFAULT_MIN_VALUES_FOR_ENUM, (
            f"Default min_values_for_enum should be {DEFAULT_MIN_VALUES_FOR_ENUM}"
        )
        assert config.max_values_for_enum == DEFAULT_MAX_VALUES_FOR_ENUM, (
            f"Default max_values_for_enum should be {DEFAULT_MAX_VALUES_FOR_ENUM}"
        )
        assert config.require_cross_file is True, "Default require_cross_file should be True"
        # Dataclass default is empty; test patterns are added in from_dict
        assert config.ignore == [], "Dataclass default ignore should be empty list"
        assert config.allowed_string_sets == [], "Default allowed_string_sets should be empty"
        assert config.exclude_variables == [], "Default exclude_variables should be empty"

    def test_config_from_dict_full(self) -> None:
        """Config should load all fields from dictionary."""
        config = StringlyTypedConfig.from_dict(
            {
                "enabled": False,
                "min_occurrences": 3,
                "min_values_for_enum": 3,
                "max_values_for_enum": 8,
                "require_cross_file": False,
                "ignore": ["tests/", "**/fixtures.py"],
                "allowed_string_sets": [["debug", "info", "warning"]],
                "exclude_variables": ["log_level"],
            }
        )
        assert config.enabled is False
        assert config.min_occurrences == 3
        assert config.min_values_for_enum == 3
        assert config.max_values_for_enum == 8
        assert config.require_cross_file is False
        # User patterns are merged with defaults
        assert "tests/" in config.ignore
        assert "**/fixtures.py" in config.ignore
        assert "**/tests/**" in config.ignore  # Default pattern still present
        assert config.allowed_string_sets == [["debug", "info", "warning"]]
        assert config.exclude_variables == ["log_level"]

    def test_config_from_dict_partial(self) -> None:
        """Config should use defaults for missing fields."""
        config = StringlyTypedConfig.from_dict({"min_occurrences": 5})
        assert config.enabled is True  # default
        assert config.min_occurrences == 5
        assert config.min_values_for_enum == DEFAULT_MIN_VALUES_FOR_ENUM  # default
        assert config.max_values_for_enum == DEFAULT_MAX_VALUES_FOR_ENUM  # default
        assert config.require_cross_file is True  # default
        # Default ignore patterns are applied
        assert "**/tests/**" in config.ignore
        assert config.allowed_string_sets == []  # default
        assert config.exclude_variables == []  # default

    def test_config_from_dict_empty(self) -> None:
        """Config should use all defaults for empty dictionary."""
        config = StringlyTypedConfig.from_dict({})
        assert config.enabled is True
        assert config.min_occurrences == DEFAULT_MIN_OCCURRENCES
        assert config.min_values_for_enum == DEFAULT_MIN_VALUES_FOR_ENUM
        assert config.max_values_for_enum == DEFAULT_MAX_VALUES_FOR_ENUM
        assert config.require_cross_file is True
        # Default ignore patterns are applied
        assert "**/tests/**" in config.ignore
        assert config.allowed_string_sets == []
        assert config.exclude_variables == []


class TestConfigValidation:
    """Test configuration validation."""

    def test_validates_min_occurrences_positive(self) -> None:
        """Config should require min_occurrences >= 1."""
        with pytest.raises(ValueError, match="min_occurrences must be at least 1"):
            StringlyTypedConfig(min_occurrences=0)

    def test_validates_min_occurrences_negative(self) -> None:
        """Config should reject negative min_occurrences."""
        with pytest.raises(ValueError, match="min_occurrences must be at least 1"):
            StringlyTypedConfig(min_occurrences=-1)

    def test_validates_min_values_for_enum(self) -> None:
        """Config should require min_values_for_enum >= 2."""
        with pytest.raises(ValueError, match="min_values_for_enum must be at least 2"):
            StringlyTypedConfig(min_values_for_enum=1)

    def test_validates_max_values_less_than_min(self) -> None:
        """Config should require max_values_for_enum >= min_values_for_enum."""
        with pytest.raises(ValueError, match="max_values_for_enum.*must be >= min_values_for_enum"):
            StringlyTypedConfig(min_values_for_enum=4, max_values_for_enum=3)

    def test_valid_equal_min_max_values(self) -> None:
        """Config should allow equal min and max values for enum."""
        config = StringlyTypedConfig(min_values_for_enum=4, max_values_for_enum=4)
        assert config.min_values_for_enum == 4
        assert config.max_values_for_enum == 4

    def test_valid_min_occurrences_boundary(self) -> None:
        """Config should accept min_occurrences = 1."""
        config = StringlyTypedConfig(min_occurrences=1)
        assert config.min_occurrences == 1

    def test_valid_min_values_for_enum_boundary(self) -> None:
        """Config should accept min_values_for_enum = 2."""
        config = StringlyTypedConfig(min_values_for_enum=2)
        assert config.min_values_for_enum == 2


class TestLanguageOverrides:
    """Test language-specific configuration overrides."""

    def test_python_language_override(self) -> None:
        """Config should apply Python-specific overrides."""
        config = StringlyTypedConfig.from_dict(
            {
                "min_occurrences": 2,
                "python": {
                    "min_occurrences": 3,
                    "exclude_variables": ["python_var"],
                },
            },
            language="python",
        )
        assert config.min_occurrences == 3, "Python override should take precedence"
        assert config.exclude_variables == ["python_var"]

    def test_typescript_language_override(self) -> None:
        """Config should apply TypeScript-specific overrides."""
        config = StringlyTypedConfig.from_dict(
            {
                "max_values_for_enum": 6,
                "typescript": {
                    "max_values_for_enum": 10,
                },
            },
            language="typescript",
        )
        assert config.max_values_for_enum == 10, "TypeScript override should take precedence"

    def test_no_language_uses_base_config(self) -> None:
        """Config should use base values when no language specified."""
        config = StringlyTypedConfig.from_dict(
            {
                "min_occurrences": 5,
                "python": {
                    "min_occurrences": 3,
                },
            },
            language=None,
        )
        assert config.min_occurrences == 5, "Should use base config when no language"

    def test_unspecified_language_uses_base_config(self) -> None:
        """Config should use base values when language not in config."""
        config = StringlyTypedConfig.from_dict(
            {
                "min_occurrences": 5,
                "python": {
                    "min_occurrences": 3,
                },
            },
            language="javascript",  # Not in config
        )
        assert config.min_occurrences == 5, "Should use base config for unknown language"

    def test_partial_language_override(self) -> None:
        """Language override should only override specified fields."""
        config = StringlyTypedConfig.from_dict(
            {
                "min_occurrences": 4,
                "min_values_for_enum": 3,
                "max_values_for_enum": 8,
                "python": {
                    "min_occurrences": 2,
                    # min_values_for_enum not specified, should use base
                },
            },
            language="python",
        )
        assert config.min_occurrences == 2, "Python override applied"
        assert config.min_values_for_enum == 3, "Base config used for unspecified field"
        assert config.max_values_for_enum == 8, "Base config used for unspecified field"
