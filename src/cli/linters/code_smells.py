"""
Purpose: CLI commands for code smell linters (dry, magic-numbers, stringly-typed)

Scope: Commands that detect code smells like duplicate code, magic numbers, and stringly-typed patterns

Overview: Provides CLI commands for code smell detection: dry finds duplicate code blocks using
    token-based hashing with SQLite caching, magic-numbers detects unnamed numeric literals that
    should be extracted as named constants, and stringly-typed detects string patterns that should
    use enums. Each command supports standard options (config, format, recursive) plus linter-specific
    options and integrates with the orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities,
    src.cli.linters.shared for linter-specific helpers, yaml for config loading

Exports: dry command, magic_numbers command, stringly_typed command

Interfaces: Click CLI commands registered to main CLI group

Implementation: Click decorators for command definition, orchestrator-based linting execution

SRP Exception: CLI command modules follow Click framework patterns requiring similar command
    structure across all linter commands. This is intentional design for consistency.

Suppressions:
    too-many-arguments: Click commands require many parameters by framework design
    too-many-positional-arguments: Click positional params match CLI arg structure
"""
# dry: ignore-block - CLI commands follow Click framework pattern with intentional repetition

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn

import click
import yaml

from src.cli.linters.shared import ensure_config_section, set_config_value
from src.cli.main import cli
from src.cli.utils import (
    execute_linting_on_paths,
    format_option,
    get_project_root_from_context,
    handle_linting_error,
    setup_base_orchestrator,
    validate_paths_exist,
)
from src.core.cli_utils import format_violations
from src.core.types import Violation

if TYPE_CHECKING:
    from src.orchestrator.core import Orchestrator

# Configure module logger
logger = logging.getLogger(__name__)


# =============================================================================
# DRY Command
# =============================================================================


def _setup_dry_orchestrator(
    path_objs: list[Path],
    config_file: str | None,
    verbose: bool,
    project_root: Path | None = None,
) -> "Orchestrator":
    """Set up orchestrator for DRY linting."""
    return setup_base_orchestrator(path_objs, None, verbose, project_root)


def _load_dry_config_file(orchestrator: "Orchestrator", config_file: str, verbose: bool) -> None:
    """Load DRY configuration from file."""
    config_path = Path(config_file)
    if not config_path.exists():
        click.echo(f"Error: Config file not found: {config_file}", err=True)
        sys.exit(2)

    with config_path.open("r", encoding="utf-8") as f:
        config: dict[str, Any] = yaml.safe_load(f)

    if "dry" in config:
        orchestrator.config.update({"dry": config["dry"]})

        if verbose:
            logger.info(f"Loaded DRY config from {config_file}")


def _apply_dry_config_override(
    orchestrator: "Orchestrator", min_lines: int | None, no_cache: bool, verbose: bool
) -> None:
    """Apply CLI option overrides to DRY config."""
    dry_config = ensure_config_section(orchestrator, "dry")
    set_config_value(dry_config, "min_duplicate_lines", min_lines, verbose)
    if no_cache:
        set_config_value(dry_config, "cache_enabled", False, verbose)


def _clear_dry_cache(orchestrator: "Orchestrator", verbose: bool) -> None:
    """Clear DRY cache before running."""
    cache_path_str = orchestrator.config.get("dry", {}).get("cache_path", ".thailint-cache/dry.db")
    cache_path = orchestrator.project_root / cache_path_str

    if cache_path.exists():
        cache_path.unlink()
        if verbose:
            logger.info(f"Cleared cache: {cache_path}")
    elif verbose:
        logger.info("Cache file does not exist, nothing to clear")


def _run_dry_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Run DRY linting and return violations."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if v.rule_id.startswith("dry.")]


