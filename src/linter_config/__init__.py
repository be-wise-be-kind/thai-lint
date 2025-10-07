"""Linter configuration system.

This package provides configuration loading and ignore directive parsing
for the thai-lint linter framework.
"""

from .ignore import IgnoreDirectiveParser
from .loader import LinterConfigLoader

__all__ = [
    "IgnoreDirectiveParser",
    "LinterConfigLoader",
]
