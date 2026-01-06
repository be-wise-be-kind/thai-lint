"""
Purpose: Shared utilities for linter CLI commands

Scope: Common helper functions and patterns used across all linter command modules

Overview: Provides reusable utilities for linter CLI commands including config section management,
    config value setting with logging, rule ID filtering, CLI context extraction, and help text
    generation. Centralizes shared patterns to reduce duplication across linter command modules
    (code_quality, code_patterns, structure, documentation, performance). All utilities are designed
    to work with the orchestrator configuration system and Click CLI framework.

Dependencies: logging for debug output, pathlib for Path type hints, click for Context type,
    dataclasses for CommandContext

Exports: ensure_config_section, set_config_value, filter_violations_by_prefix, CommandContext,
    extract_command_context, make_linter_help, ExecuteParams, prepare_standard_command,
    run_linter_command, standard_linter_options, filter_violations_by_startswith,
    create_linter_command

Interfaces: Orchestrator config dict manipulation, violation list filtering, CLI context extraction,
    help text generation

Implementation: Pure helper functions with no side effects beyond config mutation and logging
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import click

from src.cli.utils import format_option, get_project_root_from_context, handle_linting_error
from src.core.types import Violation

if TYPE_CHECKING:
    from collections.abc import Callable

    from src.orchestrator.core import Orchestrator


def standard_linter_options(f: Any) -> Any:
    """Apply standard linter CLI options to a command.

    Bundles the common options used by most linter commands:
    - paths argument (variadic)
    - config file option
    - format option
    - recursive option
    - pass_context

    Usage:
        @cli.command("my-linter")
        @standard_linter_options
        def my_linter(ctx, paths, config_file, format, recursive):
            ...
    """
    f = click.pass_context(f)
    f = click.option(
        "--recursive/--no-recursive", default=True, help="Scan directories recursively"
    )(f)
    f = format_option(f)
    f = click.option(
        "--config", "-c", "config_file", type=click.Path(), help="Path to config file"
    )(f)
    f = click.argument("paths", nargs=-1, type=click.Path())(f)
    return f


@dataclass
class CommandContext:
    """Extracted context from CLI command invocation.

    Consolidates common CLI command setup into a reusable structure.
    """

    verbose: bool
    project_root: Path | None
    path_objs: list[Path]


@dataclass
class ExecuteParams:
    """Parameters for linter execution functions.

    Bundles the common parameters passed to _execute_*_lint functions
    to reduce function signature duplication across CLI modules.
    """

    path_objs: list[Path]
    config_file: str | None
    format: str
    recursive: bool
    verbose: bool
    project_root: Path | None


def extract_command_context(ctx: click.Context, paths: tuple[str, ...]) -> CommandContext:
    """Extract common context values from CLI command invocation.

    Consolidates the repeated pattern of extracting verbose, project_root,
    and converting paths to Path objects with default handling.

    Args:
        ctx: Click context from command invocation
        paths: Tuple of path strings from command arguments

    Returns:
        CommandContext with extracted values
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    return CommandContext(verbose=verbose, project_root=project_root, path_objs=path_objs)


