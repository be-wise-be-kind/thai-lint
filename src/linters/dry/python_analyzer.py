"""
Purpose: Python source code tokenization and duplicate block analysis

Scope: Python-specific code analysis for duplicate detection

Overview: Analyzes Python source files to extract code blocks for duplicate detection. Uses
    token-based hashing approach to normalize code and generate rolling hash windows. Integrates
    TokenHasher for normalization and CodeBlock creation. Returns list of code blocks with hash
    values that can be stored in cache and queried for duplicates across the project.

Dependencies: TokenHasher, CodeBlock, DRYConfig, pathlib.Path

Exports: PythonDuplicateAnalyzer class

Interfaces: PythonDuplicateAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig)
    -> list[CodeBlock]

Implementation: Token-based analysis using TokenHasher, rolling hash windows, CodeBlock creation
"""

from pathlib import Path

from .cache import CodeBlock
from .config import DRYConfig
from .token_hasher import TokenHasher


class PythonDuplicateAnalyzer:
    """Analyzes Python code for duplicate blocks."""

    def __init__(self) -> None:
        """Initialize analyzer with token hasher."""
        self._hasher = TokenHasher()

    def analyze(self, file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]:
        """Analyze Python file for code blocks.

        Args:
            file_path: Path to Python file
            content: File content
            config: DRY configuration

        Returns:
            List of CodeBlock instances with hash values
        """
        # Tokenize code
        lines = self._hasher.tokenize(content)

        # Generate rolling hash windows
        windows = self._hasher.rolling_hash(lines, config.min_duplicate_lines)

        # Create CodeBlock instances
        blocks = []
        for hash_val, start_line, end_line, snippet in windows:
            block = CodeBlock(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                snippet=snippet,
                hash_value=hash_val,
            )
            blocks.append(block)

        return blocks
