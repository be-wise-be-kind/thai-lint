"""
File: src/linters/file_header/__init__.py
Purpose: File header linter module initialization
Exports: FileHeaderRule, lint
Depends: linter.FileHeaderRule, orchestrator.core.Orchestrator
Implements: Module-level exports and a lint() convenience function for direct library usage
Related: linter.py for main rule implementation

Overview:
    Initializes the file header linter module providing multi-language file header
    validation with mandatory field checking, atemporal language detection, and configuration
    support. Main entry point for file header linting functionality. Exposes a package-level
    lint() convenience function, mirroring the other linters (nesting, srp, file_placement), so
    callers can lint a file or directory without wiring up an orchestrator themselves.

Usage:
    from src.linters.file_header import FileHeaderRule
    rule = FileHeaderRule()
    violations = rule.check(context)

    from src.linters.file_header import lint
    violations = lint("src/", config={"required_fields": ["Purpose", "Scope", "Overview"]})

Notes: Follows standard Python module initialization pattern with __all__ export control
"""

from pathlib import Path
from typing import Any

from src.core.types import Violation

from .linter import FileHeaderRule

__all__ = ["FileHeaderRule", "lint"]


def lint(path: Path | str, config: dict[str, Any] | None = None) -> list[Violation]:
    """Lint a file or directory for file header violations.

    Args:
        path: Path to file or directory to lint.
        config: Optional file-header configuration dict (e.g. required_fields,
            enforce_atemporal, ignore). Uses defaults when omitted.

    Returns:
        List of file-header violations found.

    Example:
        >>> from src.linters.file_header import lint
        >>> violations = lint("src/", config={"required_fields": ["Purpose"]})
        >>> for v in violations:
        ...     print(f"{v.file_path}:{v.line} - {v.message}")
    """
    path_obj = Path(path) if isinstance(path, str) else path
    project_root = path_obj if path_obj.is_dir() else path_obj.parent

    orchestrator = _setup_file_header_orchestrator(project_root, config)
    violations = _execute_file_header_lint(orchestrator, path_obj)

    return [v for v in violations if "file-header" in v.rule_id]


def _setup_file_header_orchestrator(project_root: Path, config: dict[str, Any] | None) -> Any:
    """Set up an orchestrator with optional file-header config."""
    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)
    if config is not None:
        orchestrator.config["file_header"] = config
    return orchestrator


def _execute_file_header_lint(orchestrator: Any, path_obj: Path) -> list[Violation]:
    """Execute linting on a file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    if path_obj.is_dir():
        return orchestrator.lint_directory(path_obj)
    return []
