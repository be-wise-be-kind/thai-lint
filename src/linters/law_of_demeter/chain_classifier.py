"""
Purpose: Chain classification pipeline for Law of Demeter analysis

Scope: 9-filter pipeline to distinguish genuine LoD violations from legitimate patterns

Overview: Provides classify_chain() that runs a chain through an 8-filter pipeline. Each filter
    checks for a specific legitimate chaining pattern (safe prefix, module access, string
    methods, fluent APIs, AST traversal, dunder access, subscript navigation, safe terminals).
    Returns a reason string if the chain is allowed, or empty string if it is a genuine
    violation. Filter order matters: earlier filters take precedence. Test file exclusion is
    handled at the linter level (LawOfDemeterRule) to respect check_test_files config.

Dependencies: chain_extractor, filter_constants, python_analyzer

Exports: classify_chain

Interfaces: classify_chain(parts, imports, filepath) -> str

Implementation: Iterates a list of filter functions, returns first non-empty match.
    Each filter is a standalone function for A-grade complexity.
"""

from .chain_extractor import clean_part, is_subscript_part
from .filter_constants import (
    AST_NODE_ATTRS,
    AST_TRAVERSAL_THRESHOLD,
    BUILDER_METHODS,
    COLLECTION_PIPELINE_METHODS,
    KNOWN_MODULE_ROOTS,
    SAFE_CHAIN_PREFIXES,
    SAFE_TERMINAL_METHODS,
    STR_METHODS,
)
from .python_analyzer import FileImports

_FLUENT_ALLOWED = COLLECTION_PIPELINE_METHODS | BUILDER_METHODS


def classify_chain(parts: list[str], imports: FileImports, filepath: str) -> str:
    """Classify a chain through the 9-filter pipeline.

    Returns reason string if allowed, empty string if genuine violation.

    Args:
        parts: Chain parts list like ["obj", "method()", "attr"]
        imports: File-level import information
        filepath: Path to the source file

    Returns:
        Filter reason string (e.g. "safe-prefix:self") or "" for violations
    """
    for filter_fn in _FILTERS:
        result = filter_fn(parts, imports, filepath)
        if result:
            return result
    return ""


def _cleaned_parts(parts: list[str], start: int = 1) -> list[str]:
    """Extract cleaned, non-subscript parts from index onward."""
    return [m for m in (clean_part(p) for p in parts[start:] if not is_subscript_part(p)) if m]


def _all_in_set(names: list[str], allowed: frozenset[str]) -> bool:
    """Check if all names are in the allowed set."""
    return bool(names) and all(n in allowed for n in names)


def _check_safe_prefix(parts: list[str], _imports: FileImports, _filepath: str) -> str:
    """Filter 1: Check if chain starts with a known safe prefix."""
    chain_str = ".".join(clean_part(p) for p in parts)
    for prefix in SAFE_CHAIN_PREFIXES:
        if chain_str.startswith(prefix):
            return f"safe-prefix:{prefix.rstrip('.')}"
    return ""


def _check_module_access(parts: list[str], imports: FileImports, _filepath: str) -> str:
    """Filter 2: Check if chain is rooted in a module name."""
    root = clean_part(parts[0])
    if root in imports.module_names or root in KNOWN_MODULE_ROOTS:
        return f"module-access:{root}"
    return ""


def _check_string_chain(parts: list[str], _imports: FileImports, _filepath: str) -> str:
    """Filter 3: Check if chain is same-type string method chaining."""
    if _all_in_set(_cleaned_parts(parts), STR_METHODS):
        return "same-type:str"
    return _check_string_attr_variant(parts)


def _check_string_attr_variant(parts: list[str]) -> str:
    """Check for obj.attr.str_method().str_method() pattern."""
    if len(parts) < 3:
        return ""
    if _all_in_set(_cleaned_parts(parts, start=2), STR_METHODS):
        return "same-type:str-attr"
    return ""


def _check_fluent_chain(parts: list[str], _imports: FileImports, _filepath: str) -> str:
    """Filter 4: Check if chain is a fluent/builder/collection pipeline."""
    if _all_in_set(_cleaned_parts(parts), _FLUENT_ALLOWED):
        return "fluent-chain"
    return ""


def _ast_ratio_met(intermediates: list[str]) -> bool:
    """Check if enough intermediate parts are AST node attributes."""
    ast_count = sum(1 for a in intermediates if a in AST_NODE_ATTRS)
    return ast_count >= len(intermediates) * AST_TRAVERSAL_THRESHOLD


def _check_ast_traversal(parts: list[str], _imports: FileImports, _filepath: str) -> str:
    """Filter 5: Check if chain navigates AST/compiler node attributes."""
    intermediates = [clean_part(p) for p in parts[1:-1] if not is_subscript_part(p)]
    if not intermediates:
        return ""
    return "ast-traversal" if _ast_ratio_met(intermediates) else ""


def _is_dunder(name: str) -> bool:
    """Check if a name is a dunder attribute."""
    return name.startswith("__") and name.endswith("__")


def _check_dunder_access(parts: list[str], _imports: FileImports, _filepath: str) -> str:
    """Filter 6: Check if chain contains dunder protocol attributes."""
    if any(_is_dunder(clean_part(p)) for p in parts[1:]):
        return "dunder-access"
    return ""


def _check_subscript_access(parts: list[str], _imports: FileImports, _filepath: str) -> str:
    """Filter 7: Check if most chain depth comes from subscript (dict/list) access."""
    subscript_count = sum(1 for p in parts if is_subscript_part(p))
    if subscript_count >= 1 and len(parts) - subscript_count <= 2:
        return "subscript-access"
    return ""


def _check_safe_terminal(parts: list[str], _imports: FileImports, _filepath: str) -> str:
    """Filter 8: Check if chain ends with a known safe terminal method."""
    terminal = clean_part(parts[-1])
    if terminal in SAFE_TERMINAL_METHODS:
        return f"safe-terminal:{terminal}"
    return ""


_FILTERS = [
    _check_safe_prefix,
    _check_module_access,
    _check_string_chain,
    _check_fluent_chain,
    _check_ast_traversal,
    _check_dunder_access,
    _check_subscript_access,
    _check_safe_terminal,
]
