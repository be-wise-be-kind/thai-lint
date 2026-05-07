"""
Purpose: Law of Demeter linter package initialization

Scope: Exports for Law of Demeter linter module

Overview: Initializes the Law of Demeter linter package and exposes the main rule class for
    external use. Exports LawOfDemeterRule as the primary interface, along with configuration
    and analyzer classes. Provides a convenience lint() function for direct usage without
    orchestrator setup.

Dependencies: LawOfDemeterRule, LawOfDemeterConfig, python_analyzer

Exports: LawOfDemeterRule (primary), LawOfDemeterConfig, extract_chains, extract_imports, lint

Interfaces: Standard Python package initialization with __all__

Implementation: Re-export pattern for package interface, convenience function wraps orchestrator
"""

from pathlib import Path
from typing import Any

from .config import DEFAULT_MIN_CHAIN_DEPTH, LawOfDemeterConfig
from .linter import LawOfDemeterRule
from .python_analyzer import extract_chains, extract_imports

__all__ = [
    "LawOfDemeterRule",
    "LawOfDemeterConfig",
    "extract_chains",
    "extract_imports",
    "lint",
]


def lint(
    path: Path | str,
    config: dict[str, Any] | None = None,
    min_depth: int = DEFAULT_MIN_CHAIN_DEPTH,
) -> list:
    """Lint a file or directory for Law of Demeter violations.

    Args:
        path: Path to file or directory to lint
        config: Configuration dict (optional, uses defaults if not provided)
        min_depth: Minimum chain depth to report (default: 3)

    Returns:
        List of violations found
    """
    path_obj = Path(path) if isinstance(path, str) else path
    project_root = path_obj if path_obj.is_dir() else path_obj.parent

    orchestrator = _setup_orchestrator(project_root, config, min_depth)
    violations = _execute_lint(orchestrator, path_obj)

    return [v for v in violations if "law-of-demeter" in v.rule_id]


def _setup_orchestrator(project_root: Path, config: dict[str, Any] | None, min_depth: int) -> Any:
    """Set up orchestrator with LoD config."""
    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)

    if config:
        orchestrator.config["law-of-demeter"] = config
    else:
        orchestrator.config["law-of-demeter"] = {"min_chain_depth": min_depth}

    return orchestrator


def _execute_lint(orchestrator: Any, path_obj: Path) -> list:
    """Execute linting on file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    if path_obj.is_dir():
        return orchestrator.lint_directory(path_obj)
    return []
