"""
Purpose: CLI linters package that registers all linter commands to the main CLI group

Scope: Export and registration of all linter CLI commands (nesting, srp, dry, magic-numbers, etc.)

Overview: Package initialization that imports all linter command modules to trigger their registration
    with the main CLI group via Click decorators. Each submodule defines commands using @cli.command()
    decorators that automatically register with the CLI when imported. Organized by logical grouping:
    structure_quality (nesting, srp), code_smells (dry, magic-numbers), code_patterns (print-statements,
    method-property, stateless-class), structure (file-placement, pipeline), documentation (file-header).

Dependencies: Click for CLI framework, src.cli.main for CLI group, individual linter modules

Exports: All linter command functions for reference and testing

Interfaces: Click command decorators, integration with main CLI group

Implementation: Module imports trigger command registration via Click decorator side effects

Suppressions:
    - F401: Module imports trigger Click command registration via decorator side effects
"""

# Import all linter command modules to register them with the CLI
# Each module uses @cli.command() decorators that register on import
from src.cli.linters import (  # noqa: F401
    code_patterns,
    code_smells,
    documentation,
    structure,
    structure_quality,
)

# Re-export command functions for testing and reference
from src.cli.linters.code_patterns import (
    method_property,
    print_statements,
    stateless_class,
)
from src.cli.linters.code_smells import dry, magic_numbers
from src.cli.linters.documentation import file_header
from src.cli.linters.structure import file_placement, pipeline
from src.cli.linters.structure_quality import nesting, srp

__all__ = [
    # Structure quality commands
    "nesting",
    "srp",
    # Code smell commands
    "dry",
    "magic_numbers",
    # Code pattern commands
    "print_statements",
    "method_property",
    "stateless_class",
    # Structure commands
    "file_placement",
    "pipeline",
    # Documentation commands
    "file_header",
]
