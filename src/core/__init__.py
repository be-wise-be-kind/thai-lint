"""Core framework components for thai-lint.

This package contains the foundational abstractions and types that
power the plugin architecture.
"""

from .base import BaseLintContext, BaseLintRule
from .registry import RuleRegistry
from .rule_aliases import (
    LINTER_ALIASES,
    RULE_ID_ALIASES,
    is_deprecated_linter,
    is_deprecated_rule_id,
    resolve_linter_name,
    resolve_rule_id,
)
from .types import Severity, Violation

__all__ = [
    "BaseLintContext",
    "BaseLintRule",
    "LINTER_ALIASES",
    "RULE_ID_ALIASES",
    "RuleRegistry",
    "Severity",
    "Violation",
    "is_deprecated_linter",
    "is_deprecated_rule_id",
    "resolve_linter_name",
    "resolve_rule_id",
]
