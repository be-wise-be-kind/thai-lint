"""
File: src/linters/print_statements/__init__.py

Purpose: Print statements linter package exports and convenience functions

Exports: PrintStatementRule class, PrintStatementConfig dataclass, lint() convenience function

Depends: .linter for PrintStatementRule, .config for PrintStatementConfig

Implements: lint(file_path, config) -> list[Violation] for simple linting operations

Related: src/linters/magic_numbers/__init__.py, src/core/base.py

Overview: Provides the public interface for the print statements linter package. Exports main
    PrintStatementRule class for use by the orchestrator and PrintStatementConfig for configuration.
    Includes lint() convenience function that provides a simple API for running the print statements
    linter on a file without directly interacting with the orchestrator. This module serves as the
    entry point for users of the print statements linter, hiding implementation details and exposing
    only the essential components needed for linting operations.

Usage: from src.linters.print_statements import PrintStatementRule, lint
    violations = lint("path/to/file.py")

Notes: Module-level exports with __all__ definition, convenience function wrapper
"""

from .config import PrintStatementConfig
from .linter import PrintStatementRule

__all__ = ["PrintStatementRule", "PrintStatementConfig", "lint"]


def lint(file_path: str, config: dict | None = None) -> list:
    """Convenience function for linting a file for print statements.

    Args:
        file_path: Path to the file to lint
        config: Optional configuration dictionary

    Returns:
        List of violations found
    """
    from pathlib import Path

    from src.orchestrator.core import FileLintContext

    rule = PrintStatementRule()
    context = FileLintContext(
        path=Path(file_path),
        lang="python",
    )

    return rule.check(context)
