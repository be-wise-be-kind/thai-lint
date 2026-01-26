"""
Purpose: Python AST analysis for finding conditional verbose logging patterns

Scope: Detection of if verbose: logger.*() anti-patterns in Python code

Overview: Provides ConditionalVerboseAnalyzer class that traverses Python AST to find logging calls
    that are conditionally guarded by verbose flags. Detects patterns like 'if verbose: logger.debug()'
    or 'if self.verbose: logger.info()' which are anti-patterns because logging levels should be
    configured at the logger level rather than through code conditionals. Supports detection of
    various verbose condition patterns including simple names, attribute access, dict access, and
    method calls on context objects.

Dependencies: ast module for AST parsing and node types

Exports: ConditionalVerboseAnalyzer class, is_verbose_condition function, is_logger_call function

Interfaces: find_conditional_verbose_calls(tree) -> list[tuple[If, Call, int]]

Implementation: AST walk pattern with condition matching for verbose patterns and logger call detection
"""

import ast

# Logger methods that indicate a logging call
LOGGER_METHODS = frozenset({"debug", "info", "warning", "error", "critical", "log", "exception"})

# Verbose-related names that typically guard logging
VERBOSE_NAMES = frozenset({"verbose", "debug", "is_verbose", "is_debug"})


def is_verbose_condition(test: ast.expr) -> bool:
    """Check if an expression is a verbose-like condition.

    Matches patterns like:
    - verbose
    - self.verbose
    - config.verbose
    - params.verbose
    - ctx.obj.get("verbose")
    - ctx.obj["verbose"]

    Args:
        test: The condition expression to check

    Returns:
        True if the condition appears to be a verbose check
    """
    return (
        _is_simple_verbose_name(test)
        or _is_verbose_attribute(test)
        or _is_verbose_subscript(test)
        or _is_verbose_dict_get(test)
    )


def _is_simple_verbose_name(test: ast.expr) -> bool:
    """Check for simple name like 'verbose' or 'debug'."""
    return isinstance(test, ast.Name) and test.id.lower() in VERBOSE_NAMES


def _is_verbose_attribute(test: ast.expr) -> bool:
    """Check for attribute access like 'self.verbose' or 'config.verbose'."""
    if not isinstance(test, ast.Attribute):
        return False
    return test.attr.lower() in VERBOSE_NAMES


def _is_verbose_subscript(test: ast.expr) -> bool:
    """Check for subscript access like 'ctx.obj["verbose"]'."""
    if not isinstance(test, ast.Subscript):
        return False
    if not isinstance(test.slice, ast.Constant):
        return False
    value = test.slice.value
    return isinstance(value, str) and value.lower() in VERBOSE_NAMES


def _is_verbose_dict_get(test: ast.expr) -> bool:
    """Check for dict.get call like 'ctx.obj.get("verbose")'."""
    if not isinstance(test, ast.Call):
        return False
    if not _is_dict_get_call_with_args(test):
        return False
    return _first_arg_is_verbose_string(test.args[0])


def _is_dict_get_call_with_args(call: ast.Call) -> bool:
    """Check if call is a .get() method call with arguments."""
    if not isinstance(call.func, ast.Attribute):
        return False
    if call.func.attr != "get":
        return False
    return bool(call.args)


def _first_arg_is_verbose_string(arg: ast.expr) -> bool:
    """Check if argument is a verbose-related string constant."""
    if not isinstance(arg, ast.Constant):
        return False
    value = arg.value
    return isinstance(value, str) and value.lower() in VERBOSE_NAMES


def is_logger_call(node: ast.Call) -> bool:
    """Check if a Call node is a logger method call.

    Matches patterns like:
    - logger.debug()
    - logging.info()
    - self.logger.warning()
    - log.error()

    Args:
        node: The Call node to check

    Returns:
        True if this appears to be a logging call
    """
    if not isinstance(node.func, ast.Attribute):
        return False
    return node.func.attr in LOGGER_METHODS


def _extract_logger_method(node: ast.Call) -> str:
    """Extract the logger method name from a call node.

    Args:
        node: The Call node (must be a logger call)

    Returns:
        The logger method name (e.g., 'debug', 'info')
    """
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


class ConditionalVerboseAnalyzer:
    """Analyzes Python AST to find conditional verbose logging patterns."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.violations: list[tuple[ast.If, ast.Call, int]] = []

    def find_conditional_verbose_calls(
        self, tree: ast.AST
    ) -> list[tuple[ast.If, ast.Call, str, int]]:
        """Find all conditional verbose logging patterns in the AST.

        Looks for if statements with verbose-like conditions that contain
        logger method calls in their body.

        Args:
            tree: The AST to analyze

        Returns:
            List of tuples (if_node, call_node, logger_method, line_number)
        """
        verbose_if_nodes = (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.If) and is_verbose_condition(node.test)
        )

        results: list[tuple[ast.If, ast.Call, str, int]] = []
        for if_node in verbose_if_nodes:
            results.extend(self._extract_logger_call_results(if_node))

        return results

    def _extract_logger_call_results(
        self, if_node: ast.If
    ) -> list[tuple[ast.If, ast.Call, str, int]]:
        """Extract logger call results from a verbose if node."""
        logger_calls = self._find_logger_calls_in_body(if_node.body)
        return [
            (
                if_node,
                call_node,
                _extract_logger_method(call_node),
                call_node.lineno if hasattr(call_node, "lineno") else if_node.lineno,
            )
            for call_node in logger_calls
        ]

    def _find_logger_calls_in_body(self, body: list[ast.stmt]) -> list[ast.Call]:
        """Find all logger calls in a list of statements.

        Args:
            body: List of AST statements

        Returns:
            List of Call nodes that are logger calls
        """
        logger_calls: list[ast.Call] = []
        for stmt in body:
            for node in ast.walk(stmt):
                if isinstance(node, ast.Call) and is_logger_call(node):
                    logger_calls.append(node)
        return logger_calls
