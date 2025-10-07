#!/usr/bin/env python3
"""
Purpose: Nesting depth linter usage examples

Scope: Demonstrates CLI and library usage for nesting depth analysis

Overview: Shows multiple ways to use the nesting depth linter including high-level Linter API,
    direct nesting_lint convenience function, and custom depth configuration. Helps users
    understand different usage patterns for integrating nesting checks into their workflows,
    editors, or automation scripts. Includes examples for both single files and directories.

Dependencies: src.Linter, src.nesting_lint for nesting depth analysis

Exports: Example script for documentation

Interfaces: Command-line example script

Implementation: Multiple usage patterns demonstrating flexibility of the API
"""

from pathlib import Path

from src import Linter, nesting_lint


def example_high_level_api():
    """Example 1: High-level Linter API with config file."""
    print("=== Example 1: High-level API ===\n")

    # Initialize linter with config file
    linter = Linter(config_file='.thailint.yaml')

    # Lint directory with nesting rule
    violations = linter.lint('src/', rules=['nesting'])

    # Process violations
    if violations:
        print(f"Found {len(violations)} nesting violations:\n")
        for v in violations:
            print(f"  {v.file_path}:{v.line_number or '?'}")
            print(f"  {v.message}\n")
    else:
        print("✓ No nesting violations found!\n")


def example_direct_nesting_lint():
    """Example 2: Direct nesting_lint function."""
    print("=== Example 2: Direct nesting_lint() ===\n")

    # Lint specific file with custom max depth
    violations = nesting_lint(
        'src/cli.py',
        max_depth=3
    )

    if violations:
        print(f"Found {len(violations)} violations in src/cli.py:\n")
        for v in violations:
            print(f"  Line {v.line_number or '?'}: {v.message}\n")
    else:
        print("✓ src/cli.py passes nesting depth check (max: 3)\n")


def example_custom_configuration():
    """Example 3: Custom configuration without config file."""
    print("=== Example 3: Custom Configuration ===\n")

    # Lint with inline configuration
    linter = Linter()  # No config file

    # Scan directory with custom depth limit
    violations = nesting_lint(
        'src/linters/',
        max_depth=4  # More lenient
    )

    print(f"Checking src/linters/ with max_depth=4:")
    print(f"  Violations: {len(violations)}\n")


def example_process_multiple_files():
    """Example 4: Process multiple files."""
    print("=== Example 4: Multiple Files ===\n")

    files_to_check = [
        'src/cli.py',
        'src/config.py',
        'src/orchestrator/core.py',
    ]

    all_violations = []
    for file_path in files_to_check:
        if Path(file_path).exists():
            violations = nesting_lint(file_path, max_depth=3)
            all_violations.extend(violations)
            status = "✓" if not violations else "✗"
            print(f"  {status} {file_path}: {len(violations)} violations")

    print(f"\nTotal violations: {len(all_violations)}\n")


def example_with_error_handling():
    """Example 5: Robust error handling."""
    print("=== Example 5: Error Handling ===\n")

    try:
        # Attempt to lint non-existent file
        violations = nesting_lint('nonexistent.py')
        print(f"Violations: {len(violations)}")
    except FileNotFoundError as e:
        print(f"✗ File not found: {e}")
    except Exception as e:
        print(f"✗ Error during linting: {e}")

    print()


def main():
    """Run all examples."""
    print("Nesting Depth Linter - Usage Examples")
    print("=" * 50)
    print()

    example_high_level_api()
    example_direct_nesting_lint()
    example_custom_configuration()
    example_process_multiple_files()
    example_with_error_handling()

    print("=" * 50)
    print("Examples complete!")
    print("\nFor more examples, see:")
    print("  - docs/nesting-linter.md (comprehensive guide)")
    print("  - docs/api-reference.md (API documentation)")


if __name__ == "__main__":
    main()
