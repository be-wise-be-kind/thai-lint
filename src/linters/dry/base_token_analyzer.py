"""
Purpose: Base class for token-based duplicate code analysis

Scope: Common duplicate detection workflow for Python and TypeScript analyzers

Overview: Provides shared infrastructure for token-based duplicate code detection across different
    programming languages. Implements common workflow of tokenization, rolling hash window generation,
    and CodeBlock creation. Subclasses provide language-specific filtering (e.g., interface filtering
    for TypeScript). Eliminates duplication between PythonDuplicateAnalyzer and TypeScriptDuplicateAnalyzer
    by extracting shared analyze() method pattern and CodeBlock creation logic.

Dependencies: token_hasher module functions, CodeBlock, DRYConfig, pathlib.Path

Exports: BaseTokenAnalyzer class

Interfaces: BaseTokenAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]

Implementation: Template method pattern with extension point for language-specific block filtering

Suppressions:
    - stateless-class: BaseTokenAnalyzer is an intentional template method base class.
        Subclasses (PythonDuplicateAnalyzer, TypeScriptDuplicateAnalyzer) override
        _should_include_block for language-specific filtering. Statelessness is by design
        since state was moved to module-level functions in token_hasher.
"""

from pathlib import Path

from . import token_hasher
from .cache import CodeBlock
from .config import DRYConfig


class BaseTokenAnalyzer:  # thailint: ignore[stateless-class] - Template method base class for inheritance
    """Base analyzer for token-based duplicate detection.

    This is intentionally a base class for polymorphism. Subclasses
    (PythonDuplicateAnalyzer, TypeScriptDuplicateAnalyzer) override
    _should_include_block for language-specific filtering.
    """

    def analyze(self, file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]:
        """Analyze file for duplicate code blocks.

        Args:
            file_path: Path to source file
            content: File content
            config: DRY configuration

        Returns:
            List of CodeBlock instances with hash values
        """
        lines = token_hasher.tokenize(content)
        windows = token_hasher.rolling_hash(lines, config.min_duplicate_lines)

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
