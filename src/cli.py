"""
Purpose: Main CLI entrypoint with Click framework for command-line interface

Scope: CLI command definitions, option parsing, and command execution coordination

Overview: Provides the main CLI application using Click decorators for command definition, option
    parsing, and help text generation. Includes example commands (hello, config management) that
    demonstrate best practices for CLI design including error handling, logging configuration,
    context management, and user-friendly output. Serves as the entry point for the installed
    CLI tool and coordinates between user input and application logic.

Dependencies: click for CLI framework, logging for structured output, pathlib for file paths

Exports: cli (main command group), hello command, config command group, linter commands

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
        "--format",
        "-f",
        type=click.Choice(["text", "json", "sarif"]),
        default="text",
        help="Output format",
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


def _autodetect_project_root(verbose: bool, get_project_root) -> Path:
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


def _get_project_root_from_context(ctx) -> Path:
    """Get or determine project root from Click context.

    This function defers the actual determination until needed to avoid
    importing pyprojroot in test environments where it may not be available.

    Args:
        ctx: Click context containing CLI options

    Returns:
        Path to determined project root
    """
    # Check if already determined and cached
    if "project_root" in ctx.obj:
        return ctx.obj["project_root"]

    # Determine project root using stored CLI options
    explicit_root = ctx.obj.get("cli_project_root")
    config_path = ctx.obj.get("cli_config_path")
    verbose = ctx.obj.get("verbose", False)

    project_root = _determine_project_root(explicit_root, config_path, verbose)

    # Cache for future use
    ctx.obj["project_root"] = project_root

    return project_root


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.option(
    "--project-root",
    type=click.Path(),
    help="Explicitly specify project root directory (overrides auto-detection)",
)
@click.pass_context
def cli(ctx, verbose: bool, config: str | None, project_root: str | None):
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
        # Specify project root explicitly (useful in Docker)
        thai-lint --project-root /workspace/root magic-numbers backend/

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

    # Store CLI options for later project root determination
    # (deferred to avoid pyprojroot import issues in test environments)
    ctx.obj["cli_project_root"] = project_root
    ctx.obj["cli_config_path"] = config

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


@cli.command("init-config")
@click.option(
    "--preset",
    "-p",
    type=click.Choice(["strict", "standard", "lenient"]),
    default="standard",
    help="Configuration preset",
)
@click.option("--non-interactive", is_flag=True, help="Skip interactive prompts (for AI agents)")
@click.option("--force", is_flag=True, help="Overwrite existing .thailint.yaml file")
@click.option(
    "--output", "-o", type=click.Path(), default=".thailint.yaml", help="Output file path"
)
def init_config(preset: str, non_interactive: bool, force: bool, output: str):
    """
    Generate a .thailint.yaml configuration file with preset values.

    Creates a richly-commented configuration file with sensible defaults
    and optional customizations for different strictness levels.

    For AI agents, use --non-interactive mode:
      thailint init-config --non-interactive --preset lenient

    Presets:
      strict:   Minimal allowed numbers (only -1, 0, 1)
      standard: Balanced defaults (includes 2, 3, 4, 5, 10, 100, 1000)
      lenient:  Includes time conversions (adds 60, 3600)

    Examples:

        \\b
        # Interactive mode (default, for humans)
        thailint init-config

        \\b
        # Non-interactive mode (for AI agents)
        thailint init-config --non-interactive

        \\b
        # Generate with lenient preset
        thailint init-config --preset lenient

        \\b
        # Overwrite existing config
        thailint init-config --force

        \\b
        # Custom output path
        thailint init-config --output my-config.yaml
    """
    output_path = Path(output)

    # Check if file exists (unless --force)
    if output_path.exists() and not force:
        click.echo(f"Error: {output} already exists", err=True)
        click.echo("", err=True)
        click.echo("Use --force to overwrite:", err=True)
        click.echo("  thailint init-config --force", err=True)
        sys.exit(1)

    # Interactive mode: Ask user for preferences
    if not non_interactive:
        click.echo("thai-lint Configuration Generator")
        click.echo("=" * 50)
        click.echo("")
        click.echo("This will create a .thailint.yaml configuration file.")
        click.echo("For non-interactive mode (AI agents), use:")
        click.echo("  thailint init-config --non-interactive")
        click.echo("")

        # Ask for preset
        click.echo("Available presets:")
        click.echo("  strict:   Only -1, 0, 1 allowed (strictest)")
        click.echo("  standard: -1, 0, 1, 2, 3, 4, 5, 10, 100, 1000 (balanced)")
        click.echo("  lenient:  Includes time conversions 60, 3600 (most permissive)")
        click.echo("")

        preset = click.prompt(
            "Choose preset", type=click.Choice(["strict", "standard", "lenient"]), default=preset
        )

    # Generate config based on preset
    config_content = _generate_config_content(preset)

    # Write config file
    try:
        output_path.write_text(config_content, encoding="utf-8")
        click.echo("")
        click.echo(f"✓ Created {output}")
        click.echo(f"✓ Preset: {preset}")
        click.echo("")
        click.echo("Next steps:")
        click.echo(f"  1. Review and customize {output}")
        click.echo("  2. Run: thailint magic-numbers .")
        click.echo("  3. See docs: https://github.com/your-org/thai-lint")
    except OSError as e:
        click.echo(f"Error writing config file: {e}", err=True)
        sys.exit(1)


def _generate_config_content(preset: str) -> str:
    """Generate config file content based on preset."""
    # Preset configurations
    presets = {
        "strict": {
            "allowed_numbers": "[-1, 0, 1]",
            "max_small_integer": "3",
            "description": "Strict (only universal values)",
        },
        "standard": {
            "allowed_numbers": "[-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000]",
            "max_small_integer": "10",
            "description": "Standard (balanced defaults)",
        },
        "lenient": {
            "allowed_numbers": "[-1, 0, 1, 2, 3, 4, 5, 10, 60, 100, 1000, 3600]",
            "max_small_integer": "10",
            "description": "Lenient (includes time conversions)",
        },
    }

    config = presets[preset]

    # Read template
    template_path = Path(__file__).parent / "templates" / "thailint_config_template.yaml"
    template = template_path.read_text(encoding="utf-8")

    # Replace placeholders
    content = template.replace("{{PRESET}}", config["description"])
    content = content.replace("{{ALLOWED_NUMBERS}}", config["allowed_numbers"])
    content = content.replace("{{MAX_SMALL_INTEGER}}", config["max_small_integer"])

    return content


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
    project_root = _get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_file_placement_lint(
            path_objs, config_file, rules, format, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_file_placement_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, rules, format, recursive, verbose, project_root=None
):
    """Execute file placement linting."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_orchestrator(path_objs, config_file, rules, verbose, project_root)
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


