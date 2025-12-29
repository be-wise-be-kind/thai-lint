"""
Purpose: Lazy-ignores linter package exports

Scope: Detect unjustified linting suppressions in code files

Overview: Package providing lazy-ignores linter functionality. Detects when AI agents add
    linting suppressions (noqa, type:ignore, pylint:disable, nosec, thailint:ignore, etc.)
    without proper justification in the file header's Suppressions section. Enforces
    header-based declaration model where all suppressions must be documented with human
    approval.

Dependencies: src.core for base types, re for pattern matching

Exports: IgnoreType, IgnoreDirective, SuppressionEntry, LazyIgnoresConfig

Interfaces: LazyIgnoresConfig.from_dict() for YAML configuration loading

Implementation: Enum and dataclass definitions for ignore directive representation
"""

from .config import LazyIgnoresConfig
from .types import IgnoreDirective, IgnoreType, SuppressionEntry

__all__ = [
    "IgnoreType",
    "IgnoreDirective",
    "SuppressionEntry",
    "LazyIgnoresConfig",
]
