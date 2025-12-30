"""
Purpose: Configuration dataclass for stringly-typed linter

Scope: Define configurable options for stringly-typed pattern detection

Overview: Provides StringlyTypedConfig for customizing linter behavior including minimum
    occurrences required to flag patterns, enum value thresholds, cross-file detection
    settings, and ignore patterns. The stringly-typed linter detects code patterns where
    plain strings are used instead of proper enums or typed alternatives. Integrates with
    the orchestrator's configuration system to allow users to customize detection via
    .thailint.yaml configuration files. Follows the same configuration pattern as other
    thai-lint linters.

Dependencies: dataclasses, typing

Exports: StringlyTypedConfig dataclass, default constants

Interfaces: StringlyTypedConfig.from_dict() class method for configuration loading

Implementation: Dataclass with sensible defaults, validation in __post_init__, and config
    loading from dictionary with language-specific override support

Suppressions:
    - too-many-instance-attributes: Configuration dataclass with cohesive detection settings
"""

from dataclasses import dataclass, field
from typing import Any

# Default thresholds
DEFAULT_MIN_OCCURRENCES = 2
DEFAULT_MIN_VALUES_FOR_ENUM = 2
DEFAULT_MAX_VALUES_FOR_ENUM = 6

# Default ignore patterns - test directories are excluded by default
# because test fixtures commonly use string literals for mocking
DEFAULT_IGNORE_PATTERNS: list[str] = [
    "**/tests/**",
    "**/test/**",
    "**/*_test.py",
    "**/*_test.ts",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.spec.ts",
    "**/*.spec.tsx",
    "**/*.stories.ts",
    "**/*.stories.tsx",
    "**/conftest.py",
    "**/fixtures/**",
]


@dataclass
class StringlyTypedConfig:  # pylint: disable=too-many-instance-attributes
    """Configuration for stringly-typed linter.

    Note: Pylint too-many-instance-attributes disabled. This is a configuration
    dataclass serving as a data container for related stringly-typed linter settings.
    All 8 attributes are cohesively related (detection thresholds, filtering options,
    cross-file settings, exclusion patterns). Splitting would reduce cohesion and make
    configuration loading more complex without meaningful benefit. This follows the
    established pattern in DRYConfig.
    """

    enabled: bool = True
    """Whether the linter is enabled."""

    min_occurrences: int = DEFAULT_MIN_OCCURRENCES
    """Minimum number of cross-file occurrences required to flag a violation."""

    min_values_for_enum: int = DEFAULT_MIN_VALUES_FOR_ENUM
    """Minimum number of unique string values to suggest an enum."""

    max_values_for_enum: int = DEFAULT_MAX_VALUES_FOR_ENUM
    """Maximum number of unique string values to suggest an enum (above this, not enum-worthy)."""

    require_cross_file: bool = True
    """Whether to require cross-file occurrences to flag violations."""

    ignore: list[str] = field(default_factory=list)
    """File patterns to ignore. Defaults merged with test directories in from_dict."""

    allowed_string_sets: list[list[str]] = field(default_factory=list)
    """String sets that are allowed and should not be flagged."""

    exclude_variables: list[str] = field(default_factory=list)
    """Variable names to exclude from detection."""

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.min_occurrences < 1:
            raise ValueError(f"min_occurrences must be at least 1, got {self.min_occurrences}")
        if self.min_values_for_enum < 2:
            raise ValueError(
                f"min_values_for_enum must be at least 2, got {self.min_values_for_enum}"
            )
        if self.max_values_for_enum < self.min_values_for_enum:
            raise ValueError(
                f"max_values_for_enum ({self.max_values_for_enum}) must be >= "
                f"min_values_for_enum ({self.min_values_for_enum})"
            )

    @classmethod
    def from_dict(
        cls, config: dict[str, Any], language: str | None = None
    ) -> "StringlyTypedConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values
            language: Programming language for language-specific overrides

        Returns:
            StringlyTypedConfig instance with values from dictionary
        """
        # Check for language-specific overrides first
        if language and language in config:
            lang_config = config[language]
            return cls._from_merged_config(config, lang_config)

        return cls._from_base_config(config)

    @classmethod
    def _from_base_config(cls, config: dict[str, Any]) -> "StringlyTypedConfig":
        """Create config from base configuration dictionary.

        Args:
            config: Base configuration dictionary

        Returns:
            StringlyTypedConfig instance
        """
        # Merge user ignore patterns with defaults
        user_ignore = config.get("ignore", [])
        merged_ignore = DEFAULT_IGNORE_PATTERNS.copy() + user_ignore

        return cls(
            enabled=config.get("enabled", True),
            min_occurrences=config.get("min_occurrences", DEFAULT_MIN_OCCURRENCES),
            min_values_for_enum=config.get("min_values_for_enum", DEFAULT_MIN_VALUES_FOR_ENUM),
            max_values_for_enum=config.get("max_values_for_enum", DEFAULT_MAX_VALUES_FOR_ENUM),
            require_cross_file=config.get("require_cross_file", True),
            ignore=merged_ignore,
            allowed_string_sets=config.get("allowed_string_sets", []),
            exclude_variables=config.get("exclude_variables", []),
        )

    @classmethod
    def _from_merged_config(
        cls, base_config: dict[str, Any], lang_config: dict[str, Any]
    ) -> "StringlyTypedConfig":
        """Create config with language-specific overrides merged.

        Args:
            base_config: Base configuration dictionary
            lang_config: Language-specific configuration overrides

        Returns:
            StringlyTypedConfig instance with merged values
        """
        # Merge user ignore patterns with defaults
        user_ignore = lang_config.get("ignore", base_config.get("ignore", []))
        merged_ignore = DEFAULT_IGNORE_PATTERNS.copy() + user_ignore

        return cls(
            enabled=lang_config.get("enabled", base_config.get("enabled", True)),
            min_occurrences=lang_config.get(
                "min_occurrences",
                base_config.get("min_occurrences", DEFAULT_MIN_OCCURRENCES),
            ),
            min_values_for_enum=lang_config.get(
                "min_values_for_enum",
                base_config.get("min_values_for_enum", DEFAULT_MIN_VALUES_FOR_ENUM),
            ),
            max_values_for_enum=lang_config.get(
                "max_values_for_enum",
                base_config.get("max_values_for_enum", DEFAULT_MAX_VALUES_FOR_ENUM),
            ),
            require_cross_file=lang_config.get(
                "require_cross_file", base_config.get("require_cross_file", True)
            ),
            ignore=merged_ignore,
            allowed_string_sets=lang_config.get(
                "allowed_string_sets", base_config.get("allowed_string_sets", [])
            ),
            exclude_variables=lang_config.get(
                "exclude_variables", base_config.get("exclude_variables", [])
            ),
        )
