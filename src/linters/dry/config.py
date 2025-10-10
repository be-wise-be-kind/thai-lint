"""
Purpose: Configuration schema for DRY linter with caching support

Scope: DRYConfig dataclass with validation, defaults, and loading from dictionary

Overview: Defines configuration structure for the DRY linter including duplicate detection thresholds,
    caching settings, and ignore patterns. Provides validation of configuration values to ensure
    sensible defaults and prevent misconfiguration. Supports loading from YAML configuration files
    through from_dict classmethod. Cache enabled by default for performance on large codebases.

Dependencies: Python dataclasses module

Exports: DRYConfig dataclass

Interfaces: DRYConfig.__init__, DRYConfig.from_dict(config: dict) -> DRYConfig

Implementation: Dataclass with field defaults, __post_init__ validation, and dict-based construction
"""

from dataclasses import dataclass, field
from typing import Any

# Default configuration constants
DEFAULT_MIN_DUPLICATE_LINES = 3
DEFAULT_MIN_DUPLICATE_TOKENS = 30


@dataclass
class DRYConfig:  # pylint: disable=too-many-instance-attributes
    """Configuration for DRY linter.

    Note: Pylint too-many-instance-attributes disabled. This is a configuration
    dataclass serving as a data container for related DRY linter settings.
    All attributes are cohesively related (detection thresholds, language
    overrides, storage mode, filtering). Splitting would reduce cohesion and make
    configuration loading more complex without meaningful benefit.
    """

    enabled: bool = False  # Must be explicitly enabled
    min_duplicate_lines: int = DEFAULT_MIN_DUPLICATE_LINES
    min_duplicate_tokens: int = DEFAULT_MIN_DUPLICATE_TOKENS
    min_occurrences: int = 2  # Minimum occurrences to report (default: 2)

    # Language-specific overrides
    python_min_occurrences: int | None = None
    typescript_min_occurrences: int | None = None
    javascript_min_occurrences: int | None = None

    # Storage settings
    storage_mode: str = "memory"  # Options: "memory" (default) or "tempfile"

    # Ignore patterns
    ignore_patterns: list[str] = field(default_factory=lambda: ["tests/", "__init__.py"])

    # Block filters (extensible false positive filtering)
    filters: dict[str, bool] = field(
        default_factory=lambda: {
            "keyword_argument_filter": True,  # Filter keyword argument blocks
            "import_group_filter": True,  # Filter import statement groups
        }
    )

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.min_duplicate_lines <= 0:
            raise ValueError(
                f"min_duplicate_lines must be positive, got {self.min_duplicate_lines}"
            )
        if self.min_duplicate_tokens <= 0:
            raise ValueError(
                f"min_duplicate_tokens must be positive, got {self.min_duplicate_tokens}"
            )
        if self.min_occurrences <= 0:
            raise ValueError(f"min_occurrences must be positive, got {self.min_occurrences}")
        if self.storage_mode not in ("memory", "tempfile"):
            raise ValueError(
                f"storage_mode must be 'memory' or 'tempfile', got '{self.storage_mode}'"
            )

    def get_min_occurrences_for_language(self, language: str) -> int:
        """Get minimum occurrences threshold for a specific language.

        Args:
            language: Language identifier (e.g., "python", "typescript", "javascript")

        Returns:
            Minimum occurrences threshold for the language, or global default
        """
        language_lower = language.lower()

        language_overrides = {
            "python": self.python_min_occurrences,
            "typescript": self.typescript_min_occurrences,
            "javascript": self.javascript_min_occurrences,
        }

        override = language_overrides.get(language_lower)
        return override if override is not None else self.min_occurrences

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "DRYConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values

        Returns:
            DRYConfig instance with values from dictionary
        """
        # Extract language-specific min_occurrences
        python_config = config.get("python", {})
        typescript_config = config.get("typescript", {})
        javascript_config = config.get("javascript", {})

        # Load filter configuration (merge with defaults)
        default_filters = {
            "keyword_argument_filter": True,
            "import_group_filter": True,
        }
        custom_filters = config.get("filters", {})
        filters = {**default_filters, **custom_filters}

        return cls(
            enabled=config.get("enabled", False),
            min_duplicate_lines=config.get("min_duplicate_lines", DEFAULT_MIN_DUPLICATE_LINES),
            min_duplicate_tokens=config.get("min_duplicate_tokens", DEFAULT_MIN_DUPLICATE_TOKENS),
            min_occurrences=config.get("min_occurrences", 2),
            python_min_occurrences=python_config.get("min_occurrences"),
            typescript_min_occurrences=typescript_config.get("min_occurrences"),
            javascript_min_occurrences=javascript_config.get("min_occurrences"),
            storage_mode=config.get("storage_mode", "memory"),
            ignore_patterns=config.get("ignore", []),
            filters=filters,
        )
