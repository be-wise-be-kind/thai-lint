"""
Purpose: Tree-sitter based analyzer that builds CQSPattern objects for TypeScript functions

Scope: Per-function CQS analysis with config-driven filtering for TypeScript code

Overview: Provides TypeScriptFunctionAnalyzer class that traverses TypeScript AST to analyze
    each function for CQS patterns. Builds CQSPattern objects containing INPUT and OUTPUT
    operations for each function/method. Extends TypeScriptBaseAnalyzer for tree-sitter
    utilities and delegates function extraction to TypeScriptFunctionExtractor. Applies
    configuration filtering including ignore_methods for constructor exclusion and
    detect_fluent_interface for return this patterns.

Dependencies: TypeScriptBaseAnalyzer, TypeScriptFunctionExtractor, TypeScriptInputDetector,
    TypeScriptOutputDetector, CQSConfig, CQSPattern

Exports: TypeScriptFunctionAnalyzer

Interfaces: TypeScriptFunctionAnalyzer.analyze(root_node, file_path, config) -> list[CQSPattern]

Implementation: Tree-sitter function extraction with per-function INPUT/OUTPUT detection
"""

from collections.abc import Callable

from src.analyzers.typescript_base import (
    TREE_SITTER_AVAILABLE,
    Node,
    TypeScriptBaseAnalyzer,
)
from src.linters.nesting.typescript_function_extractor import TypeScriptFunctionExtractor

from .config import CQSConfig
from .types import CQSPattern, InputOperation, OutputOperation
from .typescript_input_detector import TypeScriptInputDetector
from .typescript_output_detector import TypeScriptOutputDetector


def _get_function_child_positions(func_node: Node) -> list[tuple[int, int]]:
    """Get positions of child function nodes from a function_declaration."""
    return [
        (child.start_point[0], child.start_point[1])
        for child in func_node.children
        if child.type == "function"
    ]


def _get_child_function_positions(functions: list[tuple[Node, str]]) -> set[tuple[int, int]]:
    """Get positions of function nodes that are children of function_declarations."""
    declaration_nodes = (
        func_node for func_node, _ in functions if func_node.type == "function_declaration"
    )
    return {pos for node in declaration_nodes for pos in _get_function_child_positions(node)}


def _filter_duplicate_functions(
    functions: list[tuple[Node, str]],
) -> list[tuple[Node, str]]:
    """Filter out duplicate function detections."""
    declaration_positions = _get_child_function_positions(functions)
    return [
        (func_node, func_name)
        for func_node, func_name in functions
        if not (
            func_node.type == "function"
            and (func_node.start_point[0], func_node.start_point[1]) in declaration_positions
        )
    ]


def _find_function_body(func_node: Node) -> Node | None:
    """Find the statement_block (body) of a function."""
    return next(
        (child for child in func_node.children if child.type == "statement_block"),
        None,
    )


def _ends_with_return_this(body_node: Node) -> bool:
    """Check if function body ends with 'return this'."""
    returns = [child for child in body_node.children if child.type == "return_statement"]
    if not returns:
        return False
    return any(child.type == "this" for child in returns[-1].children)


def _is_async_function(func_node: Node, text: str) -> bool:
    """Check if function is async."""
    if any(child.type == "async" for child in func_node.children):
        return True
    return text.startswith("async ")


def _is_constructor_method(node: Node, get_text: Callable[[Node], str]) -> bool:
    """Check if method is a constructor."""
    for child in node.children:
        if child.type == "property_identifier":
            return get_text(child) == "constructor"
    return False


def _get_class_type_identifier(class_node: Node, get_text: Callable[[Node], str]) -> str | None:
    """Extract the type identifier from a class node."""
    for child in class_node.children:
        if child.type == "type_identifier":
            return get_text(child)
    return None


def _find_enclosing_class_name(func_node: Node, get_text: Callable[[Node], str]) -> str | None:
    """Find enclosing class name for a method."""
    current = func_node.parent
    while current is not None:
        if current.type in ("class_declaration", "class"):
            return _get_class_type_identifier(current, get_text)
        current = current.parent
    return None


class TypeScriptFunctionAnalyzer(TypeScriptBaseAnalyzer):
    """Analyzes TypeScript AST to build CQSPattern objects for each function."""

    def __init__(self) -> None:
        """Initialize analyzer with input/output detectors."""
        super().__init__()
        self._function_extractor = TypeScriptFunctionExtractor()
        self._input_detector = TypeScriptInputDetector()
        self._output_detector = TypeScriptOutputDetector()

    def analyze(self, root_node: Node, file_path: str, config: CQSConfig) -> list[CQSPattern]:
        """Analyze TypeScript AST and return CQSPattern for each function."""
        if not TREE_SITTER_AVAILABLE or root_node is None:
            return []

        functions = self._function_extractor.collect_all_functions(root_node)
        functions = _filter_duplicate_functions(functions)

        return [
            self._analyze_function(func_node, func_name, file_path)
            for func_node, func_name in functions
            if not self._should_skip(func_node, func_name, config)
        ]

    def _should_skip(self, func_node: Node, func_name: str, config: CQSConfig) -> bool:
        """Check if function should be skipped (ignored or fluent interface)."""
        return self._is_ignored_method(
            func_node, func_name, config
        ) or self._is_fluent_interface_function(func_node, config)

    def _is_ignored_method(self, func_node: Node, func_name: str, config: CQSConfig) -> bool:
        """Check if method should be ignored based on config."""
        if func_name in config.ignore_methods:
            return True
        if func_node.type != "method_definition":
            return False
        if not _is_constructor_method(func_node, self.extract_node_text):
            return False
        return "constructor" in config.ignore_methods or "__init__" in config.ignore_methods

    def _is_fluent_interface_function(self, func_node: Node, config: CQSConfig) -> bool:
        """Check if function uses fluent interface pattern."""
        if not config.detect_fluent_interface:
            return False
        body_node = _find_function_body(func_node)
        return body_node is not None and _ends_with_return_this(body_node)

    def _analyze_function(self, func_node: Node, func_name: str, file_path: str) -> CQSPattern:
        """Analyze a single function for CQS patterns."""
        body_node = _find_function_body(func_node)
        inputs, outputs = self._detect_operations(body_node)

        return CQSPattern(
            function_name=func_name,
            line=func_node.start_point[0] + 1,
            column=func_node.start_point[1],
            file_path=file_path,
            inputs=inputs,
            outputs=outputs,
            is_method=func_node.type == "method_definition",
            is_async=_is_async_function(func_node, self.extract_node_text(func_node)),
            class_name=_find_enclosing_class_name(func_node, self.extract_node_text),
        )

    def _detect_operations(
        self, body_node: Node | None
    ) -> tuple[list[InputOperation], list[OutputOperation]]:
        """Detect INPUT and OUTPUT operations in function body."""
        if body_node is None:
            return [], []
        return (
            self._input_detector.find_inputs(body_node),
            self._output_detector.find_outputs(body_node),
        )
