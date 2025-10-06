"""
Purpose: Package initialization and version definition for CLI application

Scope: Package-level exports and metadata

Overview: Initializes the CLI application package, defines version number using semantic versioning,
    and exports the public API. Provides single source of truth for version information used by
    setup tools, CLI help text, and documentation. Exports main CLI entry point and configuration
    utilities for easy import by other modules.

Dependencies: None (minimal imports for package initialization)

Exports: __version__, cli (main CLI entry point), load_config, save_config, ConfigError

Interfaces: Package version string, CLI command group, configuration functions
"""

__version__ = "1.0.0"

from src.cli import cli
from src.config import load_config, save_config, ConfigError

__all__ = [
    '__version__',
    'cli',
    'load_config',
    'save_config',
    'ConfigError',
]
