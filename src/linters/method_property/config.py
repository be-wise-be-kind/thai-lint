"""
Purpose: Configuration schema for method-should-be-property linter

Scope: Method property linter configuration for Python files

Overview: Defines configuration schema for method-should-be-property linter. Provides
    MethodPropertyConfig dataclass with enabled flag, max_body_statements threshold (default 3)
    for determining when a method body is too complex to be a property candidate, and ignore
    patterns list for excluding specific files or directories. Includes configurable action verb
    exclusions (prefixes and names) with sensible defaults that can be extended or overridden.
    Supports per-file and per-directory config overrides through from_dict class method.
    Integrates with orchestrator's configuration system via .thailint.yaml.

Dependencies: dataclasses module for configuration structure, typing module for type hints

Exports: MethodPropertyConfig dataclass, DEFAULT_EXCLUDE_PREFIXES, DEFAULT_EXCLUDE_NAMES

Interfaces: from_dict(config, language) -> MethodPropertyConfig for configuration loading

Implementation: Dataclass with defaults matching Pythonic conventions and common use cases
"""

from dataclasses import dataclass, field
from typing import Any

# Default action verb prefixes - methods starting with these are excluded
# These represent actions/transformations, not property access
DEFAULT_EXCLUDE_PREFIXES: tuple[str, ...] = (
    "to_",  # Transformation: to_dict, to_json, to_string
    "dump_",  # Serialization: dump_to_json, dump_to_apigw
    "generate_",  # Factory: generate_report, generate_html
    "create_",  # Factory: create_instance, create_config
    "build_",  # Construction: build_query, build_html
    "make_",  # Factory: make_request, make_connection
    "render_",  # Output: render_template, render_html
    "compute_",  # Calculation: compute_hash, compute_total
    "calculate_",  # Calculation: calculate_sum, calculate_average
)

# Default action verb names - exact method names that are excluded
# These are lifecycle hooks, display actions, and resource operations
DEFAULT_EXCLUDE_NAMES: frozenset[str] = frozenset(
    {
        "finalize",  # Lifecycle hook
        "serialize",  # Transformation
        "dump",  # Serialization
        "validate",  # Validation action
        "show",  # Display action
        "display",  # Display action
        "print",  # Output action
        "refresh",  # Update action
        "reset",  # State action
        "clear",  # State action
        "close",  # Resource action
        "open",  # Resource action
        "save",  # Persistence action
        "load",  # Persistence action
        "execute",  # Action
        "run",  # Action
    }
)


def _load_list_config(
    config: dict[str, Any], key: str, override_key: str, default: tuple[str, ...]
) -> tuple[str, ...]:
    """Load a list config with extend/override semantics."""
    if override_key in config and isinstance(config[override_key], list):
        return tuple(config[override_key])
    if key in config and isinstance(config[key], list):
        return default + tuple(config[key])
    return default


def _load_set_config(
    config: dict[str, Any], key: str, override_key: str, default: frozenset[str]
) -> frozenset[str]:
    """Load a set config with extend/override semantics."""
    if override_key in config and isinstance(config[override_key], list):
        return frozenset(config[override_key])
    if key in config and isinstance(config[key], list):
        return default | frozenset(config[key])
    return default


@dataclass
class MethodPropertyConfig:  # thailint: ignore[dry]
    """Configuration for method-should-be-property linter."""

    enabled: bool = True
    max_body_statements: int = 3
    ignore: list[str] = field(default_factory=list)
    ignore_methods: list[str] = field(default_factory=list)

    # Action verb exclusions (extend defaults or override)
    exclude_prefixes: tuple[str, ...] = DEFAULT_EXCLUDE_PREFIXES
    exclude_names: frozenset[str] = DEFAULT_EXCLUDE_NAMES

    # dry: ignore-block
    @classmethod
    def from_dict(
        cls, config: dict[str, Any] | None, language: str | None = None
    ) -> "MethodPropertyConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values, or None
            language: Programming language (unused, for interface compatibility)

        Returns:
            MethodPropertyConfig instance with values from dictionary
        """
        if config is None:
            return cls()

        ignore_patterns = config.get("ignore", [])
        if not isinstance(ignore_patterns, list):
            ignore_patterns = []

        ignore_methods = config.get("ignore_methods", [])
        if not isinstance(ignore_methods, list):
            ignore_methods = []

        return cls(
            enabled=config.get("enabled", True),
            max_body_statements=config.get("max_body_statements", 3),
            ignore=ignore_patterns,
            ignore_methods=ignore_methods,
            exclude_prefixes=_load_list_config(
                config, "exclude_prefixes", "exclude_prefixes_override", DEFAULT_EXCLUDE_PREFIXES
            ),
            exclude_names=_load_set_config(
                config, "exclude_names", "exclude_names_override", DEFAULT_EXCLUDE_NAMES
            ),
        )
