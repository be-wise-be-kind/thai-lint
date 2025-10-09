"""
Purpose: Base class for token-based duplicate code analysis

Scope: Common duplicate detection workflow for Python and TypeScript analyzers

Overview: Provides shared infrastructure for token-based duplicate code detection across different
    programming languages. Implements common workflow of tokenization, rolling hash window generation,
    and CodeBlock creation. Subclasses provide language-specific filtering (e.g., interface filtering
    for TypeScript). Eliminates duplication between PythonDuplicateAnalyzer and TypeScriptDuplicateAnalyzer
    by extracting shared analyze() method pattern and CodeBlock creation logic.

Dependencies: TokenHasher, CodeBlock, DRYConfig, pathlib.Path

Exports: BaseTokenAnalyzer class

Interfaces: BaseTokenAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]

Implementation: Template method pattern with extension point for language-specific block filtering
"""

from pathlib import Path

from .cache import CodeBlock
from .config import DRYConfig
from .token_hasher import TokenHasher


class BaseTokenAnalyzer:
    """Base analyzer for token-based duplicate detection."""

    def __init__(self) -> None:
        """Initialize analyzer with token hasher."""
        self._hasher = TokenHasher()

    def analyze(self, file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]:
        """Analyze file for duplicate code blocks.

        Args:
            file_path: Path to source file
            content: File content
            config: DRY configuration

        Returns:
            List of CodeBlock instances with hash values
        """
        lines = self._hasher.tokenize(content)
        windows = self._hasher.rolling_hash(lines, config.min_duplicate_lines)

        blocks = []
        for hash_val, start_line, end_line, snippet in windows:
            if self._should_include_block(content, start_line, end_line):
                block = CodeBlock(
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    snippet=snippet,
                    hash_value=hash_val,
                )
                blocks.append(block)

        return blocks

    def _should_include_block(self, content: str, start_line: int, end_line: int) -> bool:
        """Determine if block should be included.

        Extension point for language-specific filtering.

        Args:
            content: File content
            start_line: Block start line
            end_line: Block end line

        Returns:
            True if block should be included, False to filter out
        """
        return True
