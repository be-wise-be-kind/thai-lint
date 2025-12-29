"""
Purpose: LBYL (Look Before You Leap) linter package exports

Scope: Detect LBYL anti-patterns in Python code and suggest EAFP alternatives

Overview: Package providing LBYL pattern detection for Python code. Identifies common
    anti-patterns where explicit checks are performed before operations (e.g., if key in
    dict before dict[key]) and suggests EAFP (Easier to Ask Forgiveness than Permission)
    alternatives using try/except blocks. Supports 8 pattern types including dict key
    checking, hasattr, isinstance, file exists, length checks, None checks, string
    validation, and division safety checks.

Dependencies: ast module for Python parsing, src.core for base classes

Exports: LBYLConfig, LBYLPattern, BaseLBYLDetector

Interfaces: LBYLConfig.from_dict() for YAML configuration loading

Implementation: AST-based pattern detection with configurable pattern toggles
"""

from .config import LBYLConfig
from .pattern_detectors.base import BaseLBYLDetector, LBYLPattern

__all__ = [
    "LBYLConfig",
    "LBYLPattern",
    "BaseLBYLDetector",
]
