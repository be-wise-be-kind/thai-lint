"""
Purpose: Build Violation objects with EAFP suggestions for LBYL patterns

Scope: Creates violations for detected LBYL anti-patterns with fix suggestions

Overview: Provides module-level functions that create Violation objects for LBYL
    anti-patterns detected in Python code. Each violation includes the rule ID, location,
    descriptive message, and an EAFP suggestion showing how to refactor the code using
    try/except. Supports dict key check patterns with extensibility for additional
    pattern types.

Dependencies: src.core.types for Violation, src.core.base for BaseLintContext

Exports: build_dict_key_violation, create_syntax_error_violation

Interfaces: Module functions for building LBYL violations

Implementation: Factory functions for each violation type with descriptive suggestions
"""

from src.core.base import BaseLintContext
from src.core.types import Violation


def build_dict_key_violation(
    file_path: str,
    line: int,
    column: int,
    dict_name: str,
    key_expression: str,
) -> Violation:
    """Build a violation for dict key LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        dict_name: Name of the dict being checked
        key_expression: Expression used as key

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if {key_expression} in {dict_name}' followed by "
        f"'{dict_name}[{key_expression}]'"
    )

    suggestion = (
        f"Use EAFP: 'with suppress(KeyError): value = {dict_name}[{key_expression}]' "
        f"or 'try: ... except KeyError: ...'"
    )

    return Violation(
        rule_id="lbyl.dict-key-check",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=suggestion,
    )


def create_syntax_error_violation(error: SyntaxError, context: BaseLintContext) -> Violation:
    """Create a violation for a syntax error.

    Args:
        error: The SyntaxError from parsing
        context: Lint context with file information

    Returns:
        Violation indicating syntax error
    """
    file_path = str(context.file_path) if context.file_path else "unknown"
    line = error.lineno or 1
    column = error.offset or 0

    return Violation(
        rule_id="lbyl.syntax-error",
        file_path=file_path,
        line=line,
        column=column,
        message=f"Syntax error: {error.msg}",
        suggestion="Fix the syntax error before running LBYL analysis",
    )
