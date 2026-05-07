"""
Purpose: Python AST analyzer for Law of Demeter chain detection

Scope: Extract attribute/method chains and import information from Python AST

Overview: Provides functions that walk Python AST trees to find attribute/method chains
    meeting a minimum depth threshold and extract import information for the module-access
    filter. Also provides the FileImports dataclass for tracking module names and from-imports
    per file.

Dependencies: ast, dataclasses, chain_extractor

Exports: FileImports, extract_chains, extract_imports

Interfaces: extract_chains(tree, min_depth), extract_imports(tree)

Implementation: Uses ast.walk() for chain extraction with per-line deduplication
"""

import ast
from dataclasses import dataclass, field

from .chain_extractor import chain_to_parts


@dataclass
class FileImports:
    """Tracks what names are imported as modules vs objects in a file."""

    module_names: set[str] = field(default_factory=set)
    from_imports: dict[str, str] = field(default_factory=dict)


def extract_chains(tree: ast.AST, min_depth: int) -> list[tuple[list[str], ast.AST]]:
    """Extract all attribute/method chains meeting min_depth from AST.

    Args:
        tree: Parsed Python AST
        min_depth: Minimum chain depth (number of dots) to report

    Returns:
        List of (parts, node) tuples, deduplicated per line
    """
    chains = _collect_raw_chains(tree, min_depth)
    return _deduplicate_by_line(chains)


def extract_imports(tree: ast.AST) -> FileImports:
    """Extract import information from an AST.

    Args:
        tree: Parsed Python AST

    Returns:
        FileImports with module names and from-import mappings
    """
    imports = FileImports()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            _process_import(node, imports)
        elif isinstance(node, ast.ImportFrom):
            _process_from_import(node, imports)
    return imports


def _collect_raw_chains(tree: ast.AST, min_depth: int) -> list[tuple[list[str], ast.AST]]:
    """Walk AST and collect all chains meeting minimum depth."""
    chains: list[tuple[list[str], ast.AST]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Attribute, ast.Call)):
            parts = chain_to_parts(node)
            depth = len(parts) - 1
            if depth >= min_depth:
                chains.append((parts, node))
    return chains


def _deduplicate_by_line(
    chains: list[tuple[list[str], ast.AST]],
) -> list[tuple[list[str], ast.AST]]:
    """Keep only the longest chain per line number."""
    seen: dict[int, tuple[list[str], ast.AST]] = {}
    for parts, node in chains:
        lineno = getattr(node, "lineno", 0)
        if lineno not in seen or len(parts) > len(seen[lineno][0]):
            seen[lineno] = (parts, node)
    return list(seen.values())


def _process_import(node: ast.Import, imports: FileImports) -> None:
    """Process an 'import x' or 'import x as y' statement."""
    for alias in node.names:
        name = alias.asname if alias.asname else alias.name
        imports.module_names.add(name)


def _process_from_import(node: ast.ImportFrom, imports: FileImports) -> None:
    """Process a 'from x import y' or 'from x import y as z' statement."""
    module = node.module or ""
    for alias in node.names:
        name = alias.asname if alias.asname else alias.name
        imports.from_imports[name] = module
