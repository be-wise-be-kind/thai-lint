"""
Purpose: Main CLI entrypoint with Click framework for command-line interface

Scope: CLI command definitions, option parsing, and command execution coordination

Overview: Provides the main CLI application using Click decorators for command definition, option
    parsing, and help text generation. Includes example commands (hello, config management) that
    demonstrate best practices for CLI design including error handling, logging configuration,
    context management, and user-friendly output. Serves as the entry point for the installed
    CLI tool and coordinates between user input and application logic.

Dependencies: click for CLI framework, logging for structured output, pathlib for file paths

Exports: cli (main command group), hello command, config command group, file_placement command, dry command

Interfaces: Click CLI commands, configuration context via Click ctx, logging integration

Implementation: Click decorators for commands, context passing for shared state, comprehensive help text
"""
# pylint: disable=too-many-lines
# Justification: CLI modules naturally have many commands and helper functions

import logging
import sys
from pathlib import Path

import click

from src import __version__
from src.config import ConfigError, load_config, save_config, validate_config
from src.core.cli_utils import format_violations

# Configure module logger
logger = logging.getLogger(__name__)


# Shared Click option decorators for common CLI options
def format_option(func):
    """Add --format option to a command for output format selection."""
    return click.option(
        "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Output format"
    )(func)


def setup_logging(verbose: bool = False):
    """
    Configure logging for the CLI application.

    Args:
        verbose: Enable DEBUG level logging if True, INFO otherwise.
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.pass_context
def cli(ctx, verbose: bool, config: str | None):
    """
    thai-lint - AI code linter and governance tool

    Lint and governance for AI-generated code across multiple languages.
    Identifies common mistakes, anti-patterns, and security issues.

    Examples:

        \b
        # Check for duplicate code (DRY violations)
        thai-lint dry .

        \b
        # Lint current directory for file placement issues
        thai-lint file-placement .

        \b
        # Lint with custom config
        thai-lint file-placement --config .thailint.yaml src/

        \b
        # Get JSON output
        thai-lint file-placement --format json .

        \b
        # Show help
        thai-lint --help
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Setup logging
    setup_logging(verbose)

    # Load configuration
    try:
        if config:
            ctx.obj["config"] = load_config(Path(config))
            ctx.obj["config_path"] = Path(config)
        else:
            ctx.obj["config"] = load_config()
            ctx.obj["config_path"] = None

        logger.debug("Configuration loaded successfully")
    except ConfigError as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(2)

    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--name", "-n", default="World", help="Name to greet")
@click.option("--uppercase", "-u", is_flag=True, help="Convert greeting to uppercase")
@click.pass_context
def hello(ctx, name: str, uppercase: bool):
    """
    Print a greeting message.

    This is a simple example command demonstrating CLI basics.

    Examples:

        \b
        # Basic greeting
        thai-lint hello

        \b
        # Custom name
        thai-lint hello --name Alice

        \b
        # Uppercase output
        thai-lint hello --name Bob --uppercase
    """
    config = ctx.obj["config"]
    verbose = ctx.obj.get("verbose", False)

    # Get greeting from config or use default
    greeting_template = config.get("greeting", "Hello")

    # Build greeting message
    message = f"{greeting_template}, {name}!"

    if uppercase:
        message = message.upper()

    # Output greeting
    click.echo(message)

    if verbose:
        logger.info(f"Greeted {name} with template '{greeting_template}'")


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command("show")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "yaml"]),
    default="text",
    help="Output format",
)
@click.pass_context
def config_show(ctx, format: str):
    """
    Display current configuration.

    Shows all configuration values in the specified format.

    Examples:

        \b
        # Show as text
        thai-lint config show

        \b
        # Show as JSON
        thai-lint config show --format json

        \b
        # Show as YAML
        thai-lint config show --format yaml
    """
    cfg = ctx.obj["config"]

    formatters = {
        "json": _format_config_json,
        "yaml": _format_config_yaml,
        "text": _format_config_text,
    }
    formatters[format](cfg)


def _format_config_json(cfg: dict) -> None:
    """Format configuration as JSON."""
    import json

    click.echo(json.dumps(cfg, indent=2))


def _format_config_yaml(cfg: dict) -> None:
    """Format configuration as YAML."""
    import yaml

    click.echo(yaml.dump(cfg, default_flow_style=False, sort_keys=False))


def _format_config_text(cfg: dict) -> None:
    """Format configuration as text."""
    click.echo("Current Configuration:")
    click.echo("-" * 40)
    for key, value in cfg.items():
        click.echo(f"{key:20} : {value}")


