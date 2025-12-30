"""
Purpose: Detect function calls with string literal arguments in TypeScript AST

Scope: Find function and method calls that consistently receive string arguments

Overview: Provides TypeScriptCallTracker class that uses tree-sitter to traverse TypeScript
    AST and find function and method calls where string literals are passed as arguments.
    Tracks the function name, parameter index, and string value to enable cross-file
    aggregation. When a function is called with the same set of limited string values
    across files, it suggests the parameter should be an enum. Handles both simple
    function calls (foo("value")) and method calls (obj.method("value")), including
    chained method calls.

Dependencies: TypeScriptBaseAnalyzer for tree-sitter parsing, dataclasses for pattern structure,
    src.core.constants for MAX_ATTRIBUTE_CHAIN_DEPTH

Exports: TypeScriptCallTracker class, TypeScriptFunctionCallPattern dataclass

Interfaces: TypeScriptCallTracker.find_patterns(code) -> list[TypeScriptFunctionCallPattern]

Implementation: Tree-sitter node traversal with call_expression node handling for string arguments

Suppressions:
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
    - srp: Tracker implements tree-sitter traversal with helper methods for call extraction.
        Methods support single responsibility of function call pattern detection.
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
class TypeScriptFunctionCallPattern:
    """Represents a function call with a string literal argument.

    Captures information about a function or method call where a string literal
    is passed as an argument, enabling cross-file analysis to detect limited
    value sets that should be enums.
    """

    function_name: str
    """Fully qualified function name (e.g., 'process' or 'obj.method')."""

    param_index: int
    """Index of the parameter receiving the string value (0-indexed)."""

    string_value: str
    """The string literal value passed to the function."""

    line_number: int
    """Line number where the call occurs (1-indexed)."""

    column: int
    """Column number where the call starts (0-indexed)."""


class TypeScriptCallTracker(TypeScriptBaseAnalyzer):  # thailint: ignore[srp]
    """Tracks function calls with string literal arguments in TypeScript.

    Finds patterns like 'process("active")' and 'obj.setStatus("pending")' where
    string literals are used for arguments that could be enums.

    Note: Method count exceeds SRP limit because tree-sitter traversal requires
    multiple helper methods for extracting function names, member expressions,
    and argument handling. All methods support the single responsibility of
    tracking function calls with string arguments.
    """

    def __init__(self) -> None:
        """Initialize the tracker."""
        super().__init__()
        self.patterns: list[TypeScriptFunctionCallPattern] = []

    def find_patterns(self, code: str) -> list[TypeScriptFunctionCallPattern]:
        """Find all function calls with string arguments in the code.

        Args:
            code: TypeScript source code to analyze

        Returns:
            List of TypeScriptFunctionCallPattern instances for each detected call
        """
        if not self.tree_sitter_available:
            return []

        root = self.parse_typescript(code)
        if root is None:
            return []

        return self.find_patterns_from_tree(root)

    def find_patterns_from_tree(self, tree: Node) -> list[TypeScriptFunctionCallPattern]:
        """Find all function calls with string arguments from a pre-parsed tree.

        Optimized for single-parse workflows where the tree is shared between trackers.

        Args:
            tree: Pre-parsed tree-sitter root node

        Returns:
            List of TypeScriptFunctionCallPattern instances for each detected call
        """
        self.patterns = []
        self._traverse_tree(tree)
        return self.patterns

    def _traverse_tree(self, node: Node) -> None:
        """Recursively traverse tree looking for call expressions.

        Args:
            node: Current tree-sitter node
        """
        if node.type == "call_expression":
            self._process_call_expression(node)

        for child in node.children:
            self._traverse_tree(child)

    def _process_call_expression(self, node: Node) -> None:
        """Process a call expression node for string arguments.

        Args:
            node: call_expression node
        """
        function_name = self._extract_function_name(node)
        if function_name is None:
            return

        self._check_arguments(node, function_name)

    def _extract_function_name(self, node: Node) -> str | None:
        """Extract the function name from a call expression.

        Handles simple names (foo) and member access (obj.method).

        Args:
            node: call_expression node

        Returns:
            Function name string or None if not extractable
        """
        # Find the function/method being called
        func_node = self._find_function_node(node)
        if func_node is None:
            return None

        if func_node.type == "identifier":
            return self.extract_node_text(func_node)

        if func_node.type == "member_expression":
            return self._extract_member_expression_name(func_node)

        return None

    def _find_function_node(self, node: Node) -> Node | None:
        """Find the function/method node in a call expression.

        Args:
            node: call_expression node

        Returns:
            The function or member_expression node, or None
        """
        for child in node.children:
            if child.type in ("identifier", "member_expression"):
                return child
        return None

    def _extract_member_expression_name(self, node: Node) -> str | None:
        """Extract function name from a member expression.

        Builds qualified names like 'obj.method' or 'a.b.method'.

        Args:
            node: member_expression node

        Returns:
            Qualified function name or None if too complex
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
        property_node = self._find_property_identifier(node)
        if property_node:
            parts.append(self.extract_node_text(property_node))

    def _get_next_node(self, current: Node, parts: list[str]) -> Node | None:
        """Get the next node to process in member expression chain.

        Args:
            current: Current member_expression node
            parts: List of parts (modified if terminal node found)

        Returns:
            Next node to process or None to stop
        """
        object_node = self._find_object_node(current)
        if object_node is None:
            return None

        if object_node.type == "identifier":
            parts.append(self.extract_node_text(object_node))
            return None

        if object_node.type == "member_expression":
            return object_node

        # Complex expression (call result, subscript, etc.)
        parts.append("_")
        return None

    def _find_property_identifier(self, node: Node) -> Node | None:
        """Find the property identifier in a member expression.

        Args:
            node: member_expression node

        Returns:
            property_identifier node or None
        """
        for child in node.children:
            if child.type == "property_identifier":
                return child
        return None

    def _find_object_node(self, node: Node) -> Node | None:
        """Find the object in a member expression.

        Args:
            node: member_expression node

        Returns:
            Object node (identifier or member_expression) or None
        """
        for child in node.children:
            if child.type in ("identifier", "member_expression", "call_expression"):
                return child
        return None

    def _check_arguments(self, node: Node, function_name: str) -> None:
        """Check call arguments for string literals.

        Args:
            node: call_expression node
            function_name: Extracted function name
        """
        args_node = self._find_arguments_node(node)
        if args_node is None:
            return

        param_index = 0
        for child in args_node.children:
            string_value = self._extract_string_value(child)
            if string_value is not None:
                self._add_pattern(node, function_name, param_index, string_value)
            # Only count actual arguments, not punctuation
            if child.type not in ("(", ")", ","):
                param_index += 1

    def _find_arguments_node(self, node: Node) -> Node | None:
        """Find the arguments node in a call expression.

        Args:
            node: call_expression node

        Returns:
            arguments node or None
        """
        for child in node.children:
            if child.type == "arguments":
                return child
        return None

    def _extract_string_value(self, node: Node) -> str | None:
        """Extract string value from a node if it's a string literal.

        Args:
            node: Potential string literal node

        Returns:
            String value without quotes, or None if not a string
        """
        if node.type != "string":
            return None

        text = self.extract_node_text(node)
        # Remove quotes (", ', or `)
        if len(text) >= 2:
            if text[0] in ('"', "'", "`") and text[-1] == text[0]:
                return text[1:-1]
        return None

    def _add_pattern(
        self, node: Node, function_name: str, param_index: int, string_value: str
    ) -> None:
        """Create and add a function call pattern to results.

        Args:
            node: call_expression node
            function_name: Name of the function being called
            param_index: Index of the string argument
            string_value: The string literal value
        """
        pattern = TypeScriptFunctionCallPattern(
            function_name=function_name,
            param_index=param_index,
            string_value=string_value,
            line_number=node.start_point[0] + 1,  # 1-indexed
            column=node.start_point[1],
        )
        self.patterns.append(pattern)
