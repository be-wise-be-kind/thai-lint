"""
Purpose: Entry point for running thai-lint CLI as a module (python -m src.cli)

Scope: Module execution support for direct CLI invocation

Overview: Enables running the CLI via 'python -m src.cli' by invoking the main cli group.
    This file is executed when the package is run as a module, providing an alternative
    entry point to the installed 'thailint' command.

Dependencies: src.cli for fully configured CLI

Exports: None (execution entry point only)

Interfaces: Command-line invocation via 'python -m src.cli [command] [args]'

Implementation: Imports and invokes cli() from the package
"""

from src.cli import cli

if __name__ == "__main__":
    cli()
