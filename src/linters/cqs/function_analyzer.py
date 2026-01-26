"""
Purpose: AST visitor that builds CQSPattern objects for each function in Python code

Scope: Per-function CQS analysis with config-driven filtering

Overview: Provides FunctionAnalyzer class that traverses Python AST to analyze each function
    for CQS patterns. Builds CQSPattern objects containing INPUT and OUTPUT operations for
    each function/method. Applies configuration filtering including ignore_methods for
    constructor exclusion, ignore_decorators for property-like methods, and detect_fluent_interface
    for return self patterns. Tracks class context via stack for proper method detection.

Dependencies: ast module, InputDetector, OutputDetector, CQSConfig, CQSPattern

Exports: FunctionAnalyzer

Interfaces: FunctionAnalyzer.analyze(tree: ast.Module) -> list[CQSPattern]

Implementation: AST NodeVisitor with class context tracking and config-based filtering

Suppressions:
    - N802: visit_ClassDef, visit_FunctionDef, visit_AsyncFunctionDef follow Python AST
        visitor naming convention (camelCase required by ast.NodeVisitor)
    - invalid-name: AST visitor methods follow required camelCase naming convention
"""

import ast
from collections.abc import Sequence

from .config import CQSConfig
from .input_detector import InputDetector
from .output_detector import OutputDetector
from .types import CQSPattern, InputOperation, OutputOperation


def _get_name_from_decorator(dec: ast.expr) -> str | None:
    """Extract decorator name from a single decorator expression."""
    if isinstance(dec, ast.Name):
        return dec.id
    if isinstance(dec, ast.Attribute):
        return dec.attr
    if isinstance(dec, ast.Call):
        return _get_name_from_call_decorator(dec.func)
    return None


def _get_name_from_call_decorator(func: ast.expr) -> str | None:
    """Extract name from Call decorator's func attribute."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _get_decorator_names(decorators: list[ast.expr]) -> list[str]:
    """Extract decorator names from decorator list."""
    names = [_get_name_from_decorator(dec) for dec in decorators]
    return [name for name in names if name is not None]


def _has_return_self(body: Sequence[ast.stmt]) -> bool:
    """Check if function body ends with 'return self'."""
    if not body:
        return False

    last_stmt = body[-1]
    if not isinstance(last_stmt, ast.Return):
        return False
    if last_stmt.value is None:
        return False
    return isinstance(last_stmt.value, ast.Name) and last_stmt.value.id == "self"


def _is_fluent_interface(node: ast.FunctionDef | ast.AsyncFunctionDef, config: CQSConfig) -> bool:
    """Check if function uses fluent interface pattern (return self)."""
    if not config.detect_fluent_interface:
        return False
    return _has_return_self(node.body)


def _is_function_definition(stmt: ast.stmt) -> bool:
    """Check if statement is a function definition."""
    return isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))


def _detect_inputs_in_body(
    body: Sequence[ast.stmt], input_detector: InputDetector
) -> list[InputOperation]:
    """Detect INPUT operations in function body statements."""
    inputs: list[InputOperation] = []
    stmts = [stmt for stmt in body if not _is_function_definition(stmt)]
    for stmt in stmts:
        mini_module = ast.Module(body=[stmt], type_ignores=[])
        stmt_inputs = input_detector.find_inputs(mini_module)
        inputs.extend(stmt_inputs)
    return inputs


def _detect_outputs_in_body(
    body: Sequence[ast.stmt], output_detector: OutputDetector
) -> list[OutputOperation]:
    """Detect OUTPUT operations in function body statements."""
    outputs: list[OutputOperation] = []
    stmts = [stmt for stmt in body if not _is_function_definition(stmt)]
    for stmt in stmts:
        mini_module = ast.Module(body=[stmt], type_ignores=[])
        stmt_outputs = output_detector.find_outputs(mini_module)
        outputs.extend(stmt_outputs)
    return outputs


class FunctionAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST to build CQSPattern objects for each function."""

    def __init__(self, file_path: str, config: CQSConfig) -> None:
        """Initialize the analyzer."""
        self._file_path = file_path
        self._config = config
        self._input_detector = InputDetector()
        self._output_detector = OutputDetector()
        self._patterns: list[CQSPattern] = []
        self._class_stack: list[str] = []

    def analyze(self, tree: ast.Module) -> list[CQSPattern]:
        """Analyze AST and return CQSPattern for each function."""
        self._patterns = []
        self._class_stack = []
        self.visit(tree)
        return list(self._patterns)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit class definition to track class context."""
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit function definition to analyze for CQS patterns."""
        self._analyze_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit async function definition to analyze for CQS patterns."""
        self._analyze_function(node, is_async=True)

    def _analyze_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ) -> None:
        """Analyze a function/method for CQS patterns."""
        # Check if function should be ignored
        if self._should_ignore_function(node):
            self.generic_visit(node)
            return

        # Check for fluent interface pattern
        if _is_fluent_interface(node, self._config):
            self.generic_visit(node)
            return

        # Detect INPUTs and OUTPUTs in function body only (not nested functions)
        inputs = _detect_inputs_in_body(node.body, self._input_detector)
        outputs = _detect_outputs_in_body(node.body, self._output_detector)

        # Build pattern
        pattern = self._build_pattern(node, is_async, inputs, outputs)
        self._patterns.append(pattern)

        # Continue visiting nested functions
        self.generic_visit(node)

    def _build_pattern(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        is_async: bool,
        inputs: list[InputOperation],
        outputs: list[OutputOperation],
    ) -> CQSPattern:
        """Build CQSPattern from function node and detected operations."""
        is_method = len(self._class_stack) > 0
        class_name = self._class_stack[-1] if self._class_stack else None

        return CQSPattern(
            function_name=node.name,
            line=node.lineno,
            column=node.col_offset,
            file_path=self._file_path,
            inputs=inputs,
            outputs=outputs,
            is_method=is_method,
            is_async=is_async,
            class_name=class_name,
        )

    def _should_ignore_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if function should be ignored based on config."""
        # Check ignore_methods (e.g., __init__, __new__)
        if node.name in self._config.ignore_methods:
            return True

        # Check ignore_decorators (e.g., @property, @cached_property)
        decorator_names = _get_decorator_names(node.decorator_list)
        return any(name in self._config.ignore_decorators for name in decorator_names)
