"""
Purpose: Build Violation objects with EAFP suggestions for LBYL patterns

Scope: Creates violations for detected LBYL anti-patterns with fix suggestions

Overview: Provides module-level functions that create Violation objects for LBYL
    anti-patterns detected in Python code. Each violation includes the rule ID, location,
    descriptive message, and an EAFP suggestion showing how to refactor the code using
    try/except. Supports dict key check, hasattr, isinstance, file exists, len check,
    None check, string validator, and division zero-check patterns.

Dependencies: src.core.types for Violation, src.core.base for BaseLintContext

Exports: build_dict_key_violation, build_hasattr_violation, build_isinstance_violation,
    build_file_exists_violation, build_len_check_violation, create_syntax_error_violation,
    build_none_check_violation, build_string_validator_violation, build_division_check_violation

Interfaces: Module functions for building LBYL violations

Implementation: Factory functions for each violation type with descriptive suggestions

Suppressions:
    too-many-arguments, too-many-positional-arguments: build_string_validator_violation
        requires 6 parameters (file_path, line, column, string_name, validator_method,
        conversion_func) to create accurate violation messages and suggestions
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


def build_hasattr_violation(
    file_path: str,
    line: int,
    column: int,
    object_name: str,
    attribute_name: str,
) -> Violation:
    """Build a violation for hasattr LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        object_name: Name of the object being checked
        attribute_name: Name of the attribute being checked

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if hasattr({object_name}, '{attribute_name}')' followed by "
        f"'{object_name}.{attribute_name}'"
    )

    suggestion = f"Use EAFP: 'try: {object_name}.{attribute_name} except AttributeError: ...'"

    return Violation(
        rule_id="lbyl.hasattr-check",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=suggestion,
    )


def build_isinstance_violation(
    file_path: str,
    line: int,
    column: int,
    object_name: str,
    type_name: str,
) -> Violation:
    """Build a violation for isinstance LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        object_name: Name of the object being checked
        type_name: Name of the type being checked against

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if isinstance({object_name}, {type_name})' before type-specific operation"
    )

    suggestion = (
        "Consider EAFP: 'try: ... except (TypeError, AttributeError): ...' "
        "instead of isinstance check"
    )

    return Violation(
        rule_id="lbyl.isinstance-check",
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


def build_file_exists_violation(
    file_path: str,
    line: int,
    column: int,
    path_expression: str,
    check_type: str,
) -> Violation:
    """Build a violation for file exists LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        path_expression: Expression representing the file path being checked
        check_type: Type of check ("os.path.exists", "Path.exists", "exists")

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if {check_type}({path_expression})' followed by "
        f"file operation on '{path_expression}'"
    )

    suggestion = (
        f"Use EAFP: 'try: with open({path_expression}) as f: ... except FileNotFoundError: ...'"
    )

    return Violation(
        rule_id="lbyl.file-exists-check",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=suggestion,
    )


def build_len_check_violation(
    file_path: str,
    line: int,
    column: int,
    collection_name: str,
    index_expression: str,
) -> Violation:
    """Build a violation for len check LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        collection_name: Name of the collection being checked
        index_expression: Expression used as index

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if len({collection_name}) > {index_expression}' followed by "
        f"'{collection_name}[...]'"
    )

    suggestion = (
        f"Use EAFP: 'try: value = {collection_name}[{index_expression}] except IndexError: ...'"
    )

    return Violation(
        rule_id="lbyl.len-check",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=suggestion,
    )


def build_none_check_violation(
    file_path: str,
    line: int,
    column: int,
    variable_name: str,
) -> Violation:
    """Build a violation for None check LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        variable_name: Name of the variable being checked for None

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if {variable_name} is not None' followed by '{variable_name}.<method>()'"
    )

    suggestion = (
        f"Use EAFP: 'try: {variable_name}.<method>() except AttributeError: ...' "
        f"or check if None is a valid state to handle differently"
    )

    return Violation(
        rule_id="lbyl.none-check",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=suggestion,
    )


def build_string_validator_violation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    file_path: str,
    line: int,
    column: int,
    string_name: str,
    validator_method: str,
    conversion_func: str,
) -> Violation:
    """Build a violation for string validator LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        string_name: Name of the string being validated
        validator_method: Validation method used (isnumeric, isdigit, etc.)
        conversion_func: Conversion function used (int, float)

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if {string_name}.{validator_method}()' followed by "
        f"'{conversion_func}({string_name})'"
    )

    suggestion = f"Use EAFP: 'try: value = {conversion_func}({string_name}) except ValueError: ...'"

    return Violation(
        rule_id="lbyl.string-validator",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=suggestion,
    )


def build_division_check_violation(
    file_path: str,
    line: int,
    column: int,
    divisor_name: str,
    operation: str,
) -> Violation:
    """Build a violation for division zero-check LBYL pattern.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        divisor_name: Name of the divisor being checked for zero
        operation: Division operation used (/, //, %, /=, //=, %=)

    Returns:
        Violation object with EAFP suggestion
    """
    message = (
        f"LBYL pattern: 'if {divisor_name} != 0' followed by "
        f"'{operation}' operation with '{divisor_name}'"
    )

    suggestion = (
        f"Use EAFP: 'try: result = ... {operation} {divisor_name} except ZeroDivisionError: ...'"
    )

    return Violation(
        rule_id="lbyl.division-check",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=suggestion,
    )
