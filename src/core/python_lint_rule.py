"""
Purpose: Base class for Python-only linters with common boilerplate

Scope: Shared infrastructure for Python-only lint rules

Overview: Provides PythonOnlyLintRule abstract base class that handles common boilerplate
    for Python-only linters. Subclasses implement the abstract properties and analysis
    method while the base class handles language checking, config loading, and enabled
    checking. This eliminates duplicate code across Python-only linters like CQS and LBYL.

Dependencies: BaseLintRule, BaseLintContext, Language, load_linter_config, has_file_content

Exports: PythonOnlyLintRule

Interfaces: Subclasses implement _config_key, _config_class, _analyze, and rule metadata

Implementation: Template method pattern for Python linter boilerplate
"""

from abc import abstractmethod
from typing import Any, Generic

from .base import BaseLintContext, BaseLintRule
from .constants import Language
from .linter_utils import ConfigType, has_file_content, load_linter_config
from .types import Violation


class PythonOnlyLintRule(BaseLintRule, Generic[ConfigType]):
    """Base class for Python-only linters with common boilerplate.

    Handles language checking, config loading, and enabled checking.
    Subclasses provide the config key, config class, and analysis logic.
    """

    def __init__(self, config: ConfigType | None = None) -> None:
        """Initialize with optional config override.

        Args:
            config: Optional configuration override for testing
        """
        self._config_override = config

    @property
    @abstractmethod
    def _config_key(self) -> str:
        """Configuration key in metadata (e.g., 'cqs', 'lbyl')."""
        raise NotImplementedError

    @property
    @abstractmethod
    def _config_class(self) -> type[ConfigType]:
        """Configuration class type."""
        raise NotImplementedError

    @abstractmethod
    def _analyze(self, code: str, file_path: str, config: ConfigType) -> list[Violation]:
        """Perform linter-specific analysis.

        Args:
            code: Python source code
            file_path: Path to the file
            config: Loaded configuration

        Returns:
            List of violations found
        """
        raise NotImplementedError

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for violations in the given context.

        Args:
            context: The lint context containing file information.

        Returns:
            List of violations found.
        """
        if not self._should_analyze(context):
            return []

        config = self._get_config(context)
        if not self._is_enabled(config):
            return []

        file_path = str(context.file_path) if context.file_path else "unknown"
        return self._analyze(context.file_content or "", file_path, config)

    def _should_analyze(self, context: BaseLintContext) -> bool:
        """Check if context should be analyzed."""
        return context.language == Language.PYTHON and has_file_content(context)

    def _get_config(self, context: BaseLintContext) -> ConfigType:
        """Get configuration, using override if provided."""
        if self._config_override is not None:
            return self._config_override
        return load_linter_config(context, self._config_key, self._config_class)

    def _is_enabled(self, config: Any) -> bool:
        """Check if linter is enabled in config."""
        return getattr(config, "enabled", True)
