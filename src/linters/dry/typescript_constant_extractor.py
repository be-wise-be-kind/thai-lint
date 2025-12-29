"""
Purpose: Extract TypeScript module-level constants using tree-sitter parsing

Scope: TypeScript constant extraction for duplicate constants detection

Overview: Extracts module-level constant definitions from TypeScript source code using tree-sitter.
    Identifies constants as top-level `const` declarations where the variable name matches the
    UPPER_SNAKE_CASE naming convention (e.g., const API_TIMEOUT = 30). Excludes non-const
    declarations (let, var), class-level constants, and function-level constants to focus on
    public module constants that should be consolidated across files.

Dependencies: tree-sitter, tree-sitter-typescript, re for pattern matching, ConstantInfo,
    TypeScriptValueExtractor

Exports: TypeScriptConstantExtractor class

Interfaces: TypeScriptConstantExtractor.extract(content: str) -> list[ConstantInfo]

Implementation: Tree-sitter-based parsing with const declaration filtering and ALL_CAPS regex matching

Suppressions:
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
    - broad-exception-caught: Defensive parsing for malformed TypeScript code
"""

from typing import Any

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE, TS_PARSER

from .constant import CONSTANT_NAME_PATTERN, ConstantInfo
from .typescript_value_extractor import TypeScriptValueExtractor

if TREE_SITTER_AVAILABLE:
    from tree_sitter import Node
else:
    Node = Any  # type: ignore[assignment,misc]

# Node types that represent values
VALUE_TYPES = frozenset(
    (
        "number",
        "string",
        "true",
        "false",
        "null",
        "identifier",
        "array",
        "object",
        "call_expression",
    )
)


class TypeScriptConstantExtractor:
    """Extracts module-level constants from TypeScript source code."""

    def __init__(self) -> None:
        """Initialize the TypeScript constant extractor."""
        self.tree_sitter_available = TREE_SITTER_AVAILABLE
        self._value_extractor = TypeScriptValueExtractor()

    def extract(self, content: str) -> list[ConstantInfo]:
        """Extract constants from TypeScript source code."""
        root = _parse_content(content)
        if root is None:
            return []
        constants: list[ConstantInfo] = []
        for child in root.children:
            constants.extend(self._extract_from_node(child, content))
        return constants

    def _extract_from_node(self, node: Node, content: str) -> list[ConstantInfo]:
        """Extract constants from a single AST node."""
        if node.type == "lexical_declaration":
            return self._extract_from_lexical_declaration(node, content)
        if node.type == "export_statement":
            return self._extract_from_export(node, content)
        return []

    def _extract_from_lexical_declaration(self, node: Node, content: str) -> list[ConstantInfo]:
        """Extract constants from a lexical declaration."""
        if not _is_const_declaration(node):
            return []
        return [
            info
            for c in node.children
            if c.type == "variable_declarator"
            and (info := self._extract_from_declarator(c, content))
        ]

    def _extract_from_export(self, node: Node, content: str) -> list[ConstantInfo]:
        """Extract constants from an export statement."""
        for child in node.children:
            if child.type == "lexical_declaration":
                return self._extract_from_lexical_declaration(child, content)
        return []

    def _extract_from_declarator(self, node: Node, content: str) -> ConstantInfo | None:
        """Extract constant info from a variable declarator."""
        name, value = _get_name_and_value(node, content, self._value_extractor)
        if not name or not _is_constant_name(name):
            return None
        return ConstantInfo(name=name, line_number=node.start_point[0] + 1, value=value)


def _parse_content(content: str) -> Node | None:
    """Parse content and return root node, or None on failure."""
    if not TREE_SITTER_AVAILABLE or TS_PARSER is None:
        return None
    try:
        return TS_PARSER.parse(bytes(content, "utf8")).root_node
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def _is_const_declaration(node: Node) -> bool:
    """Check if lexical declaration is a const."""
    return any(child.type == "const" for child in node.children)


def _get_name_and_value(
    node: Node, content: str, extractor: TypeScriptValueExtractor
) -> tuple[str | None, str | None]:
    """Extract name and value from declarator node."""
    name = next(
        (extractor.get_node_text(c, content) for c in node.children if c.type == "identifier"),
        None,
    )
    value = next(
        (extractor.get_value_string(c, content) for c in node.children if c.type in VALUE_TYPES),
        None,
    )
    return name, value


def _is_constant_name(name: str) -> bool:
    """Check if name matches constant naming convention."""
    return not name.startswith("_") and bool(CONSTANT_NAME_PATTERN.match(name))
