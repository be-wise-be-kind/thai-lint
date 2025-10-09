"""
Purpose: Shared utility functions for linter framework patterns

Scope: Common config loading, metadata access, and context validation utilities for all linters

Overview: Provides reusable helper functions to eliminate duplication across linter implementations.
    Includes utilities for loading configuration from context metadata with language-specific overrides,
    extracting metadata fields safely with type validation, and validating context state. Standardizes
    common patterns used by srp, nesting, dry, and file_placement linters. Reduces boilerplate code
    while maintaining type safety and proper error handling.

Dependencies: BaseLintContext from src.core.base

Exports: get_metadata, get_metadata_value, load_linter_config, has_file_content

Interfaces: All functions take BaseLintContext and return typed values (dict, str, bool, Any)

Implementation: Type-safe metadata access with fallbacks, generic config loading with language support
"""

from typing import Any, Protocol, TypeVar

from src.core.base import BaseLintContext


# Protocol for config classes that support from_dict
class ConfigProtocol(Protocol):
    """Protocol for configuration classes with from_dict class method."""

    @classmethod
    def from_dict(
        cls, config_dict: dict[str, Any], language: str | None = None
    ) -> "ConfigProtocol":
        """Create config instance from dictionary."""


# Type variable for config classes
ConfigType = TypeVar("ConfigType", bound=ConfigProtocol)  # pylint: disable=invalid-name


def get_metadata(context: BaseLintContext) -> dict[str, Any]:
    """Get metadata dictionary from context with safe fallback.

    Args:
        context: Lint context containing optional metadata

    Returns:
        Metadata dictionary, or empty dict if not available
    """
    metadata = getattr(context, "metadata", None)
    if metadata is None or not isinstance(metadata, dict):
        return {}
    return dict(metadata)  # Explicit cast to satisfy type checker


def get_metadata_value(context: BaseLintContext, key: str, default: Any = None) -> Any:
    """Get specific value from context metadata with safe fallback.

    Args:
        context: Lint context containing optional metadata
        key: Metadata key to retrieve
        default: Default value if key not found

    Returns:
        Metadata value or default
    """
    metadata = get_metadata(context)
    return metadata.get(key, default)


def get_language(context: BaseLintContext) -> str | None:
    """Get language from context.

    Args:
        context: Lint context containing optional language

    Returns:
        Language string or None
    """
    return getattr(context, "language", None)


def get_project_root(context: BaseLintContext) -> str | None:
    """Get project root from context metadata.

    Args:
        context: Lint context containing optional metadata

    Returns:
        Project root path or None
    """
    metadata = get_metadata(context)
    project_root = metadata.get("project_root")
    return str(project_root) if project_root is not None else None


def load_linter_config(
    context: BaseLintContext,
    config_key: str,
    config_class: type[ConfigType],
) -> ConfigType:
    """Load linter configuration from context metadata with language-specific overrides.

    Args:
        context: Lint context containing metadata
        config_key: Key to look up in metadata (e.g., "srp", "nesting", "dry")
        config_class: Configuration class with from_dict() class method

    Returns:
        Configuration instance (uses default config if metadata unavailable)

    Example:
        config = load_linter_config(context, "srp", SRPConfig)
    """
    metadata = get_metadata(context)
    config_dict = metadata.get(config_key, {})

    if not isinstance(config_dict, dict):
        return config_class()

    # Get language for language-specific thresholds
    language = get_language(context)

    # Call from_dict with language if config class supports it
    # This works for SRPConfig, NestingConfig, etc.
    try:
        result = config_class.from_dict(config_dict, language=language)
        return result  # type: ignore[return-value]
    except TypeError:
        # Fallback for config classes that don't support language parameter
        result_fallback = config_class.from_dict(config_dict)
        return result_fallback  # type: ignore[return-value]


def has_file_content(context: BaseLintContext) -> bool:
    """Check if context has file content available.

    Args:
        context: Lint context to check

    Returns:
        True if file_content is not None
    """
    return context.file_content is not None


def has_file_path(context: BaseLintContext) -> bool:
    """Check if context has file path available.

    Args:
        context: Lint context to check

    Returns:
        True if file_path is not None
    """
    return context.file_path is not None


def should_process_file(context: BaseLintContext) -> bool:
    """Check if file should be processed (has both content and path).

    Args:
        context: Lint context to check

    Returns:
        True if file has both content and path available
    """
    return has_file_content(context) and has_file_path(context)