@cli.command("dry")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--min-lines", type=int, help="Override min duplicate lines threshold")
@click.option("--no-cache", is_flag=True, help="Disable SQLite cache (force rehash)")
@click.option("--clear-cache", is_flag=True, help="Clear cache before running")
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def dry(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    min_lines: int | None,
    no_cache: bool,
    clear_cache: bool,
    recursive: bool,
) -> None:
    # Justification for Pylint disables:
    # - too-many-arguments/positional: CLI requires 1 ctx + 1 arg + 6 options = 8 params
    """
    Check for duplicate code (DRY principle violations).

    Detects duplicate code blocks across your project using token-based hashing
    with SQLite caching for fast incremental scans.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint dry

        \b
        # Check specific directory
        thai-lint dry src/

        \b
        # Check single file
        thai-lint dry src/app.py

        \b
        # Check multiple files
        thai-lint dry src/app.py src/service.py tests/test_app.py

        \b
        # Use custom config file
        thai-lint dry --config .thailint.yaml src/

        \b
        # Override minimum duplicate lines threshold
        thai-lint dry --min-lines 5 .

        \b
        # Disable cache (force re-analysis)
        thai-lint dry --no-cache .

        \b
        # Clear cache before running
        thai-lint dry --clear-cache .

        \b
        # Get JSON output
        thai-lint dry --format json .
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_dry_lint(
            path_objs,
            config_file,
            format,
            min_lines,
            no_cache,
            clear_cache,
            recursive,
            verbose,
            project_root,
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_dry_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    min_lines: int | None,
    no_cache: bool,
    clear_cache: bool,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute DRY linting."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_dry_orchestrator(path_objs, config_file, verbose, project_root)

    if config_file:
        _load_dry_config_file(orchestrator, config_file, verbose)

    _apply_dry_config_override(orchestrator, min_lines, no_cache, verbose)

    if clear_cache:
        _clear_dry_cache(orchestrator, verbose)

    dry_violations = _run_dry_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(dry_violations)} DRY violation(s)")

    format_violations(dry_violations, format)
    sys.exit(1 if dry_violations else 0)


# =============================================================================
# Magic Numbers Command
# =============================================================================


def _setup_magic_numbers_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for magic-numbers command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_magic_numbers_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute magic-numbers lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "magic-number" in v.rule_id]


@cli.command("magic-numbers")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def magic_numbers(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> None:
    """Check for magic numbers in code.

    Detects unnamed numeric literals in Python and TypeScript/JavaScript code
    that should be extracted as named constants for better readability.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint magic-numbers

        \b
        # Check specific directory
        thai-lint magic-numbers src/

        \b
        # Check single file
        thai-lint magic-numbers src/app.py

        \b
        # Check multiple files
        thai-lint magic-numbers src/app.py src/utils.py tests/test_app.py

        \b
        # Check mix of files and directories
        thai-lint magic-numbers src/app.py tests/

        \b
        # Get JSON output
        thai-lint magic-numbers --format json .

        \b
        # Use custom config file
        thai-lint magic-numbers --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_magic_numbers_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_magic_numbers_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute magic-numbers lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_magic_numbers_orchestrator(path_objs, config_file, verbose, project_root)
    magic_numbers_violations = _run_magic_numbers_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(magic_numbers_violations)} magic number violation(s)")

    format_violations(magic_numbers_violations, format)
    sys.exit(1 if magic_numbers_violations else 0)


# =============================================================================
# Stringly-Typed Command
# =============================================================================


def _setup_stringly_typed_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for stringly-typed command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_stringly_typed_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute stringly-typed lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "stringly-typed" in v.rule_id]


@cli.command("stringly-typed")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def stringly_typed(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> None:
    """Check for stringly-typed patterns in code.

    Detects string patterns in Python and TypeScript/JavaScript code that should
    use enums or typed alternatives. Finds membership validation, equality chains,
    and function calls with limited string values across multiple files.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint stringly-typed

        \b
        # Check specific directory
        thai-lint stringly-typed src/

        \b
        # Check single file
        thai-lint stringly-typed src/handlers.py

        \b
        # Check multiple files
        thai-lint stringly-typed src/handlers.py src/services.py

        \b
        # Get JSON output
        thai-lint stringly-typed --format json .

        \b
        # Get SARIF output for IDE integration
        thai-lint stringly-typed --format sarif .

        \b
        # Use custom config file
        thai-lint stringly-typed --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_stringly_typed_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_stringly_typed_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute stringly-typed lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_stringly_typed_orchestrator(path_objs, config_file, verbose, project_root)
    stringly_violations = _run_stringly_typed_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(stringly_violations)} stringly-typed violation(s)")

    format_violations(stringly_violations, format)
    sys.exit(1 if stringly_violations else 0)
