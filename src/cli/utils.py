"""
Purpose: Shared CLI utilities and helper functions for thai-lint commands

Scope: Project root resolution, path validation, common decorators, and orchestrator setup

Overview: Provides reusable utilities for CLI commands including project root determination with
    precedence rules (explicit > config-inferred > auto-detected), path existence validation,
    common Click option decorators (format, project-root), and orchestrator setup helpers.
    Centralizes shared logic to reduce duplication across linter command modules while
    maintaining consistent behavior for all CLI operations.

Dependencies: click for CLI framework, pathlib for file paths, logging for debug output,
    src.orchestrator for linting execution, src.utils.project_root for auto-detection

Exports: format_option decorator, get_project_root_from_context, validate_paths_exist,
    setup_base_orchestrator, execute_linting_on_paths, handle_linting_error

Interfaces: Click context integration via ctx.obj, Path objects for file operations

Implementation: Uses Click decorators for option definitions, deferred imports for orchestrator
    to support test environments, caches project root in context for efficiency
"""

import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

import click

if TYPE_CHECKING:
    from src.orchestrator.core import Orchestrator

# Configure module logger
logger = logging.getLogger(__name__)


# =============================================================================
# Common Option Decorators
# =============================================================================


F = TypeVar("F", bound=Callable[..., object])


def format_option(func: F) -> F:
    """Add --format option to a command for output format selection."""
    return click.option(
        "--format",
        "-f",
        type=click.Choice(["text", "json", "sarif"]),
        default="text",
        help="Output format",
    )(func)


def parallel_option(func: F) -> F:
    """Add --parallel option to enable multi-core file processing."""
    return click.option(
        "--parallel",
        "-p",
        is_flag=True,
        default=False,
        help="Enable parallel file processing (uses multiple CPU cores)",
    )(func)


# =============================================================================
# Project Root Determination
# =============================================================================


def _determine_project_root(
    explicit_root: str | None, config_path: str | None, verbose: bool
) -> Path:
    """Determine project root with precedence rules.

    Precedence order:
    1. Explicit --project-root (highest priority)
    2. Inferred from --config path directory
    3. Auto-detection via get_project_root() (fallback)

    Args:
        explicit_root: Explicitly specified project root path (from --project-root)
        config_path: Config file path (from --config)
        verbose: Whether verbose logging is enabled

    Returns:
        Path to determined project root

    Raises:
        SystemExit: If explicit_root doesn't exist or is not a directory
    """
    from src.utils.project_root import get_project_root

    # Priority 1: Explicit --project-root
    if explicit_root:
        return _resolve_explicit_project_root(explicit_root, verbose)

    # Priority 2: Infer from --config path
    if config_path:
        return _infer_root_from_config(config_path, verbose)

    # Priority 3: Auto-detection (fallback)
    return _autodetect_project_root(verbose, get_project_root)


def _resolve_explicit_project_root(explicit_root: str, verbose: bool) -> Path:
    """Resolve and validate explicitly specified project root.

    Args:
        explicit_root: Explicitly specified project root path
        verbose: Whether verbose logging is enabled

    Returns:
        Resolved project root path

    Raises:
        SystemExit: If explicit_root doesn't exist or is not a directory
    """
    root = Path(explicit_root)
    # Check existence before resolving to handle relative paths in test environments
    if not root.exists():
        click.echo(f"Error: Project root does not exist: {explicit_root}", err=True)
        sys.exit(2)
    if not root.is_dir():
        click.echo(f"Error: Project root must be a directory: {explicit_root}", err=True)
        sys.exit(2)

    # Now resolve after validation
    root = root.resolve()

    if verbose:
        logger.debug(f"Using explicit project root: {root}")
    return root


def _infer_root_from_config(config_path: str, verbose: bool) -> Path:
    """Infer project root from config file path.

    Args:
        config_path: Config file path
        verbose: Whether verbose logging is enabled

    Returns:
        Inferred project root (parent directory of config file)
    """
    config_file = Path(config_path).resolve()
    inferred_root = config_file.parent

    if verbose:
        logger.debug(f"Inferred project root from config path: {inferred_root}")
    return inferred_root


def _autodetect_project_root(
    verbose: bool, get_project_root: Callable[[Path | None], Path]
) -> Path:
    """Auto-detect project root using project root detection.

    Args:
        verbose: Whether verbose logging is enabled
        get_project_root: Function to detect project root

    Returns:
        Auto-detected project root
    """
    auto_root = get_project_root(None)
    if verbose:
        logger.debug(f"Auto-detected project root: {auto_root}")
    return auto_root


def get_project_root_from_context(ctx: click.Context) -> Path | None:
    """Get or determine project root from Click context.

    This function defers the actual determination until needed to avoid
    importing pyprojroot in test environments where it may not be available.

    Returns None when no explicit root is specified (via --project-root or --config),
    allowing the orchestrator to auto-detect from target paths instead of CWD.

    Args:
        ctx: Click context containing CLI options

    Returns:
        Path to determined project root, or None for auto-detection from target paths
    """
    # Check if already determined and cached
    if "project_root" in ctx.obj:
        cached: Path | None = ctx.obj["project_root"]
        return cached

    project_root = _determine_project_root_for_context(ctx)
    ctx.obj["project_root"] = project_root
    return project_root


