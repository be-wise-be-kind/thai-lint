"""
Purpose: Python AST analysis for finding method-should-be-property candidates

Scope: Python method detection and property candidacy analysis

Overview: Provides PythonMethodAnalyzer class that traverses Python AST to find methods that
    should be converted to @property decorators. Identifies simple accessor methods (returning
    self._attribute), get_* prefixed methods (Java-style), and simple computed values. Implements
    comprehensive exclusion rules to minimize false positives: methods with parameters, side
    effects (assignments, loops, try/except), external function calls, decorators, complex bodies,
    dunder methods, and async definitions. Returns structured data about each candidate including
    method name, class name, line number, and column for violation reporting.

Dependencies: ast module for AST parsing and node types, config module for exclusion defaults

Exports: PythonMethodAnalyzer class, PropertyCandidate dataclass

Interfaces: find_property_candidates(tree) -> list[PropertyCandidate]

Implementation: AST walk pattern with comprehensive method body analysis and exclusion checks
"""

import ast
from dataclasses import dataclass

from .config import DEFAULT_EXCLUDE_NAMES, DEFAULT_EXCLUDE_PREFIXES


@dataclass
class PropertyCandidate:
    """Represents a method that should be a property."""

    method_name: str
    class_name: str
    line: int
    column: int
    is_get_prefix: bool


