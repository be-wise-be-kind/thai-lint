"""
Purpose: Detect scattered string comparisons in Python AST

Scope: Find equality/inequality comparisons with string literals across Python files

Overview: Provides ComparisonTracker class that traverses Python AST to find scattered
    string comparisons like `if env == "production"`. Tracks the variable name, compared
    string value, and operator to enable cross-file aggregation. When a variable is compared
    to multiple unique string values across files, it suggests the variable should be an enum.
    Excludes common false positives like `__name__ == "__main__"` and type name checks.

Dependencies: ast module for AST parsing, dataclasses for pattern structure,
    src.core.constants for MAX_ATTRIBUTE_CHAIN_DEPTH

Exports: ComparisonTracker class, ComparisonPattern dataclass

Interfaces: ComparisonTracker.find_patterns(tree) -> list[ComparisonPattern]

Implementation: AST NodeVisitor pattern with Compare node handling for string comparisons

Suppressions:
    - invalid-name: visit_Compare follows AST NodeVisitor method naming convention
    - srp: Tracker implements AST visitor pattern with multiple visit methods.
        Methods support single responsibility of comparison pattern detection.
"""

import ast
from dataclasses import dataclass

from src.core.constants import MAX_ATTRIBUTE_CHAIN_DEPTH


@dataclass
class ComparisonPattern:
    """Represents a string comparison found in Python code.

    Captures information about a comparison like `if (env == "production")` to
    enable cross-file analysis for detecting scattered string comparisons that
    suggest missing enums.
    """

    variable_name: str
    """Variable name being compared (e.g., 'env' or 'self.status')."""

    compared_value: str
    """The string literal value being compared to."""

    operator: str
    """The comparison operator ('==' or '!=')."""

    line_number: int
    """Line number where the comparison occurs (1-indexed)."""

    column: int
    """Column number where the comparison starts (0-indexed)."""


# Excluded variable names that are common false positives
_EXCLUDED_VARIABLES = frozenset(
    {
        "__name__",
        "__class__.__name__",
    }
)

# Excluded values that are common in legitimate comparisons
_EXCLUDED_VALUES = frozenset(
    {
        "__main__",
    }
)


class ComparisonTracker(ast.NodeVisitor):  # thailint: ignore[srp]
    """Tracks scattered string comparisons in Python AST.

    Finds patterns like `if env == "production"` and `if status != "deleted"` where
    string literals are used for comparisons that could use enums instead.

    Note: Method count exceeds SRP limit because AST traversal requires multiple helper
    methods for extracting variable names, attribute names, and pattern filtering. All
    methods support the single responsibility of tracking string comparisons.
    """

    def __init__(self) -> None:
        """Initialize the tracker."""
        self.patterns: list[ComparisonPattern] = []

    def find_patterns(self, tree: ast.AST) -> list[ComparisonPattern]:
        """Find all string comparisons in the AST.

        Args:
            tree: The AST to analyze

        Returns:
            List of ComparisonPattern instances for each detected comparison
        """
        self.patterns = []
        self.visit(tree)
        return self.patterns

    def visit_Compare(self, node: ast.Compare) -> None:  # pylint: disable=invalid-name
        """Visit a Compare node to check for string comparisons.

        Handles both `var == "string"` and `"string" == var` patterns.

        Args:
            node: The Compare node to analyze
        """
        self._check_comparison(node)
        self.generic_visit(node)

    def _check_comparison(self, node: ast.Compare) -> None:
        """Check if comparison is a string comparison to track.

        Args:
            node: The Compare node to check
        """
        # Only handle simple binary comparisons
        if len(node.ops) != 1 or len(node.comparators) != 1:
            return

        operator = node.ops[0]
        if not isinstance(operator, (ast.Eq, ast.NotEq)):
            return

        op_str = "==" if isinstance(operator, ast.Eq) else "!="
        left = node.left
        right = node.comparators[0]

        # Try both orientations: var == "string" and "string" == var
        self._try_extract_pattern(left, right, op_str, node)
        self._try_extract_pattern(right, left, op_str, node)

    def _try_extract_pattern(
        self,
        var_side: ast.expr,
        string_side: ast.expr,
        operator: str,
        node: ast.Compare,
    ) -> None:
        """Try to extract a pattern from a comparison.

        Args:
            var_side: The expression that might be a variable
            string_side: The expression that might be a string literal
            operator: The comparison operator
            node: The original Compare node for location info
        """
        # Check if string_side is a string literal
        if not isinstance(string_side, ast.Constant):
            return
        if not isinstance(string_side.value, str):
            return

        string_value = string_side.value

        # Extract variable name
        var_name = self._extract_variable_name(var_side)
        if var_name is None:
            return

        # Check for excluded patterns
        if self._should_exclude(var_name, string_value):
            return

        self._add_pattern(var_name, string_value, operator, node)

    def _extract_variable_name(self, node: ast.expr) -> str | None:
        """Extract variable name from an expression.

        Handles simple names (var) and attribute access (obj.attr).

        Args:
            node: The expression to extract from

        Returns:
            Variable name string or None if not extractable
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return self._extract_attribute_name(node)
        return None

    def _extract_attribute_name(self, node: ast.Attribute) -> str | None:
        """Extract attribute name from an attribute access.

        Builds qualified names like 'obj.attr' or 'a.b.attr'.

        Args:
            node: The Attribute node

        Returns:
            Qualified attribute name or None if too complex
        """
        parts: list[str] = [node.attr]
        current = node.value
        depth = 0

        while depth < MAX_ATTRIBUTE_CHAIN_DEPTH:
            if isinstance(current, ast.Name):
                parts.append(current.id)
                break
            if isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
                depth += 1
            else:
                # Complex expression, still return what we have
                parts.append("_")
                break

        return ".".join(reversed(parts))

    def _should_exclude(self, var_name: str, string_value: str) -> bool:
        """Check if this comparison should be excluded.

        Filters out common patterns that are not stringly-typed code:
        - __name__ == "__main__"
        - __class__.__name__ checks

        Args:
            var_name: The variable name
            string_value: The string value

        Returns:
            True if the comparison should be excluded
        """
        if var_name in _EXCLUDED_VARIABLES:
            return True
        if string_value in _EXCLUDED_VALUES:
            return True
        # Also exclude if the full qualified name ends with __name__
        if var_name.endswith("__name__"):
            return True
        return False

    def _add_pattern(
        self, var_name: str, string_value: str, operator: str, node: ast.Compare
    ) -> None:
        """Create and add a comparison pattern to results.

        Args:
            var_name: The variable name
            string_value: The string value being compared
            operator: The comparison operator
            node: The Compare node for location info
        """
        pattern = ComparisonPattern(
            variable_name=var_name,
            compared_value=string_value,
            operator=operator,
            line_number=node.lineno,
            column=node.col_offset,
        )
        self.patterns.append(pattern)
