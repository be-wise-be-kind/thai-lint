"""
Purpose: CLI package entry point and public API for thai-lint command-line interface

Scope: Re-export fully configured CLI with all commands registered

Overview: Provides the public API for the modular CLI package by re-exporting the CLI group from
    src.cli.main and triggering command registration by importing submodules. Importing from this
    module (src.cli) gives access to the complete CLI with all commands. Maintains backward
    compatibility with code that imports from src.cli while enabling modular organization.

Dependencies: src.cli.main for CLI group, src.cli.config for config commands, src.cli.linters
    for linter commands

Exports: cli (main Click command group with all commands registered)

Interfaces: Single import point for CLI access via 'from src.cli import cli'

Implementation: Imports submodules to trigger command registration via Click decorators

Suppressions:
    - F401: Module re-exports required for public API interface
"""

# Import the CLI group from main module
# Import config and linters to register their commands with the CLI group
from src.cli import config as _config_module  # noqa: F401
from src.cli import linters as _linters_module  # noqa: F401
from src.cli.main import cli  # noqa: F401

__all__ = ["cli"]
