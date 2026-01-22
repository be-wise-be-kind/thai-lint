"""
Purpose: CQS (Command-Query Separation) linter package exports

Scope: Detect CQS violations in Python and TypeScript code

Overview: Package providing CQS violation detection for Python and TypeScript code.
    Identifies functions that mix INPUT operations (queries that return values captured
    in variables) and OUTPUT operations (commands that perform side effects without
    capturing return values). Functions should either query state and return a value,
    or command a change and return nothing. Mixing these violates CQS principles and
    makes code harder to reason about.

Dependencies: ast module for Python parsing, tree-sitter for TypeScript parsing

Exports: CQSConfig, CQSPattern, InputOperation, OutputOperation

Interfaces: CQSConfig.from_dict() for YAML configuration loading

Implementation: AST-based pattern detection with configurable ignore rules
"""

from .config import CQSConfig
from .input_detector import InputDetector
from .output_detector import OutputDetector
from .python_analyzer import PythonCQSAnalyzer
from .types import CQSPattern, InputOperation, OutputOperation

__all__ = [
    "CQSConfig",
    "CQSPattern",
    "InputDetector",
    "InputOperation",
    "OutputDetector",
    "OutputOperation",
    "PythonCQSAnalyzer",
]
