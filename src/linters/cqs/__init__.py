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

Exports: CQSConfig, CQSPattern, CQSRule, FunctionAnalyzer, InputOperation, OutputOperation,
    PythonCQSAnalyzer, build_cqs_violation

Interfaces: CQSConfig.from_dict() for YAML configuration loading,
    CQSRule.check() for BaseLintRule interface

Implementation: AST-based pattern detection with configurable ignore rules
"""

from .config import CQSConfig
from .function_analyzer import FunctionAnalyzer
from .input_detector import InputDetector
from .linter import CQSRule
from .output_detector import OutputDetector
from .python_analyzer import PythonCQSAnalyzer
from .types import CQSPattern, InputOperation, OutputOperation
from .violation_builder import build_cqs_violation

__all__ = [
    "CQSConfig",
    "CQSPattern",
    "CQSRule",
    "FunctionAnalyzer",
    "InputDetector",
    "InputOperation",
    "OutputDetector",
    "OutputOperation",
    "PythonCQSAnalyzer",
    "build_cqs_violation",
]
