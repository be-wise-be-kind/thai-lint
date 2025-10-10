"""
Purpose: Configuration schema for Single Responsibility Principle linter

Scope: SRPConfig dataclass with max_methods, max_loc, and keyword settings

Overview: Defines configuration schema for SRP linter. Provides SRPConfig dataclass with
    max_methods field (default 7), max_loc field (default 200), and check_keywords flag
    (default True) with configurable responsibility keywords. Supports per-file and
    per-directory config overrides. Validates that thresholds are positive integers.
    Integrates with the orchestrator's configuration system to allow users to customize
    SRP thresholds via .thailint.yaml configuration files. Keywords list identifies
    generic class names that often indicate SRP violations (Manager, Handler, etc.).

Dependencies: dataclasses, typing

Exports: SRPConfig dataclass

Interfaces: SRPConfig(max_methods, max_loc, check_keywords, keywords), from_dict class method

Implementation: Dataclass with validation and defaults, heuristic-based SRP detection thresholds
"""

from dataclasses import dataclass, field
from typing import Any

# Default SRP threshold constants
DEFAULT_MAX_METHODS_PER_CLASS = 7
DEFAULT_MAX_LOC_PER_CLASS = 200


@dataclass
class SRPConfig:
    """Configuration for SRP linter."""

    max_methods: int = DEFAULT_MAX_METHODS_PER_CLASS  # Maximum methods per class
    max_loc: int = DEFAULT_MAX_LOC_PER_CLASS  # Maximum lines of code per class
    enabled: bool = True
    check_keywords: bool = True
    keywords: list[str] = field(
        default_factory=lambda: ["Manager", "Handler", "Processor", "Utility", "Helper"]
    )
    ignore: list[str] = field(default_factory=list)  # Path patterns to ignore

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_methods <= 0:
            raise ValueError(f"max_methods must be positive, got {self.max_methods}")
        if self.max_loc <= 0:
            raise ValueError(f"max_loc must be positive, got {self.max_loc}")

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "SRPConfig":
        """Load configuration from dictionary with language-specific overrides.

        Args:
            config: Dictionary containing configuration values
            language: Programming language (python, typescript, javascript) for language-specific thresholds

        Returns:
            SRPConfig instance with values from dictionary
        """
        # Get language-specific config if available
        if language and language in config:
            lang_config = config[language]
            max_methods = lang_config.get(
                "max_methods", config.get("max_methods", DEFAULT_MAX_METHODS_PER_CLASS)
            )
            max_loc = lang_config.get("max_loc", config.get("max_loc", DEFAULT_MAX_LOC_PER_CLASS))
        else:
            max_methods = config.get("max_methods", DEFAULT_MAX_METHODS_PER_CLASS)
            max_loc = config.get("max_loc", DEFAULT_MAX_LOC_PER_CLASS)

        return cls(
            max_methods=max_methods,
            max_loc=max_loc,
            enabled=config.get("enabled", True),
            check_keywords=config.get("check_keywords", True),
            keywords=config.get(
                "keywords", ["Manager", "Handler", "Processor", "Utility", "Helper"]
            ),
            ignore=config.get("ignore", []),
        )
