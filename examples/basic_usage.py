#!/usr/bin/env python3
"""
Purpose: Basic usage example demonstrating high-level Linter API

Scope: Simple linting example for new users

Overview: Demonstrates basic usage of the Linter class for programmatic linting. Shows
    initialization with config file, linting a directory with rule filtering, and
    processing violations. Serves as quickstart example for library users who want
    to integrate thailint into their tools, editors, or automation scripts.

Dependencies: src.Linter for linting operations

Exports: Example script for documentation

Interfaces: Command-line example script

Implementation: Simple linear flow showing initialization, linting, and output
"""

from src import Linter


def main():
    """Run basic linting example."""
    # Initialize linter with config file
    linter = Linter(config_file='.thailint.yaml')

    # Lint a directory with specific rules
    violations = linter.lint('src/', rules=['file-placement'])

    # Process violations
    if violations:
        print(f"Found {len(violations)} violations:")
        for violation in violations:
            print(f"  {violation.file_path}: {violation.message}")
    else:
        print("No violations found!")


if __name__ == "__main__":
    main()
