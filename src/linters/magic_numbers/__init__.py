"""
Purpose: Magic numbers linter package exports and convenience functions

Scope: Public API for magic numbers linter module

Overview: Provides the public interface for the magic numbers linter package. Exports main
    MagicNumberRule class for use by the orchestrator and MagicNumberConfig for configuration.
    Includes lint() convenience function that provides a simple API for running the magic numbers
    linter on a file or directory without directly interacting with the orchestrator. This module
    serves as the entry point for users of the magic numbers linter, hiding implementation details
    and exposing only the essential components needed for linting operations.

Dependencies: .linter for MagicNumberRule, .config for MagicNumberConfig

Exports: MagicNumberRule class, MagicNumberConfig dataclass, lint() convenience function

Interfaces: lint(path, config) -> list[Violation] for simple linting operations

Implementation: Module-level exports with __all__ definition, convenience function wrapper
"""

from .config import MagicNumberConfig
from .linter import MagicNumberRule

__all__ = ["MagicNumberRule", "MagicNumberConfig", "lint"]


def lint(file_path: str, config: dict | None = None) -> list:
    """Convenience function for linting a file for magic numbers.

    Args:
        file_path: Path to the file to lint
        config: Optional configuration dictionary

    Returns:
        List of violations found
    """
    from pathlib import Path

    from src.orchestrator.core import FileLintContext

    rule = MagicNumberRule()
    context = FileLintContext(
        path=Path(file_path),
        lang="python",
    )

    return rule.check(context)
