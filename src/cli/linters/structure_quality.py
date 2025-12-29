"""
Purpose: CLI commands for structure quality linters (nesting, srp)

Scope: Commands that analyze code structure for quality issues

Overview: Provides CLI commands for structure quality linting: nesting checks for excessive nesting
    depth in control flow statements, and srp detects Single Responsibility Principle violations in
    classes. Each command supports standard options (config, format, recursive) plus linter-specific
    options (max-depth, max-methods, max-loc) and integrates with the orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities,
    src.cli.linters.shared for linter-specific helpers

Exports: nesting command, srp command

Interfaces: Click CLI commands registered to main CLI group

Implementation: Click decorators for command definition, orchestrator-based linting execution

SRP Exception: CLI command modules follow Click framework patterns requiring similar command
    structure across all linter commands. This is intentional design for consistency.

Suppressions:
    - too-many-arguments,too-many-positional-arguments: Click commands require many parameters by framework design
"""
# dry: ignore-block - CLI commands follow Click framework pattern with intentional repetition

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

import click

from src.cli.linters.shared import ensure_config_section, set_config_value
from src.cli.main import cli
from src.cli.utils import (
    execute_linting_on_paths,
    format_option,
    get_project_root_from_context,
    handle_linting_error,
    parallel_option,
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
# Nesting Command
# =============================================================================


def _setup_nesting_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for nesting command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _apply_nesting_config_override(
    orchestrator: "Orchestrator", max_depth: int | None, verbose: bool
) -> None:
    """Apply max_depth override to orchestrator config."""
    if max_depth is None:
        return

    nesting_config = ensure_config_section(orchestrator, "nesting")
    nesting_config["max_nesting_depth"] = max_depth
    _apply_nesting_to_languages(nesting_config, max_depth)

    if verbose:
        logger.debug(f"Overriding max_nesting_depth to {max_depth}")


def _apply_nesting_to_languages(nesting_config: dict, max_depth: int) -> None:
    """Apply max_depth to language-specific configs."""
    for lang in ["python", "typescript", "javascript"]:
        if lang in nesting_config:
            nesting_config[lang]["max_nesting_depth"] = max_depth


def _run_nesting_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool, parallel: bool = False
) -> list[Violation]:
    """Execute nesting lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive, parallel)
    return [v for v in all_violations if "nesting" in v.rule_id]


@cli.command("nesting")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--max-depth", type=int, help="Override max nesting depth (default: 4)")
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@parallel_option
@click.pass_context
def nesting(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    max_depth: int | None,
    recursive: bool,
    parallel: bool,
) -> None:
    """Check for excessive nesting depth in code.

    Analyzes Python and TypeScript files for deeply nested code structures
    (if/for/while/try statements) and reports violations.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint nesting

        \b
        # Check specific directory
        thai-lint nesting src/

        \b
        # Check single file
        thai-lint nesting src/app.py

        \b
        # Check multiple files
        thai-lint nesting src/app.py src/utils.py tests/test_app.py

        \b
        # Check mix of files and directories
        thai-lint nesting src/app.py tests/

        \b
        # Use custom max depth
        thai-lint nesting --max-depth 3 src/

        \b
        # Get JSON output
        thai-lint nesting --format json .

        \b
        # Use custom config file
        thai-lint nesting --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_nesting_lint(
            path_objs, config_file, format, max_depth, recursive, parallel, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_nesting_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    max_depth: int | None,
    recursive: bool,
    parallel: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute nesting lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_nesting_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_nesting_config_override(orchestrator, max_depth, verbose)
    nesting_violations = _run_nesting_lint(orchestrator, path_objs, recursive, parallel)

    if verbose:
        logger.info(f"Found {len(nesting_violations)} nesting violation(s)")

    format_violations(nesting_violations, format)
    sys.exit(1 if nesting_violations else 0)


# =============================================================================
# SRP Command
# =============================================================================


def _setup_srp_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for SRP command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _apply_srp_config_override(
    orchestrator: "Orchestrator", max_methods: int | None, max_loc: int | None, verbose: bool
) -> None:
    """Apply max_methods and max_loc overrides to orchestrator config."""
    if max_methods is None and max_loc is None:
        return

    srp_config = ensure_config_section(orchestrator, "srp")
    set_config_value(srp_config, "max_methods", max_methods, verbose)
    set_config_value(srp_config, "max_loc", max_loc, verbose)


def _run_srp_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute SRP lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "srp" in v.rule_id]


@cli.command("srp")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--max-methods", type=int, help="Override max methods per class (default: 7)")
@click.option("--max-loc", type=int, help="Override max lines of code per class (default: 200)")
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def srp(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    max_methods: int | None,
    max_loc: int | None,
    recursive: bool,
) -> None:
    """Check for Single Responsibility Principle violations.

    Analyzes Python and TypeScript classes for SRP violations using heuristics:
    - Method count exceeding threshold (default: 7)
    - Lines of code exceeding threshold (default: 200)
    - Responsibility keywords in class names (Manager, Handler, Processor, etc.)

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint srp

        \b
        # Check specific directory
        thai-lint srp src/

        \b
        # Check single file
        thai-lint srp src/app.py

        \b
        # Check multiple files
        thai-lint srp src/app.py src/service.py tests/test_app.py

        \b
        # Use custom thresholds
        thai-lint srp --max-methods 10 --max-loc 300 src/

        \b
        # Get JSON output
        thai-lint srp --format json .

        \b
        # Use custom config file
        thai-lint srp --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_srp_lint(
            path_objs, config_file, format, max_methods, max_loc, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_srp_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    max_methods: int | None,
    max_loc: int | None,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute SRP lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_srp_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_srp_config_override(orchestrator, max_methods, max_loc, verbose)
    srp_violations = _run_srp_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(srp_violations)} SRP violation(s)")

    format_violations(srp_violations, format)
    sys.exit(1 if srp_violations else 0)