@config.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx, key: str):
    """
    Get specific configuration value.

    KEY: Configuration key to retrieve

    Examples:

        \b
        # Get log level
        thai-lint config get log_level

        \b
        # Get greeting template
        thai-lint config get greeting
    """
    cfg = ctx.obj["config"]

    if key not in cfg:
        click.echo(f"Configuration key not found: {key}", err=True)
        sys.exit(1)

    click.echo(cfg[key])


def _convert_value_type(value: str):
    """Convert string value to appropriate type."""
    if value.lower() in ["true", "false"]:
        return value.lower() == "true"
    if value.isdigit():
        return int(value)
    if value.replace(".", "", 1).isdigit() and value.count(".") == 1:
        return float(value)
    return value


def _validate_and_report_errors(cfg: dict):
    """Validate configuration and report errors."""
    is_valid, errors = validate_config(cfg)
    if not is_valid:
        click.echo("Invalid configuration:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        sys.exit(1)


def _save_and_report_success(cfg: dict, key: str, value, config_path, verbose: bool):
    """Save configuration and report success."""
    save_config(cfg, config_path)
    click.echo(f"✓ Set {key} = {value}")
    if verbose:
        logger.info(f"Configuration updated: {key}={value}")


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx, key: str, value: str):
    """
    Set configuration value.

    KEY: Configuration key to set

    VALUE: New value for the key

    Examples:

        \b
        # Set log level
        thai-lint config set log_level DEBUG

        \b
        # Set greeting template
        thai-lint config set greeting "Hi"

        \b
        # Set numeric value
        thai-lint config set max_retries 5
    """
    cfg = ctx.obj["config"]
    converted_value = _convert_value_type(value)
    cfg[key] = converted_value

    try:
        _validate_and_report_errors(cfg)
    except Exception as e:
        click.echo(f"Validation error: {e}", err=True)
        sys.exit(1)

    try:
        config_path = ctx.obj.get("config_path")
        verbose = ctx.obj.get("verbose", False)
        _save_and_report_success(cfg, key, converted_value, config_path, verbose)
    except ConfigError as e:
        click.echo(f"Error saving configuration: {e}", err=True)
        sys.exit(1)


@config.command("reset")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def config_reset(ctx, yes: bool):
    """
    Reset configuration to defaults.

    Examples:

        \b
        # Reset with confirmation
        thai-lint config reset

        \b
        # Reset without confirmation
        thai-lint config reset --yes
    """
    if not yes:
        click.confirm("Reset configuration to defaults?", abort=True)

    from src.config import DEFAULT_CONFIG

    try:
        config_path = ctx.obj.get("config_path")
        save_config(DEFAULT_CONFIG.copy(), config_path)
        click.echo("✓ Configuration reset to defaults")

        if ctx.obj.get("verbose"):
            logger.info("Configuration reset to defaults")
    except ConfigError as e:
        click.echo(f"Error resetting configuration: {e}", err=True)
        sys.exit(1)


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
    # All parameters and logic are necessary for flexible CLI usage.
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

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_file_placement_lint(path_objs, config_file, rules, format, recursive, verbose)
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_file_placement_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, rules, format, recursive, verbose
):
    """Execute file placement linting."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_orchestrator(path_objs, config_file, rules, verbose)
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)

    # Filter to only file-placement violations
    violations = [v for v in all_violations if v.rule_id.startswith("file-placement")]

    if verbose:
        logger.info(f"Found {len(violations)} violation(s)")

    format_violations(violations, format)
    sys.exit(1 if violations else 0)


def _handle_linting_error(error: Exception, verbose: bool) -> None:
    """Handle linting errors."""
    click.echo(f"Error during linting: {error}", err=True)
    if verbose:
        logger.exception("Linting failed with exception")
    sys.exit(2)


def _validate_paths_exist(path_objs: list[Path]) -> None:
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


def _find_project_root(start_path: Path) -> Path:
    """Find project root by looking for .git or pyproject.toml.

    DEPRECATED: Use src.utils.project_root.get_project_root() instead.

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to project root, or start_path if no markers found
    """
    from src.utils.project_root import get_project_root

    return get_project_root(start_path)


def _setup_orchestrator(path_objs, config_file, rules, verbose):
    """Set up and configure the orchestrator."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Find actual project root (where .git or pyproject.toml exists)
    # This ensures .artifacts/ is always created at project root, not in subdirectories
    first_path = path_objs[0] if path_objs else Path.cwd()
    search_start = first_path if first_path.is_dir() else first_path.parent
    project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if rules:
        _apply_inline_rules(orchestrator, rules, verbose)
    elif config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _apply_inline_rules(orchestrator, rules, verbose):
    """Parse and apply inline JSON rules."""
    rules_config = _parse_json_rules(rules)
    orchestrator.config.update(rules_config)
    _log_applied_rules(rules_config, verbose)


