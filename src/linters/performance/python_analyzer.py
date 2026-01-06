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
        self,
        node: ast.AST,
        violations: list[StringConcatViolation],
        in_loop: str | None = None,
        reset_vars: set[str] | None = None,
    ) -> None:
        """Recursively find string concatenation in loops.

        Args:
            node: Current AST node
            violations: List to append violations to
            in_loop: Type of enclosing loop ('for' or 'while'), None if not in loop
            reset_vars: Variables reset to string values in current loop body
        """
        if reset_vars is None:
            reset_vars = set()

        # When entering a new loop, find variables reset in its body
        loop_type = self._get_loop_type(node)
        current_loop: str | None
        current_reset_vars: set[str]
        if loop_type:
            # Find variables assigned to strings in this loop's body
            loop_reset_vars = self._find_vars_reset_in_loop(node)
            current_loop = loop_type
            current_reset_vars = loop_reset_vars
        else:
            current_loop = in_loop
            current_reset_vars = reset_vars

        self._check_for_string_concat(node, violations, current_loop, current_reset_vars)

        for child in ast.iter_child_nodes(node):
            self._find_concat_in_loops(child, violations, current_loop, current_reset_vars)

    def _get_loop_type(self, node: ast.AST) -> str | None:
        """Get the loop type if node is a loop, else None."""
        if isinstance(node, ast.For):
            return "for"
        if isinstance(node, ast.While):
            return "while"
        return None

    def _find_vars_reset_in_loop(self, loop_node: ast.AST) -> set[str]:
        """Find variables that are assigned to string values in a loop body.

        These variables are "reset" each iteration and should not be flagged
        for O(n²) string concatenation since they don't accumulate across iterations.

        Args:
            loop_node: A For or While loop AST node

        Returns:
            Set of variable names that are reset to strings in the loop body
        """
        reset_vars: set[str] = set()

        # Get the loop body
        if isinstance(loop_node, (ast.For, ast.While)):
            body = loop_node.body
        else:
            return reset_vars

        # Scan assignments in the loop body (not nested loops)
        for stmt in body:
            self._collect_string_assigns(stmt, reset_vars)

        return reset_vars

    def _collect_string_assigns(self, node: ast.AST, reset_vars: set[str]) -> None:
        """Collect variable names assigned to string values in a node.

        Args:
            node: AST node to scan
            reset_vars: Set to add found variable names to
        """
        self._check_simple_assign(node, reset_vars)
        self._check_annotated_assign(node, reset_vars)
        self._recurse_control_flow(node, reset_vars)

    def _check_simple_assign(self, node: ast.AST, reset_vars: set[str]) -> None:
        """Check if node is a simple assignment to a string value."""
        if not isinstance(node, ast.Assign):
            return
        for target in node.targets:
            if isinstance(target, ast.Name) and self._is_string_value(node.value):
                reset_vars.add(target.id)

    def _check_annotated_assign(self, node: ast.AST, reset_vars: set[str]) -> None:
        """Check if node is an annotated assignment to a string value."""
        if not isinstance(node, ast.AnnAssign):
            return
        if node.value and isinstance(node.target, ast.Name) and self._is_string_value(node.value):
            reset_vars.add(node.target.id)

    def _recurse_control_flow(self, node: ast.AST, reset_vars: set[str]) -> None:
        """Recurse into control flow (if/else, try/except) but NOT into nested loops."""
        if isinstance(node, ast.If):
            self._recurse_if_node(node, reset_vars)
        elif isinstance(node, ast.Try):
            self._recurse_try_node(node, reset_vars)

    def _recurse_if_node(self, node: ast.If, reset_vars: set[str]) -> None:
        """Recurse into if/else branches."""
        for stmt in node.body + node.orelse:
            self._collect_string_assigns(stmt, reset_vars)

    def _recurse_try_node(self, node: ast.Try, reset_vars: set[str]) -> None:
        """Recurse into try/except/finally branches."""
        for stmt in node.body + node.orelse + node.finalbody:
            self._collect_string_assigns(stmt, reset_vars)
        for handler in node.handlers:
            for stmt in handler.body:
                self._collect_string_assigns(stmt, reset_vars)

    def _check_for_string_concat(
        self,
        node: ast.AST,
        violations: list[StringConcatViolation],
        loop_type: str | None,
        reset_vars: set[str] | None = None,
    ) -> None:
        """Check if node is a string concatenation in a loop and add violation if so."""
        if not self._is_add_aug_assign_in_loop(node, loop_type):
            return
        self._process_aug_assign(node, violations, loop_type or "", reset_vars)

    def _process_aug_assign(
        self,
        node: ast.AST,
        violations: list[StringConcatViolation],
        loop_type: str,
        reset_vars: set[str] | None,
    ) -> None:
        """Process an augmented assignment node for potential violations."""
        if not isinstance(node, ast.AugAssign) or not isinstance(node.target, ast.Name):
            return
        var_name = node.target.id
        if self._should_skip_reset_var(var_name, reset_vars):
            return
        self._add_string_concat_violation(node, var_name, loop_type, violations)

    def _should_skip_reset_var(self, var_name: str, reset_vars: set[str] | None) -> bool:
        """Check if variable is reset in the loop and should be skipped."""
        return reset_vars is not None and var_name in reset_vars

    def _is_add_aug_assign_in_loop(self, node: ast.AST, loop_type: str | None) -> bool:
        """Check if node is a += augmented assignment in a loop."""
        if not loop_type or not isinstance(node, ast.AugAssign):
            return False
        return isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name)

    def _add_string_concat_violation(
        self,
        node: ast.AugAssign,
        var_name: str,
        loop_type: str,
        violations: list[StringConcatViolation],
    ) -> None:
        """Add violation if variable is likely a string."""
        if not self._is_likely_string_variable(var_name, node.value):
            return
        violations.append(
            StringConcatViolation(
                variable_name=var_name,
                line_number=node.lineno,
                column=node.col_offset,
                loop_type=loop_type,
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