def _setup_orchestrator(path_objs, config_file, rules, verbose, project_root=None):
    """Set up and configure the orchestrator."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Use provided project_root or fall back to auto-detection
    project_root = _get_or_detect_project_root(path_objs, project_root, get_project_root)

    orchestrator = Orchestrator(project_root=project_root)
    _apply_orchestrator_config(orchestrator, config_file, rules, verbose)

    return orchestrator


def _get_or_detect_project_root(path_objs, project_root, get_project_root):
    """Get provided project root or auto-detect from paths.

    Args:
        path_objs: List of path objects
        project_root: Optionally provided project root
        get_project_root: Function to detect project root

    Returns:
        Project root path
    """
    if project_root is not None:
        return project_root

    # Find actual project root (where .git or pyproject.toml exists)
    # This ensures .artifacts/ is always created at project root, not in subdirectories
    first_path = path_objs[0] if path_objs else Path.cwd()
    search_start = first_path if first_path.is_dir() else first_path.parent
    return get_project_root(search_start)


def _apply_orchestrator_config(orchestrator, config_file, rules, verbose):
    """Apply configuration to orchestrator.

    Args:
        orchestrator: Orchestrator instance
        config_file: Path to config file (optional)
        rules: Inline JSON rules (optional)
        verbose: Whether verbose logging is enabled
    """
    if rules:
        _apply_inline_rules(orchestrator, rules, verbose)
    elif config_file:
        _load_config_file(orchestrator, config_file, verbose)


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


def _setup_nesting_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for nesting command."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Use provided project_root or fall back to auto-detection
    if project_root is None:
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _apply_nesting_config_override(orchestrator, max_depth: int | None, verbose: bool):
    """Apply max_depth override to orchestrator config."""
    if max_depth is None:
        return

    # Ensure nesting config exists
    if "nesting" not in orchestrator.config:
        orchestrator.config["nesting"] = {}

    nesting_config = orchestrator.config["nesting"]

    # Set top-level max_nesting_depth
    nesting_config["max_nesting_depth"] = max_depth

    # Override language-specific configs to ensure CLI option takes precedence
    _override_language_specific_nesting(nesting_config, max_depth)

    if verbose:
        logger.debug(f"Overriding max_nesting_depth to {max_depth}")


def _override_language_specific_nesting(nesting_config: dict, max_depth: int):
    """Override language-specific nesting depth configs.

    Args:
        nesting_config: Nesting configuration dictionary
        max_depth: Maximum nesting depth to set
    """
    for lang in ["python", "typescript", "javascript"]:
        if lang in nesting_config:
            nesting_config[lang]["max_nesting_depth"] = max_depth


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
    project_root = _get_project_root_from_context(ctx)

    # Default to current directory if no paths provided
    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_nesting_lint(
            path_objs, config_file, format, max_depth, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_nesting_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, max_depth, recursive, verbose, project_root=None
):
    """Execute nesting lint."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_nesting_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_nesting_config_override(orchestrator, max_depth, verbose)
    nesting_violations = _run_nesting_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(nesting_violations)} nesting violation(s)")

    format_violations(nesting_violations, format)
    sys.exit(1 if nesting_violations else 0)


