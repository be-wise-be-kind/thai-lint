"""
Purpose: Nesting depth linter package initialization

Scope: Exports for nesting depth linter module

Overview: Initializes the nesting depth linter package and exposes the main rule class for
    external use. Exports NestingDepthRule as the primary interface for the nesting linter,
    allowing the orchestrator to discover and instantiate the rule. Also exports configuration
    and analyzer classes for advanced use cases. This module serves as the entry point for
    the nesting linter functionality within the thai-lint framework.

Dependencies: NestingDepthRule, NestingConfig, PythonNestingAnalyzer, TypeScriptNestingAnalyzer

Exports: NestingDepthRule (primary), NestingConfig, PythonNestingAnalyzer, TypeScriptNestingAnalyzer

Interfaces: Standard Python package initialization with __all__ for explicit exports

Implementation: Simple re-export pattern for package interface
"""

from .config import NestingConfig
from .linter import NestingDepthRule
from .python_analyzer import PythonNestingAnalyzer
from .typescript_analyzer import TypeScriptNestingAnalyzer

__all__ = [
    "NestingDepthRule",
    "NestingConfig",
    "PythonNestingAnalyzer",
    "TypeScriptNestingAnalyzer",
]
