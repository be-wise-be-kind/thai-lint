"""
Purpose: Configuration schema for stateless-class linter

Scope: Stateless class linter configuration for Python files

Overview: Defines configuration schema for stateless-class linter. Provides
    StatelessClassConfig dataclass with enabled flag, min_methods threshold (default 2)
    for determining minimum methods required to flag a class as stateless, and ignore
    patterns list for excluding specific files or directories. Supports per-file and
    per-directory config overrides through from_dict class method. Integrates with
    orchestrator's configuration system via .thailint.yaml.

Dependencies: dataclasses module for configuration structure, typing module for type hints

Exports: StatelessClassConfig dataclass

Interfaces: from_dict(config, language) -> StatelessClassConfig for configuration loading

Implementation: Dataclass with defaults matching stateless class detection conventions
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StatelessClassConfig:
    """Configuration for stateless-class linter."""

    enabled: bool = True
    min_methods: int = 2
    ignore: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(
        cls, config: dict[str, Any] | None, language: str | None = None
    ) -> "StatelessClassConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values, or None
            language: Programming language (unused, for interface compatibility)

        Returns:
            StatelessClassConfig instance with values from dictionary
        """
        if config is None:
            return cls()

        ignore_patterns = config.get("ignore", [])
        if not isinstance(ignore_patterns, list):
            ignore_patterns = []

        return cls(
            enabled=config.get("enabled", True),
            min_methods=config.get("min_methods", 2),
            ignore=ignore_patterns,
        )