def _determine_project_root_for_context(ctx: click.Context) -> Path | None:
    """Determine project root from context options.

    Args:
        ctx: Click context containing CLI options

    Returns:
        Path if explicit root or config specified, None for auto-detection
    """
    explicit_root = ctx.obj.get("cli_project_root")
    config_path = ctx.obj.get("cli_config_path")
    verbose = ctx.obj.get("verbose", False)

    if explicit_root:
        return _resolve_explicit_project_root(explicit_root, verbose)

    if config_path:
        return _infer_root_from_config(config_path, verbose)

    # No explicit root - return None for auto-detection from target paths
    if verbose:
        logger.debug("No explicit project root, will auto-detect from target paths")
    return None


# =============================================================================
# Path Validation
# =============================================================================


def validate_paths_exist(path_objs: list[Path]) -> None:
    """Validate that all provided paths exist.

    Args:
        path_objs: List of Path objects to validate

    Raises:
        SystemExit: If any path doesn't exist (exit code 2)
    """
    for path in path_objs:
        if not path.exists():
            click.echo(f"Error: Path does not exist: {path}", err=True)
            click.echo("", err=True)
            click.echo(
                "Hint: When using Docker, ensure paths are inside the mounted volume:", err=True
            )
            click.echo(
                "  docker run -v $(pwd):/data thailint <command> /data/your-file.py", err=True
            )
            sys.exit(2)


# =============================================================================
# Error Handling
# =============================================================================


def handle_linting_error(error: Exception, verbose: bool) -> None:
    """Handle linting errors.

    Args:
        error: The exception that occurred
        verbose: Whether verbose logging is enabled
    """
    click.echo(f"Error during linting: {error}", err=True)
    if verbose:
        logger.exception("Linting failed with exception")
    sys.exit(2)


# =============================================================================
# Orchestrator Setup
# =============================================================================


def get_or_detect_project_root(path_objs: list[Path], project_root: Path | None) -> Path:
    """Get provided project root or auto-detect from paths.

    Args:
        path_objs: List of path objects
        project_root: Optionally provided project root

    Returns:
        Project root path
    """
    if project_root is not None:
        return project_root

    from src.utils.project_root import get_project_root

    # Find actual project root (where .git or pyproject.toml exists)
    first_path = path_objs[0] if path_objs else Path.cwd()
    search_start = first_path if first_path.is_dir() else first_path.parent
    return get_project_root(search_start)


def setup_base_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for linter commands.

    Args:
        path_objs: List of path objects to lint
        config_file: Optional config file path
        verbose: Whether verbose logging is enabled
        project_root: Optional explicit project root

    Returns:
        Configured Orchestrator instance
    """
    from src.orchestrator.core import Orchestrator

    root = get_or_detect_project_root(path_objs, project_root)
    orchestrator = Orchestrator(project_root=root)

    if config_file:
        load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def load_config_file(orchestrator: "Orchestrator", config_file: str, verbose: bool) -> None:
    """Load configuration from external file.

    Args:
        orchestrator: Orchestrator instance
        config_file: Path to config file
        verbose: Whether verbose logging is enabled
    """
    config_path = Path(config_file)
    if not config_path.exists():
        click.echo(f"Error: Config file not found: {config_file}", err=True)
        sys.exit(2)

    # Load config into orchestrator
    orchestrator.config = orchestrator.config_loader.load(config_path)

    if verbose:
        logger.debug(f"Loaded config from: {config_file}")


# =============================================================================
# Linting Execution
# =============================================================================


def separate_files_and_dirs(path_objs: list[Path]) -> tuple[list[Path], list[Path]]:
    """Separate file paths from directory paths.

    Args:
        path_objs: List of Path objects

    Returns:
        Tuple of (files, directories)
    """
    files = [p for p in path_objs if p.is_file()]
    dirs = [p for p in path_objs if p.is_dir()]
    return files, dirs


def execute_linting_on_paths(
    orchestrator: "Orchestrator",
    path_objs: list[Path],
    recursive: bool,
    parallel: bool = False,
) -> list[Any]:
    """Execute linting on list of file/directory paths.

    Args:
        orchestrator: Orchestrator instance
        path_objs: List of Path objects (files or directories)
        recursive: Whether to scan directories recursively
        parallel: Whether to use parallel processing for multiple files

    Returns:
        List of violations from all paths
    """
    files, dirs = separate_files_and_dirs(path_objs)

    violations = []

    # Lint files
    if files:
        if parallel:
            violations.extend(orchestrator.lint_files_parallel(files))
        else:
            violations.extend(orchestrator.lint_files(files))

    # Lint directories
    for dir_path in dirs:
        if parallel:
            violations.extend(orchestrator.lint_directory_parallel(dir_path, recursive=recursive))
        else:
            violations.extend(orchestrator.lint_directory(dir_path, recursive=recursive))

    return violations
