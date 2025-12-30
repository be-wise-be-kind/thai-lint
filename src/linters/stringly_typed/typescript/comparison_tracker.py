"""
Purpose: Detect scattered string comparisons in TypeScript code using tree-sitter

Scope: Find equality/inequality comparisons with string literals across TypeScript files

Overview: Provides TypeScriptComparisonTracker class that uses tree-sitter to traverse
    TypeScript AST and find scattered string comparisons like `if (env === "production")`.
    Tracks the variable name, compared string value, and operator to enable cross-file
    aggregation. When a variable is compared to multiple unique string values across files,
    it suggests the variable should be an enum. Excludes common false positives like template
    literals and typeof comparisons.

Dependencies: TypeScriptBaseAnalyzer for tree-sitter parsing, dataclasses for pattern structure,
    src.core.constants for MAX_ATTRIBUTE_CHAIN_DEPTH

Exports: TypeScriptComparisonTracker class, TypeScriptComparisonPattern dataclass

Interfaces: TypeScriptComparisonTracker.find_patterns(code) -> list[TypeScriptComparisonPattern]

Implementation: Tree-sitter node traversal with binary_expression node handling for string
    comparisons

Suppressions:
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
    - srp: Tracker implements tree-sitter traversal with helper methods for node extraction.
        Methods support single responsibility of comparison pattern detection.
"""

from dataclasses import dataclass
from typing import Any

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE, TypeScriptBaseAnalyzer
from src.core.constants import MAX_ATTRIBUTE_CHAIN_DEPTH

if TREE_SITTER_AVAILABLE:
    from tree_sitter import Node
else:
    Node = Any  # type: ignore[assignment,misc]


@dataclass
class TypeScriptComparisonPattern:
    """Represents a string comparison found in TypeScript code.

    Captures information about a comparison like `if (env === "production")` to
    enable cross-file analysis for detecting scattered string comparisons that
    suggest missing enums.
    """

    variable_name: str
    """Variable name being compared (e.g., 'env' or 'this.status')."""

    compared_value: str
    """The string literal value being compared to."""

    operator: str
    """The comparison operator ('===', '==', '!==', '!=')."""

    line_number: int
    """Line number where the comparison occurs (1-indexed)."""

    column: int
    """Column number where the comparison starts (0-indexed)."""


# Operators that indicate string comparison
_COMPARISON_OPERATORS = frozenset({"===", "==", "!==", "!="})


