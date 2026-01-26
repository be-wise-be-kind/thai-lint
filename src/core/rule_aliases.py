"""
Purpose: Rule ID aliasing system for backward compatibility during rule renaming

Scope: Maps deprecated rule IDs to canonical rule IDs for configuration and filtering

Overview: Provides a mapping system for rule IDs that allows backward compatibility when rules
    are renamed. Users can continue using deprecated rule IDs in configuration files and ignore
    directives, which are transparently resolved to their canonical forms. Supports both
    direct rule ID mapping and linter-level command aliasing. Used by configuration parsing,
    violation filtering, and ignore directive processing.

Dependencies: None (pure Python module)

Exports: RULE_ID_ALIASES dict, LINTER_ALIASES dict, resolve_rule_id function,
    resolve_linter_name function

Interfaces: resolve_rule_id(rule_id) -> str, resolve_linter_name(name) -> str

Implementation: Simple dictionary-based lookup with identity fallback for unknown rule IDs
"""

# Maps deprecated rule IDs to their canonical replacements
RULE_ID_ALIASES: dict[str, str] = {
    "print-statements.detected": "improper-logging.print-statement",
}

# Maps deprecated linter command names to their canonical replacements
LINTER_ALIASES: dict[str, str] = {
    "print-statements": "improper-logging",
}


def resolve_rule_id(rule_id: str) -> str:
    """Resolve a rule ID to its canonical form.

    If the rule ID has been renamed, returns the new canonical name.
    Otherwise, returns the rule ID unchanged.

    Args:
        rule_id: The rule ID to resolve (may be deprecated or canonical)

    Returns:
        The canonical rule ID
    """
    return RULE_ID_ALIASES.get(rule_id, rule_id)


def resolve_linter_name(name: str) -> str:
    """Resolve a linter command name to its canonical form.

    If the linter has been renamed, returns the new canonical name.
    Otherwise, returns the name unchanged.

    Args:
        name: The linter command name to resolve (may be deprecated or canonical)

    Returns:
        The canonical linter name
    """
    return LINTER_ALIASES.get(name, name)


def is_deprecated_rule_id(rule_id: str) -> bool:
    """Check if a rule ID is deprecated.

    Args:
        rule_id: The rule ID to check

    Returns:
        True if the rule ID is deprecated (has an alias)
    """
    return rule_id in RULE_ID_ALIASES


def is_deprecated_linter(name: str) -> bool:
    """Check if a linter name is deprecated.

    Args:
        name: The linter name to check

    Returns:
        True if the linter name is deprecated (has an alias)
    """
    return name in LINTER_ALIASES
