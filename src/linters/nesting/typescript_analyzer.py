"""
Purpose: TypeScript AST-based nesting depth calculator

Scope: TypeScript code nesting depth analysis using typescript-estree parser

Overview: Analyzes TypeScript code to calculate maximum nesting depth using AST traversal.
    Implements visitor pattern to walk TypeScript AST, tracking current depth and maximum depth
    found. Increments depth for IfStatement, ForStatement, ForInStatement, ForOfStatement,
    WhileStatement, DoWhileStatement, TryStatement, CatchClause, and SwitchStatement nodes.
    Starts depth counting at 1 for function body. Returns maximum depth found and location.
    Currently provides stub implementation for TypeScript parsing that returns empty results,
    allowing Python tests to pass while TypeScript support is deferred.

Dependencies: subprocess for calling typescript-estree parser (Node.js) - not yet implemented

Exports: TypeScriptNestingAnalyzer class with calculate_max_depth method

Interfaces: calculate_max_depth(func_node: dict) -> tuple[int, int], parse_typescript method

Implementation: AST visitor pattern with depth tracking for TypeScript, stub for parsing
"""

from typing import Any


class TypeScriptNestingAnalyzer:
    """Calculates maximum nesting depth in TypeScript functions."""

    NESTING_NODE_TYPES = {
        "IfStatement",
        "ForStatement",
        "ForInStatement",
        "ForOfStatement",
        "WhileStatement",
        "DoWhileStatement",
        "TryStatement",
        "CatchClause",
        "SwitchStatement",
        "WithStatement",  # Deprecated but exists
    }

    def parse_typescript(self, code: str) -> dict[str, Any]:
        """Parse TypeScript code to AST using typescript-estree.

        Note: Requires Node.js and @typescript-eslint/typescript-estree.
        Currently returns stub for testing - full implementation deferred to TypeScript focus.

        Args:
            code: TypeScript source code to parse

        Returns:
            AST dictionary from typescript-estree (currently stub)
        """
        # TODO: Implement actual TypeScript parsing via Node.js
        # For now, return empty AST to allow Python tests to pass
        return {"type": "Program", "body": []}

    def calculate_max_depth(self, func_node: dict[str, Any]) -> tuple[int, int]:
        """Calculate maximum nesting depth in a TypeScript function.

        Args:
            func_node: TypeScript function AST node (dict from typescript-estree)

        Returns:
            Tuple of (max_depth, line_number_of_max_depth)
        """
        max_depth = 0
        max_depth_line = func_node.get("loc", {}).get("start", {}).get("line", 0)

        def visit_node(node: dict[str, Any], current_depth: int = 0) -> None:
            nonlocal max_depth, max_depth_line

            if current_depth > max_depth:
                max_depth = current_depth
                max_depth_line = node.get("loc", {}).get("start", {}).get("line", 0)

            # Check if node increases nesting depth
            if node.get("type") in self.NESTING_NODE_TYPES:
                current_depth += 1

            # Visit children (recursively walk all dict/list values)
            for _key, value in node.items():
                if isinstance(value, dict) and "type" in value:
                    visit_node(value, current_depth)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and "type" in item:
                            visit_node(item, current_depth)

        # Start at depth 1 for function body
        body = func_node.get("body", {})
        if body:
            visit_node(body, 1)

        return max_depth, max_depth_line
