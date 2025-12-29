"""
Purpose: Configuration management commands for thai-lint CLI

Scope: Commands for viewing, modifying, and initializing thai-lint configuration

Overview: Provides CLI commands for managing thai-lint configuration including show (display
    configuration in text/json/yaml), get (retrieve specific value), set (modify value with
    validation), reset (restore defaults), and init-config (generate new .thailint.yaml with
    presets). Supports both interactive and non-interactive modes for human and AI agent
    workflows. Integrates with the config module for loading, saving, and validation.

Dependencies: click for CLI framework, src.config for config operations, pathlib for file paths,
    json and yaml for output formatting

Exports: config_group (Click command group), init_config command, show_config, get_config,
    set_config, reset_config commands

Interfaces: Click commands registered to main CLI group, config presets (strict/standard/lenient)

Implementation: Uses Click decorators for command definition, supports multiple output formats,
    validates configuration changes before saving, uses template file for init-config generation
"""

import logging
import sys
from pathlib import Path

import click
import yaml

from src.config import ConfigError, save_config, validate_config

from .config_merge import perform_merge
from .main import cli

# Configure module logger
logger = logging.getLogger(__name__)


# =============================================================================
# Config Command Group
# =============================================================================


@cli.group()
def config() -> None:
    """Configuration management commands."""
    pass


# =============================================================================
# Config Show Command
# =============================================================================


@config.command("show")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "yaml"]),
    default="text",
    help="Output format",
)
@click.pass_context
def config_show(ctx: click.Context, format: str) -> None:
    """Display current configuration.

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
    click.echo(yaml.dump(cfg, default_flow_style=False, sort_keys=False))


def _format_config_text(cfg: dict) -> None:
    """Format configuration as text."""
    click.echo("Current Configuration:")
    click.echo("-" * 40)
    for key, value in cfg.items():
        click.echo(f"{key:20} : {value}")


# =============================================================================
# Config Get Command
# =============================================================================


@config.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx: click.Context, key: str) -> None:
    """Get specific configuration value.

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


# =============================================================================
# Config Set Command
# =============================================================================


def _convert_value_type(value: str) -> bool | int | float | str:
    """Convert string value to appropriate type."""
    if value.lower() in ["true", "false"]:
        return value.lower() == "true"
    if value.isdigit():
        return int(value)
    if value.replace(".", "", 1).isdigit() and value.count(".") == 1:
        return float(value)
    return value


def _validate_and_report_errors(cfg: dict) -> None:
    """Validate configuration and report errors."""
    is_valid, errors = validate_config(cfg)
    if not is_valid:
        click.echo("Invalid configuration:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        sys.exit(1)


def _save_and_report_success(
    cfg: dict, key: str, value: bool | int | float | str, config_path: Path | None, verbose: bool
) -> None:
    """Save configuration and report success."""
    save_config(cfg, config_path)
    click.echo(f"Set {key} = {value}")
    if verbose:
        logger.info(f"Configuration updated: {key}={value}")


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set configuration value.

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


# =============================================================================
# Config Reset Command
# =============================================================================


@config.command("reset")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def config_reset(ctx: click.Context, yes: bool) -> None:
    """Reset configuration to defaults.

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
        click.echo("Configuration reset to defaults")

        if ctx.obj.get("verbose"):
            logger.info("Configuration reset to defaults")
    except ConfigError as e:
        click.echo(f"Error resetting configuration: {e}", err=True)
        sys.exit(1)


# =============================================================================
# Init Config Command
# =============================================================================


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
def init_config(preset: str, non_interactive: bool, force: bool, output: str) -> None:
    """Generate a .thailint.yaml configuration file with preset values.

    Creates a richly-commented configuration file with sensible defaults
    and optional customizations for different strictness levels.

    If a config file already exists, missing linter sections will be added
    without modifying existing settings. Use --force to completely overwrite.

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
        # Overwrite existing config (replaces entire file)
        thailint init-config --force

        \\b
        # Custom output path
        thailint init-config --output my-config.yaml
    """
    output_path = Path(output)

    # Interactive mode: Ask user for preferences
    if not non_interactive:
        preset = _run_interactive_preset_selection(preset)

    # If file exists and not forcing overwrite, merge missing sections
    if output_path.exists() and not force:
        perform_merge(output_path, preset, output, _generate_config_content)
        return

    # Generate full config based on preset
    config_content = _generate_config_content(preset)

    # Write config file
    _write_config_file(output_path, config_content, preset, output)


def _run_interactive_preset_selection(default_preset: str) -> str:
    """Run interactive preset selection.

    Args:
        default_preset: Default preset to use if user accepts default

    Returns:
        Selected preset name
    """
    click.echo("thai-lint Configuration Generator")
    click.echo("=" * 50)
    click.echo("")
    click.echo("This will create a .thailint.yaml configuration file.")
    click.echo("For non-interactive mode (AI agents), use:")
    click.echo("  thailint init-config --non-interactive")
    click.echo("")

    # Show preset options
    click.echo("Available presets:")
    click.echo("  strict:   Only -1, 0, 1 allowed (strictest)")
    click.echo("  standard: -1, 0, 1, 2, 3, 4, 5, 10, 100, 1000 (balanced)")
    click.echo("  lenient:  Includes time conversions 60, 3600 (most permissive)")
    click.echo("")

    preset_choices = click.Choice(["strict", "standard", "lenient"])
    result: str = click.prompt("Choose preset", type=preset_choices, default=default_preset)
    return result


def _generate_config_content(preset: str) -> str:
    """Generate config file content based on preset.

    Args:
        preset: Preset name (strict, standard, or lenient)

    Returns:
        Generated configuration file content
    """
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

    # Read template - use parent of parent since we're in src/cli/
    template_path = Path(__file__).parent.parent / "templates" / "thailint_config_template.yaml"
    template = template_path.read_text(encoding="utf-8")

    # Replace placeholders
    content = template.replace("{{PRESET}}", config["description"])
    content = content.replace("{{ALLOWED_NUMBERS}}", config["allowed_numbers"])
    content = content.replace("{{MAX_SMALL_INTEGER}}", config["max_small_integer"])

    return content


def _write_config_file(output_path: Path, content: str, preset: str, output: str) -> None:
    """Write configuration file and show success message.

    Args:
        output_path: Path to write file to
        content: File content to write
        preset: Selected preset name
        output: Output filename for display
    """
    try:
        output_path.write_text(content, encoding="utf-8")
        click.echo("")
        click.echo(f"Created {output}")
        click.echo(f"Preset: {preset}")
        click.echo("")
        click.echo("Next steps:")
        click.echo(f"  1. Review and customize {output}")
        click.echo("  2. Run: thailint magic-numbers .")
        click.echo("  3. See docs: https://github.com/your-org/thai-lint")
    except OSError as e:
        click.echo(f"Error writing config file: {e}", err=True)
        sys.exit(1)


# =============================================================================
# Hello Command (Example Command)
# =============================================================================


@cli.command()
@click.option("--name", "-n", default="World", help="Name to greet")
@click.option("--uppercase", "-u", is_flag=True, help="Convert greeting to uppercase")
@click.pass_context
def hello(ctx: click.Context, name: str, uppercase: bool) -> None:
    """Print a greeting message.

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
