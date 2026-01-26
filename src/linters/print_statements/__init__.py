"""
File: src/linters/print_statements/__init__.py

Purpose: Improper logging linter package exports and convenience functions

Exports: PrintStatementRule, ConditionalVerboseRule classes, PrintStatementConfig dataclass,
    lint() convenience function, ImproperLoggingPrintRule alias

Depends: .linter for PrintStatementRule, .conditional_verbose_rule for ConditionalVerboseRule,
    .config for PrintStatementConfig

Implements: lint(file_path, config) -> list[Violation] for simple linting operations

Related: src/linters/magic_numbers/__init__.py, src/core/base.py

Overview: Provides the public interface for the improper logging linter package (formerly
    print-statements). Exports PrintStatementRule for detecting print/console statements and
    ConditionalVerboseRule for detecting conditional verbose logging anti-patterns. Both rules
    use rule IDs prefixed with 'improper-logging.' for unified filtering. Includes lint()
    convenience function for simple API usage without the orchestrator. ImproperLoggingPrintRule
    is provided as an alias for PrintStatementRule for semantic clarity.

Usage: from src.linters.print_statements import PrintStatementRule, ConditionalVerboseRule, lint
    violations = lint("path/to/file.py")

Notes: Module-level exports with __all__ definition, convenience function wrapper
"""

from .conditional_verbose_rule import ConditionalVerboseRule
from .config import PrintStatementConfig
from .linter import PrintStatementRule

# Alias for semantic clarity (both detect improper logging patterns)
ImproperLoggingPrintRule = PrintStatementRule

__all__ = [
    "PrintStatementRule",
    "ConditionalVerboseRule",
    "PrintStatementConfig",
    "ImproperLoggingPrintRule",
    "lint",
]


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
