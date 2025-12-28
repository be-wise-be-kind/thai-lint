"""
Purpose: Build violations for function call patterns with limited string values

Scope: Function call violation message and suggestion generation

Overview: Handles building violation objects for function calls that consistently receive
    a limited set of string values, suggesting they should use enums. Generates messages
    with cross-file references and actionable suggestions. Separated from main violation
    generator to maintain SRP compliance with focused responsibility.

Dependencies: Violation, Severity, StoredFunctionCall, StringlyTypedConfig

Exports: build_function_call_violations function

Interfaces: build_function_call_violations(calls, unique_values) -> list[Violation]

Implementation: Builds violations with cross-file references and enum suggestions
"""

from pathlib import Path

from src.core.types import Severity, Violation

from .storage import StoredFunctionCall


def build_function_call_violations(
    calls: list[StoredFunctionCall], unique_values: set[str]
) -> list[Violation]:
    """Build violations for all calls to a function with limited values.

    Args:
        calls: All calls to the function/param
        unique_values: Set of unique string values passed

    Returns:
        List of violations for each call site
    """
    return [_build_violation(call, calls, unique_values) for call in calls]


def _build_cross_references(call: StoredFunctionCall, all_calls: list[StoredFunctionCall]) -> str:
    """Build cross-reference string for other function call locations.

    Args:
        call: Current call
        all_calls: All calls with same function/param

    Returns:
        Comma-separated list of file:line references
    """
    refs = []
    for other in all_calls:
        if other.file_path != call.file_path or other.line_number != call.line_number:
            refs.append(f"{Path(other.file_path).name}:{other.line_number}")

    return ", ".join(refs[:5])  # Limit to 5 references


def _build_violation(
    call: StoredFunctionCall,
    all_calls: list[StoredFunctionCall],
    unique_values: set[str],
) -> Violation:
    """Build a single violation for a function call.

    Args:
        call: The specific call to create violation for
        all_calls: All calls to the same function/param
        unique_values: Set of unique string values passed

    Returns:
        Violation instance
    """
    message = _build_message(call, all_calls, unique_values)
    suggestion = _build_suggestion(call, unique_values)

    return Violation(
        rule_id="stringly-typed.limited-values",
        file_path=str(call.file_path),
        line=call.line_number,
        column=call.column,
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,
    )


def _build_message(
    call: StoredFunctionCall,
    all_calls: list[StoredFunctionCall],
    unique_values: set[str],
) -> str:
    """Build violation message for function call pattern.

    Args:
        call: Current function call
        all_calls: All calls to the same function/param
        unique_values: Set of unique values passed

    Returns:
        Human-readable violation message
    """
    file_count = len({c.file_path for c in all_calls})
    values_str = ", ".join(f"'{v}'" for v in sorted(unique_values))
    param_desc = f"parameter {call.param_index}" if call.param_index > 0 else "first parameter"

    message = (
        f"Function '{call.function_name}' {param_desc} is called with "
        f"only {len(unique_values)} unique string values [{values_str}] "
        f"across {file_count} file(s)."
    )

    other_refs = _build_cross_references(call, all_calls)
    if other_refs:
        message += f" Also called in: {other_refs}."

    return message


def _build_suggestion(call: StoredFunctionCall, unique_values: set[str]) -> str:
    """Build fix suggestion for function call pattern.

    Args:
        call: The function call
        unique_values: Set of unique values passed

    Returns:
        Human-readable suggestion
    """
    return (
        f"Consider defining an enum or type union with the "
        f"{len(unique_values)} possible values for '{call.function_name}' "
        f"parameter {call.param_index}."
    )
