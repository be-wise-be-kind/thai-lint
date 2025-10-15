"""
File: src/linters/file_header/config.py
Purpose: Configuration model for file header linter
Exports: FileHeaderConfig dataclass
Depends: dataclasses, pathlib
Implements: Configuration with validation and defaults
Related: linter.py for configuration usage

Overview:
    Defines configuration structure for file header linter including required fields
    per language, ignore patterns, and validation options. Provides defaults matching
    ai-doc-standard.md requirements and supports loading from .thailint.yaml configuration.

Usage:
    config = FileHeaderConfig()
    config = FileHeaderConfig.from_dict(config_dict, "python")

Notes: Dataclass with validation and language-specific defaults
"""

from dataclasses import dataclass, field


@dataclass
class FileHeaderConfig:
    """Configuration for file header linting."""

    # Required fields by language
    required_fields_python: list[str] = field(
        default_factory=lambda: [
            "Purpose",
            "Scope",
            "Overview",
            "Dependencies",
            "Exports",
            "Interfaces",
            "Implementation",
        ]
    )

    # Enforce atemporal language checking
    enforce_atemporal: bool = True

    # Patterns to ignore (file paths)
    ignore: list[str] = field(
        default_factory=lambda: ["test/**", "**/migrations/**", "**/__init__.py"]
    )

    @classmethod
    def from_dict(cls, config_dict: dict, language: str) -> "FileHeaderConfig":
        """Create config from dictionary.

        Args:
            config_dict: Dictionary of configuration values
            language: Programming language for language-specific config

        Returns:
            FileHeaderConfig instance with values from dictionary
        """
        return cls(
            required_fields_python=config_dict.get("required_fields", {}).get(
                "python", cls().required_fields_python
            ),
            enforce_atemporal=config_dict.get("enforce_atemporal", True),
            ignore=config_dict.get("ignore", cls().ignore),
        )
