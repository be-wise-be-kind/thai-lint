"""
Purpose: TypeScript tree-sitter analyzer for Law of Demeter chain detection

Scope: Extract attribute/method chains and import information from TypeScript AST

Overview: Provides TypeScriptDemeterAnalyzer that extends TypeScriptBaseAnalyzer to walk
    tree-sitter ASTs for member_expression and call_expression nodes. Extracts chain parts
    with call markers and optional chaining indicators. Extracts import-to-module mappings
    from import_statement nodes (named imports, namespace imports, default imports). Reuses
    FileImports dataclass from the Python analyzer for cross-language consistency. Provides
    TSNodeAdapter for bridging tree-sitter node metadata to the violation builder interface.

Dependencies: src.analyzers.typescript_base, src.linters.law_of_demeter.python_analyzer

Exports: TypeScriptDemeterAnalyzer, TSNodeAdapter, has_optional_chain

Interfaces: extract_chains(root, min_depth), extract_imports(root)

Implementation: Tree-sitter node traversal with chain deduplication by line, optional chain
    detection via optional_chain node type, adapter pattern for violation builder compatibility
"""

from dataclasses import dataclass
from typing import Any

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE, TypeScriptBaseAnalyzer

from .python_analyzer import FileImports


@dataclass
class TSNodeAdapter:
    """Adapts tree-sitter node position info to violation builder interface."""

    lineno: int
    col_offset: int


def has_optional_chain(parts: list[str]) -> bool:
    """Check if chain parts contain optional chaining markers.

    Args:
        parts: Chain parts list

    Returns:
        True if any part starts with '?' indicating optional chaining
    """
    return any(p.startswith("?") for p in parts)


class TypeScriptDemeterAnalyzer(TypeScriptBaseAnalyzer):
    """Analyzes TypeScript code for Law of Demeter chain patterns."""

    def extract_chains(self, root: Any, min_depth: int) -> list[tuple[list[str], Any]]:
        """Extract attribute/method chains meeting min_depth from tree-sitter AST.

        Args:
            root: Tree-sitter root node
            min_depth: Minimum chain depth (number of dots) to report

        Returns:
            List of (parts, node_adapter) tuples, deduplicated per line
        """
        if not TREE_SITTER_AVAILABLE or root is None:
            return []

        chains = _collect_raw_chains(self, root, min_depth)
        return _deduplicate_by_line(chains)

    def extract_imports(self, root: Any) -> FileImports:
        """Extract import information from TypeScript AST.

        Args:
            root: Tree-sitter root node

        Returns:
            FileImports with module names and from-import mappings
        """
        if not TREE_SITTER_AVAILABLE or root is None:
            return FileImports()

        imports = FileImports()
        for node in self.walk_tree(root, "import_statement"):
            _process_import_statement(self, node, imports)
        return imports


def _collect_raw_chains(
    analyzer: TypeScriptDemeterAnalyzer, root: Any, min_depth: int
) -> list[tuple[list[str], TSNodeAdapter]]:
    """Walk AST and collect all chains meeting minimum depth."""
    chains: list[tuple[list[str], TSNodeAdapter]] = []
    seen_nodes: set[int] = set()

    for node in analyzer.walk_tree(root, "member_expression"):
        _try_extract_chain(node, min_depth, chains, seen_nodes)

    for node in analyzer.walk_tree(root, "call_expression"):
        _try_extract_from_call(node, min_depth, chains, seen_nodes)

    return chains


def _try_extract_chain(
    node: Any,
    min_depth: int,
    chains: list[tuple[list[str], TSNodeAdapter]],
    seen_nodes: set[int],
) -> None:
    """Try to extract a chain from a member_expression node."""
    if id(node) in seen_nodes:
        return
    parts = _chain_to_parts(node)
    depth = len(parts) - 1
    if depth >= min_depth:
        adapter = _make_adapter(node)
        chains.append((parts, adapter))
        _mark_descendants(node, seen_nodes)


def _try_extract_from_call(
    node: Any,
    min_depth: int,
    chains: list[tuple[list[str], TSNodeAdapter]],
    seen_nodes: set[int],
) -> None:
    """Try to extract a chain from a call_expression wrapping a member_expression."""
    if id(node) in seen_nodes:
        return
    func_child = _first_child(node)
    if func_child is not None and func_child.type == "member_expression":
        parts = _chain_to_parts(node)
        depth = len(parts) - 1
        if depth >= min_depth:
            adapter = _make_adapter(node)
            chains.append((parts, adapter))
            _mark_descendants(node, seen_nodes)


def _mark_descendants(node: Any, seen: set[int]) -> None:
    """Mark all descendant nodes as seen to avoid duplicate extraction."""
    for child in node.children:
        seen.add(id(child))
        _mark_descendants(child, seen)


def _chain_to_parts(node: Any) -> list[str]:
    """Walk a tree-sitter node to extract chain parts."""
    parts: list[str] = []
    current = node
    pending_call = False

    while current is not None:
        current, pending_call = _process_ts_node(current, parts, pending_call)

    parts.reverse()
    return parts


