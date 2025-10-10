"""
Purpose: File analysis orchestration for duplicate detection

Scope: Coordinates language-specific analyzers

Overview: Orchestrates file analysis by delegating to language-specific analyzers (Python, TypeScript).
    Analyzes files fresh every run - no cache loading. Separates file analysis orchestration from
    main linter rule logic to maintain SRP compliance.

Dependencies: PythonDuplicateAnalyzer, TypeScriptDuplicateAnalyzer, DRYConfig, CodeBlock

Exports: FileAnalyzer class

Interfaces: FileAnalyzer.analyze(file_path, content, language, config)

Implementation: Delegates to language-specific analyzers, always performs fresh analysis
"""

from pathlib import Path

from .block_filter import BlockFilterRegistry, create_default_registry
from .cache import CodeBlock
from .config import DRYConfig
from .python_analyzer import PythonDuplicateAnalyzer
from .typescript_analyzer import TypeScriptDuplicateAnalyzer


class FileAnalyzer:
    """Orchestrates file analysis for duplicate detection."""

    def __init__(self, config: DRYConfig | None = None) -> None:
        """Initialize with language-specific analyzers.

        Args:
            config: DRY configuration (used to configure filters)
        """
        # Create filter registry based on config
        filter_registry = self._create_filter_registry(config)

        # Initialize analyzers with filter registry
        self._python_analyzer = PythonDuplicateAnalyzer(filter_registry)
        self._typescript_analyzer = TypeScriptDuplicateAnalyzer()

    def _create_filter_registry(self, config: DRYConfig | None) -> BlockFilterRegistry:
        """Create filter registry based on configuration.

        Args:
            config: DRY configuration

        Returns:
            Configured BlockFilterRegistry
        """
        registry = create_default_registry()

        if not config:
            return registry

        # Configure filters based on config.filters dict
        for filter_name, enabled in config.filters.items():
            if enabled:
                registry.enable_filter(filter_name)
            else:
                registry.disable_filter(filter_name)

        return registry

    def analyze(
        self,
        file_path: Path,
        content: str,
        language: str,
        config: DRYConfig,
    ) -> list[CodeBlock]:
        """Analyze file for duplicate code blocks.

        Args:
            file_path: Path to file
            content: File content
            language: File language
            config: DRY configuration

        Returns:
            List of CodeBlock instances
        """
        # Analyze file based on language
        if language == "python":
            return self._python_analyzer.analyze(file_path, content, config)
        if language in ("typescript", "javascript"):
            return self._typescript_analyzer.analyze(file_path, content, config)
        return []