def prepare_standard_command(
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> ExecuteParams:
    """Prepare standard linter command execution parameters.

    Combines context extraction and ExecuteParams creation into a single call.
    Use with commands that have the standard options (config, format, recursive).

    Args:
        ctx: Click context from command invocation
        paths: Tuple of path strings from command arguments
        config_file: Optional config file path
        format: Output format
        recursive: Whether to scan recursively

    Returns:
        ExecuteParams ready for _execute_*_lint function
    """
    cmd_ctx = extract_command_context(ctx, paths)
    return ExecuteParams(
        path_objs=cmd_ctx.path_objs,
        config_file=config_file,
        format=format,
        recursive=recursive,
        verbose=cmd_ctx.verbose,
        project_root=cmd_ctx.project_root,
    )


def run_linter_command(
    execute_fn: "Callable[[ExecuteParams], None]",
    params: ExecuteParams,
) -> None:
    """Run a linter command with standard error handling.

    Wraps the try/except pattern used by all linter commands.

    Args:
        execute_fn: The _execute_*_lint function to call
        params: ExecuteParams for the execution
    """
    try:
        execute_fn(params)
    except Exception as e:
        handle_linting_error(e, params.verbose)


# Configure module logger
logger = logging.getLogger(__name__)


def ensure_config_section(orchestrator: "Orchestrator", section: str) -> dict[str, Any]:
    """Ensure a config section exists and return it.

    Args:
        orchestrator: Orchestrator instance with config dict
        section: Name of the config section to ensure exists

    Returns:
        The config section dict (created if it didn't exist)
    """
    if section not in orchestrator.config:
        orchestrator.config[section] = {}
    config_section: dict[str, Any] = orchestrator.config[section]
    return config_section


def set_config_value(config: dict[str, Any], key: str, value: Any, verbose: bool) -> None:
    """Set a config value with optional debug logging.

    Only sets the value if it is not None.

    Args:
        config: Config dict to update
        key: Config key to set
        value: Value to set (skipped if None)
        verbose: Whether to log the override
    """
    if value is None:
        return
    config[key] = value
    if verbose:
        logger.debug(f"Overriding {key} to {value}")


def filter_violations_by_prefix(violations: list[Violation], prefix: str) -> list[Violation]:
    """Filter violations to those matching a rule ID prefix.

    Args:
        violations: List of violation objects with rule_id attribute
        prefix: Prefix to match against rule_id

    Returns:
        Filtered list of violations where rule_id contains the prefix
    """
    return [v for v in violations if prefix in v.rule_id]


def filter_violations_by_startswith(violations: list[Violation], prefix: str) -> list[Violation]:
    """Filter violations to those with rule_id starting with prefix.

    Args:
        violations: List of violation objects with rule_id attribute
        prefix: Prefix that rule_id must start with

    Returns:
        Filtered list of violations where rule_id starts with the prefix
    """
    return [v for v in violations if v.rule_id.startswith(prefix)]


def create_linter_command(
    name: str,
    execute_fn: "Callable[[ExecuteParams], None]",
    brief: str,
    description: str,
) -> "Callable[..., None]":
    """Create a standard linter CLI command.

    Factory function that generates Click commands with consistent structure,
    eliminating boilerplate duplication across linter command modules.

    Args:
        name: CLI command name (e.g., "magic-numbers")
        execute_fn: The _execute_*_lint function to call
        brief: Brief one-line description
        description: Detailed multi-line description

    Returns:
        Decorated Click command function
    """
    from src.cli.main import cli

    @cli.command(name, help=make_linter_help(name, brief, description))
    @standard_linter_options
    def command(
        ctx: click.Context,
        paths: tuple[str, ...],
        config_file: str | None,
        format: str,
        recursive: bool,
    ) -> None:
        params = prepare_standard_command(ctx, paths, config_file, format, recursive)
        run_linter_command(execute_fn, params)

    return command


def make_linter_help(command: str, brief: str, description: str) -> str:
    """Generate standardized CLI help text for linter commands.

    Creates consistent help text following the established pattern with
    examples showing common usage patterns.

    Args:
        command: CLI command name (e.g., "magic-numbers")
        brief: Brief one-line description
        description: Detailed multi-line description

    Returns:
        Formatted help text string for Click command
    """
    return f"""{brief}

    {description}

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \\b
        # Check current directory (all files recursively)
        thai-lint {command}

        \\b
        # Check specific directory
        thai-lint {command} src/

        \\b
        # Check single file
        thai-lint {command} src/app.py

        \\b
        # Get JSON output
        thai-lint {command} --format json .

        \\b
        # Use custom config file
        thai-lint {command} --config .thailint.yaml src/
    """
