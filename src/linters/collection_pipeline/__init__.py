"""
Purpose: Collection pipeline linter package initialization

Scope: Exports for collection-pipeline linter module

Overview: Initializes the collection-pipeline linter package and exposes the main rule class
    for external use. Exports CollectionPipelineRule as the primary interface for the linter,
    allowing the orchestrator to discover and instantiate the rule. Also exports configuration
    and detector classes for advanced use cases. Provides a convenience lint() function for
    direct usage without orchestrator setup. This module serves as the entry point for
    the collection-pipeline linter functionality within the thai-lint framework.

Dependencies: CollectionPipelineRule, CollectionPipelineConfig, PipelinePatternDetector

Exports: CollectionPipelineRule (primary), CollectionPipelineConfig, PipelinePatternDetector, lint

Interfaces: Standard Python package initialization with __all__ for explicit exports

Implementation: Simple re-export pattern for package interface, convenience lint function
"""

from pathlib import Path
from typing import Any

from .config import DEFAULT_MIN_CONTINUES, CollectionPipelineConfig
from .detector import PatternMatch, PipelinePatternDetector
from .linter import CollectionPipelineRule

__all__ = [
    "CollectionPipelineRule",
    "CollectionPipelineConfig",
    "PipelinePatternDetector",
    "PatternMatch",
    "lint",
]


def lint(
    path: Path | str,
    config: dict[str, Any] | None = None,
    min_continues: int = DEFAULT_MIN_CONTINUES,
) -> list:
    """Lint a file or directory for collection pipeline violations.

    Args:
        path: Path to file or directory to lint
        config: Configuration dict (optional, uses defaults if not provided)
        min_continues: Minimum if/continue patterns to flag (default: 1)

    Returns:
        List of violations found

    Example:
        >>> from src.linters.collection_pipeline import lint
        >>> violations = lint('src/my_module.py', min_continues=2)
        >>> for v in violations:
        ...     print(f"{v.file_path}:{v.line} - {v.message}")
    """
    path_obj = Path(path) if isinstance(path, str) else path
    project_root = path_obj if path_obj.is_dir() else path_obj.parent

    orchestrator = _setup_pipeline_orchestrator(project_root, config, min_continues)
    violations = _execute_pipeline_lint(orchestrator, path_obj)

    return [v for v in violations if "collection-pipeline" in v.rule_id]


def _setup_pipeline_orchestrator(
    project_root: Path, config: dict[str, Any] | None, min_continues: int
) -> Any:
    """Set up orchestrator with collection-pipeline config."""
    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)

    if config:
        orchestrator.config["collection-pipeline"] = config
    else:
        orchestrator.config["collection-pipeline"] = {"min_continues": min_continues}

    return orchestrator


def _execute_pipeline_lint(orchestrator: Any, path_obj: Path) -> list:
    """Execute linting on file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    if path_obj.is_dir():
        return orchestrator.lint_directory(path_obj)
    return []
