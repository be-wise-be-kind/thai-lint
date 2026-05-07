"""
Purpose: Configuration schema for Law of Demeter linter

Scope: LawOfDemeterConfig dataclass with chain depth, test file, and filter settings

Overview: Defines configuration schema for the Law of Demeter linter. Provides LawOfDemeterConfig
    dataclass with min_chain_depth (default 3), check_test_files toggle, and extensible filter
    lists (safe_prefixes, fluent_methods, exempt_modules). User-provided lists are merged with
    defaults so users extend built-in filter coverage.

Dependencies: dataclasses, typing, filter_constants

Exports: LawOfDemeterConfig dataclass

Interfaces: LawOfDemeterConfig(min_chain_depth, enabled, ...), from_dict() classmethod

Implementation: Dataclass with validation and list merging, follows NestingConfig pattern
"""

from dataclasses import dataclass, field
from typing import Any

from .filter_constants import SAFE_CHAIN_PREFIXES

DEFAULT_MIN_CHAIN_DEPTH = 3


def _default_safe_prefixes() -> list[str]:
    """Return default safe prefixes as a mutable list."""
    return list(SAFE_CHAIN_PREFIXES)


def _default_fluent_methods() -> list[str]:
    """Return default fluent method names."""
    return [
        "filter",
        "map",
        "select",
        "where",
        "order_by",
        "limit",
        "offset",
        "exclude",
        "groupby",
        "sorted",
        "set",
        "build",
        "add",
        "configure",
        "then",
        "catch",
        "pipe",
        "use",
    ]


@dataclass
class LawOfDemeterConfig:
    """Configuration for Law of Demeter linter."""

    min_chain_depth: int = DEFAULT_MIN_CHAIN_DEPTH
    enabled: bool = True
    check_test_files: bool = False
    safe_prefixes: list[str] = field(default_factory=_default_safe_prefixes)
    fluent_methods: list[str] = field(default_factory=_default_fluent_methods)
    exempt_modules: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.min_chain_depth <= 0:
            raise ValueError(f"min_chain_depth must be positive, got {self.min_chain_depth}")

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "LawOfDemeterConfig":
        """Load configuration from dictionary, merging user lists with defaults.

        Args:
            config: Dictionary containing configuration values
            language: Programming language (unused, for protocol compatibility)

        Returns:
            LawOfDemeterConfig instance with merged values
        """
        instance = cls(
            min_chain_depth=config.get("min_chain_depth", DEFAULT_MIN_CHAIN_DEPTH),
            enabled=config.get("enabled", True),
            check_test_files=config.get("check_test_files", False),
        )
        _merge_user_lists(instance, config)
        return instance


def _merge_user_lists(instance: LawOfDemeterConfig, config: dict[str, Any]) -> None:
    """Merge user-provided lists with defaults on the config instance."""
    _extend_unique(instance.safe_prefixes, config.get("safe_prefixes", []))
    _extend_unique(instance.fluent_methods, config.get("fluent_methods", []))
    _extend_unique(instance.exempt_modules, config.get("exempt_modules", []))


def _extend_unique(target: list[str], additions: list[str]) -> None:
    """Add items to target list if not already present."""
    for item in additions:
        if item not in target:
            target.append(item)
