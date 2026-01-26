"""
Purpose: Builds Violation objects from CQSPattern instances

Scope: Violation message formatting and suggestion generation for CQS violations

Overview: Provides build_cqs_violation function that converts a CQSPattern with a detected
    CQS violation into a Violation object with properly formatted message. Message includes
    function name (with class prefix for methods), lists INPUT operations with line numbers,
    lists OUTPUT operations with line numbers, and provides actionable suggestion to split
    the function into separate query and command functions.

Dependencies: CQSPattern, InputOperation, OutputOperation, Violation, Severity

Exports: build_cqs_violation

Interfaces: build_cqs_violation(pattern: CQSPattern) -> Violation

Implementation: String formatting with INPUT/OUTPUT line number aggregation
"""

from src.core.types import Severity, Violation

from .types import CQSPattern


def _format_inputs(pattern: CQSPattern) -> str:
    """Format INPUT operations for violation message.

    Args:
        pattern: CQSPattern containing inputs

    Returns:
        Formatted string listing INPUTs with line numbers
    """
    if not pattern.inputs:
        return ""

    parts = [f"Line {inp.line}: {inp.target} = {inp.expression}" for inp in pattern.inputs]
    return "; ".join(parts)


def _format_outputs(pattern: CQSPattern) -> str:
    """Format OUTPUT operations for violation message.

    Args:
        pattern: CQSPattern containing outputs

    Returns:
        Formatted string listing OUTPUTs with line numbers
    """
    if not pattern.outputs:
        return ""

    parts = [f"Line {out.line}: {out.expression}" for out in pattern.outputs]
    return "; ".join(parts)


def build_cqs_violation(pattern: CQSPattern) -> Violation:
    """Build a Violation object from a CQSPattern.

    Creates a violation message that includes:
    - Function name (with class prefix for methods)
    - List of INPUT operations with line numbers
    - List of OUTPUT operations with line numbers
    - Suggestion to split into query and command functions

    Args:
        pattern: CQSPattern representing a function that violates CQS

    Returns:
        Violation object with formatted message and suggestion
    """
    full_name = pattern.get_full_name()

    # Build detailed message
    inputs_str = _format_inputs(pattern)
    outputs_str = _format_outputs(pattern)

    message = (
        f"Function '{full_name}' violates CQS: mixes queries and commands. "
        f"INPUTs: {inputs_str}. OUTPUTs: {outputs_str}."
    )

    suggestion = "Split into separate query and command functions."

    return Violation(
        rule_id="cqs",
        file_path=pattern.file_path,
        line=pattern.line,
        column=pattern.column,
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,
    )