def _process_ts_node(current: Any, parts: list[str], pending_call: bool) -> tuple[Any, bool]:
    """Process a single tree-sitter node during chain extraction."""
    if current.type == "member_expression":
        return _handle_member_expression(current, parts, pending_call)

    if current.type == "call_expression":
        return _first_child(current), True

    return _handle_terminal_node(current, parts, pending_call)


def _handle_member_expression(node: Any, parts: list[str], pending_call: bool) -> tuple[Any, bool]:
    """Extract property from member_expression and return object node."""
    prop_name = _get_property_name(node)
    is_optional = _node_has_optional_chain(node)

    if is_optional:
        prop_name = "?" + prop_name

    parts.append(prop_name + _call_suffix(pending_call))
    return _first_child(node), False


def _handle_terminal_node(node: Any, parts: list[str], pending_call: bool) -> tuple[None, bool]:
    """Handle terminal nodes (identifier, this, etc.)."""
    name = _get_node_name(node)
    parts.append(name + _call_suffix(pending_call))
    return None, False


def _get_property_name(node: Any) -> str:
    """Get property name from a member_expression node."""
    for child in node.children:
        if child.type == "property_identifier":
            return child.text.decode() if child.text else "?"
    return "?"


def _node_has_optional_chain(node: Any) -> bool:
    """Check if a member_expression uses optional chaining (?.)."""
    return any(child.type == "optional_chain" for child in node.children)


def _get_node_name(node: Any) -> str:
    """Extract name from a terminal node."""
    if node.type == "this":
        return "this"
    if node.type == "identifier":
        return node.text.decode() if node.text else "?"
    return node.text.decode() if node.text else "?"


def _call_suffix(pending: bool) -> str:
    """Return '()' if a call is pending, else empty string."""
    return "()" if pending else ""


def _first_child(node: Any) -> Any:
    """Get the first child of a node, or None."""
    return node.children[0] if node.children else None


def _make_adapter(node: Any) -> TSNodeAdapter:
    """Create a TSNodeAdapter from a tree-sitter node."""
    row, col = node.start_point
    return TSNodeAdapter(lineno=row + 1, col_offset=col)


def _deduplicate_by_line(
    chains: list[tuple[list[str], TSNodeAdapter]],
) -> list[tuple[list[str], TSNodeAdapter]]:
    """Keep only the longest chain per line number."""
    seen: dict[int, tuple[list[str], TSNodeAdapter]] = {}
    for parts, adapter in chains:
        line = adapter.lineno
        if line not in seen or len(parts) > len(seen[line][0]):
            seen[line] = (parts, adapter)
    return list(seen.values())


# ============================================================================
# Import extraction
# ============================================================================


def _process_import_statement(
    analyzer: TypeScriptDemeterAnalyzer, node: Any, imports: FileImports
) -> None:
    """Process a single import_statement node."""
    module_name = _extract_module_source(analyzer, node)
    clause = analyzer.find_child_by_type(node, "import_clause")
    if clause is None:
        return

    _process_import_clause(analyzer, clause, module_name, imports)


def _process_import_clause(
    analyzer: TypeScriptDemeterAnalyzer,
    clause: Any,
    module_name: str,
    imports: FileImports,
) -> None:
    """Process import_clause to extract bindings."""
    for child in clause.children:
        if child.type == "named_imports":
            _process_named_imports(analyzer, child, module_name, imports)
        elif child.type == "namespace_import":
            _process_namespace_import(analyzer, child, imports)
        elif child.type == "identifier":
            _process_default_import(child, imports)


def _process_default_import(node: Any, imports: FileImports) -> None:
    """Process default import: import X from 'module'."""
    name = node.text.decode() if node.text else ""
    if name:
        imports.module_names.add(name)


def _process_named_imports(
    analyzer: TypeScriptDemeterAnalyzer,
    node: Any,
    module_name: str,
    imports: FileImports,
) -> None:
    """Process named_imports: import { X, Y } from 'module'."""
    for specifier in analyzer.walk_tree(node, "import_specifier"):
        ident = analyzer.find_child_by_type(specifier, "identifier")
        if ident is not None:
            name = ident.text.decode() if ident.text else ""
            if name:
                imports.from_imports[name] = module_name


def _process_namespace_import(
    analyzer: TypeScriptDemeterAnalyzer,
    node: Any,
    imports: FileImports,
) -> None:
    """Process namespace_import: import * as X from 'module'."""
    ident = analyzer.find_child_by_type(node, "identifier")
    if ident is not None:
        name = ident.text.decode() if ident.text else ""
        if name:
            imports.module_names.add(name)


def _extract_module_source(analyzer: TypeScriptDemeterAnalyzer, node: Any) -> str:
    """Extract module source string from import_statement."""
    string_node = analyzer.find_child_by_type(node, "string")
    if string_node is None:
        return ""

    frag = analyzer.find_child_by_type(string_node, "string_fragment")
    if frag is not None:
        return frag.text.decode() if frag.text else ""

    return ""
