"""
Purpose: Configuration schema for print statements linter

Scope: Print statements linter configuration for all supported languages

Overview: Defines configuration schema for print statements linter. Provides PrintStatementConfig
    dataclass with enabled flag, ignore patterns list, allow_in_scripts setting (default True to
    allow print in __main__ blocks), and console_methods set (default includes log, warn, error,
    debug, info) for TypeScript/JavaScript console method detection. Supports per-file and
    per-directory config overrides through from_dict class method. Integrates with orchestrator's
    configuration system to allow users to customize detection via .thailint.yaml configuration.

Dependencies: dataclasses module for configuration structure, typing module for type hints

Exports: PrintStatementConfig dataclass

Interfaces: from_dict(config, language) -> PrintStatementConfig for configuration loading from dictionary

Implementation: Dataclass with defaults matching common use cases and language-specific override support
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PrintStatementConfig:
    """Configuration for print statements linter."""

    enabled: bool = True
    ignore: list[str] = field(default_factory=list)
    allow_in_scripts: bool = True
    console_methods: set[str] = field(
        default_factory=lambda: {"log", "warn", "error", "debug", "info"}
    )

    @classmethod
    def from_dict(
        cls, config: dict[str, Any], language: str | None = None
    ) -> "PrintStatementConfig":
        """Load configuration from dictionary with language-specific overrides.

        Args:
            config: Dictionary containing configuration values
            language: Programming language (python, typescript, javascript)
                for language-specific settings

        Returns:
            PrintStatementConfig instance with values from dictionary
        """
        # Get language-specific config if available
        if language and language in config:
            lang_config = config[language]
            allow_in_scripts = lang_config.get(
                "allow_in_scripts", config.get("allow_in_scripts", True)
            )
            console_methods = set(
                lang_config.get(
                    "console_methods",
                    config.get("console_methods", ["log", "warn", "error", "debug", "info"]),
                )
            )
        else:
            allow_in_scripts = config.get("allow_in_scripts", True)
            console_methods = set(
                config.get("console_methods", ["log", "warn", "error", "debug", "info"])
            )

        ignore_patterns = config.get("ignore", [])
        if not isinstance(ignore_patterns, list):
            ignore_patterns = []

        return cls(
            enabled=config.get("enabled", True),
            ignore=ignore_patterns,
            allow_in_scripts=allow_in_scripts,
            console_methods=console_methods,
        )
