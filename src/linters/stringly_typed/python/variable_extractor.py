"""
Purpose: Extract variable names from Python AST nodes

Scope: AST node analysis for identifying variable names in expressions

Overview: Provides functions to extract variable names from various Python AST expression
    types including simple names, attribute access chains, and method calls. Handles
    complex expressions by returning None when the variable cannot be simply identified.
    Supports extraction from Name nodes, Attribute chains (e.g., self.status), and Call
    nodes for method calls (e.g., x.lower()).

Dependencies: ast module for AST node types

Exports: extract_variable_name, extract_attribute_chain functions

Interfaces: extract_variable_name(node) -> str | None for general extraction,
    extract_attribute_chain(node) -> str for attribute chain extraction

Implementation: Pattern matching on AST node types with recursive chain handling
"""

import ast


def extract_variable_name(node: ast.AST) -> str | None:
    """Extract variable name from an expression node.

    Identifies the variable being used in an expression, handling
    simple names, attribute access, and method calls.

    Args:
        node: AST node representing an expression

    Returns:
        Variable name if identifiable, None for complex expressions
    """
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        return extract_attribute_chain(node)

    if isinstance(node, ast.Call):
        return _extract_call_variable(node)

    return None


def extract_attribute_chain(node: ast.Attribute) -> str:
    """Extract full attribute chain as string.

    Builds a dotted string representation of attribute access,
    e.g., 'self.status' or 'obj.attr.subattr'.

    Args:
        node: Attribute node to extract from

    Returns:
        String representation of attribute chain
    """
    parts: list[str] = [node.attr]
    current = node.value

    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value

    if isinstance(current, ast.Name):
        parts.append(current.id)

    parts.reverse()
    return ".".join(parts)


def _extract_call_variable(node: ast.Call) -> str | None:
    """Extract variable from a method call expression.

    For expressions like x.lower(), returns 'x'.
    For complex calls like get_value().lower(), returns None.

    Args:
        node: Call node to extract from

    Returns:
        Variable name if identifiable, None otherwise
    """
    if not isinstance(node.func, ast.Attribute):
        return None

    value = node.func.value
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Attribute):
        return extract_attribute_chain(value)

    return None
