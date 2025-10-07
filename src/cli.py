"""
Purpose: Main CLI entrypoint with Click framework for command-line interface

Scope: CLI command definitions, option parsing, and command execution coordination

Overview: Provides the main CLI application using Click decorators for command definition, option
    parsing, and help text generation. Includes example commands (hello, config management) that
    demonstrate best practices for CLI design including error handling, logging configuration,
    context management, and user-friendly output. Serves as the entry point for the installed
    CLI tool and coordinates between user input and application logic.

Dependencies: click for CLI framework, logging for structured output, pathlib for file paths

Exports: cli (main command group), hello command, config command group, file_placement command

Interfaces: Click CLI commands, configuration context via Click ctx, logging integration

Implementation: Click decorators for commands, context passing for shared state, comprehensive help text
"""

import logging
import sys
from pathlib import Path

import click

from src import __version__
from src.config import ConfigError, load_config, save_config, validate_config

# Configure module logger
logger = logging.getLogger(__name__)


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

    if format == "json":
        import json

        click.echo(json.dumps(cfg, indent=2))
    elif format == "yaml":
        import yaml

        click.echo(yaml.dump(cfg, default_flow_style=False, sort_keys=False))
    else:
        # Text format
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
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@click.option("--rules", "-r", help="Inline JSON rules configuration")
@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Output format"
)
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def file_placement(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements
    ctx, path: str, config_file: str | None, rules: str | None, format: str, recursive: bool
):
    # Justification for Pylint disables:
    # - too-many-arguments/positional: CLI requires 1 ctx + 1 arg + 4 options = 6 params
    # - too-many-locals/statements: Complex CLI logic for config, linting, and output formatting
    # All parameters and logic are necessary for flexible CLI usage.
    """
    Lint files for proper file placement.

    Checks that files are placed in appropriate directories according to
    configured rules and patterns.

    PATH: File or directory to lint (defaults to current directory)

    Examples:

        \b
        # Lint current directory
        thai-lint file-placement

        \b
        # Lint specific directory
        thai-lint file-placement src/

        \b
        # Use custom config
        thai-lint file-placement --config rules.json .

        \b
        # Inline JSON rules
        thai-lint file-placement --rules '{"allow": [".*\\.py$"]}' .
    """
    verbose = ctx.obj.get("verbose", False)
    path_obj = Path(path)

    try:
        orchestrator = _setup_orchestrator(path_obj, config_file, rules, verbose)
        violations = _execute_linting(orchestrator, path_obj, recursive)

        if verbose:
            logger.info(f"Found {len(violations)} violation(s)")

        _output_violations(violations, format)
        sys.exit(1 if violations else 0)

    except Exception as e:
        click.echo(f"Error during linting: {e}", err=True)
        if verbose:
            logger.exception("Linting failed with exception")
        sys.exit(2)


def _setup_orchestrator(path_obj, config_file, rules, verbose):
    """Set up and configure the orchestrator."""
    from src.orchestrator.core import Orchestrator

    project_root = path_obj if path_obj.is_dir() else path_obj.parent
    orchestrator = Orchestrator(project_root=project_root)

    if rules:
        _apply_inline_rules(orchestrator, rules, verbose)
    elif config_file:
        _load_config_file(orchestrator, config_file, verbose)

    return orchestrator


def _apply_inline_rules(orchestrator, rules, verbose):
    """Parse and apply inline JSON rules."""
    import json

    import yaml

    try:
        rules_config = json.loads(rules)

        # Update orchestrator config
        orchestrator.config.update(rules_config)

        # Also write to .ai/layout.yaml for file-placement linter (if writable)
        try:
            ai_dir = orchestrator.project_root / ".ai"
            ai_dir.mkdir(exist_ok=True)
            layout_file = ai_dir / "layout.yaml"

            # Wrap rules in file-placement structure
            layout_config = {"file-placement": rules_config}
            with layout_file.open("w", encoding="utf-8") as f:
                yaml.dump(layout_config, f)

            if verbose:
                logger.debug(f"Applied inline rules: {rules_config}")
                logger.debug(f"Written layout config to: {layout_file}")
        except OSError as e:
            # If we can't write the layout file, log but continue
            # The orchestrator config is still updated
            if verbose:
                logger.debug(f"Could not write layout config: {e}")
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in --rules: {e}", err=True)
        sys.exit(2)


def _load_config_file(orchestrator, config_file, verbose):
    """Load configuration from external file."""
    import yaml

    config_path = Path(config_file)
    if not config_path.exists():
        click.echo(f"Error: Config file not found: {config_file}", err=True)
        sys.exit(2)

    # Load config into orchestrator
    orchestrator.config = orchestrator.config_loader.load(config_path)

    # Also copy to .ai/layout.yaml for file-placement linter (if writable)
    try:
        ai_dir = orchestrator.project_root / ".ai"
        ai_dir.mkdir(exist_ok=True)
        layout_file = ai_dir / "layout.yaml"

        # Write loaded config to layout file
        with layout_file.open("w", encoding="utf-8") as f:
            yaml.dump(orchestrator.config, f)

        if verbose:
            logger.debug(f"Loaded config from: {config_file}")
            logger.debug(f"Written layout config to: {layout_file}")
    except OSError as e:
        # If we can't write the layout file, log but continue
        if verbose:
            logger.debug(f"Could not write layout config: {e}")


def _execute_linting(orchestrator, path_obj, recursive):
    """Execute linting on file or directory."""
    if path_obj.is_file():
        return orchestrator.lint_file(path_obj)
    return orchestrator.lint_directory(path_obj, recursive=recursive)


def _output_violations(violations, format):
    """Format and output violations."""
    if format == "json":
        _output_json(violations)
    else:
        _output_text(violations)


def _output_json(violations):
    """Output violations in JSON format."""
    import json

    output = {
        "violations": [
            {
                "rule_id": v.rule_id,
                "file_path": str(v.file_path),
                "line": v.line,
                "column": v.column,
                "message": v.message,
                "severity": v.severity.name,
            }
            for v in violations
        ],
        "total": len(violations),
    }
    click.echo(json.dumps(output, indent=2))


def _output_text(violations):
    """Output violations in text format."""
    if violations:
        click.echo(f"Found {len(violations)} violation(s):\n")
        for v in violations:
            location = f"{v.file_path}:{v.line}" if v.line else str(v.file_path)
            if v.column:
                location += f":{v.column}"
            click.echo(f"  {location}")
            click.echo(f"    [{v.severity.name}] {v.rule_id}: {v.message}")
            click.echo()
    else:
        click.echo("✓ No violations found")


if __name__ == "__main__":
    cli()
