"""
Purpose: Configuration model for file header linter

Scope: File header linter configuration for all supported languages

Overview: Defines configuration structure for file header linter including required fields
    per language, ignore patterns, and validation options. Provides defaults matching
    FILE_HEADER_STANDARDS.md requirements and supports loading from .thailint.yaml configuration.
    Supports Python, TypeScript/JavaScript, Bash, Markdown, CSS, and Jinja/HTML template file
    types with language-specific required field sets. Includes the optional Tags field with an
    allowed_tags controlled vocabulary, atemporal language enforcement configuration, and file
    ignore patterns.

Dependencies: dataclasses module for configuration structure

Exports: FileHeaderConfig dataclass

Interfaces: from_dict(config_dict, language) -> FileHeaderConfig for configuration loading

Implementation: Dataclass with language-specific field lists and factory method for config loading
"""

from dataclasses import dataclass, field

# Default required fields per language. CSS-style names use Title Case; Markdown frontmatter
# uses lowercase keys. Jinja/HTML templates require only the prose fields.
DEFAULT_REQUIRED_FIELDS: dict[str, list[str]] = {
    "python": [
        "Purpose",
        "Scope",
        "Overview",
        "Dependencies",
        "Exports",
        "Interfaces",
        "Implementation",
    ],
    "typescript": [
        "Purpose",
        "Scope",
        "Overview",
        "Dependencies",
        "Exports",
        "Props/Interfaces",
        "State/Behavior",
    ],
    "bash": ["Purpose", "Scope", "Overview", "Dependencies", "Exports", "Usage", "Environment"],
    "markdown": ["purpose", "scope", "overview", "audience", "status"],
    "css": ["Purpose", "Scope", "Overview", "Dependencies", "Exports", "Interfaces", "Environment"],
    "html": ["Purpose", "Scope", "Overview"],
}


@dataclass
class FileHeaderConfig:
    """Configuration for file header linting."""

    # Required header fields keyed by language (javascript reuses the typescript set at lookup)
    required_fields_by_language: dict[str, list[str]] = field(
        default_factory=lambda: {
            lang: list(fields) for lang, fields in DEFAULT_REQUIRED_FIELDS.items()
        }
    )

    # Allowed tag vocabulary for the optional Tags field (empty = any tag accepted)
    allowed_tags: list[str] = field(default_factory=list)

    # Enforce atemporal language checking
    enforce_atemporal: bool = True

    # Patterns to ignore (file paths)
    ignore: list[str] = field(
        default_factory=lambda: ["test/**", "**/migrations/**", "**/__init__.py"]
    )

    def required_fields_for(self, language: str) -> list[str]:
        """Return the required fields configured for a language ([] if none)."""
        return self.required_fields_by_language.get(language, [])

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
            required_fields_by_language=cls._resolve_required_fields(
                required_fields, defaults.required_fields_by_language
            ),
            allowed_tags=config_dict.get("allowed_tags", defaults.allowed_tags),
            enforce_atemporal=config_dict.get("enforce_atemporal", True),
            ignore=config_dict.get("ignore", defaults.ignore),
        )

    @staticmethod
    def _resolve_required_fields(
        required_fields: list | dict, defaults: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        """Resolve the required-fields config into a per-language map.

        A list applies the same fields to every language; a dict overrides per language
        while falling back to defaults for languages not specified.
        """
        if isinstance(required_fields, list):
            return dict.fromkeys(defaults, required_fields)

        return {lang: required_fields.get(lang, fields) for lang, fields in defaults.items()}
