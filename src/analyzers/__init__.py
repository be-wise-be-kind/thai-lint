"""
Purpose: Analyzers package for language-specific AST analysis base classes

Scope: Language analyzers (TypeScript, Python) providing shared parsing and traversal utilities

Overview: Package containing base analyzer classes for different programming languages.
    Provides common tree-sitter initialization, AST parsing, and node traversal patterns
    to eliminate duplicate code across linters. Each language has a base analyzer class
    (TypeScriptBaseAnalyzer, etc.) that linter-specific analyzers extend. Centralizes
    language parsing infrastructure to improve maintainability and consistency.

Dependencies: tree-sitter, language-specific tree-sitter bindings

Exports: TypeScriptBaseAnalyzer

Interfaces: Base analyzer classes with parse(), walk_tree(), and extract() methods

Implementation: Composition-based design for linter analyzers to use base utilities
"""

from .typescript_base import TypeScriptBaseAnalyzer

__all__ = ["TypeScriptBaseAnalyzer"]
