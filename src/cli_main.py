"""
Purpose: Main CLI entrypoint for thai-lint command-line interface

Scope: CLI package initialization and command registration via module imports

Overview: Thin entry point that imports and re-exports the fully configured CLI from the modular
    src.cli package. All linter commands are registered via decorator side effects when their
    modules are imported. Configuration commands (hello, config group, init-config) are in
    src.cli.config, and linter commands (nesting, srp, dry, magic-numbers, file-placement,
    print-statements, file-header, method-property, stateless-class, pipeline) are in
    src.cli.linters submodules.

Dependencies: click for CLI framework, src.cli for modular CLI package

Exports: cli (main command group with all commands registered)

Interfaces: Click CLI commands, integration with Orchestrator for linting execution

Implementation: Module imports trigger command registration via Click decorator side effects

Suppressions:
    - F401: Module re-exports and imports trigger Click command registration via decorator side effects
"""

# Import the main CLI group from the modular package
# Import config module to register configuration commands
# (hello, config group, init-config)
from src.cli import config as _config_module  # noqa: F401

# Import linters package to register all linter commands
# (nesting, srp, dry, magic-numbers, file-placement, print-statements,
#  file-header, method-property, stateless-class, pipeline)
from src.cli import linters as _linters_module  # noqa: F401
from src.cli.main import cli  # noqa: F401

if __name__ == "__main__":
    cli()
