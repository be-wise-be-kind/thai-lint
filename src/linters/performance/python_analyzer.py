"""
Purpose: Python AST-based string concatenation in loop detector

Scope: Detect O(n²) string building patterns using += in for/while loops

Overview: Analyzes Python code to detect string concatenation inside loops using AST traversal.
    Implements heuristic-based detection using variable naming patterns and initialization values.
    Detects `result += str(item)` patterns inside for/while loops that indicate O(n²) complexity.
    Provides suggestions for using join() or list comprehension instead.

Dependencies: ast module for Python parsing, constants module for shared patterns

Exports: PythonStringConcatAnalyzer class with find_violations method

Interfaces: find_violations(tree: ast.AST) -> list[dict] with violation info

Implementation: AST visitor pattern detecting augmented assignments in loop contexts

Suppressions:
    - srp.violation: Class uses many small methods to achieve A-grade cyclomatic complexity.
      This is an intentional tradeoff - low complexity is prioritized over strict SRP adherence.
    - type: ignore[arg-type]: Narrowed types after isinstance checks require explicit casts.
    - type: ignore[union-attr]: Access to .id on ast.Name after isinstance(node.target, ast.Name) check.
"""

import ast
from dataclasses import dataclass

from .constants import STRING_VARIABLE_PATTERNS


@dataclass
class StringConcatViolation:
    """Represents a string concatenation violation found in code."""

    variable_name: str
    line_number: int
    column: int
    loop_type: str  # 'for' or 'while'


