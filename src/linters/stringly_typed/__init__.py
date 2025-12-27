"""
Purpose: Stringly-typed linter package exports

Scope: Public API for stringly-typed linter module

Overview: Provides the public interface for the stringly-typed linter package. Exports
    StringlyTypedConfig for configuration and StringlyTypedRule for linting. The stringly-typed
    linter detects code patterns where plain strings are used instead of proper enums or typed
    alternatives, helping identify potential type safety improvements. Supports cross-file
    detection to find repeated string patterns across the codebase. Includes IgnoreChecker
    for inline ignore directive support.

Dependencies: .config for StringlyTypedConfig, .linter for StringlyTypedRule,
    .storage for StringlyTypedStorage, .ignore_checker for IgnoreChecker

Exports: StringlyTypedConfig, StringlyTypedRule, StringlyTypedStorage, StoredPattern,
    IgnoreChecker

Interfaces: Configuration loading via StringlyTypedConfig.from_dict(),
    StringlyTypedRule.check() and finalize() for linting, IgnoreChecker.filter_violations()

Implementation: Module-level exports with __all__ definition
"""

from src.linters.stringly_typed.config import StringlyTypedConfig
from src.linters.stringly_typed.ignore_checker import IgnoreChecker
from src.linters.stringly_typed.linter import StringlyTypedRule
from src.linters.stringly_typed.storage import StoredPattern, StringlyTypedStorage

__all__ = [
    "StringlyTypedConfig",
    "IgnoreChecker",
    "StringlyTypedRule",
    "StringlyTypedStorage",
    "StoredPattern",
]
