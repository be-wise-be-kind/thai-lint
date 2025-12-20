"""
Purpose: CLI package entry point and public API for thai-lint command-line interface

Scope: Re-export fully configured CLI with all commands registered

Overview: Provides the public API for the modular CLI package by re-exporting the fully configured
    CLI from src.cli_main, which has all linter commands registered. Importing from this module
    (src.cli) gives access to the complete CLI with all commands. Maintains backward compatibility
    with code that imports from src.cli while enabling modular organization of CLI commands.

Dependencies: src.cli_main for fully configured CLI with all commands

Exports: cli (main Click command group with all commands registered)

Interfaces: Single import point for CLI access via 'from src.cli import cli'

Implementation: Re-exports cli from src.cli_main to ensure all commands are registered
"""

# Import the fully configured CLI from cli_main (has all linter commands registered)
# This ensures backward compatibility with code that imports from src.cli
from src.cli_main import cli  # noqa: F401

__all__ = ["cli"]
