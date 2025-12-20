"""
Purpose: Stringly-typed linter package exports

Scope: Public API for stringly-typed linter module

Overview: Provides the public interface for the stringly-typed linter package. Exports
    StringlyTypedConfig for configuration of the linter. The stringly-typed linter detects
    code patterns where plain strings are used instead of proper enums or typed alternatives,
    helping identify potential type safety improvements. This module serves as the entry
    point for users of the stringly-typed linter.

Dependencies: .config for StringlyTypedConfig

Exports: StringlyTypedConfig dataclass

Interfaces: Configuration loading via StringlyTypedConfig.from_dict()

Implementation: Module-level exports with __all__ definition
"""

from src.linters.stringly_typed.config import StringlyTypedConfig

__all__ = ["StringlyTypedConfig"]
