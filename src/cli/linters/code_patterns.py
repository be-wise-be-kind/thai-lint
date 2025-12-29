"""
Purpose: CLI commands for code pattern linters (print-statements, method-property, stateless-class, lazy-ignores)

Scope: Commands that detect code patterns and anti-patterns in Python code

Overview: Provides CLI commands for code pattern linting: print-statements detects print() and
    console.log calls that should use proper logging, method-property finds methods that should be
    @property decorators, stateless-class detects classes without state that should be module
    functions, and lazy-ignores detects unjustified linting suppressions. Each command supports
    standard options (config, format, recursive) and integrates with the orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities

Exports: print_statements command, method_property command, stateless_class command, lazy_ignores command

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
# Print Statements Command
# =============================================================================


def _setup_print_statements_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for print-statements command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_print_statements_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute print-statements lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "print-statement" in v.rule_id]


@cli.command("print-statements")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def print_statements(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> None:
    """Check for print/console statements in code.

    Detects print() calls in Python and console.log/warn/error/debug/info calls
    in TypeScript/JavaScript that should be replaced with proper logging.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint print-statements

        \b
        # Check specific directory
        thai-lint print-statements src/

        \b
        # Check single file
        thai-lint print-statements src/app.py

        \b
        # Check multiple files
        thai-lint print-statements src/app.py src/utils.ts tests/test_app.py

        \b
        # Get JSON output
        thai-lint print-statements --format json .

        \b
        # Use custom config file
        thai-lint print-statements --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_print_statements_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_print_statements_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute print-statements lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_print_statements_orchestrator(
        path_objs, config_file, verbose, project_root
    )
    print_statements_violations = _run_print_statements_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(print_statements_violations)} print statement violation(s)")

    format_violations(print_statements_violations, format)
    sys.exit(1 if print_statements_violations else 0)


# =============================================================================
# Method Property Command
# =============================================================================


def _setup_method_property_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for method-property command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_method_property_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute method-property lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "method-property" in v.rule_id]


@cli.command("method-property")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def method_property(
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> None:
    """Check for methods that should be @property decorators.

    Detects Python methods that could be converted to properties following
    Pythonic conventions:
    - Methods returning only self._attribute or self.attribute
    - get_* prefixed methods (Java-style getters)
    - Simple computed values with no side effects

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint method-property

        \b
        # Check specific directory
        thai-lint method-property src/

        \b
        # Check single file
        thai-lint method-property src/models.py

        \b
        # Check multiple files
        thai-lint method-property src/models.py src/services.py

        \b
        # Get JSON output
        thai-lint method-property --format json .

        \b
        # Get SARIF output for CI/CD integration
        thai-lint method-property --format sarif src/

        \b
        # Use custom config file
        thai-lint method-property --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_method_property_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_method_property_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute method-property lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_method_property_orchestrator(
        path_objs, config_file, verbose, project_root
    )
    method_property_violations = _run_method_property_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(method_property_violations)} method-property violation(s)")

    format_violations(method_property_violations, format)
    sys.exit(1 if method_property_violations else 0)


# =============================================================================
# Stateless Class Command
# =============================================================================


def _setup_stateless_class_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for stateless-class command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_stateless_class_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute stateless-class lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "stateless-class" in v.rule_id]


@cli.command("stateless-class")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def stateless_class(
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> None:
    """Check for stateless classes that should be module functions.

    Detects Python classes that have no constructor (__init__), no instance
    state, and 2+ methods - indicating they should be refactored to module-level
    functions instead of using a class as a namespace.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint stateless-class

        \b
        # Check specific directory
        thai-lint stateless-class src/

        \b
        # Check single file
        thai-lint stateless-class src/utils.py

        \b
        # Check multiple files
        thai-lint stateless-class src/utils.py src/helpers.py

        \b
        # Get JSON output
        thai-lint stateless-class --format json .

        \b
        # Get SARIF output for CI/CD integration
        thai-lint stateless-class --format sarif src/

        \b
        # Use custom config file
        thai-lint stateless-class --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_stateless_class_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_stateless_class_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute stateless-class lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_stateless_class_orchestrator(
        path_objs, config_file, verbose, project_root
    )
    stateless_class_violations = _run_stateless_class_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(stateless_class_violations)} stateless-class violation(s)")

    format_violations(stateless_class_violations, format)
    sys.exit(1 if stateless_class_violations else 0)


# =============================================================================
# Lazy Ignores Command
# =============================================================================


def _setup_lazy_ignores_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for lazy-ignores command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_lazy_ignores_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute lazy-ignores lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if v.rule_id.startswith("lazy-ignores")]


@cli.command("lazy-ignores")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def lazy_ignores(
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
) -> None:
    """Check for unjustified linting suppressions.

    Detects ignore directives (noqa, type:ignore, pylint:disable, nosec) that lack
    corresponding entries in the file header's Suppressions section. Enforces a
    header-based suppression model requiring human approval for all linting bypasses.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint lazy-ignores

        \b
        # Check specific directory
        thai-lint lazy-ignores src/

        \b
        # Check single file
        thai-lint lazy-ignores src/routes.py

        \b
        # Check multiple files
        thai-lint lazy-ignores src/routes.py src/utils.py

        \b
        # Get JSON output
        thai-lint lazy-ignores --format json .

        \b
        # Get SARIF output for CI/CD integration
        thai-lint lazy-ignores --format sarif src/

        \b
        # Use custom config file
        thai-lint lazy-ignores --config .thailint.yaml src/
    """
    verbose: bool = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_lazy_ignores_lint(path_objs, config_file, format, recursive, verbose, project_root)
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_lazy_ignores_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs: list[Path],
    config_file: str | None,
    format: str,
    recursive: bool,
    verbose: bool,
    project_root: Path | None = None,
) -> NoReturn:
    """Execute lazy-ignores lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_lazy_ignores_orchestrator(path_objs, config_file, verbose, project_root)
    lazy_ignores_violations = _run_lazy_ignores_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(lazy_ignores_violations)} lazy-ignores violation(s)")

    format_violations(lazy_ignores_violations, format)
    sys.exit(1 if lazy_ignores_violations else 0)