def _parse_json_rules(rules: str) -> dict:
    """Parse JSON rules string, exit on error."""
    import json

    try:
        return json.loads(rules)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in --rules: {e}", err=True)
        sys.exit(2)


def _log_applied_rules(rules_config: dict, verbose: bool) -> None:
    """Log applied rules if verbose."""
    if verbose:
        logger.debug(f"Applied inline rules: {rules_config}")


def _load_config_file(orchestrator, config_file, verbose):
    """Load configuration from external file."""
    config_path = Path(config_file)
    if not config_path.exists():
        click.echo(f"Error: Config file not found: {config_file}", err=True)
        sys.exit(2)

    # Load config into orchestrator
    orchestrator.config = orchestrator.config_loader.load(config_path)

    if verbose:
        logger.debug(f"Loaded config from: {config_file}")


def _execute_linting(orchestrator, path_obj, recursive):
    """Execute linting on file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    return orchestrator.lint_directory(path_obj, recursive=recursive)


def _separate_files_and_dirs(path_objs: list[Path]) -> tuple[list[Path], list[Path]]:
    """Separate file paths from directory paths.

    Args:
        path_objs: List of Path objects

    Returns:
        Tuple of (files, directories)
    """
    files = [p for p in path_objs if p.is_file()]
    dirs = [p for p in path_objs if p.is_dir()]
    return files, dirs


def _lint_files_if_any(orchestrator, files: list[Path]) -> list:
    """Lint files if list is non-empty.

    Args:
        orchestrator: Orchestrator instance
        files: List of file paths

    Returns:
        List of violations
    """
    if files:
        return orchestrator.lint_files(files)
    return []


def _lint_directories(orchestrator, dirs: list[Path], recursive: bool) -> list:
    """Lint all directories.

    Args:
        orchestrator: Orchestrator instance
        dirs: List of directory paths
        recursive: Whether to scan recursively

    Returns:
        List of violations from all directories
    """
    violations = []
    for dir_path in dirs:
        violations.extend(orchestrator.lint_directory(dir_path, recursive=recursive))
    return violations


def _execute_linting_on_paths(orchestrator, path_objs: list[Path], recursive: bool) -> list:
    """Execute linting on list of file/directory paths.

    Args:
        orchestrator: Orchestrator instance
        path_objs: List of Path objects (files or directories)
        recursive: Whether to scan directories recursively

    Returns:
        List of violations from all paths
    """
    files, dirs = _separate_files_and_dirs(path_objs)

    violations = []
    violations.extend(_lint_files_if_any(orchestrator, files))
    violations.extend(_lint_directories(orchestrator, dirs, recursive))

    return violations


def _setup_nesting_orchestrator(path_objs: list[Path], config_file: str | None, verbose: bool):
    """Set up orchestrator for nesting command."""
    # Use first path to determine project root
    first_path = path_objs[0] if path_objs else Path.cwd()
    project_root = first_path if first_path.is_dir() else first_path.parent

    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _apply_nesting_config_override(orchestrator, max_depth: int | None, verbose: bool):
    """Apply max_depth override to orchestrator config."""
    if max_depth is None:
        return

    if "nesting" not in orchestrator.config:
        orchestrator.config["nesting"] = {}
    orchestrator.config["nesting"]["max_nesting_depth"] = max_depth

    if verbose:
        logger.debug(f"Overriding max_nesting_depth to {max_depth}")


def _run_nesting_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute nesting lint on files or directories."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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

    # Default to current directory if no paths provided
    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_nesting_lint(path_objs, config_file, format, max_depth, recursive, verbose)
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_nesting_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, max_depth, recursive, verbose
):
    """Execute nesting lint."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_nesting_orchestrator(path_objs, config_file, verbose)
    _apply_nesting_config_override(orchestrator, max_depth, verbose)
    nesting_violations = _run_nesting_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(nesting_violations)} nesting violation(s)")

    format_violations(nesting_violations, format)
    sys.exit(1 if nesting_violations else 0)


