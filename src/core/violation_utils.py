"""
Purpose: Shared utility functions for violation processing across linters

Scope: Common violation-related operations used by multiple linters

Overview: Provides shared utility functions for working with violations, including
    extracting line text and checking for ignore directives. These patterns were
    previously duplicated across multiple linter modules (magic_numbers, print_statements,
    method_property). Centralizing them here improves maintainability and ensures
    consistent behavior across all linters.

Dependencies: BaseLintContext, Violation types

Exports: get_violation_line, has_python_noqa, has_typescript_noqa

Interfaces:
    get_violation_line(violation, context) -> str | None
    has_python_noqa(line_text) -> bool
    has_typescript_noqa(line_text) -> bool

Implementation: Simple text extraction and pattern matching
"""

from src.core.base import BaseLintContext
from src.core.types import Violation


def get_violation_line(violation: Violation, context: BaseLintContext) -> str | None:
    """Get the line text for a violation, lowercased.

    Args:
        violation: Violation to get line for
        context: Lint context with file content

    Returns:
        Lowercased line text, or None if not available
    """
    if not context.file_content:
        return None

    lines = context.file_content.splitlines()
    if violation.line <= 0 or violation.line > len(lines):
        return None

    return lines[violation.line - 1].lower()


def has_python_noqa(line_text: str) -> bool:
    """Check if line has Python-style noqa directive.

    Args:
        line_text: Lowercased line text

    Returns:
        True if line has # noqa comment
    """
    return "# noqa" in line_text


def has_typescript_noqa(line_text: str) -> bool:
    """Check if line has TypeScript-style noqa directive.

    Args:
        line_text: Lowercased line text

    Returns:
        True if line has // noqa comment
    """
    return "// noqa" in line_text
