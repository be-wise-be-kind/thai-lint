"""
Purpose: Detect membership validation patterns in Python AST

Scope: Find 'x in ("a", "b")' and 'x not in (...)' patterns

Overview: Provides MembershipValidationDetector class that traverses Python AST to find
    membership validation patterns where strings are used instead of enums. Detects
    Compare nodes with In/NotIn operators and string literal collections (tuple, set,
    list). Returns structured MembershipPattern dataclass instances with string values,
    operator type, location, and optional variable name. Filters out non-string
    collections, single-element collections, and variable references.

Dependencies: ast module for AST parsing, dataclasses for pattern structure,
    variable_extractor for variable name extraction

Exports: MembershipValidationDetector class, MembershipPattern dataclass

Interfaces: MembershipValidationDetector.find_patterns(tree) -> list[MembershipPattern]

Implementation: AST NodeVisitor pattern with Compare node handling for In/NotIn operators

Suppressions:
    - invalid-name: visit_Compare follows AST NodeVisitor method naming convention
"""

import ast
from dataclasses import dataclass

from .constants import MIN_VALUES_FOR_PATTERN
from .variable_extractor import extract_variable_name


@dataclass
class MembershipPattern:
    """Represents a detected membership validation pattern.

    Captures the essential information about a stringly-typed membership check
    including the string values being compared, the operator used, source location,
    and the variable being tested if identifiable.
    """

    string_values: set[str]
    """Set of string values in the membership test."""

    operator: str
    """Operator used: 'in' or 'not in'."""

    line_number: int
    """Line number where the pattern occurs (1-indexed)."""

    column: int
    """Column number where the pattern starts (0-indexed)."""

    variable_name: str | None
    """Variable name being tested, if identifiable from a simple expression."""


class MembershipValidationDetector(ast.NodeVisitor):
    """Detects membership validation patterns in Python AST.

    Finds patterns like 'x in ("a", "b")' and 'x not in {"c", "d"}' where
    strings are used for validation instead of proper enums.
    """

    def __init__(self) -> None:
        """Initialize the detector."""
        self.patterns: list[MembershipPattern] = []

    def find_patterns(self, tree: ast.AST) -> list[MembershipPattern]:
        """Find all membership validation patterns in the AST.

        Args:
            tree: The AST to analyze

        Returns:
            List of MembershipPattern instances for each detected pattern
        """
        self.patterns = []
        self.visit(tree)
        return self.patterns

    def visit_Compare(self, node: ast.Compare) -> None:  # pylint: disable=invalid-name
        """Visit a Compare node to check for membership patterns.

        Handles Compare nodes with In or NotIn operators where the
        comparator is a literal collection of strings.

        Args:
            node: The Compare node to analyze
        """
        for op_index, operator in enumerate(node.ops):
            self._check_membership_operator(node, operator, op_index)
        self.generic_visit(node)

    def _check_membership_operator(
        self, node: ast.Compare, operator: ast.cmpop, op_index: int
    ) -> None:
        """Check if an operator forms a valid membership pattern.

        Args:
            node: The Compare node containing the operator
            operator: The comparison operator to check
            op_index: Index of the operator in the Compare node
        """
        if not isinstance(operator, (ast.In, ast.NotIn)):
            return

        comparator = node.comparators[op_index]
        string_values = _extract_string_values(comparator)

        if string_values is None or len(string_values) < MIN_VALUES_FOR_PATTERN:
            return

        self._add_pattern(node, operator, string_values)

    def _add_pattern(self, node: ast.Compare, operator: ast.cmpop, string_values: set[str]) -> None:
        """Create and add a membership pattern to results.

        Args:
            node: The Compare node containing the pattern
            operator: The In or NotIn operator
            string_values: Set of string values detected
        """
        operator_str = "in" if isinstance(operator, ast.In) else "not in"
        variable_name = extract_variable_name(node.left)

        pattern = MembershipPattern(
            string_values=string_values,
            operator=operator_str,
            line_number=node.lineno,
            column=node.col_offset,
            variable_name=variable_name,
        )
        self.patterns.append(pattern)


def _extract_string_values(node: ast.AST) -> set[str] | None:
    """Extract string values from a collection literal.

    Args:
        node: AST node representing the collection

    Returns:
        Set of string values if all elements are strings, None otherwise
    """
    elements = _get_collection_elements(node)
    if elements is None or len(elements) == 0:
        return None

    return _collect_string_constants(elements)


def _get_collection_elements(node: ast.AST) -> list[ast.expr] | None:
    """Get elements from a collection literal node.

    Args:
        node: AST node that may be a collection literal

    Returns:
        List of element nodes if node is a collection, None otherwise
    """
    if isinstance(node, ast.Tuple):
        return list(node.elts)
    if isinstance(node, ast.Set):
        return list(node.elts)
    if isinstance(node, ast.List):
        return list(node.elts)
    return None


def _collect_string_constants(elements: list[ast.expr]) -> set[str] | None:
    """Collect string constants from a list of AST expression nodes.

    Args:
        elements: List of expression nodes from a collection

    Returns:
        Set of string values if all elements are string constants, None otherwise
    """
    string_values: set[str] = set()

    for element in elements:
        if not isinstance(element, ast.Constant):
            return None
        if not isinstance(element.value, str):
            return None
        string_values.add(element.value)

    return string_values
