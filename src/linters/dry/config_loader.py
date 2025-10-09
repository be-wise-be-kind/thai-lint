"""
Purpose: Configuration loading from lint context metadata

Scope: Extracts and validates DRY configuration from context

Overview: Handles extraction of DRY configuration from BaseLintContext metadata dictionary.
    Validates configuration structure and converts to DRYConfig instance. Separates config
    loading logic from main linter rule to maintain SRP compliance.

Dependencies: BaseLintContext, DRYConfig

Exports: ConfigLoader class

Interfaces: ConfigLoader.load_config(context) -> DRYConfig

Implementation: Extracts from context metadata, validates dict structure, uses DRYConfig.from_dict()
"""

from src.core.base import BaseLintContext

from .config import DRYConfig


class ConfigLoader:
    """Loads DRY configuration from lint context."""

    def load_config(self, context: BaseLintContext) -> DRYConfig:
        """Load configuration from context metadata.

        Args:
            context: Lint context containing metadata

        Returns:
            DRYConfig instance
        """
        metadata = getattr(context, "metadata", None)
        if not isinstance(metadata, dict):
            return DRYConfig()

        config_dict = metadata.get("dry", {})
        if not isinstance(config_dict, dict):
            return DRYConfig()

        return DRYConfig.from_dict(config_dict)
