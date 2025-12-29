"""
Purpose: CLI commands for project structure linters (file-placement, pipeline)

Scope: File placement validation and collection pipeline anti-pattern detection commands

Overview: Provides CLI commands for project structure linting: file-placement checks that files are
    in appropriate directories according to configured rules, and pipeline detects for loops with
    embedded if/continue filtering that could use collection pipelines. Both commands support
    standard options (config, format, recursive) and integrate with the orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities,
    src.cli.linters.shared for linter-specific helpers

Exports: file_placement command, pipeline command

Interfaces: Click CLI commands registered to main CLI group

Implementation: Click decorators for command definition, orchestrator-based linting execution

SRP Exception: CLI command modules follow Click framework patterns requiring similar command
    structure across all linter commands. This is intentional design for consistency.

Suppressions:
    - too-many-arguments,too-many-positional-arguments: Click commands require many parameters by framework design
"""
# dry: ignore-block - CLI commands follow Click framework pattern with intentional repetition

import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn

import click

from src.cli.linters.shared import ensure_config_section, set_config_value
from src.cli.main import cli
from src.cli.utils import (
    execute_linting_on_paths,
    format_option,
    get_or_detect_project_root,
    get_project_root_from_context,
    handle_linting_error,
    load_config_file,
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
# File Placement Command
# =============================================================================


def _setup_orchestrator(
    path_objs: list[Path],
    config_file: str | None,
    rules: str | None,
    verbose: bool,
    project_root: Path | None = None,
) -> "Orchestrator":
    """Set up and configure the orchestrator for file-placement."""
    from src.orchestrator.core import Orchestrator

    project_root = get_or_detect_project_root(path_objs, project_root)
    orchestrator = Orchestrator(project_root=project_root)
    _apply_orchestrator_config(orchestrator, config_file, rules, verbose)
    return orchestrator


def _apply_orchestrator_config(
    orchestrator: "Orchestrator", config_file: str | None, rules: str | None, verbose: bool
) -> None:
    """Apply configuration to orchestrator."""
    if rules:
        _apply_inline_rules(orchestrator, rules, verbose)
    elif config_file:
        load_config_file(orchestrator, config_file, verbose)


def _apply_inline_rules(orchestrator: "Orchestrator", rules: str, verbose: bool) -> None:
    """Parse and apply inline JSON rules."""
    rules_config = _parse_json_rules(rules)
    orchestrator.config.update(rules_config)
    if verbose:
        logger.debug(f"Applied inline rules: {rules_config}")


def _parse_json_rules(rules: str) -> dict[str, Any]:
    """Parse JSON rules string, exit on error."""
    try:
        result: dict[str, Any] = json.loads(rules)
        return result
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in --rules: {e}", err=True)
        sys.exit(2)


@cli.command("file-placement")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@click.option("--rules", "-r", help="Inline JSON rules configuration")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def file_placement(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    rules: str | None,
    format: str,
    recursive: bool,
) -> None:
    # Justification for Pylint disables:
    # - too-many-arguments/positional: CLI requires 1 ctx + 1 arg + 4 options = 6 params
    """
    Lint files for proper file placement.

    Checks that files are placed in appropriate directories according to
    configured rules and patterns.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Lint current directory (all files recursively)
        thai-lint file-placement

        \b
        # Lint specific directory
        thai-lint file-placement src/

        \b
        # Lint single file
        thai-lint file-placement src/app.py

        \b
        # Lint multiple files
        thai-lint file-placement src/app.py src/utils.py tests/test_app.py

        \b
        # Use custom config
        thai-lint file-placement --config rules.json .

        \b
        # Inline JSON rules
        thai-lint file-placement --rules '{"allow": [".*\\.py$"]}' .
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_file_placement_lint(
            path_objs, config_file, rules, format, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_file_placement_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    rules: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute file placement linting."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_orchestrator(path_objs, config_file, rules, verbose, project_root)
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)

    # Filter to only file-placement violations
    violations = [v for v in all_violations if v.rule_id.startswith("file-placement")]

    if verbose:
        logger.info(f"Found {len(violations)} violation(s)")

    format_violations(violations, format)
    sys.exit(1 if violations else 0)


# =============================================================================
# Collection Pipeline Command
# =============================================================================


def _setup_pipeline_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for pipeline command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _apply_pipeline_config_override(
    orchestrator: "Orchestrator", min_continues: int | None, verbose: bool
) -> None:
    """Apply min_continues override to orchestrator config."""
    if min_continues is None:
        return

    pipeline_config = ensure_config_section(orchestrator, "collection_pipeline")
    set_config_value(pipeline_config, "min_continues", min_continues, verbose)


def _run_pipeline_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute collection-pipeline lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "collection-pipeline" in v.rule_id]


@cli.command("pipeline")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--min-continues", type=int, help="Override min continue guards to flag (default: 1)")
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def pipeline(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    min_continues: int | None,
    recursive: bool,
) -> None:
    """Check for collection pipeline anti-patterns in code.

    Detects for loops with embedded if/continue filtering patterns that could
    be refactored to use collection pipelines (generator expressions, filter()).

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all Python files recursively)
        thai-lint pipeline

        \b
        # Check specific directory
        thai-lint pipeline src/

        \b
        # Check single file
        thai-lint pipeline src/app.py

        \b
        # Only flag loops with 2+ continue guards
        thai-lint pipeline --min-continues 2 src/

        \b
        # Get JSON output
        thai-lint pipeline --format json .

        \b
        # Get SARIF output for CI/CD integration
        thai-lint pipeline --format sarif src/

        \b
        # Use custom config file
        thai-lint pipeline --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_pipeline_lint(
            path_objs, config_file, format, min_continues, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_pipeline_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    min_continues: int | None,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute collection-pipeline lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_pipeline_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_pipeline_config_override(orchestrator, min_continues, verbose)
    pipeline_violations = _run_pipeline_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(pipeline_violations)} collection-pipeline violation(s)")

    format_violations(pipeline_violations, format)
    sys.exit(1 if pipeline_violations else 0)
