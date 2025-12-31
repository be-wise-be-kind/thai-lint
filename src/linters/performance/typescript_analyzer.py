"""
Purpose: TypeScript tree-sitter based string concatenation in loop detector

Scope: Detect O(n²) string building patterns using += in TypeScript loops

Overview: Analyzes TypeScript code to detect string concatenation inside loops using tree-sitter.
    Implements heuristic-based detection using variable naming patterns and initialization values.
    Detects `result += item` patterns inside for/while/do loops that indicate O(n²) complexity.
    Provides suggestions for using join() or array-based building instead.

Dependencies: TypeScriptBaseAnalyzer, tree-sitter, tree-sitter-typescript, constants module

Exports: TypeScriptStringConcatAnalyzer class with find_violations method

Interfaces: find_violations(root_node) -> list[dict] with violation info

Implementation: Tree-sitter traversal detecting augmented assignments in loop contexts

Suppressions:
    - srp.violation: Class uses many small methods to achieve A-grade cyclomatic complexity.
      This is an intentional tradeoff - low complexity is prioritized over strict SRP adherence.
"""

from dataclasses import dataclass

from src.analyzers.typescript_base import (
    TREE_SITTER_AVAILABLE,
    Node,
    TypeScriptBaseAnalyzer,
)

from .constants import LOOP_NODE_TYPES_TS, STRING_VARIABLE_PATTERNS


@dataclass
class StringConcatViolation:
    """Represents a string concatenation violation found in code."""

    variable_name: str
    line_number: int
    column: int
    loop_type: str  # 'for', 'for_in', 'while', 'do'


# thailint: ignore-next-line[srp.violation] Uses small focused methods to reduce complexity
class TypeScriptStringConcatAnalyzer(TypeScriptBaseAnalyzer):
    """Detects string concatenation in loops for TypeScript code."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        super().__init__()
        self._string_variables: set[str] = set()

    def find_violations(self, root_node: Node) -> list[StringConcatViolation]:
        """Find all string concatenation in loop violations.

        Args:
            root_node: Tree-sitter AST root node

        Returns:
            List of violations found
        """
        if not TREE_SITTER_AVAILABLE or root_node is None:
            return []

        violations: list[StringConcatViolation] = []
        self._string_variables = set()

        # First pass: identify variables initialized as strings
        self._identify_string_variables(root_node)

        # Second pass: find += in loops
        self._find_concat_in_loops(root_node, violations, None)

        return violations

    def _identify_string_variables(self, node: Node) -> None:
        """Identify variables that are initialized as strings.

        Args:
            node: AST node to analyze
        """
        self._check_variable_declarator(node)
        for child in node.children:
            self._identify_string_variables(child)

    def _check_variable_declarator(self, node: Node) -> None:
        """Check if a variable_declarator node initializes a string variable."""
        if node.type != "variable_declarator":
            return
        name_node = self.find_child_by_type(node, "identifier")
        value_node = self._find_string_value(node)
        if name_node and value_node:
            self._string_variables.add(self.extract_node_text(name_node))

    def _find_string_value(self, node: Node) -> Node | None:
        """Find a string or template_string child node."""
        for child in node.children:
            if child.type in ("string", "template_string"):
                return child
        return None

    def _find_concat_in_loops(
        self, node: Node, violations: list[StringConcatViolation], loop_type: str | None
    ) -> None:
        """Recursively find string concatenation in loops.

        Args:
            node: Current AST node
            violations: List to append violations to
            loop_type: Type of enclosing loop, None if not in loop
        """
        # Track loop entry
        current_loop = loop_type
        if node.type in LOOP_NODE_TYPES_TS:
            current_loop = node.type.replace("_statement", "").replace("_", "_")

        # Check for augmented assignment (+=)
        if node.type == "augmented_assignment_expression" and current_loop:
            self._check_augmented_assignment(node, violations, current_loop)

        # Recurse into children
        for child in node.children:
            self._find_concat_in_loops(child, violations, current_loop)

    def _check_augmented_assignment(
        self, node: Node, violations: list[StringConcatViolation], loop_type: str
    ) -> None:
        """Check if an augmented assignment is string concatenation.

        Args:
            node: Augmented assignment node
            violations: List to append violations to
            loop_type: Type of enclosing loop
        """
        if not self._is_plus_equals(node):
            return
        var_name = self._get_var_name(node)
        if not var_name:
            return
        value_node = self._get_value_node(node)
        if self._is_likely_string_variable(var_name, value_node):
            self._create_violation(node, var_name, loop_type, violations)

    def _is_plus_equals(self, node: Node) -> bool:
        """Check if node has a += operator."""
        return any(child.type == "+=" for child in node.children)

    def _get_var_name(self, node: Node) -> str | None:
        """Get the variable name from an augmented assignment."""
        for child in node.children:
            if child.type == "identifier":
                return self.extract_node_text(child)
        return None

    def _get_value_node(self, node: Node) -> Node | None:
        """Get the value node from an augmented assignment."""
        children = node.children
        operator_idx = self._find_plus_equals_index(children)
        if operator_idx < 0:
            return None
        return self._find_value_after_operator(children, operator_idx)

    def _find_plus_equals_index(self, children: list[Node]) -> int:
        """Find the index of the += operator in children."""
        for i, child in enumerate(children):
            if child.type == "+=":
                return i
        return -1

    def _find_value_after_operator(self, children: list[Node], operator_idx: int) -> Node | None:
        """Find the first non-identifier value after the operator."""
        for child in children[operator_idx + 1 :]:
            if child.type != "identifier":
                return child
        return None

    def _create_violation(
        self, node: Node, var_name: str, loop_type: str, violations: list[StringConcatViolation]
    ) -> None:
        """Create and append a string concat violation."""
        violations.append(
            StringConcatViolation(
                variable_name=var_name,
                line_number=node.start_point[0] + 1,
                column=node.start_point[1],
                loop_type=loop_type,
            )
        )

    def _is_likely_string_variable(self, var_name: str, value_node: Node | None) -> bool:
        """Determine if a variable is likely a string being concatenated.

        Args:
            var_name: Variable name
            value_node: Value being added (may be None)

        Returns:
            True if this is likely string concatenation
        """
        return self._is_known_string_var(var_name) or self._is_string_value_node(value_node)

    def _is_known_string_var(self, var_name: str) -> bool:
        """Check if variable is known or named like a string."""
        return var_name in self._string_variables or var_name.lower() in STRING_VARIABLE_PATTERNS

    def _is_string_value_node(self, value_node: Node | None) -> bool:
        """Check if value node is a string or contains a string."""
        if not value_node:
            return False
        if value_node.type in ("string", "template_string"):
            return True
        if value_node.type == "binary_expression":
            return any(child.type in ("string", "template_string") for child in value_node.children)
        return False

    def deduplicate_violations(
        self, violations: list[StringConcatViolation]
    ) -> list[StringConcatViolation]:
        """Deduplicate violations to report one per variable.

        Args:
            violations: List of all violations found

        Returns:
            Deduplicated list with one violation per variable
        """
        seen: set[str] = set()
        result: list[StringConcatViolation] = []

        for v in violations:
            if v.variable_name not in seen:
                seen.add(v.variable_name)
                result.append(v)

        return result
