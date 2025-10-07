#!/usr/bin/env python3
"""
Purpose: Advanced usage example demonstrating direct linter imports and custom workflows

Scope: Advanced linting patterns for power users

Overview: Demonstrates advanced usage patterns including direct linter imports, custom
    configuration objects, orchestrator usage, and custom violation processing. Shows
    flexibility of the library API for users who need fine-grained control over linting
    operations, custom rule sets, or integration with existing systems.

Dependencies: src.Linter, src.Orchestrator, src.linters.file_placement for advanced operations

Exports: Example script for documentation

Interfaces: Command-line example script

Implementation: Multiple examples showing different API usage patterns and flexibility
"""

from pathlib import Path

from src import Linter, Orchestrator, file_placement_lint


def example_direct_linter_import():
    """Example: Using direct linter imports."""
    print("=== Direct Linter Import Example ===")

    # Import specific linter directly
    config = {
        "allow": [r".*\.py$"],
        "deny": [r".*test.*\.py$"],
    }

    violations = file_placement_lint(Path("src/"), config)

    print(f"Found {len(violations)} violations using direct import")


def example_orchestrator_usage():
    """Example: Using orchestrator directly for advanced control."""
    print("\n=== Orchestrator Example ===")

    # Initialize orchestrator with project root
    orchestrator = Orchestrator(project_root=Path.cwd())

    # Lint specific file
    violations = orchestrator.lint_file(Path("src/api.py"))

    print(f"Found {len(violations)} violations in src/api.py")


def example_custom_config():
    """Example: Using Linter with programmatic config."""
    print("\n=== Custom Config Example ===")

    # Initialize without config file (uses defaults)
    linter = Linter()

    # Lint with all rules
    all_violations = linter.lint("src/")
    print(f"All rules: {len(all_violations)} violations")

    # Lint with specific rules only
    fp_violations = linter.lint("src/", rules=["file-placement"])
    print(f"File placement only: {len(fp_violations)} violations")


def example_violation_processing():
    """Example: Advanced violation processing and reporting."""
    print("\n=== Violation Processing Example ===")

    linter = Linter()
    violations = linter.lint("src/")

    # Group violations by file
    by_file = {}
    for v in violations:
        file_path = str(v.file_path)
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append(v)

    # Report grouped violations
    for file_path, file_violations in by_file.items():
        print(f"\n{file_path}:")
        for v in file_violations:
            print(f"  - [{v.severity.name}] {v.message}")

    # Filter by severity
    errors = [v for v in violations if v.severity.name == "ERROR"]
    print(f"\nTotal errors: {len(errors)}")


def main():
    """Run all advanced examples."""
    example_direct_linter_import()
    example_orchestrator_usage()
    example_custom_config()
    example_violation_processing()


if __name__ == "__main__":
    main()
