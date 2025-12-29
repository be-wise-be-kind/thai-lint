"""
Purpose: CLI commands for documentation linters (file-header)

Scope: Commands that validate documentation standards in source files

Overview: Provides CLI commands for documentation linting: file-header validates that source files
    have proper documentation headers with required fields (Purpose, Scope, Overview, etc.) and
    detects temporal language patterns (dates, temporal qualifiers, state change references).
    Supports Python, TypeScript, JavaScript, Bash, Markdown, and CSS files. Integrates with the
    orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities

Exports: file_header command

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
# File Header Command
# =============================================================================


def _setup_file_header_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for file-header command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_file_header_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute file-header lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "file-header" in v.rule_id]


@cli.command("file-header")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def file_header(
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> None:
    """Check file headers for mandatory fields and atemporal language.

    Validates that source files have proper documentation headers containing
    required fields (Purpose, Scope, Overview, etc.) and don't use temporal
    language (dates, "currently", "now", etc.).

    Supports Python, TypeScript, JavaScript, Bash, Markdown, and CSS files.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint file-header

        \b
        # Check specific directory
        thai-lint file-header src/

        \b
        # Check single file
        thai-lint file-header src/cli.py

        \b
        # Check multiple files
        thai-lint file-header src/cli.py src/api.py tests/

        \b
        # Get JSON output
        thai-lint file-header --format json .

        \b
        # Get SARIF output for CI/CD integration
        thai-lint file-header --format sarif src/

        \b
        # Use custom config file
        thai-lint file-header --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_file_header_lint(path_objs, config_file, format, recursive, verbose, project_root)
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_file_header_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute file-header lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_file_header_orchestrator(path_objs, config_file, verbose, project_root)
    file_header_violations = _run_file_header_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(file_header_violations)} file header violation(s)")

    format_violations(file_header_violations, format)
    sys.exit(1 if file_header_violations else 0)
