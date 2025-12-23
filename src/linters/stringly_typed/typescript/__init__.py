"""
Purpose: TypeScript stringly-typed pattern detection module

Scope: TypeScript and JavaScript code analysis for stringly-typed patterns

Overview: Provides TypeScript-specific analyzers for detecting stringly-typed code patterns
    using tree-sitter AST analysis. Includes function call tracking for detecting function
    parameters that consistently receive limited string value sets. Supports both TypeScript
    and JavaScript files with shared detection logic. Designed to identify parameters that
    should use enums instead of raw strings.

Dependencies: tree-sitter, tree-sitter-typescript, TypeScriptBaseAnalyzer

Exports: TypeScriptCallTracker, TypeScriptFunctionCallPattern

Interfaces: TypeScriptCallTracker.find_patterns(code) -> list[TypeScriptFunctionCallPattern]

Implementation: Tree-sitter based AST traversal for call expression analysis
"""

from .analyzer import TypeScriptStringlyTypedAnalyzer
from .call_tracker import TypeScriptCallTracker, TypeScriptFunctionCallPattern

__all__ = [
    "TypeScriptCallTracker",
    "TypeScriptFunctionCallPattern",
    "TypeScriptStringlyTypedAnalyzer",
]
