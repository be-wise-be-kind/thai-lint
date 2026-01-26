"""
Purpose: Rule ID matching utilities for ignore directive processing

Scope: Pattern matching between rule IDs and ignore patterns

Overview: Provides functions for matching rule IDs against ignore patterns. Supports
    exact matching, wildcard matching (*.suffix), prefix matching (category matches
    category.specific), and alias resolution for backward compatibility with renamed
    rules. All comparisons are case-insensitive to handle variations in rule ID formatting.

Dependencies: re for regex operations, src.core.rule_aliases for alias resolution

Exports: rule_matches, check_bracket_rules, check_space_separated_rules

Interfaces: rule_matches(rule_id, pattern) -> bool for checking if rule matches pattern

Implementation: String-based pattern matching with wildcard, prefix, and alias support
"""

import re

from src.core.rule_aliases import RULE_ID_ALIASES


def rule_matches(rule_id: str, pattern: str) -> bool:
    """Check if rule ID matches pattern (supports wildcards, prefixes, and aliases).

    Supports backward compatibility through alias resolution:
    - Pattern "print-statements" matches rule_id "improper-logging.print-statement"
    - Pattern "print-statements.*" matches rule_id "improper-logging.print-statement"

    Args:
        rule_id: Rule ID to check (e.g., "improper-logging.print-statement").
        pattern: Pattern with optional wildcard (e.g., "nesting.*" or "print-statements").

    Returns:
        True if rule matches pattern.
    """
    if _matches_pattern_directly(rule_id, pattern):
        return True

    return _matches_via_alias(rule_id, pattern)


def _matches_pattern_directly(rule_id: str, pattern: str) -> bool:
    """Check if rule ID matches pattern without alias resolution."""
    rule_id_lower = rule_id.lower()
    pattern_lower = pattern.lower()

    if pattern_lower.endswith("*"):
        prefix = pattern_lower[:-1]
        return rule_id_lower.startswith(prefix)

    if rule_id_lower == pattern_lower:
        return True

    if rule_id_lower.startswith(pattern_lower + "."):
        return True

    return False


def _matches_via_alias(rule_id: str, pattern: str) -> bool:
    """Check if rule ID matches pattern through alias resolution."""
    pattern_lower = pattern.lower()
    rule_id_lower = rule_id.lower()

    # Find deprecated IDs that alias to our rule_id and check pattern match
    return any(
        _pattern_matches_deprecated_id(pattern_lower, deprecated_id)
        for deprecated_id, canonical_id in RULE_ID_ALIASES.items()
        if canonical_id.lower() == rule_id_lower
    )


def _pattern_matches_deprecated_id(pattern_lower: str, deprecated_id: str) -> bool:
    """Check if pattern matches a deprecated rule ID."""
    deprecated_id_lower = deprecated_id.lower()

    # Pattern exactly matches deprecated ID
    if pattern_lower == deprecated_id_lower:
        return True

    # Pattern is prefix/wildcard that matches deprecated ID's category
    deprecated_category = deprecated_id.split(".", maxsplit=1)[0].lower()
    if pattern_lower == deprecated_category:
        return True
    if pattern_lower == deprecated_category + ".*":
        return True

    return False


def check_bracket_rules(rules_text: str, rule_id: str) -> bool:
    """Check if bracketed rules match the rule ID.

    Args:
        rules_text: Comma-separated rule patterns from bracket syntax
        rule_id: Rule ID to match against

    Returns:
        True if any pattern matches the rule ID
    """
    ignored_rules = [r.strip() for r in rules_text.split(",")]
    return any(rule_matches(rule_id, r) for r in ignored_rules)


def check_space_separated_rules(rules_text: str, rule_id: str) -> bool:
    """Check if space-separated rules match the rule ID.

    Args:
        rules_text: Space or comma-separated rule patterns
        rule_id: Rule ID to match against

    Returns:
        True if any pattern matches the rule ID
    """
    ignored_rules = [r.strip() for r in re.split(r"[,\s]+", rules_text) if r.strip()]
    return any(rule_matches(rule_id, r) for r in ignored_rules)


def rules_match_violation(ignored_rules: set[str], rule_id: str) -> bool:
    """Check if any of the ignored rules match the violation rule ID.

    Args:
        ignored_rules: Set of rule patterns to check
        rule_id: Rule ID of the violation

    Returns:
        True if any pattern matches (or if wildcard "*" is present)
    """
    if "*" in ignored_rules:
        return True
    return any(rule_matches(rule_id, pattern) for pattern in ignored_rules)
