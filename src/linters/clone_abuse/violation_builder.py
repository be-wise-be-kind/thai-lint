"""
Purpose: Build Violation objects for Rust clone abuse patterns

Scope: Creates violations with actionable suggestions for clone-in-loop, clone-chain,
    and unnecessary-clone patterns

Overview: Provides module-level functions that create Violation objects for detected
    .clone() abuse patterns in Rust code. Each violation includes the rule ID, location,
    descriptive message explaining the performance or correctness impact, and a suggestion
    for safer alternatives such as borrowing, Rc/Arc for shared ownership, or Cow for
    clone-on-write patterns.

Dependencies: src.core.types for Violation dataclass

Exports: build_clone_in_loop_violation, build_clone_chain_violation, build_unnecessary_clone_violation

Interfaces: Module functions taking file_path, line, column, context and returning Violation

Implementation: Factory functions for each clone abuse pattern with pattern-specific suggestions
"""

from src.core.types import Violation

_CLONE_IN_LOOP_SUGGESTION = (
    "Consider borrowing instead of cloning in a loop. "
    "If ownership is needed, use Rc/Arc for shared ownership or collect references."
)

_CLONE_CHAIN_SUGGESTION = (
    "Chained .clone().clone() is redundant. "
    "A single .clone() produces an owned copy; the second clone is unnecessary."
)

_UNNECESSARY_CLONE_SUGGESTION = (
    "This .clone() may be unnecessary if the original value is not used after cloning. "
    "Consider passing ownership directly, borrowing, or using Cow for clone-on-write."
)


def build_clone_in_loop_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for .clone() call inside a loop body."""
    message = f".clone() called inside a loop body may cause performance issues: {context}"

    return Violation(
        rule_id="clone-abuse.clone-in-loop",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_CLONE_IN_LOOP_SUGGESTION,
    )


def build_clone_chain_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for chained .clone().clone() calls."""
    message = f"Chained .clone().clone() is redundant: {context}"

    return Violation(
        rule_id="clone-abuse.clone-chain",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_CLONE_CHAIN_SUGGESTION,
    )


def build_unnecessary_clone_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for unnecessary .clone() before move."""
    message = f".clone() may be unnecessary when the original is not used afterward: {context}"

    return Violation(
        rule_id="clone-abuse.unnecessary-clone",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_UNNECESSARY_CLONE_SUGGESTION,
    )