class PythonMethodAnalyzer:  # thailint: ignore[srp]
    """Analyzes Python AST to find methods that should be properties."""

    def __init__(
        self,
        max_body_statements: int = 3,
        exclude_prefixes: tuple[str, ...] | None = None,
        exclude_names: frozenset[str] | None = None,
    ) -> None:
        """Initialize the analyzer.

        Args:
            max_body_statements: Maximum statements in method body
            exclude_prefixes: Action verb prefixes to exclude (uses defaults if None)
            exclude_names: Action verb names to exclude (uses defaults if None)
        """
        self.max_body_statements = max_body_statements
        self.exclude_prefixes = exclude_prefixes or DEFAULT_EXCLUDE_PREFIXES
        self.exclude_names = exclude_names or DEFAULT_EXCLUDE_NAMES
        self.candidates: list[PropertyCandidate] = []
        self._visited_classes: set[int] = set()

    def find_property_candidates(self, tree: ast.AST) -> list[PropertyCandidate]:
        """Find all methods that should be properties.

        Args:
            tree: The AST to analyze

        Returns:
            List of PropertyCandidate objects
        """
        self.candidates = []
        self._visit_classes(tree)
        return self.candidates

    def _visit_classes(self, tree: ast.AST) -> None:
        """Visit all top-level and nested classes in the AST.

        Args:
            tree: AST to traverse
        """
        self._visited_classes.clear()
        self._visit_node(tree)

    def _visit_node(self, node: ast.AST) -> None:
        """Visit a node and its children for classes.

        Args:
            node: AST node to visit
        """
        if isinstance(node, ast.ClassDef):
            class_id = id(node)
            if class_id not in self._visited_classes:
                self._visited_classes.add(class_id)
                self._analyze_class(node)
        else:
            for child in ast.iter_child_nodes(node):
                self._visit_node(child)

    def _analyze_class(self, class_node: ast.ClassDef) -> None:
        """Analyze a class for property candidates.

        Args:
            class_node: The ClassDef node
        """
        for item in class_node.body:
            self._process_class_item(item, class_node.name)

    def _process_class_item(self, item: ast.stmt, class_name: str) -> None:
        """Process a single item in a class body.

        Args:
            item: Item in the class body
            class_name: Name of the containing class
        """
        if isinstance(item, ast.FunctionDef):
            self._check_method(item, class_name)
        elif isinstance(item, ast.ClassDef):
            self._process_nested_class(item)

    def _process_nested_class(self, class_node: ast.ClassDef) -> None:
        """Process a nested class, avoiding duplicates.

        Args:
            class_node: The nested class node
        """
        class_id = id(class_node)
        if class_id in self._visited_classes:
            return
        self._visited_classes.add(class_id)
        self._analyze_class(class_node)

    def _check_method(self, method: ast.FunctionDef, class_name: str) -> None:
        """Check if method should be a property.

        Args:
            method: The FunctionDef node
            class_name: Name of the containing class
        """
        if not self._is_property_candidate(method):
            return

        is_get_prefix = method.name.startswith("get_") and len(method.name) > 4
        candidate = PropertyCandidate(
            method_name=method.name,
            class_name=class_name,
            line=method.lineno,
            column=method.col_offset,
            is_get_prefix=is_get_prefix,
        )
        self.candidates.append(candidate)

    def _is_property_candidate(self, method: ast.FunctionDef) -> bool:
        """Check if method should be a property.

        Args:
            method: The FunctionDef node

        Returns:
            True if method is a property candidate
        """
        # All conditions must be met for property candidacy
        checks = [
            not self._is_dunder_method(method),
            not self._is_action_verb_method(method),
            not self._has_decorators(method),
            self._takes_only_self(method),
            self._has_simple_body(method),
            self._returns_value(method),
            not self._has_side_effects(method),
            not self._has_control_flow(method),
            not self._has_external_calls(method),
        ]
        return all(checks)

    def _is_dunder_method(self, method: ast.FunctionDef) -> bool:
        """Check if method is a dunder method.

        Args:
            method: The method node

        Returns:
            True if dunder method
        """
        name = method.name
        return name.startswith("__") and name.endswith("__")

    def _is_action_verb_method(self, method: ast.FunctionDef) -> bool:
        """Check if method is an action verb (transformation/lifecycle method).

        Methods like to_dict(), to_json(), finalize() represent actions, not
        property access. These should remain as methods following Python idioms.
        Also handles private method variants like _to_dict(), _generate_html().

        Args:
            method: The method node

        Returns:
            True if method is an action verb
        """
        name = method.name

        # Strip leading underscores to handle private method variants
        # e.g., _generate_legend_section should match generate_* pattern
        stripped_name = name.lstrip("_")

        # Check for action verb prefixes like to_*, generate_*, etc.
        for prefix in self.exclude_prefixes:
            if stripped_name.startswith(prefix) and len(stripped_name) > len(prefix):
                return True

        # Check for specific action verb names (also check stripped version)
        return name in self.exclude_names or stripped_name in self.exclude_names

    def _has_decorators(self, method: ast.FunctionDef) -> bool:
        """Check if method has any decorators.

        Args:
            method: The method node

        Returns:
            True if method has decorators
        """
        return len(method.decorator_list) > 0

    def _takes_only_self(self, method: ast.FunctionDef) -> bool:
        """Check if method takes only self parameter.

        Args:
            method: The method node

        Returns:
            True if only self parameter
        """
        args = method.args
        has_only_self_arg = len(args.args) == 1
        has_extra_args = self._has_extra_args(args)
        return has_only_self_arg and not has_extra_args

    def _has_extra_args(self, args: ast.arguments) -> bool:
        """Check if arguments has extra parameters beyond self.

        Args:
            args: Method arguments node

        Returns:
            True if extra arguments present
        """
        has_positional_only = bool(args.posonlyargs)
        has_vararg = args.vararg is not None
        has_keyword_only = bool(args.kwonlyargs)
        has_kwarg = args.kwarg is not None
        has_defaults = bool(args.defaults)
        has_kw_defaults = args.kw_defaults and any(d is not None for d in args.kw_defaults)

        return any(
            [
                has_positional_only,
                has_vararg,
                has_keyword_only,
                has_kwarg,
                has_defaults,
                has_kw_defaults,
            ]
        )

    def _has_simple_body(self, method: ast.FunctionDef) -> bool:
        """Check if method body is simple (1-3 statements).

        Args:
            method: The method node

        Returns:
            True if body is simple enough
        """
        # Filter out docstrings
        body = self._get_non_docstring_body(method)

        # Check statement count
        if len(body) > self.max_body_statements:
            return False

        if len(body) == 0:
            return False

        return True

    def _get_non_docstring_body(self, method: ast.FunctionDef) -> list[ast.stmt]:
        """Get method body excluding docstrings.

        Args:
            method: The method node

        Returns:
            List of statements excluding docstrings
        """
        body = method.body
        if not body:
            return []

        # Check if first statement is a docstring
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            if isinstance(first.value.value, str):
                return body[1:]

        return body

    def _returns_value(self, method: ast.FunctionDef) -> bool:
        """Check if method returns a non-None value.

        Args:
            method: The method node

        Returns:
            True if method returns a value
        """
        body = self._get_non_docstring_body(method)
        if not body:
            return False
        last = body[-1]
        return self._is_value_return(last)

    def _is_value_return(self, node: ast.stmt) -> bool:
        """Check if node is a return statement with a non-None value.

        Args:
            node: Statement node to check

        Returns:
            True if return statement with value
        """
        if not isinstance(node, ast.Return):
            return False
        if node.value is None:
            return False
        if isinstance(node.value, ast.Constant) and node.value.value is None:
            return False
        return True

    def _has_side_effects(self, method: ast.FunctionDef) -> bool:
        """Check if method has side effects (assignments to self.*).

        Args:
            method: The method node

        Returns:
            True if has side effects
        """
        return any(self._is_side_effect_node(node) for node in ast.walk(method))

    def _is_side_effect_node(self, node: ast.AST) -> bool:
        """Check if a node represents a side effect.

        Args:
            node: AST node to check

        Returns:
            True if node is a side effect
        """
        return (
            self._is_self_assign(node)
            or self._is_self_aug_assign(node)
            or self._is_self_ann_assign(node)
            or self._is_self_delete(node)
        )

    def _is_self_assign(self, node: ast.AST) -> bool:
        """Check if node is assignment to self."""
        return isinstance(node, ast.Assign) and self._assigns_to_self(node.targets)

    def _is_self_aug_assign(self, node: ast.AST) -> bool:
        """Check if node is augmented assignment to self."""
        return isinstance(node, ast.AugAssign) and self._is_self_target(node.target)

    def _is_self_ann_assign(self, node: ast.AST) -> bool:
        """Check if node is annotated assignment to self."""
        if not isinstance(node, ast.AnnAssign):
            return False
        return node.value is not None and self._is_self_target(node.target)

    def _is_self_delete(self, node: ast.AST) -> bool:
        """Check if node is delete of self attribute."""
        return isinstance(node, ast.Delete) and self._assigns_to_self(node.targets)

    def _assigns_to_self(self, targets: list[ast.expr]) -> bool:
        """Check if any target is a self attribute.

        Args:
            targets: Assignment targets

        Returns:
            True if assigning to self.*
        """
        for target in targets:
            if self._is_self_target(target):
                return True
        return False

    def _is_self_target(self, target: ast.expr) -> bool:
        """Check if target is a self attribute (self.* or self._*).

        Args:
            target: Assignment target

        Returns:
            True if target is self.*
        """
        if isinstance(target, ast.Attribute):
            if isinstance(target.value, ast.Name) and target.value.id == "self":
                return True
        return False

    # Node types that indicate complex control flow
    _CONTROL_FLOW_TYPES: tuple[type, ...] = (
        ast.For,
        ast.While,
        ast.Try,
        ast.If,
        ast.With,
        ast.Raise,
        ast.ListComp,
        ast.DictComp,
        ast.SetComp,
        ast.GeneratorExp,
    )

    def _has_control_flow(self, method: ast.FunctionDef) -> bool:
        """Check if method has complex control flow.

        Args:
            method: The method node

        Returns:
            True if has complex control flow
        """
        return any(isinstance(node, self._CONTROL_FLOW_TYPES) for node in ast.walk(method))

    def _has_external_calls(self, method: ast.FunctionDef) -> bool:
        """Check if method has external function calls.

        External calls are top-level function calls like print(), format_date().
        Method calls on objects like self._name.upper() or v.strip() are OK.

        Args:
            method: The method node

        Returns:
            True if has external calls
        """
        call_nodes = (node for node in ast.walk(method) if isinstance(node, ast.Call))
        return any(self._is_external_function_call(node) for node in call_nodes)

    def _is_external_function_call(self, call: ast.Call) -> bool:
        """Check if call is an external function (not a method on an object).

        Args:
            call: The Call node

        Returns:
            True if external function call like print(), format_date()
        """
        func = call.func

        # Simple name call like print(), format_date()
        if isinstance(func, ast.Name):
            return True

        # Method call like obj.method() - these are OK
        if isinstance(func, ast.Attribute):
            return False

        return False
