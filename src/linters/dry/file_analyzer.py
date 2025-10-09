"""
Purpose: File analysis orchestration for duplicate detection

Scope: Coordinates language-specific analyzers and cache checking

Overview: Orchestrates file analysis by delegating to language-specific analyzers (Python, TypeScript)
    and checking cache freshness. Handles cache hits by loading from cache, and cache misses by
    analyzing files. Separates file analysis orchestration from main linter rule logic to maintain
    SRP compliance.

Dependencies: PythonDuplicateAnalyzer, TypeScriptDuplicateAnalyzer, DRYCache, DRYConfig, CodeBlock

Exports: FileAnalyzer class

Interfaces: FileAnalyzer.analyze_or_load(file_path, content, language, config, cache)

Implementation: Delegates to language-specific analyzers, checks cache freshness
"""

from dataclasses import dataclass
from pathlib import Path

from .cache import CodeBlock, DRYCache
from .config import DRYConfig
from .python_analyzer import PythonDuplicateAnalyzer
from .typescript_analyzer import TypeScriptDuplicateAnalyzer


@dataclass
class FileAnalysisContext:
    """Context for file analysis."""

    file_path: Path
    content: str
    language: str
    config: DRYConfig
    cache: DRYCache | None


class FileAnalyzer:
    """Orchestrates file analysis with cache support."""

    def __init__(self) -> None:
        """Initialize with language-specific analyzers."""
        self._python_analyzer = PythonDuplicateAnalyzer()
        self._typescript_analyzer = TypeScriptDuplicateAnalyzer()

    def analyze_or_load(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        file_path: Path,
        content: str,
        language: str,
        config: DRYConfig,
        cache: DRYCache | None = None,
    ) -> list[CodeBlock]:
        """Analyze file or load from cache.

        Args:
            file_path: Path to file
            content: File content
            language: File language
            config: DRY configuration
            cache: Optional cache instance

        Returns:
            List of CodeBlock instances
        """
        # Check if file is fresh in cache
        if cache:
            mtime = file_path.stat().st_mtime
            if cache.is_fresh(file_path, mtime):
                return cache.load(file_path)

        # Analyze file based on language
        return self._analyze_file(file_path, content, language, config)

    def _analyze_file(
        self, file_path: Path, content: str, language: str, config: DRYConfig
    ) -> list[CodeBlock]:
        """Analyze file based on language.

        Args:
            file_path: Path to file
            content: File content
            language: File language
            config: DRY configuration

        Returns:
            List of CodeBlock instances
        """
        if language == "python":
            return self._python_analyzer.analyze(file_path, content, config)
        if language in ("typescript", "javascript"):
            return self._typescript_analyzer.analyze(file_path, content, config)
        return []
