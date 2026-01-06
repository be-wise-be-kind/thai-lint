"""
Purpose: Performance linter package initialization

Scope: Exports for performance linter module

Overview: Initializes the performance linter package and exposes the main rule classes for
    external use. Exports StringConcatLoopRule as the primary interface for the performance
    linter, allowing the orchestrator to discover and instantiate the rule. Also exports
    configuration and analyzer classes for advanced use cases. Provides a convenience lint()
    function for direct usage without orchestrator setup. This module serves as the entry
    point for the performance linter functionality within the thai-lint framework.

Dependencies: StringConcatLoopRule, PerformanceConfig, analyzers

Exports: StringConcatLoopRule (primary), PerformanceConfig, analyzers, lint

Interfaces: Standard Python package initialization with __all__ for explicit exports

Implementation: Simple re-export pattern for package interface, convenience function
"""

from pathlib import Path
from typing import Any

from .config import PerformanceConfig
from .linter import StringConcatLoopRule
from .python_analyzer import PythonStringConcatAnalyzer
from .regex_analyzer import PythonRegexInLoopAnalyzer
from .regex_linter import RegexInLoopRule
from .typescript_analyzer import TypeScriptStringConcatAnalyzer

__all__ = [
    "StringConcatLoopRule",
    "RegexInLoopRule",
    "PerformanceConfig",
    "PythonStringConcatAnalyzer",
    "PythonRegexInLoopAnalyzer",
    "TypeScriptStringConcatAnalyzer",
    "lint",
]


def lint(
    path: Path | str,
    config: dict[str, Any] | None = None,
) -> list:
    """Lint a file or directory for performance issues.

    Args:
        path: Path to file or directory to lint
        config: Configuration dict (optional, uses defaults if not provided)

    Returns:
        List of violations found

    Example:
        >>> from src.linters.performance import lint
        >>> violations = lint('src/my_module.py')
        >>> for v in violations:
        ...     print(f"{v.file_path}:{v.line} - {v.message}")
    """
    path_obj = Path(path) if isinstance(path, str) else path
    project_root = path_obj if path_obj.is_dir() else path_obj.parent

    orchestrator = _setup_performance_orchestrator(project_root, config)
    violations = _execute_performance_lint(orchestrator, path_obj)

    return [v for v in violations if "performance" in v.rule_id]


def _setup_performance_orchestrator(project_root: Path, config: dict[str, Any] | None) -> Any:
    """Set up orchestrator with performance config."""
    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)

    if config:
        orchestrator.config["performance"] = config
    else:
        orchestrator.config["performance"] = {"enabled": True}

    return orchestrator


def _execute_performance_lint(orchestrator: Any, path_obj: Path) -> list:
    """Execute linting on file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    if path_obj.is_dir():
        return orchestrator.lint_directory(path_obj)
    return []
