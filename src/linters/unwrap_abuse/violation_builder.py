"""
Purpose: Build Violation objects for Rust unwrap/expect abuse patterns

Scope: Creates violations with actionable suggestions for unwrap and expect calls

Overview: Provides module-level functions that create Violation objects for detected
    .unwrap() and .expect() calls in Rust code. Each violation includes the rule ID,
    location, descriptive message explaining the risk of panicking, and a suggestion
    for safer alternatives such as the ? operator, unwrap_or(), unwrap_or_default(),
    or match/if-let expressions.

Dependencies: src.core.types for Violation dataclass

Exports: build_unwrap_violation, build_expect_violation

Interfaces: Module functions taking file_path, line, column, context and returning Violation

Implementation: Factory functions for unwrap and expect violation types with pattern-specific suggestions
"""

from src.core.types import Violation

_UNWRAP_SUGGESTION = (
    "Use the ? operator, .unwrap_or(), .unwrap_or_default(), "
    "or match/if-let for safe error handling."
)

_EXPECT_SUGGESTION = (
    "Use the ? operator with a descriptive error via .context() or .with_context(), "
    "or use match/if-let for explicit error handling."
)


def build_unwrap_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for .unwrap() call.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        context: Code context around the violation

    Returns:
        Violation object with safer alternative suggestion
    """
    message = f".unwrap() call may panic at runtime: {context}"

    return Violation(
        rule_id="unwrap-abuse.unwrap-call",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_UNWRAP_SUGGESTION,
    )


def build_expect_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for .expect() call.

    Args:
        file_path: Path to the file containing the violation
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        context: Code context around the violation

    Returns:
        Violation object with safer alternative suggestion
    """
    message = f".expect() call may panic at runtime: {context}"

    return Violation(
        rule_id="unwrap-abuse.expect-call",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_EXPECT_SUGGESTION,
    )
