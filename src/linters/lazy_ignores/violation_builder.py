"""
Purpose: Build agent-friendly violation messages for lazy-ignores linter

Scope: Violation construction for unjustified ignores and orphaned header suppressions

Overview: Provides functions to construct Violation objects with AI-agent-friendly error
    messages. Messages include explicit guidance for adding Suppressions section entries to
    file headers and emphasize the requirement for human approval before adding suppressions.
    Designed to help AI coding assistants understand the proper workflow for handling linting
    suppressions rather than blindly adding ignore directives.

Dependencies: src.core.types for Violation dataclass

Exports: build_unjustified_violation, build_orphaned_violation

Interfaces: Two builder functions returning Violation objects

Implementation: Template-based message construction with rule ID formatting
"""

from src.core.types import Severity, Violation


def build_unjustified_violation(
    file_path: str,
    line: int,
    column: int,
    rule_id: str,
    raw_text: str,
) -> Violation:
    """Create violation for an ignore directive without header justification.

    Args:
        file_path: Path to the file containing the violation.
        line: Line number where the ignore was found (1-indexed).
        column: Column number where the ignore starts (0-indexed).
        rule_id: The rule ID(s) being suppressed (e.g., "PLR0912").
        raw_text: The raw ignore directive text found in code.

    Returns:
        Violation object with agent-friendly guidance message.
    """
    message = (
        f"Unjustified suppression found: {raw_text} "
        f"(ASK PERMISSION before adding Suppressions header)"
    )

    suggestion = _build_unjustified_suggestion(rule_id)

    return Violation(
        rule_id="lazy-ignores.unjustified",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,
    )


def _build_unjustified_suggestion(rule_id: str) -> str:
    """Build the suggestion text for unjustified violations.

    Args:
        rule_id: The rule ID(s) being suppressed.

    Returns:
        Formatted suggestion string with header instructions.
    """
    # Handle multiple rules (e.g., "PLR0912, PLR0915")
    rule_ids = [r.strip() for r in rule_id.split(",")]

    suppression_entries = "\n".join(f"    {rid}: [Your justification here]" for rid in rule_ids)

    return f"""To fix, add an entry to the file header Suppressions section:

    Suppressions:
{suppression_entries}

IMPORTANT: Adding suppressions requires human approval.
Do not add this entry without explicit permission from a human reviewer.
Ask first, then add if approved."""


def build_orphaned_violation(
    file_path: str,
    header_line: int,
    rule_id: str,
    justification: str,
) -> Violation:
    """Create violation for a header entry without matching code ignore.

    Args:
        file_path: Path to the file containing the orphaned entry.
        header_line: Line number of the suppression in the header (1-indexed).
        rule_id: The orphaned rule ID from the header.
        justification: The justification text from the header.

    Returns:
        Violation object suggesting removal of the orphaned entry.
    """
    message = f"Orphaned suppression in header: {rule_id}: {justification}"

    suggestion = _build_orphaned_suggestion(rule_id)

    return Violation(
        rule_id="lazy-ignores.orphaned",
        file_path=file_path,
        line=header_line,
        column=0,
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,
    )


def _build_orphaned_suggestion(rule_id: str) -> str:
    """Build the suggestion text for orphaned violations.

    Args:
        rule_id: The orphaned rule ID.

    Returns:
        Formatted suggestion string with removal instructions.
    """
    return f"""This rule is declared in the Suppressions section but no matching
ignore directive was found in the code.

Either:
1. Remove the entry for {rule_id} from the Suppressions section if the ignore was removed from code
2. Add the ignore directive if it's missing from the code"""
