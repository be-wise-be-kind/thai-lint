"""
File: src/linters/file_header/config.py
Purpose: Configuration model for file header linter
Exports: FileHeaderConfig dataclass
Depends: dataclasses
Implements: Configuration with validation and defaults
Related: linter.py for configuration usage

Overview:
    Defines configuration structure for file header linter including required fields
    per language, ignore patterns, and validation options. Provides defaults matching
    ai-doc-standard.md requirements and supports loading from .thailint.yaml configuration.
    Supports Python, TypeScript/JavaScript, Bash, Markdown, and CSS file types.

Usage:
    config = FileHeaderConfig()
    config = FileHeaderConfig.from_dict(config_dict, "python")

Notes: Dataclass with validation and language-specific defaults
"""

from dataclasses import dataclass, field


@dataclass
class FileHeaderConfig:
    """Configuration for file header linting."""

    # Required fields by language - Python
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

    # Required fields by language - TypeScript/JavaScript
    required_fields_typescript: list[str] = field(
        default_factory=lambda: [
            "Purpose",
            "Scope",
            "Overview",
            "Dependencies",
            "Exports",
            "Props/Interfaces",
            "State/Behavior",
        ]
    )

    # Required fields by language - Bash
    required_fields_bash: list[str] = field(
        default_factory=lambda: [
            "Purpose",
            "Scope",
            "Overview",
            "Dependencies",
            "Exports",
            "Usage",
            "Environment",
        ]
    )

    # Required fields by language - Markdown (lowercase for YAML frontmatter)
    required_fields_markdown: list[str] = field(
        default_factory=lambda: [
            "purpose",
            "scope",
            "overview",
            "audience",
            "status",
        ]
    )

    # Required fields by language - CSS
    required_fields_css: list[str] = field(
        default_factory=lambda: [
            "Purpose",
            "Scope",
            "Overview",
            "Dependencies",
            "Exports",
            "Interfaces",
            "Environment",
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
        defaults = cls()
        required_fields = config_dict.get("required_fields", {})

        return cls(
            required_fields_python=required_fields.get("python", defaults.required_fields_python),
            required_fields_typescript=required_fields.get(
                "typescript", defaults.required_fields_typescript
            ),
            required_fields_bash=required_fields.get("bash", defaults.required_fields_bash),
            required_fields_markdown=required_fields.get(
                "markdown", defaults.required_fields_markdown
            ),
            required_fields_css=required_fields.get("css", defaults.required_fields_css),
            enforce_atemporal=config_dict.get("enforce_atemporal", True),
            ignore=config_dict.get("ignore", defaults.ignore),
        )
