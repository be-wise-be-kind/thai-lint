"""
Purpose: Configuration schema for magic numbers linter

Scope: MagicNumberConfig dataclass with allowed_numbers and max_small_integer settings

Overview: Defines configuration schema for magic numbers linter. Provides MagicNumberConfig dataclass
    with allowed_numbers set (default includes common acceptable numbers like -1, 0, 1, 2, 3, 4, 5, 10, 100, 1000)
    and max_small_integer threshold (default 10) for range() contexts. Supports per-file and per-directory
    config overrides through from_dict class method. Validates that configuration values are appropriate
    types. Integrates with orchestrator's configuration system to allow users to customize allowed numbers
    via .thailint.yaml configuration files.

Dependencies: dataclasses for class definition, typing for type hints

Exports: MagicNumberConfig dataclass

Interfaces: MagicNumberConfig(allowed_numbers: set, max_small_integer: int, enabled: bool),
    from_dict class method for loading configuration from dictionary

Implementation: Dataclass with validation and defaults, matches reference implementation patterns
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MagicNumberConfig:
    """Configuration for magic numbers linter."""

    enabled: bool = True
    allowed_numbers: set[int | float] = field(
        default_factory=lambda: {-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000}
    )
    max_small_integer: int = 10
    ignore: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_small_integer <= 0:
            raise ValueError(f"max_small_integer must be positive, got {self.max_small_integer}")

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "MagicNumberConfig":
        """Load configuration from dictionary with language-specific overrides.

        Args:
            config: Dictionary containing configuration values
            language: Programming language (python, typescript, javascript)
                for language-specific settings

        Returns:
            MagicNumberConfig instance with values from dictionary
        """
        # Get language-specific config if available
        if language and language in config:
            lang_config = config[language]
            allowed_numbers = set(
                lang_config.get(
                    "allowed_numbers",
                    config.get("allowed_numbers", {-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000}),
                )
            )
            max_small_integer = lang_config.get(
                "max_small_integer", config.get("max_small_integer", 10)
            )
        else:
            allowed_numbers = set(
                config.get("allowed_numbers", {-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000})
            )
            max_small_integer = config.get("max_small_integer", 10)

        ignore_patterns = config.get("ignore", [])
        if not isinstance(ignore_patterns, list):
            ignore_patterns = []

        return cls(
            enabled=config.get("enabled", True),
            allowed_numbers=allowed_numbers,
            max_small_integer=max_small_integer,
            ignore=ignore_patterns,
        )
