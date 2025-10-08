"""
Purpose: TypeScript/JavaScript source code analysis stub for duplicate detection

Scope: TypeScript and JavaScript file analysis placeholder

Overview: Stub implementation for TypeScript and JavaScript duplicate code analysis. Returns empty
    list in PR2, deferring full implementation to PR3 when tree-sitter integration will be added.
    Allows DRY linter to handle TypeScript files gracefully without errors while Python duplicate
    detection is validated. Full tokenization and AST-based analysis to be implemented in PR3.

Dependencies: CodeBlock, DRYConfig, pathlib.Path

Exports: TypeScriptDuplicateAnalyzer class

Interfaces: TypeScriptDuplicateAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig)
    -> list[CodeBlock]

Implementation: Stub returning empty list, TODO marker for PR3 tree-sitter implementation
"""

from pathlib import Path

from .cache import CodeBlock
from .config import DRYConfig


class TypeScriptDuplicateAnalyzer:
    """Analyzes TypeScript/JavaScript code for duplicate blocks."""

    def __init__(self) -> None:
        """Initialize analyzer."""
        pass

    def analyze(self, file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]:
        """Analyze TypeScript/JavaScript file for code blocks.

        TODO PR3: Implement tree-sitter based TypeScript tokenization
        Currently returns empty list as stub implementation.

        Args:
            file_path: Path to TypeScript/JavaScript file
            content: File content
            config: DRY configuration

        Returns:
            Empty list (stub implementation for PR2)
        """
        # Stub implementation - returns no blocks
        # Full implementation in PR3 will use tree-sitter for tokenization
        return []
