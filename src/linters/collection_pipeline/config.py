"""
Purpose: Configuration dataclass for collection-pipeline linter

Scope: Define configurable options for embedded filtering pattern detection

Overview: Provides CollectionPipelineConfig for customizing linter behavior including
    minimum number of continue patterns to flag, enable/disable toggle, and ignore
    patterns. Integrates with the orchestrator's configuration system to allow users
    to customize collection-pipeline detection via .thailint.yaml configuration files.
    Follows the same configuration pattern as other thai-lint linters.

Dependencies: dataclasses, typing

Exports: CollectionPipelineConfig dataclass, DEFAULT_MIN_CONTINUES constant

Interfaces: CollectionPipelineConfig.from_dict() class method for configuration loading

Implementation: Dataclass with sensible defaults and config loading from dictionary
"""

from dataclasses import dataclass, field
from typing import Any

# Default threshold for minimum continue guards to flag
DEFAULT_MIN_CONTINUES = 1


@dataclass
class CollectionPipelineConfig:
    """Configuration for collection-pipeline linter."""

    enabled: bool = True
    """Whether the linter is enabled."""

    min_continues: int = DEFAULT_MIN_CONTINUES
    """Minimum number of if/continue patterns required to flag a violation."""

    ignore: list[str] = field(default_factory=list)
    """File patterns to ignore."""

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.min_continues < 1:
            raise ValueError(f"min_continues must be at least 1, got {self.min_continues}")

    @classmethod
    def from_dict(
        cls, config: dict[str, Any], language: str | None = None
    ) -> "CollectionPipelineConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values
            language: Programming language (unused, for interface compatibility)

        Returns:
            CollectionPipelineConfig instance with values from dictionary
        """
        return cls(
            enabled=config.get("enabled", True),
            min_continues=config.get("min_continues", DEFAULT_MIN_CONTINUES),
            ignore=config.get("ignore", []),
        )
