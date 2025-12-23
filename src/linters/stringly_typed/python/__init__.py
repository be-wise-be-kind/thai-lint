"""
Purpose: Python-specific detection for stringly-typed patterns

Scope: Python AST analysis for membership validation, equality chains, and function calls

Overview: Exposes Python analysis components for detecting stringly-typed patterns in Python
    source code. Includes validation_detector for finding 'x in ("a", "b")' patterns,
    conditional_detector for finding if/elif chains and match statements, call_tracker for
    finding function calls with string arguments, and analyzer for coordinating detection
    across Python files. Uses AST traversal to identify where plain strings are used instead
    of proper enums or typed alternatives.

Dependencies: ast module for Python AST parsing

Exports: MembershipValidationDetector, ConditionalPatternDetector, FunctionCallTracker,
    PythonStringlyTypedAnalyzer

Interfaces: Detector and analyzer classes for Python stringly-typed pattern detection

Implementation: AST NodeVisitor pattern for traversing Python syntax trees
"""

from .analyzer import PythonStringlyTypedAnalyzer
from .call_tracker import FunctionCallTracker
from .conditional_detector import ConditionalPatternDetector
from .validation_detector import MembershipValidationDetector

__all__ = [
    "ConditionalPatternDetector",
    "FunctionCallTracker",
    "MembershipValidationDetector",
    "PythonStringlyTypedAnalyzer",
]
