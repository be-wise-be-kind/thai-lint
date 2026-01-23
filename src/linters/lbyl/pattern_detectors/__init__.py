"""
Purpose: Pattern detector exports for LBYL linter

Scope: All AST-based pattern detectors for LBYL anti-pattern detection

Overview: Exports pattern detector classes for the LBYL linter. Each detector is an
    AST NodeVisitor that identifies specific LBYL anti-patterns. Detectors include
    dict key checking, hasattr, isinstance, file exists, and length checks.

Dependencies: ast module, base detector class

Exports: BaseLBYLDetector, LBYLPattern, DictKeyDetector, DictKeyPattern, HasattrDetector,
    HasattrPattern, IsinstanceDetector, IsinstancePattern, FileExistsDetector,
    FileExistsPattern, LenCheckDetector, LenCheckPattern

Interfaces: find_patterns(tree: ast.AST) -> list[LBYLPattern]

Implementation: Modular detector pattern for extensible LBYL detection
"""

from .base import BaseLBYLDetector, LBYLPattern
from .dict_key_detector import DictKeyDetector, DictKeyPattern
from .file_exists_detector import FileExistsDetector, FileExistsPattern
from .hasattr_detector import HasattrDetector, HasattrPattern
from .isinstance_detector import IsinstanceDetector, IsinstancePattern
from .len_check_detector import LenCheckDetector, LenCheckPattern

__all__ = [
    "BaseLBYLDetector",
    "LBYLPattern",
    "DictKeyDetector",
    "DictKeyPattern",
    "FileExistsDetector",
    "FileExistsPattern",
    "HasattrDetector",
    "HasattrPattern",
    "IsinstanceDetector",
    "IsinstancePattern",
    "LenCheckDetector",
    "LenCheckPattern",
]
