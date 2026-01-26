"""
Purpose: Pattern detector exports for LBYL linter

Scope: All AST-based pattern detectors for LBYL anti-pattern detection

Overview: Exports pattern detector classes for the LBYL linter. Each detector is an
    AST NodeVisitor that identifies specific LBYL anti-patterns. Detectors include
    dict key checking, hasattr, isinstance, file exists, length checks, None checks,
    string validators, and division zero-checks.

Dependencies: ast module, base detector class

Exports: BaseLBYLDetector, LBYLPattern, DictKeyDetector, DictKeyPattern, HasattrDetector,
    HasattrPattern, IsinstanceDetector, IsinstancePattern, FileExistsDetector,
    FileExistsPattern, LenCheckDetector, LenCheckPattern, NoneCheckDetector,
    NoneCheckPattern, StringValidatorDetector, StringValidatorPattern,
    DivisionCheckDetector, DivisionCheckPattern

Interfaces: find_patterns(tree: ast.AST) -> list[LBYLPattern]

Implementation: Modular detector pattern for extensible LBYL detection
"""

from .base import BaseLBYLDetector, LBYLPattern
from .dict_key_detector import DictKeyDetector, DictKeyPattern
from .division_check_detector import DivisionCheckDetector, DivisionCheckPattern
from .file_exists_detector import FileExistsDetector, FileExistsPattern
from .hasattr_detector import HasattrDetector, HasattrPattern
from .isinstance_detector import IsinstanceDetector, IsinstancePattern
from .len_check_detector import LenCheckDetector, LenCheckPattern
from .none_check_detector import NoneCheckDetector, NoneCheckPattern
from .string_validator_detector import StringValidatorDetector, StringValidatorPattern

__all__ = [
    "BaseLBYLDetector",
    "LBYLPattern",
    "DictKeyDetector",
    "DictKeyPattern",
    "DivisionCheckDetector",
    "DivisionCheckPattern",
    "FileExistsDetector",
    "FileExistsPattern",
    "HasattrDetector",
    "HasattrPattern",
    "IsinstanceDetector",
    "IsinstancePattern",
    "LenCheckDetector",
    "LenCheckPattern",
    "NoneCheckDetector",
    "NoneCheckPattern",
    "StringValidatorDetector",
    "StringValidatorPattern",
]
