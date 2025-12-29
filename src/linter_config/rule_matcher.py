"""
Purpose: Rule ID matching utilities for ignore directive processing

Scope: Pattern matching between rule IDs and ignore patterns

Overview: Provides functions for matching rule IDs against ignore patterns. Supports
    exact matching, wildcard matching (*.suffix), and prefix matching (category matches
    category.specific). All comparisons are case-insensitive to handle variations in
    rule ID formatting.

Dependencies: re for regex operations

Exports: rule_matches, check_bracket_rules, check_space_separated_rules

Interfaces: rule_matches(rule_id, pattern) -> bool for checking if rule matches pattern

Implementation: String-based pattern matching with wildcard and prefix support
"""

import re


def rule_matches(rule_id: str, pattern: str) -> bool:
    """Check if rule ID matches pattern (supports wildcards and prefixes).

    Args:
        rule_id: Rule ID to check (e.g., "nesting.excessive-depth").
        pattern: Pattern with optional wildcard (e.g., "nesting.*" or "nesting").

    Returns:
        True if rule matches pattern.
    """
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