def _setup_srp_orchestrator(path_objs: list[Path], config_file: str | None, verbose: bool):
    """Set up orchestrator for SRP command."""
    first_path = path_objs[0] if path_objs else Path.cwd()
    project_root = first_path if first_path.is_dir() else first_path.parent

    from src.orchestrator.core import Orchestrator

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _apply_srp_config_override(
    orchestrator, max_methods: int | None, max_loc: int | None, verbose: bool
):
    """Apply max_methods and max_loc overrides to orchestrator config."""
    if max_methods is None and max_loc is None:
        return

    if "srp" not in orchestrator.config:
        orchestrator.config["srp"] = {}

    _apply_srp_max_methods(orchestrator, max_methods, verbose)
    _apply_srp_max_loc(orchestrator, max_loc, verbose)


def _apply_srp_max_methods(orchestrator, max_methods: int | None, verbose: bool):
    """Apply max_methods override."""
    if max_methods is not None:
        orchestrator.config["srp"]["max_methods"] = max_methods
        if verbose:
            logger.debug(f"Overriding max_methods to {max_methods}")


def _apply_srp_max_loc(orchestrator, max_loc: int | None, verbose: bool):
    """Apply max_loc override."""
    if max_loc is not None:
        orchestrator.config["srp"]["max_loc"] = max_loc
        if verbose:
            logger.debug(f"Overriding max_loc to {max_loc}")


def _run_srp_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute SRP lint on files or directories."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_srp_lint(path_objs, config_file, format, max_methods, max_loc, recursive, verbose)
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_srp_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, max_methods, max_loc, recursive, verbose
):
    """Execute SRP lint."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_srp_orchestrator(path_objs, config_file, verbose)
    _apply_srp_config_override(orchestrator, max_methods, max_loc, verbose)
    srp_violations = _run_srp_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(srp_violations)} SRP violation(s)")

    format_violations(srp_violations, format)
    sys.exit(1 if srp_violations else 0)


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
    # All parameters are necessary for flexible DRY linter CLI usage.
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

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_dry_lint(
            path_objs, config_file, format, min_lines, no_cache, clear_cache, recursive, verbose
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_dry_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, min_lines, no_cache, clear_cache, recursive, verbose
):
    """Execute DRY linting."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_dry_orchestrator(path_objs, config_file, verbose)
    _apply_dry_config_override(orchestrator, min_lines, no_cache, verbose)

    if clear_cache:
        _clear_dry_cache(orchestrator, verbose)

    dry_violations = _run_dry_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(dry_violations)} DRY violation(s)")

    format_violations(dry_violations, format)
    sys.exit(1 if dry_violations else 0)


def _setup_dry_orchestrator(path_objs, config_file, verbose):
    """Set up orchestrator for DRY linting."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    first_path = path_objs[0] if path_objs else Path.cwd()
    search_start = first_path if first_path.is_dir() else first_path.parent
    project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_dry_config_file(orchestrator, config_file, verbose)

    return orchestrator


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
    _ensure_dry_config_exists(orchestrator)
    _apply_min_lines_override(orchestrator, min_lines, verbose)
    _apply_cache_override(orchestrator, no_cache, verbose)


def _ensure_dry_config_exists(orchestrator):
    """Ensure dry config section exists."""
    if "dry" not in orchestrator.config:
        orchestrator.config["dry"] = {}


def _apply_min_lines_override(orchestrator, min_lines, verbose):
    """Apply min_lines override if provided."""
    if min_lines is None:
        return

    orchestrator.config["dry"]["min_duplicate_lines"] = min_lines
    if verbose:
        logger.info(f"Override: min_duplicate_lines = {min_lines}")


def _apply_cache_override(orchestrator, no_cache, verbose):
    """Apply cache override if requested."""
    if not no_cache:
        return

    orchestrator.config["dry"]["cache_enabled"] = False
    if verbose:
        logger.info("Override: cache_enabled = False")


def _clear_dry_cache(orchestrator, verbose):
    """Clear DRY cache before running."""
    cache_path_str = orchestrator.config.get("dry", {}).get("cache_path", ".thailint-cache/dry.db")
    cache_path = orchestrator.project_root / cache_path_str

    if cache_path.exists():
        cache_path.unlink()
        if verbose:
            logger.info(f"Cleared cache: {cache_path}")
    else:
        if verbose:
            logger.info("Cache file does not exist, nothing to clear")


def _run_dry_lint(orchestrator, path_objs, recursive):
    """Run DRY linting and return violations."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)

    # Filter to only DRY violations
    dry_violations = [v for v in all_violations if v.rule_id.startswith("dry.")]

    return dry_violations


if __name__ == "__main__":
    cli()