class TypeScriptComparisonTracker(TypeScriptBaseAnalyzer):  # thailint: ignore[srp]
    """Tracks scattered string comparisons in TypeScript code.

    Finds patterns like `if (env === "production")` and `if (status !== "deleted")`
    where string literals are used for comparisons that could use enums instead.

    Note: Method count exceeds SRP limit because tree-sitter traversal requires
    multiple helper methods for extracting variable names, member expressions,
    and string handling. All methods support the single responsibility of
    tracking string comparisons.
    """

    def __init__(self) -> None:
        """Initialize the tracker."""
        super().__init__()
        self.patterns: list[TypeScriptComparisonPattern] = []

    def find_patterns(self, code: str) -> list[TypeScriptComparisonPattern]:
        """Find all string comparisons in the code.

        Args:
            code: TypeScript source code to analyze

        Returns:
            List of TypeScriptComparisonPattern instances for each detected comparison
        """
        if not self.tree_sitter_available:
            return []

        root = self.parse_typescript(code)
        if root is None:
            return []

        return self.find_patterns_from_tree(root)

    def find_patterns_from_tree(self, tree: Node) -> list[TypeScriptComparisonPattern]:
        """Find all string comparisons from a pre-parsed tree.

        Optimized for single-parse workflows where the tree is shared between trackers.

        Args:
            tree: Pre-parsed tree-sitter root node

        Returns:
            List of TypeScriptComparisonPattern instances for each detected comparison
        """
        self.patterns = []
        self._traverse_tree(tree)
        return self.patterns

    def _traverse_tree(self, node: Node) -> None:
        """Recursively traverse tree looking for binary expressions.

        Args:
            node: Current tree-sitter node
        """
        if node.type == "binary_expression":
            self._process_binary_expression(node)

        for child in node.children:
            self._traverse_tree(child)

    def _process_binary_expression(self, node: Node) -> None:
        """Process a binary expression node for string comparisons.

        Args:
            node: binary_expression node
        """
        operator = self._extract_operator(node)
        if operator is None or operator not in _COMPARISON_OPERATORS:
            return

        # Get left and right operands
        operands = self._get_operands(node)
        if operands is None:
            return

        left, right = operands

        # Try both orientations: var === "string" and "string" === var
        self._try_extract_pattern(left, right, operator, node)
        self._try_extract_pattern(right, left, operator, node)

    def _extract_operator(self, node: Node) -> str | None:
        """Extract the operator from a binary expression.

        Args:
            node: binary_expression node

        Returns:
            Operator string or None
        """
        for child in node.children:
            if child.type in ("===", "==", "!==", "!="):
                return child.type
        return None

    def _get_operands(self, node: Node) -> tuple[Node, Node] | None:
        """Get the left and right operands of a binary expression.

        Args:
            node: binary_expression node

        Returns:
            Tuple of (left, right) nodes or None if structure is unexpected
        """
        operands = []
        for child in node.children:
            # Skip operators
            if child.type not in ("===", "==", "!==", "!="):
                operands.append(child)

        if len(operands) >= 2:
            return (operands[0], operands[1])
        return None

    def _try_extract_pattern(
        self,
        var_side: Node,
        string_side: Node,
        operator: str,
        node: Node,
    ) -> None:
        """Try to extract a pattern from a comparison.

        Args:
            var_side: The node that might be a variable
            string_side: The node that might be a string literal
            operator: The comparison operator
            node: The original binary_expression node for location info
        """
        # Check if string_side is a string literal (not a template literal)
        string_value = self._extract_string_value(string_side)
        if string_value is None:
            return

        # Extract variable name
        var_name = self._extract_variable_name(var_side)
        if var_name is None:
            return

        # Check for excluded patterns
        if self._should_exclude(var_side, var_name, string_value):
            return

        self._add_pattern(var_name, string_value, operator, node)

    def _extract_string_value(self, node: Node) -> str | None:
        """Extract string value from a node if it's a string literal.

        Excludes template literals with interpolation.

        Args:
            node: Potential string literal node

        Returns:
            String value without quotes, or None if not a simple string
        """
        if node.type != "string":
            return None

        text = self.extract_node_text(node)
        if len(text) < 2:
            return None

        return self._strip_quotes(text)

    def _strip_quotes(self, text: str) -> str | None:
        """Strip quotes from a string literal, excluding template interpolation.

        Args:
            text: The raw string text including quotes

        Returns:
            The string value without quotes, or None if invalid
        """
        first_char = text[0]

        # Template literal (backticks) - exclude if has interpolation
        if first_char == "`":
            return None if "${" in text else text[1:-1]

        # Regular string literal (single or double quotes)
        if first_char in ('"', "'") and text[-1] == first_char:
            return text[1:-1]

        return None

    def _extract_variable_name(self, node: Node) -> str | None:
        """Extract variable name from a node.

        Handles simple identifiers and member expressions.

        Args:
            node: Potential variable node

        Returns:
            Variable name string or None if not extractable
        """
        if node.type == "identifier":
            return self.extract_node_text(node)
        if node.type == "member_expression":
            return self._extract_member_expression_name(node)
        return None

    def _extract_member_expression_name(self, node: Node) -> str | None:
        """Extract name from a member expression.

        Builds qualified names like 'obj.attr' or 'a.b.attr'.

        Args:
            node: member_expression node

        Returns:
            Qualified name or None if too complex
        """
        parts: list[str] = []
        current: Node | None = node

        for _ in range(MAX_ATTRIBUTE_CHAIN_DEPTH):
            if current is None:
                break
            self._add_property_name(current, parts)
            current = self._get_next_node(current, parts)

        return ".".join(reversed(parts)) if parts else None

    def _add_property_name(self, node: Node, parts: list[str]) -> None:
        """Add property name to parts list if found.

        Args:
            node: member_expression node
            parts: List to append property name to
        """
        for child in node.children:
            if child.type == "property_identifier":
                parts.append(self.extract_node_text(child))
                break

    def _get_next_node(self, current: Node, parts: list[str]) -> Node | None:
        """Get the next node to process in member expression chain.

        Args:
            current: Current member_expression node
            parts: List of parts (modified if terminal node found)

        Returns:
            Next node to process or None to stop
        """
        for child in current.children:
            if child.type == "identifier":
                parts.append(self.extract_node_text(child))
                return None
            if child.type == "member_expression":
                return child
            if child.type == "this":
                parts.append("this")
                return None

        # Complex expression
        parts.append("_")
        return None

    def _should_exclude(self, var_node: Node, var_name: str, string_value: str) -> bool:
        """Check if this comparison should be excluded.

        Filters out common patterns that are not stringly-typed code:
        - typeof comparisons
        - Standard type checks

        Args:
            var_node: The variable side node
            var_name: The variable name
            string_value: The string value

        Returns:
            True if the comparison should be excluded
        """
        if self._is_typeof_expression(var_node):
            return True

        if var_name == "typeof":
            return True

        return False

    def _is_typeof_expression(self, node: Node) -> bool:
        """Check if node is a typeof unary expression."""
        if node.type != "unary_expression":
            return False
        return any(child.type == "typeof" for child in node.children)

    def _add_pattern(self, var_name: str, string_value: str, operator: str, node: Node) -> None:
        """Create and add a comparison pattern to results.

        Args:
            var_name: The variable name
            string_value: The string value being compared
            operator: The comparison operator
            node: The binary_expression node for location info
        """
        pattern = TypeScriptComparisonPattern(
            variable_name=var_name,
            compared_value=string_value,
            operator=operator,
            line_number=node.start_point[0] + 1,  # 1-indexed
            column=node.start_point[1],
        )
        self.patterns.append(pattern)
