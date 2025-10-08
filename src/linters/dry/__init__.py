"""
Purpose: DRY (Don't Repeat Yourself) linter module exports

Scope: Module-level exports for DRY linter components

Overview: Provides centralized exports for the DRY linter module components. Exposes the main
    DRYRule class for duplicate code detection, configuration dataclass, and analyzer components.
    Simplifies imports for consumers by providing a single import point for all DRY linter
    functionality. Follows the established pattern from nesting and SRP linters.

Dependencies: linter.DRYRule, config.DRYConfig

Exports: DRYRule (main rule class), DRYConfig (configuration)

Interfaces: Module-level __all__ list defining public API

Implementation: Standard Python module with explicit exports via __all__
"""

from .config import DRYConfig
from .linter import DRYRule

__all__ = ["DRYRule", "DRYConfig"]
