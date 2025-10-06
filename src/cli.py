"""
Purpose: Main CLI entrypoint with Click framework for command-line interface

Scope: CLI command definitions, option parsing, and command execution coordination

Overview: Provides the main CLI application using Click decorators for command definition, option
    parsing, and help text generation. Includes example commands (hello, config management) that
    demonstrate best practices for CLI design including error handling, logging configuration,
    context management, and user-friendly output. Serves as the entry point for the installed
    CLI tool and coordinates between user input and application logic.

Dependencies: click for CLI framework, logging for structured output, pathlib for file paths

Exports: cli (main command group), hello command, config command group

Interfaces: Click CLI commands, configuration context via Click ctx, logging integration

Implementation: Click decorators for commands, context passing for shared state, comprehensive help text
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from src.config import load_config, save_config, validate_config, ConfigError
from src import __version__

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
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )


@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=click.Path(), help='Path to config file')
@click.pass_context
def cli(ctx, verbose: bool, config: Optional[str]):
    """
    {{PROJECT_NAME}} - {{PROJECT_DESCRIPTION}}

    A professional command-line tool built with Python and Click.

    Examples:

        \b
        # Show help
        {{PROJECT_NAME}} --help

        \b
        # Run with verbose output
        {{PROJECT_NAME}} --verbose hello --name World

        \b
        # Use custom config
        {{PROJECT_NAME}} --config myconfig.yaml config show
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Setup logging
    setup_logging(verbose)

    # Load configuration
    try:
        if config:
            ctx.obj['config'] = load_config(Path(config))
            ctx.obj['config_path'] = Path(config)
        else:
            ctx.obj['config'] = load_config()
            ctx.obj['config_path'] = None

        logger.debug("Configuration loaded successfully")
    except ConfigError as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(2)

    ctx.obj['verbose'] = verbose


@cli.command()
@click.option('--name', '-n', default='World', help='Name to greet')
@click.option('--uppercase', '-u', is_flag=True, help='Convert greeting to uppercase')
@click.pass_context
def hello(ctx, name: str, uppercase: bool):
    """
    Print a greeting message.

    This is a simple example command demonstrating CLI basics.

    Examples:

        \b
        # Basic greeting
        {{PROJECT_NAME}} hello

        \b
        # Custom name
        {{PROJECT_NAME}} hello --name Alice

        \b
        # Uppercase output
        {{PROJECT_NAME}} hello --name Bob --uppercase
    """
    config = ctx.obj['config']
    verbose = ctx.obj.get('verbose', False)

    # Get greeting from config or use default
    greeting_template = config.get('greeting', 'Hello')

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


@config.command('show')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'yaml']),
              default='text', help='Output format')
@click.pass_context
def config_show(ctx, format: str):
    """
    Display current configuration.

    Shows all configuration values in the specified format.

    Examples:

        \b
        # Show as text
        {{PROJECT_NAME}} config show

        \b
        # Show as JSON
        {{PROJECT_NAME}} config show --format json

        \b
        # Show as YAML
        {{PROJECT_NAME}} config show --format yaml
    """
    cfg = ctx.obj['config']

    if format == 'json':
        import json
        click.echo(json.dumps(cfg, indent=2))
    elif format == 'yaml':
        import yaml
        click.echo(yaml.dump(cfg, default_flow_style=False, sort_keys=False))
    else:
        # Text format
        click.echo("Current Configuration:")
        click.echo("-" * 40)
        for key, value in cfg.items():
            click.echo(f"{key:20} : {value}")


@config.command('get')
@click.argument('key')
@click.pass_context
def config_get(ctx, key: str):
    """
    Get specific configuration value.

    KEY: Configuration key to retrieve

    Examples:

        \b
        # Get log level
        {{PROJECT_NAME}} config get log_level

        \b
        # Get greeting template
        {{PROJECT_NAME}} config get greeting
    """
    cfg = ctx.obj['config']

    if key not in cfg:
        click.echo(f"Configuration key not found: {key}", err=True)
        sys.exit(1)

    click.echo(cfg[key])


@config.command('set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx, key: str, value: str):
    """
    Set configuration value.

    KEY: Configuration key to set

    VALUE: New value for the key

    Examples:

        \b
        # Set log level
        {{PROJECT_NAME}} config set log_level DEBUG

        \b
        # Set greeting template
        {{PROJECT_NAME}} config set greeting "Hi"

        \b
        # Set numeric value
        {{PROJECT_NAME}} config set max_retries 5
    """
    cfg = ctx.obj['config']

    # Type conversion for common types
    if value.lower() in ['true', 'false']:
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
        value = float(value)

    # Update config
    cfg[key] = value

    # Validate updated config
    try:
        is_valid, errors = validate_config(cfg)
        if not is_valid:
            click.echo("Invalid configuration:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Validation error: {e}", err=True)
        sys.exit(1)

    # Save config
    try:
        config_path = ctx.obj.get('config_path')
        save_config(cfg, config_path)
        click.echo(f"✓ Set {key} = {value}")

        if ctx.obj.get('verbose'):
            logger.info(f"Configuration updated: {key}={value}")
    except ConfigError as e:
        click.echo(f"Error saving configuration: {e}", err=True)
        sys.exit(1)


@config.command('reset')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def config_reset(ctx, yes: bool):
    """
    Reset configuration to defaults.

    Examples:

        \b
        # Reset with confirmation
        {{PROJECT_NAME}} config reset

        \b
        # Reset without confirmation
        {{PROJECT_NAME}} config reset --yes
    """
    if not yes:
        click.confirm('Reset configuration to defaults?', abort=True)

    from src.config import DEFAULT_CONFIG

    try:
        config_path = ctx.obj.get('config_path')
        save_config(DEFAULT_CONFIG.copy(), config_path)
        click.echo("✓ Configuration reset to defaults")

        if ctx.obj.get('verbose'):
            logger.info("Configuration reset to defaults")
    except ConfigError as e:
        click.echo(f"Error resetting configuration: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