# thailint: ignore-next-line[srp.violation] Uses small focused methods to reduce complexity
class PythonStringConcatAnalyzer:
    """Detects string concatenation in loops for Python code."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self._string_variables: set[str] = set()
        self._non_string_variables: set[str] = set()  # Lists, numbers, etc.

    def find_violations(self, tree: ast.AST) -> list[StringConcatViolation]:
        """Find all string concatenation in loop violations.

        Args:
            tree: Python AST to analyze

        Returns:
            List of violations found
        """
        violations: list[StringConcatViolation] = []
        self._string_variables = set()
        self._non_string_variables = set()

        # First pass: identify variables initialized as strings or non-strings
        self._identify_string_variables(tree)

        # Second pass: find += in loops
        self._find_concat_in_loops(tree, violations)

        return violations

    def _identify_string_variables(self, tree: ast.AST) -> None:
        """Identify variables that are initialized as strings or non-strings.

        Args:
            tree: AST to analyze
        """
        for node in ast.walk(tree):
            self._process_assignment_node(node)

    def _process_assignment_node(self, node: ast.AST) -> None:
        """Process a single assignment node to track variable types."""
        if isinstance(node, ast.Assign):
            self._process_simple_assign(node)
        elif isinstance(node, ast.AnnAssign):
            self._process_annotated_assign(node)

    def _process_simple_assign(self, node: ast.Assign) -> None:
        """Process a simple assignment node."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._classify_variable(target.id, node.value)

    def _process_annotated_assign(self, node: ast.AnnAssign) -> None:
        """Process an annotated assignment node."""
        if node.value and isinstance(node.target, ast.Name):
            self._classify_variable(node.target.id, node.value)

    def _classify_variable(self, var_name: str, value: ast.expr) -> None:
        """Classify a variable as string or non-string based on its value."""
        if self._is_string_value(value):
            self._string_variables.add(var_name)
        elif self._is_non_string_value(value):
            self._non_string_variables.add(var_name)

    def _is_string_value(self, node: ast.expr) -> bool:
        """Check if an expression is a string value.

        Args:
            node: Expression node to check

        Returns:
            True if the expression is a string literal or f-string
        """
        # String literal: "", '', """..."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return True

        # f-string: f"..."
        if isinstance(node, ast.JoinedStr):
            return True

        return False

    def _is_non_string_value(self, node: ast.expr) -> bool:
        """Check if an expression is clearly not a string (list, number, etc).

        Args:
            node: Expression node to check

        Returns:
            True if the expression is clearly not a string
        """
        # Collection literals: [], {}, set()
        if isinstance(node, (ast.List, ast.Dict, ast.Set)):
            return True
        # Numeric literal: 0, 1.0
        return isinstance(node, ast.Constant) and isinstance(node.value, (int, float))

    def _find_concat_in_loops(
        self, node: ast.AST, violations: list[StringConcatViolation], in_loop: str | None = None
    ) -> None:
        """Recursively find string concatenation in loops.

        Args:
            node: Current AST node
            violations: List to append violations to
            in_loop: Type of enclosing loop ('for' or 'while'), None if not in loop
        """
        current_loop = self._get_loop_type(node) or in_loop
        self._check_for_string_concat(node, violations, current_loop)

        for child in ast.iter_child_nodes(node):
            self._find_concat_in_loops(child, violations, current_loop)

    def _get_loop_type(self, node: ast.AST) -> str | None:
        """Get the loop type if node is a loop, else None."""
        if isinstance(node, ast.For):
            return "for"
        if isinstance(node, ast.While):
            return "while"
        return None

    def _check_for_string_concat(
        self, node: ast.AST, violations: list[StringConcatViolation], loop_type: str | None
    ) -> None:
        """Check if node is a string concatenation in a loop and add violation if so."""
        if not self._is_string_aug_assign(node, loop_type):
            return
        self._maybe_add_violation(node, violations, loop_type)  # type: ignore[arg-type]

    def _is_string_aug_assign(self, node: ast.AST, loop_type: str | None) -> bool:
        """Check if node is a string augmented assignment in a loop."""
        if not loop_type or not isinstance(node, ast.AugAssign):
            return False
        return isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name)

    def _maybe_add_violation(
        self, node: ast.AugAssign, violations: list[StringConcatViolation], loop_type: str | None
    ) -> None:
        """Add violation if this is a string concatenation."""
        var_name = node.target.id  # type: ignore[union-attr]
        if not self._is_likely_string_variable(var_name, node.value):
            return
        violations.append(
            StringConcatViolation(
                variable_name=var_name,
                line_number=node.lineno,
                column=node.col_offset,
                loop_type=loop_type or "",
            )
        )

    def _is_likely_string_variable(self, var_name: str, value: ast.expr) -> bool:
        """Determine if a variable is likely a string being concatenated.

        Args:
            var_name: Variable name
            value: Value being added

        Returns:
            True if this is likely string concatenation
        """
        if var_name in self._non_string_variables:
            return False
        return (
            self._is_known_string_var(var_name)
            or self._is_string_value(value)
            or self._is_str_call(value)
            or self._is_string_binop(value)
        )

    def _is_known_string_var(self, var_name: str) -> bool:
        """Check if variable is known or named like a string."""
        return var_name in self._string_variables or var_name.lower() in STRING_VARIABLE_PATTERNS

    def _is_str_call(self, value: ast.expr) -> bool:
        """Check if value is a str() call."""
        if not isinstance(value, ast.Call):
            return False
        return isinstance(value.func, ast.Name) and value.func.id == "str"

    def _is_string_binop(self, value: ast.expr) -> bool:
        """Check if value is a binary op with string operand."""
        if not isinstance(value, ast.BinOp) or not isinstance(value.op, ast.Add):
            return False
        return self._is_string_value(value.left) or self._is_string_value(value.right)

    def deduplicate_violations(
        self, violations: list[StringConcatViolation]
    ) -> list[StringConcatViolation]:
        """Deduplicate violations to report one per loop, not per +=.

        Args:
            violations: List of all violations found

        Returns:
            Deduplicated list with one violation per variable per loop
        """
        # Group by variable name and keep first occurrence
        seen: set[str] = set()
        result: list[StringConcatViolation] = []

        for v in violations:
            if v.variable_name not in seen:
                seen.add(v.variable_name)
                result.append(v)

        return result
