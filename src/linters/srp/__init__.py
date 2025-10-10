"""
Purpose: SRP linter package initialization

Scope: Exports for Single Responsibility Principle linter module

Overview: Initializes the SRP linter package and exposes the main rule class for external use.
    Exports SRPRule as the primary interface for the SRP linter, allowing the orchestrator to
    discover and instantiate the rule. Also exports configuration and analyzer classes for
    advanced use cases. Provides a convenience lint() function for direct usage without
    orchestrator setup. This module serves as the entry point for the SRP linter functionality
    within the thai-lint framework, enabling detection of classes with too many responsibilities.

Dependencies: SRPRule, SRPConfig, PythonSRPAnalyzer, TypeScriptSRPAnalyzer

Exports: SRPRule (primary), SRPConfig, PythonSRPAnalyzer, TypeScriptSRPAnalyzer, lint

Interfaces: Standard Python package initialization with __all__ for explicit exports, lint() convenience function

Implementation: Simple re-export pattern for package interface, convenience function wraps orchestrator
"""

from pathlib import Path
from typing import Any

from .config import DEFAULT_MAX_LOC_PER_CLASS, DEFAULT_MAX_METHODS_PER_CLASS, SRPConfig
from .linter import SRPRule
from .python_analyzer import PythonSRPAnalyzer
from .typescript_analyzer import TypeScriptSRPAnalyzer

__all__ = [
    "SRPRule",
    "SRPConfig",
    "PythonSRPAnalyzer",
    "TypeScriptSRPAnalyzer",
    "lint",
]


def lint(
    path: Path | str,
    config: dict[str, Any] | None = None,
    max_methods: int = DEFAULT_MAX_METHODS_PER_CLASS,
    max_loc: int = DEFAULT_MAX_LOC_PER_CLASS,
) -> list:
    """Lint a file or directory for SRP violations.

    Args:
        path: Path to file or directory to lint
        config: Configuration dict (optional, uses defaults if not provided)
        max_methods: Maximum allowed methods per class (default: 7)
        max_loc: Maximum allowed lines of code per class (default: 200)

    Returns:
        List of violations found

    Example:
        >>> from src.linters.srp import lint
        >>> violations = lint('src/my_module.py', max_methods=5)
        >>> for v in violations:
        ...     print(f"{v.file_path}:{v.line} - {v.message}")
    """
    path_obj = Path(path) if isinstance(path, str) else path
    project_root = path_obj if path_obj.is_dir() else path_obj.parent

    orchestrator = _setup_srp_orchestrator(project_root, config, max_methods, max_loc)
    violations = _execute_srp_lint(orchestrator, path_obj)

    return [v for v in violations if "srp" in v.rule_id]


def _setup_srp_orchestrator(
    project_root: Path,
    config: dict[str, Any] | None,
    max_methods: int,
    max_loc: int,
) -> Any:
    """Set up orchestrator with SRP config."""
    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)

    if config:
        orchestrator.config["srp"] = config
    else:
        orchestrator.config["srp"] = {
            "max_methods": max_methods,
            "max_loc": max_loc,
        }

    return orchestrator


def _execute_srp_lint(orchestrator: Any, path_obj: Path) -> list:
    """Execute linting on file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    if path_obj.is_dir():
        return orchestrator.lint_directory(path_obj)
    return []
