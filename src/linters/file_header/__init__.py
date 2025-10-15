"""
File: src/linters/file_header/__init__.py
Purpose: File header linter module initialization
Exports: FileHeaderRule
Depends: linter.FileHeaderRule
Implements: Module-level exports for clean API
Related: linter.py for main rule implementation

Overview:
    Initializes the file header linter module providing multi-language file header
    validation with mandatory field checking, atemporal language detection, and configuration
    support. Main entry point for file header linting functionality.

Usage:
    from src.linters.file_header import FileHeaderRule
    rule = FileHeaderRule()
    violations = rule.check(context)

Notes: Follows standard Python module initialization pattern with __all__ export control
"""

from .linter import FileHeaderRule

__all__ = ["FileHeaderRule"]
