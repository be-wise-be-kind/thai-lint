"""
Purpose: Configuration dataclass for CQS (Command-Query Separation) linter

Scope: Pattern toggles, ignore patterns, and YAML configuration loading

Overview: Provides CQSConfig dataclass with configurable options for CQS violation
    detection. Controls minimum operation thresholds, methods to ignore (constructors
    by default), decorators to ignore (property-like by default), and fluent interface
    detection. Configuration can be loaded from dictionary (YAML) with sensible defaults.

Dependencies: dataclasses, typing

Exports: CQSConfig

Interfaces: CQSConfig.from_dict() for YAML configuration loading

Implementation: Dataclass with factory defaults and conservative default settings
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CQSConfig:
    """Configuration for CQS linter."""

    enabled: bool = True
    min_operations: int = 1
    ignore_methods: list[str] = field(default_factory=lambda: ["__init__", "__new__"])
    ignore_decorators: list[str] = field(default_factory=lambda: ["property", "cached_property"])
    ignore_patterns: list[str] = field(default_factory=list)
    detect_fluent_interface: bool = True

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "CQSConfig":
        """Load configuration from dictionary (YAML).

        Args:
            config: Dictionary containing configuration values.
            language: Reserved for future multi-language support.

        Returns:
            CQSConfig instance with values from dictionary or defaults.
        """
        # Language parameter reserved for future multi-language support
        _ = language
        return cls(
            enabled=config.get("enabled", True),
            min_operations=config.get("min_operations", 1),
            ignore_methods=config.get("ignore_methods", ["__init__", "__new__"]),
            ignore_decorators=config.get("ignore_decorators", ["property", "cached_property"]),
            ignore_patterns=config.get("ignore_patterns", []),
            detect_fluent_interface=config.get("detect_fluent_interface", True),
        )
