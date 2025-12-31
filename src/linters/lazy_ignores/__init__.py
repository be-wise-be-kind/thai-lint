"""
Purpose: Lazy-ignores linter package exports

Scope: Detect unjustified linting suppressions in code files

Overview: Package providing lazy-ignores linter functionality. Detects when AI agents add
    linting suppressions (noqa, type:ignore, pylint:disable, nosec, thailint:ignore, etc.)
    or test skips (pytest.mark.skip, it.skip, describe.skip) without proper justification
    in the file header's Suppressions section. Enforces header-based declaration model
    where all suppressions must be documented with human approval.

Dependencies: src.core for base types, re for pattern matching

Exports: IgnoreType, IgnoreDirective, SuppressionEntry, LazyIgnoresConfig,
    PythonIgnoreDetector, TypeScriptIgnoreDetector, TestSkipDetector, SuppressionsParser

Interfaces: LazyIgnoresConfig.from_dict() for YAML configuration loading

Implementation: Enum and dataclass definitions for ignore directive representation
"""

from .config import LazyIgnoresConfig
from .header_parser import SuppressionsParser
from .linter import LazyIgnoresRule
from .python_analyzer import PythonIgnoreDetector
from .skip_detector import TestSkipDetector
from .types import IgnoreDirective, IgnoreType, SuppressionEntry
from .typescript_analyzer import TypeScriptIgnoreDetector
from .violation_builder import build_orphaned_violation, build_unjustified_violation

__all__ = [
    "IgnoreType",
    "IgnoreDirective",
    "SuppressionEntry",
    "LazyIgnoresConfig",
    "PythonIgnoreDetector",
    "TypeScriptIgnoreDetector",
    "TestSkipDetector",
    "SuppressionsParser",
    "LazyIgnoresRule",
    "build_unjustified_violation",
    "build_orphaned_violation",
]
