"""
Purpose: Core constants and enums used across the thai-lint codebase

Scope: Centralized definitions for language names, storage modes, config extensions

Overview: Provides type-safe enums and constants for consistent stringly-typed patterns
    across the codebase. Includes Language enum for programming language detection,
    StorageMode for cache storage options, and CONFIG_EXTENSIONS for config file
    discovery. Using enums ensures compile-time safety and IDE autocompletion.

Dependencies: enum module

Exports: Language enum, StorageMode enum, CONFIG_EXTENSIONS, IgnoreDirective enum,
    HEADER_SCAN_LINES, MAX_ATTRIBUTE_CHAIN_DEPTH

Interfaces: Use enum values instead of string literals throughout codebase

Implementation: Standard Python enums with string values for compatibility
"""

from enum import Enum


class Language(str, Enum):
    """Supported programming languages for linting."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    MARKDOWN = "markdown"


class StorageMode(str, Enum):
    """Storage modes for DRY linter cache."""

    MEMORY = "memory"
    TEMPFILE = "tempfile"


class IgnoreDirective(str, Enum):
    """Inline ignore directive types."""

    IGNORE = "ignore"
    IGNORE_FILE = "ignore-file"


# Valid config file extensions
CONFIG_EXTENSIONS: tuple[str, str] = (".yaml", ".yml")

# Number of lines to scan at file start for ignore directives and headers
HEADER_SCAN_LINES: int = 10

# Maximum depth for attribute chain traversal (e.g., obj.attr.attr2.attr3)
MAX_ATTRIBUTE_CHAIN_DEPTH: int = 3
