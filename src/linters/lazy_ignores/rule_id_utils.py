"""
Purpose: Pure utility functions for rule ID parsing and matching

Scope: String parsing utilities for comma-separated rule lists and type:ignore formats

Overview: Provides pure functions for parsing and matching rule IDs in various formats
    used by the lazy-ignores linter. Handles comma-separated rule lists (e.g.,
    "too-many-arguments,too-many-positional-arguments") and type:ignore bracket
    formats (e.g., "type:ignore[arg-type,return-value]"). Functions are stateless
    and can be easily tested in isolation.

Dependencies: None (pure Python string operations)

Exports: extract_type_ignore_bracket, split_comma_list, rule_in_comma_list,
    rule_in_type_ignore_bracket, any_part_in_set, comma_list_has_used_rule,
    type_ignore_bracket_has_used_rule

Interfaces: All functions take strings/sets and return strings/bools

Implementation: String parsing with early returns for invalid formats
"""

TYPE_IGNORE_PREFIX = "type:ignore["


def extract_type_ignore_bracket(suppression_key: str) -> str | None:
    """Extract content from type:ignore[...] format.

    Args:
        suppression_key: String that may be in type:ignore[rules] format

    Returns:
        Content between brackets, or None if not valid format
    """
    if not suppression_key.startswith(TYPE_IGNORE_PREFIX):
        return None
    if not suppression_key.endswith("]"):
        return None
    return suppression_key[len(TYPE_IGNORE_PREFIX) : -1]


def split_comma_list(content: str) -> list[str]:
    """Split comma-separated string into stripped parts.

    Args:
        content: Comma-separated string

    Returns:
        List of stripped parts, or empty list if no commas
    """
    if "," not in content:
        return []
    return [p.strip() for p in content.split(",")]


def rule_in_comma_list(rule_id: str, suppression_key: str) -> bool:
    """Check if rule_id is in a plain comma-separated list.

    Args:
        rule_id: Normalized rule ID to find
        suppression_key: String that may contain comma-separated rules

    Returns:
        True if rule_id is found in the comma-separated parts
    """
    parts = split_comma_list(suppression_key)
    return rule_id in parts


def rule_in_type_ignore_bracket(rule_id: str, suppression_key: str) -> bool:
    """Check if rule_id is in type:ignore[rule1,rule2] format.

    Args:
        rule_id: Normalized rule ID to find
        suppression_key: String that may be in type:ignore[rules] format

    Returns:
        True if rule_id is found in the bracket content
    """
    bracket_content = extract_type_ignore_bracket(suppression_key)
    if bracket_content is None:
        return False
    parts = split_comma_list(bracket_content)
    return rule_id in parts


def any_part_in_set(content: str, rule_ids: set[str]) -> bool:
    """Check if any comma-separated part of content is in rule_ids.

    Args:
        content: Comma-separated string
        rule_ids: Set of rule IDs to check against

    Returns:
        True if any part is in the set
    """
    parts = split_comma_list(content)
    return any(p in rule_ids for p in parts)


def comma_list_has_used_rule(suppression_key: str, used_rule_ids: set[str]) -> bool:
    """Check if any rule in a comma-separated suppression is used.

    Args:
        suppression_key: Comma-separated suppression key
        used_rule_ids: Set of rule IDs used in code

    Returns:
        True if any comma-separated rule is in used_rule_ids
    """
    parts = split_comma_list(suppression_key)
    return any(p in used_rule_ids for p in parts)


def type_ignore_bracket_has_used_rule(suppression_key: str, used_rule_ids: set[str]) -> bool:
    """Check if type:ignore[rules] suppression has any used rule.

    Args:
        suppression_key: String in type:ignore[rules] format
        used_rule_ids: Set of rule IDs used in code

    Returns:
        True if bracket content or any comma part is in used_rule_ids
    """
    bracket_content = extract_type_ignore_bracket(suppression_key)
    if bracket_content is None:
        return False
    if bracket_content in used_rule_ids:
        return True
    return any_part_in_set(bracket_content, used_rule_ids)


def is_type_ignore_format_in_suppressions(normalized: str, suppressions: dict[str, str]) -> bool:
    """Check if type:ignore[rule] format is in suppressions.

    Args:
        normalized: Normalized rule ID
        suppressions: Dict of suppression keys to justifications

    Returns:
        True if type:ignore[normalized] is in suppressions
    """
    return f"type:ignore[{normalized}]" in suppressions


def rule_matches_suppression(rule_id: str, suppression_key: str, is_type_ignore: bool) -> bool:
    """Check if rule_id matches a suppression key (plain or type:ignore format).

    Args:
        rule_id: Normalized rule ID to find
        suppression_key: Suppression key to check
        is_type_ignore: True if this is a type:ignore directive

    Returns:
        True if rule_id is found in the suppression key
    """
    if rule_in_comma_list(rule_id, suppression_key):
        return True
    if is_type_ignore:
        return rule_in_type_ignore_bracket(rule_id, suppression_key)
    return False


def find_rule_in_suppressions(
    normalized: str, suppressions: dict[str, str], is_type_ignore: bool
) -> bool:
    """Check if rule appears in any comma-separated suppression entry.

    Args:
        normalized: Normalized rule ID to find
        suppressions: Dict of suppression keys to justifications
        is_type_ignore: True if this is a type:ignore directive

    Returns:
        True if rule is found in any suppression's comma list
    """
    return any(
        rule_matches_suppression(normalized, suppression_key, is_type_ignore)
        for suppression_key in suppressions
    )
