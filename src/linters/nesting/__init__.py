"""
Purpose: Nesting depth linter package initialization

Scope: Exports for nesting depth linter module

Overview: Initializes the nesting depth linter package and exposes the main rule class for
    external use. Exports NestingDepthRule as the primary interface for the nesting linter,
    allowing the orchestrator to discover and instantiate the rule. Also exports configuration
    and analyzer classes for advanced use cases. Provides a convenience lint() function for
    direct usage without orchestrator setup. This module serves as the entry point for
    the nesting linter functionality within the thai-lint framework.

Dependencies: NestingDepthRule, NestingConfig, PythonNestingAnalyzer, TypeScriptNestingAnalyzer

Exports: NestingDepthRule (primary), NestingConfig, PythonNestingAnalyzer, TypeScriptNestingAnalyzer, lint

Interfaces: Standard Python package initialization with __all__ for explicit exports, lint() convenience function

Implementation: Simple re-export pattern for package interface, convenience function wraps orchestrator
"""

from pathlib import Path
from typing import Any

from .config import DEFAULT_MAX_NESTING_DEPTH, NestingConfig
from .linter import NestingDepthRule
from .python_analyzer import PythonNestingAnalyzer
from .typescript_analyzer import TypeScriptNestingAnalyzer

__all__ = [
    "NestingDepthRule",
    "NestingConfig",
    "PythonNestingAnalyzer",
    "TypeScriptNestingAnalyzer",
    "lint",
]


def lint(
    path: Path | str,
    config: dict[str, Any] | None = None,
    max_depth: int = DEFAULT_MAX_NESTING_DEPTH,
) -> list:
    """Lint a file or directory for nesting depth violations.

    Args:
        path: Path to file or directory to lint
        config: Configuration dict (optional, uses defaults if not provided)
        max_depth: Maximum allowed nesting depth (default: 4)

    Returns:
        List of violations found

    Example:
        >>> from src.linters.nesting import lint
        >>> violations = lint('src/my_module.py', max_depth=3)
        >>> for v in violations:
        ...     print(f"{v.file_path}:{v.line} - {v.message}")
    """
    path_obj = Path(path) if isinstance(path, str) else path
    project_root = path_obj if path_obj.is_dir() else path_obj.parent

    orchestrator = _setup_nesting_orchestrator(project_root, config, max_depth)
    violations = _execute_nesting_lint(orchestrator, path_obj)

    return [v for v in violations if "nesting" in v.rule_id]


def _setup_nesting_orchestrator(
    project_root: Path, config: dict[str, Any] | None, max_depth: int
) -> Any:
    """Set up orchestrator with nesting config."""
    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)

    if config:
        orchestrator.config["nesting"] = config
    else:
        orchestrator.config["nesting"] = {"max_nesting_depth": max_depth}

    return orchestrator


def _execute_nesting_lint(orchestrator: Any, path_obj: Path) -> list:
    """Execute linting on file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    if path_obj.is_dir():
        return orchestrator.lint_directory(path_obj)
    return []
