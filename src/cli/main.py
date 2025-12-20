"""
Purpose: Main CLI group definition and core setup for thai-lint command-line interface

Scope: Core Click group configuration, version handling, global options, and context setup

Overview: Defines the root CLI command group using Click framework with version option and global
    options (verbose, config, project-root). Handles context initialization, logging setup, and
    configuration loading. Serves as the central entry point that other CLI modules register
    commands against. Provides the foundation for modular CLI architecture where commands are
    defined in separate modules but registered to this main group.

Dependencies: click for CLI framework, src.config for configuration loading, src.__version__ for
    version info

Exports: cli (main Click command group), setup_logging function

Interfaces: Click context object with config, verbose, project_root options stored in ctx.obj

Implementation: Uses Click decorators for group definition, stores parsed options in context
    for child commands to access. Defers project root determination to avoid import issues
    in test environments.
"""

import logging
import sys
from pathlib import Path

import click

from src import __version__
from src.config import ConfigError, load_config

# Configure module logger
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI application.

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
@click.option(
    "--project-root",
    type=click.Path(),
    help="Explicitly specify project root directory (overrides auto-detection)",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: str | None, project_root: str | None) -> None:
    """thai-lint - AI code linter and governance tool

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
