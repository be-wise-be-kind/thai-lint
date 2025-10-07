"""Core framework components for thai-lint.

This package contains the foundational abstractions and types that
power the plugin architecture.
"""

from .base import BaseLintContext, BaseLintRule
from .registry import RuleRegistry
from .types import Severity, Violation

__all__ = [
    "BaseLintContext",
    "BaseLintRule",
    "RuleRegistry",
    "Severity",
    "Violation",
]