def _setup_srp_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for SRP command."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Use provided project_root or fall back to auto-detection
    if project_root is None:
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

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
    project_root = _get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_srp_lint(
            path_objs, config_file, format, max_methods, max_loc, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_srp_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, max_methods, max_loc, recursive, verbose, project_root=None
):
    """Execute SRP lint."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_srp_orchestrator(path_objs, config_file, verbose, project_root)
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
    project_root = _get_project_root_from_context(ctx)

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
        _handle_linting_error(e, verbose)


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
    _validate_paths_exist(path_objs)
    orchestrator = _setup_dry_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_dry_config_override(orchestrator, min_lines, no_cache, verbose)

    if clear_cache:
        _clear_dry_cache(orchestrator, verbose)

    dry_violations = _run_dry_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(dry_violations)} DRY violation(s)")

    format_violations(dry_violations, format)
    sys.exit(1 if dry_violations else 0)


def _setup_dry_orchestrator(path_objs, config_file, verbose, project_root=None):
    """Set up orchestrator for DRY linting."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Use provided project_root or fall back to auto-detection
    if project_root is None:
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


def _setup_magic_numbers_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for magic-numbers command."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Use provided project_root or fall back to auto-detection
    if project_root is None:
        # Find actual project root (where .git or .thailint.yaml exists)
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _run_magic_numbers_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute magic-numbers lint on files or directories."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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
    project_root = _get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_magic_numbers_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_magic_numbers_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, recursive, verbose, project_root=None
):
    """Execute magic-numbers lint."""
    _validate_paths_exist(path_objs)
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
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    if project_root is None:
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _run_print_statements_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute print-statements lint on files or directories."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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
    project_root = _get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_print_statements_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_print_statements_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, recursive, verbose, project_root=None
):
    """Execute print-statements lint."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_print_statements_orchestrator(
        path_objs, config_file, verbose, project_root
    )
    print_statements_violations = _run_print_statements_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(print_statements_violations)} print statement violation(s)")

    format_violations(print_statements_violations, format)
    sys.exit(1 if print_statements_violations else 0)


# File Header Command Helper Functions


def _setup_file_header_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for file-header command."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Use provided project_root or fall back to auto-detection
    if project_root is None:
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _run_file_header_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute file-header lint on files or directories."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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
    project_root = _get_project_root_from_context(ctx)

    # Default to current directory if no paths provided
    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_file_header_lint(path_objs, config_file, format, recursive, verbose, project_root)
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_file_header_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, recursive, verbose, project_root=None
):
    """Execute file-header lint."""
    _validate_paths_exist(path_objs)
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
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    if project_root is None:
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _run_method_property_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute method-property lint on files or directories."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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
    project_root = _get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_method_property_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_method_property_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, recursive, verbose, project_root=None
):
    """Execute method-property lint."""
    _validate_paths_exist(path_objs)
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
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    if project_root is None:
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _run_stateless_class_lint(orchestrator, path_objs: list[Path], recursive: bool):
    """Execute stateless-class lint on files or directories."""
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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
    project_root = _get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_stateless_class_lint(
            path_objs, config_file, format, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_stateless_class_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, recursive, verbose, project_root=None
):
    """Execute stateless-class lint."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_stateless_class_orchestrator(
        path_objs, config_file, verbose, project_root
    )
    stateless_class_violations = _run_stateless_class_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(stateless_class_violations)} stateless-class violation(s)")

    format_violations(stateless_class_violations, format)
    sys.exit(1 if stateless_class_violations else 0)


# Collection Pipeline command helper functions


def _setup_pipeline_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
):
    """Set up orchestrator for pipeline command."""
    from src.orchestrator.core import Orchestrator
    from src.utils.project_root import get_project_root

    # Use provided project_root or fall back to auto-detection
    if project_root is None:
        first_path = path_objs[0] if path_objs else Path.cwd()
        search_start = first_path if first_path.is_dir() else first_path.parent
        project_root = get_project_root(search_start)

    orchestrator = Orchestrator(project_root=project_root)

    if config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


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
    all_violations = _execute_linting_on_paths(orchestrator, path_objs, recursive)
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
    project_root = _get_project_root_from_context(ctx)

    if not paths:
        paths = (".",)

    path_objs = [Path(p) for p in paths]

    try:
        _execute_pipeline_lint(
            path_objs, config_file, format, min_continues, recursive, verbose, project_root
        )
    except Exception as e:
        _handle_linting_error(e, verbose)


def _execute_pipeline_lint(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    path_objs, config_file, format, min_continues, recursive, verbose, project_root=None
):
    """Execute collection-pipeline lint."""
    _validate_paths_exist(path_objs)
    orchestrator = _setup_pipeline_orchestrator(path_objs, config_file, verbose, project_root)
    _apply_pipeline_config_override(orchestrator, min_continues, verbose)
    pipeline_violations = _run_pipeline_lint(orchestrator, path_objs, recursive)

    if verbose:
        logger.info(f"Found {len(pipeline_violations)} collection-pipeline violation(s)")

    format_violations(pipeline_violations, format)
    sys.exit(1 if pipeline_violations else 0)


if __name__ == "__main__":
    cli()
