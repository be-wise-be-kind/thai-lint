"""
Purpose: Main CLI entrypoint with linter commands for thai-lint command-line interface

Scope: CLI command definitions for linter commands registered to the main CLI group

Overview: Provides linter commands for the installed CLI tool (file-placement, nesting, srp, dry,
    magic-numbers, print-statements, file-header, method-property, stateless-class, pipeline).
    Imports the main CLI group and utilities from src/cli/ package. Configuration commands
    (hello, config group, init-config) are registered via the src/cli/config module import.
    Linter commands are candidates for extraction to src/cli/linters/ in future modularization.

Dependencies: click for CLI framework, src.cli for main group and utilities, pathlib for file paths

Exports: cli (main command group with all commands registered)

Interfaces: Click CLI commands, integration with Orchestrator for linting execution

Implementation: Click decorators for commands, imports from modular src.cli package
"""
# pylint: disable=too-many-lines
# Justification: Linter commands remain here pending PR3 modularization

import logging
import sys
from pathlib import Path

import click

# Import from modular CLI package
from src.cli.main import cli  # noqa: F401
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

# Import config module to register commands (hello, config group, init-config)
from src.cli import config as _config_module  # noqa: F401  # isort: skip

# Configure module logger
logger = logging.getLogger(__name__)


# =============================================================================
# File Placement Linter Command
# =============================================================================


def _setup_orchestrator(path_objs, config_file, rules, verbose, project_root=None):
    """Set up and configure the orchestrator."""
    from src.orchestrator.core import Orchestrator

    # Use provided project_root or fall back to auto-detection
    project_root = get_or_detect_project_root(path_objs, project_root)

    orchestrator = Orchestrator(project_root=project_root)
    _apply_orchestrator_config(orchestrator, config_file, rules, verbose)

    return orchestrator


def _apply_orchestrator_config(orchestrator, config_file, rules, verbose):
    """Apply configuration to orchestrator."""
    if rules:
        _apply_inline_rules(orchestrator, rules, verbose)
    elif config_file:
        load_config_file(orchestrator, config_file, verbose)


def _apply_inline_rules(orchestrator, rules, verbose):
    """Parse and apply inline JSON rules."""
    rules_config = _parse_json_rules(rules)
    orchestrator.config.update(rules_config)
    if verbose:
        logger.debug(f"Applied inline rules: {rules_config}")


def _parse_json_rules(rules: str) -> dict:
    """Parse JSON rules string, exit on error."""
    import json

    try:
        return json.loads(rules)
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
def file_placement(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    rules: str | None,
    format: str,
    recursive: bool,
):
    # Justification for Pylint disables:
    # - too-many-arguments/positional: CLI requires 1 ctx + 1 arg + 4 options = 6 params
    # - too-many-locals/statements: Complex CLI logic for config, linting, and output formatting
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs, config_file, rules, format, recursive, verbose, project_root=None
):
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
# Nesting Linter Command
# =============================================================================


def _setup_nesting_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for nesting command."""
    orchestrator = setup_base_orchestrator(path_objs, config_file, verbose, project_root)
    return orchestrator


def _ensure_config_section(orchestrator, section: str) -> dict:
    """Ensure config section exists and return it."""
    if section not in orchestrator.config:
        orchestrator.config[section] = {}
    return orchestrator.config[section]


def _apply_nesting_config_override(orchestrator, max_depth: int | None, verbose: bool):
    """Apply max_depth override to orchestrator config."""
    if max_depth is None:
        return

    nesting_config = _ensure_config_section(orchestrator, "nesting")
    nesting_config["max_nesting_depth"] = max_depth
    _apply_nesting_to_languages(nesting_config, max_depth)

    if verbose:
        logger.debug(f"Overriding max_nesting_depth to {max_depth}")


def _apply_nesting_to_languages(nesting_config: dict, max_depth: int) -> None:
    """Apply max_depth to language-specific configs."""
    for lang in ["python", "typescript", "javascript"]:
        if lang in nesting_config:
            nesting_config[lang]["max_nesting_depth"] = max_depth


def _run_nesting_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute nesting lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "nesting" in v.rule_id]


@cli.command("nesting")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option("--max-depth", type=int, help="Override max nesting depth (default: 4)")
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def nesting(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    max_depth: int | None,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_nesting_lint(
            path_objs, config_file, format, max_depth, recursive, verbose, project_root
        )
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_nesting_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, max_depth, recursive, verbose, project_root=None
):
    """Execute nesting lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_nesting_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_nesting_config_override(orchestrator, max_depth, verbose)
    nesting_violations = _run_nesting_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(nesting_violations)} nesting violation(s)")

    format_violations(nesting_violations, format)
    sys.exit(1 if nesting_violations else 0)


# =============================================================================
# SRP Linter Command
# =============================================================================


def _setup_srp_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for SRP command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _set_config_value(config: dict, key: str, value, verbose: bool) -> None:
    """Set config value with optional debug logging."""
    if value is None:
        return
    config[key] = value
    if verbose:
        logger.debug(f"Overriding {key} to {value}")


def _apply_srp_config_override(
    orchestrator, max_methods: int | None, max_loc: int | None, verbose: bool
):
    """Apply max_methods and max_loc overrides to orchestrator config."""
    if max_methods is None and max_loc is None:
        return

    srp_config = _ensure_config_section(orchestrator, "srp")
    _set_config_value(srp_config, "max_methods", max_methods, verbose)
    _set_config_value(srp_config, "max_loc", max_loc, verbose)


