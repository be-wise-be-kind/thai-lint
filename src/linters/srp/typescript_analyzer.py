"""
Purpose: TypeScript AST analyzer for detecting SRP violations in TypeScript classes

Scope: TypeScriptSRPAnalyzer class for analyzing TypeScript classes using tree-sitter

Overview: Implements TypeScript-specific SRP analysis using tree-sitter parser to analyze class
    definitions. Walks the AST to find all class declarations, then analyzes each class for
    SRP violation indicators: method count, lines of code, and responsibility keywords. Collects
    comprehensive metrics including class name, method count, LOC, keyword presence, and location
    information. Handles TypeScript-specific features like decorators, getters, setters, and
    constructor parameters. Returns structured metric dictionaries that the main linter uses to
    create violations. Gracefully handles missing tree-sitter dependency.

Dependencies: tree-sitter, tree-sitter-typescript for TypeScript parsing, typing for type hints

Exports: TypeScriptSRPAnalyzer class

Interfaces: find_all_classes(tree), analyze_class(class_node, source, config)

Implementation: tree-sitter AST walking pattern, metric collection, optional dependency handling
"""

from typing import Any

try:
    import tree_sitter_typescript as tstypescript
    from tree_sitter import Language, Parser

    TS_LANGUAGE = Language(tstypescript.language_typescript())
    TS_PARSER = Parser(TS_LANGUAGE)
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    TS_PARSER = None  # type: ignore

from .config import SRPConfig


class TypeScriptSRPAnalyzer:
    """Analyzes TypeScript classes for SRP violations."""

    def parse_typescript(self, code: str) -> Any:
        """Parse TypeScript code to AST using tree-sitter.

        Args:
            code: TypeScript source code to parse

        Returns:
            Tree-sitter AST root node, or None if parsing fails
        """
        if not TREE_SITTER_AVAILABLE or TS_PARSER is None:
            return None

        tree = TS_PARSER.parse(bytes(code, "utf8"))
        return tree.root_node

    def find_all_classes(self, root_node: Any) -> list[Any]:
        """Find all class declarations in TypeScript AST.

        Args:
            root_node: Root tree-sitter node to search

        Returns:
            List of all class declaration nodes
        """
        if not TREE_SITTER_AVAILABLE or root_node is None:
            return []

        classes: list[Any] = []
        self._walk_tree(root_node, classes)
        return classes

    def _walk_tree(self, node: Any, classes: list[Any]) -> None:
        """Recursively walk tree to find class declarations.

        Args:
            node: Current tree-sitter node
            classes: List to accumulate class nodes
        """
        if node.type == "class_declaration":
            classes.append(node)

        for child in node.children:
            self._walk_tree(child, classes)

    def analyze_class(self, class_node: Any, source: str, config: SRPConfig) -> dict[str, Any]:
        """Analyze a TypeScript class for SRP metrics.

        Args:
            class_node: Tree-sitter node representing a class declaration
            source: Full source code of the file
            config: SRP configuration with thresholds and keywords

        Returns:
            Dictionary with class metrics (name, method_count, loc, etc.)
        """
        class_name = self._get_class_name(class_node)
        method_count = self._count_methods(class_node)
        loc = self._count_loc(class_node, source)
        has_keyword = any(keyword in class_name for keyword in config.keywords)

        return {
            "class_name": class_name,
            "method_count": method_count,
            "loc": loc,
            "has_keyword": has_keyword,
            "line": class_node.start_point[0] + 1,
            "column": class_node.start_point[1],
        }

    def _get_class_name(self, class_node: Any) -> str:
        """Extract class name from class declaration node.

        Args:
            class_node: Tree-sitter class declaration node

        Returns:
            Class name as string
        """
        for child in class_node.children:
            if child.type == "type_identifier":
                return child.text.decode("utf8")
        return "UnknownClass"

    def _count_methods(self, class_node: Any) -> int:
        """Count methods in a TypeScript class.

        Args:
            class_node: Tree-sitter class declaration node

        Returns:
            Number of methods in the class
        """
        body = self._get_class_body(class_node)
        if not body:
            return 0

        methods = 0
        for child in body.children:
            if child.type in ("method_definition", "public_field_definition"):
                # Only count method definitions, not properties
                if child.type == "method_definition":
                    methods += 1
        return methods

    def _get_class_body(self, class_node: Any) -> Any:
        """Get class body node.

        Args:
            class_node: Tree-sitter class declaration node

        Returns:
            Class body node or None
        """
        for child in class_node.children:
            if child.type == "class_body":
                return child
        return None

    def _count_loc(self, class_node: Any, source: str) -> int:
        """Count lines of code in a TypeScript class.

        Args:
            class_node: Tree-sitter class declaration node
            source: Full source code of the file

        Returns:
            Number of code lines in the class
        """
        start_line = class_node.start_point[0]
        end_line = class_node.end_point[0]
        lines = source.split("\n")[start_line : end_line + 1]

        # Filter out blank lines and comments
        code_lines = [
            line
            for line in lines
            if line.strip()
            and not line.strip().startswith("//")
            and not line.strip().startswith("/*")
        ]
        return len(code_lines)
