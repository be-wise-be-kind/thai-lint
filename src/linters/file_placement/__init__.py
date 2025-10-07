"""
Purpose: File placement linter module
Scope: File organization and placement validation
"""

from pathlib import Path
from typing import Any

from .linter import FilePlacementLinter, FilePlacementRule

__all__ = ["FilePlacementLinter", "FilePlacementRule", "lint"]


def lint(path: Path | str, config: dict[str, Any] | None = None) -> list:
    """Lint a file or directory using file placement rules.

    Args:
        path: Path to file or directory to lint
        config: Configuration dict (compatible with FilePlacementLinter)

    Returns:
        List of violations
    """
    path_obj = Path(path) if isinstance(path, str) else path
    linter = FilePlacementLinter(config_obj=config or {})

    if path_obj.is_file():
        return linter.lint_path(path_obj)
    if path_obj.is_dir():
        return linter.lint_directory(path_obj)
    return []