def _run_srp_lint(orchestrator, path_objs: list[Path], recursive: bool):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    max_methods: int | None,
    max_loc: int | None,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs, config_file, format, max_methods, max_loc, recursive, verbose, project_root=None
):
    """Execute SRP lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_srp_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_srp_config_override(orchestrator, max_methods, max_loc, verbose)
    srp_violations = _run_srp_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(srp_violations)} SRP violation(s)")

    format_violations(srp_violations, format)
    sys.exit(1 if srp_violations else 0)


# =============================================================================
# DRY Linter Command
# =============================================================================


def _setup_dry_orchestrator(path_objs, config_file, verbose, project_root=None):
    """Set up orchestrator for DRY linting."""
    return setup_base_orchestrator(path_objs, None, verbose, project_root)


def _load_dry_config_file(orchestrator, config_file, verbose):
    """Load DRY configuration from file."""
    import yaml

    config_path = Path(config_file)
    if not config_path.exists():
        click.echo(f"Error: Config file not found: {config_file}", err=True)
        sys.exit(2)

    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "dry" in config:
        orchestrator.config.update({"dry": config["dry"]})

        if verbose:
            logger.info(f"Loaded DRY config from {config_file}")


def _apply_dry_config_override(orchestrator, min_lines, no_cache, verbose):
    """Apply CLI option overrides to DRY config."""
    dry_config = _ensure_config_section(orchestrator, "dry")
    _set_config_value(dry_config, "min_duplicate_lines", min_lines, verbose)
    if no_cache:
        _set_config_value(dry_config, "cache_enabled", False, verbose)


def _clear_dry_cache(orchestrator, verbose):
    """Clear DRY cache before running."""
    cache_path_str = orchestrator.config.get("dry", {}).get("cache_path", ".thailint-cache/dry.db")
    cache_path = orchestrator.project_root / cache_path_str

    if cache_path.exists():
        cache_path.unlink()
        if verbose:
            logger.info(f"Cleared cache: {cache_path}")
    elif verbose:
        logger.info("Cache file does not exist, nothing to clear")


def _run_dry_lint(orchestrator, path_objs, recursive):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    min_lines: int | None,
    no_cache: bool,
    clear_cache: bool,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs,
    config_file,
    format,
    min_lines,
    no_cache,
    clear_cache,
    recursive,
    verbose,
    project_root=None,
):
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
# Magic Numbers Linter Command
# =============================================================================


def _setup_magic_numbers_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for magic-numbers command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_magic_numbers_lint(orchestrator, path_objs: list[Path], recursive: bool):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs, config_file, format, recursive, verbose, project_root=None
):
    """Execute magic-numbers lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_magic_numbers_orchestrator(path_objs, config_file, verbose, project_root)
    magic_numbers_violations = _run_magic_numbers_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(magic_numbers_violations)} magic number violation(s)")

    format_violations(magic_numbers_violations, format)
    sys.exit(1 if magic_numbers_violations else 0)


# =============================================================================
# Print Statements Linter Command
# =============================================================================


def _setup_print_statements_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for print-statements command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_print_statements_lint(orchestrator, path_objs: list[Path], recursive: bool):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs, config_file, format, recursive, verbose, project_root=None
):
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
# File Header Linter Command
# =============================================================================


def _setup_file_header_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for file-header command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_file_header_lint(orchestrator, path_objs: list[Path], recursive: bool):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
    project_root = get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_file_header_lint(path_objs, config_file, format, recursive, verbose, project_root)
    except Exception as e:
        handle_linting_error(e, verbose)


def _execute_file_header_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, recursive, verbose, project_root=None
):
    """Execute file-header lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_file_header_orchestrator(path_objs, config_file, verbose, project_root)
    file_header_violations = _run_file_header_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(file_header_violations)} file header violation(s)")

    format_violations(file_header_violations, format)
    sys.exit(1 if file_header_violations else 0)


# =============================================================================
# Method Property Linter Command
# =============================================================================


def _setup_method_property_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for method-property command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_method_property_lint(orchestrator, path_objs: list[Path], recursive: bool):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs, config_file, format, recursive, verbose, project_root=None
):
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
# Stateless Class Linter Command
# =============================================================================


def _setup_stateless_class_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for stateless-class command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_stateless_class_lint(orchestrator, path_objs: list[Path], recursive: bool):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs, config_file, format, recursive, verbose, project_root=None
):
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
# Collection Pipeline Command
# =============================================================================


def _setup_pipeline_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for pipeline command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _apply_pipeline_config_override(orchestrator, min_continues: int | None, verbose: bool):
    """Apply min_continues override to orchestrator config."""
    if min_continues is None:
        return

    if "collection_pipeline" not in orchestrator.config:
        orchestrator.config["collection_pipeline"] = {}

    orchestrator.config["collection_pipeline"]["min_continues"] = min_continues
    if verbose:
        logger.debug(f"Overriding min_continues to {min_continues}")


def _run_pipeline_lint(orchestrator, path_objs: list[Path], recursive: bool):
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
    ctx,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    min_continues: int | None,
    recursive: bool,
):
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
    verbose = ctx.obj.get("verbose", False)
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
    path_objs, config_file, format, min_continues, recursive, verbose, project_root=None
):
    """Execute collection-pipeline lint."""
    validate_paths_exist(path_objs)
    orchestrator = _setup_pipeline_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_pipeline_config_override(orchestrator, min_continues, verbose)
    pipeline_violations = _run_pipeline_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(pipeline_violations)} collection-pipeline violation(s)")

    format_violations(pipeline_violations, format)
    sys.exit(1 if pipeline_violations else 0)


if __name__ == "__main__":
    cli()
