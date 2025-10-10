#!/usr/bin/env python3
"""
Purpose: Magic numbers linter usage examples

Scope: Demonstrates CLI and library usage for magic numbers detection

Overview: Shows multiple ways to use the magic numbers linter including high-level Linter API,
    direct magic_numbers_lint convenience function, and custom configuration. Helps users
    understand different usage patterns for integrating magic number checks into their workflows,
    editors, or automation scripts. Includes examples for both single files and directories with
    custom allowed numbers and thresholds.

Dependencies: src.Linter, src.linters.magic_numbers.lint for magic number detection

Exports: Example script for documentation

Interfaces: Command-line example script

Implementation: Multiple usage patterns demonstrating flexibility of the API
"""

from pathlib import Path

from src import Linter
from src.linters.magic_numbers import lint as magic_numbers_lint


def example_high_level_api():
    """Example 1: High-level Linter API with config file."""
    print("=== Example 1: High-level API ===\n")

    # Initialize linter with config file
    linter = Linter(config_file='.thailint.yaml')

    # Lint directory with magic-numbers rule
    violations = linter.lint('src/', rules=['magic-numbers'])

    # Process violations
    if violations:
        print(f"Found {len(violations)} magic number violations:\n")
        for v in violations:
            print(f"  {v.file_path}:{v.line_number or '?'}")
            print(f"  {v.message}\n")
    else:
        print("✓ No magic number violations found!\n")


def example_direct_magic_numbers_lint():
    """Example 2: Direct magic_numbers_lint function."""
    print("=== Example 2: Direct magic_numbers_lint() ===\n")

    # Lint specific file with default config
    violations = magic_numbers_lint('src/cli.py')

    if violations:
        print(f"Found {len(violations)} violations in src/cli.py:\n")
        for v in violations:
            print(f"  Line {v.line_number or '?'}: {v.message}\n")
    else:
        print("✓ src/cli.py passes magic numbers check\n")


def example_custom_configuration():
    """Example 3: Custom configuration without config file."""
    print("=== Example 3: Custom Configuration ===\n")

    # Lint with custom allowed numbers
    violations = magic_numbers_lint(
        'src/linters/',
        config={
            'allowed_numbers': [0, 1, 2, 60, 3600],  # Include time units
            'max_small_integer': 20  # More lenient for range()
        }
    )

    print(f"Checking src/linters/ with custom config:")
    print(f"  Allowed numbers: [0, 1, 2, 60, 3600]")
    print(f"  Max small integer: 20")
    print(f"  Violations: {len(violations)}\n")


def example_strict_configuration():
    """Example 4: Strict configuration (only very common values)."""
    print("=== Example 4: Strict Configuration ===\n")

    # Very strict - only 0, 1, -1 allowed
    violations = magic_numbers_lint(
        'src/config.py',
        config={
            'allowed_numbers': [-1, 0, 1],
            'max_small_integer': 3
        }
    )

    print("Strict mode: Only -1, 0, 1 allowed, max range() = 3")
    if violations:
        print(f"  Found {len(violations)} violations (more strict)\n")
        for v in violations[:3]:  # Show first 3
            print(f"    {v.message}")
    else:
        print("  ✓ No violations\n")


def example_process_multiple_files():
    """Example 5: Process multiple files."""
    print("=== Example 5: Multiple Files ===\n")

    files_to_check = [
        'src/cli.py',
        'src/config.py',
        'src/orchestrator/core.py',
    ]

    all_violations = []
    for file_path in files_to_check:
        if Path(file_path).exists():
            violations = magic_numbers_lint(file_path)
            all_violations.extend(violations)
            status = "✓" if not violations else "✗"
            print(f"  {status} {file_path}: {len(violations)} violations")

    print(f"\nTotal violations: {len(all_violations)}\n")


def example_with_error_handling():
    """Example 6: Robust error handling."""
    print("=== Example 6: Error Handling ===\n")

    try:
        # Attempt to lint non-existent file
        violations = magic_numbers_lint('nonexistent.py')
        print(f"Violations: {len(violations)}")
    except FileNotFoundError as e:
        print(f"✗ File not found: {e}")
    except Exception as e:
        print(f"✗ Error during linting: {e}")

    print()


def example_detect_constants_file():
    """Example 7: Detecting magic numbers in config/constants."""
    print("=== Example 7: Constants File ===\n")

    # Create temporary constants file
    constants_file = Path('/tmp/test_constants.py')
    constants_file.write_text("""
# Constants file - uppercase names should be OK
MAX_RETRIES = 5
TIMEOUT_SECONDS = 30

# Lowercase - will be flagged
timeout = 60  # This is a magic number
max_users = 100  # This too
""")

    violations = magic_numbers_lint(str(constants_file))

    print(f"Checking constants file:")
    if violations:
        print(f"  Found {len(violations)} violations:")
        for v in violations:
            print(f"    Line {v.line_number}: {v.message}")
    else:
        print("  ✓ All constants properly named")

    print()


def example_acceptable_contexts():
    """Example 8: Demonstrating acceptable contexts."""
    print("=== Example 8: Acceptable Contexts ===\n")

    # Create test file with acceptable numbers
    test_file = Path('/tmp/test_acceptable.py')
    test_file.write_text("""
# Acceptable: Constant definition (UPPERCASE)
MAX_SIZE = 100

# Acceptable: Small integer in range()
for i in range(5):
    pass

# Acceptable: String repetition
print("-" * 40)

# NOT acceptable: Magic number
timeout = 3600
""")

    violations = magic_numbers_lint(str(test_file))

    print("File with mixed acceptable/unacceptable numbers:")
    print(f"  Total numbers: 4 (100, 5, 40, 3600)")
    print(f"  Violations: {len(violations)} (only 3600)")
    print(f"  Acceptable: Constants, small range(), string repetition\n")


def main():
    """Run all examples."""
    print("Magic Numbers Linter - Usage Examples")
    print("=" * 50)
    print()

    example_high_level_api()
    example_direct_magic_numbers_lint()
    example_custom_configuration()
    example_strict_configuration()
    example_process_multiple_files()
    example_with_error_handling()
    example_detect_constants_file()
    example_acceptable_contexts()

    print("=" * 50)
    print("Examples complete!")
    print("\nFor more examples, see:")
    print("  - docs/magic-numbers-linter.md (comprehensive guide)")
    print("  - docs/how-to-ignore-violations.md (ignore patterns)")
    print("  - docs/api-reference.md (API documentation)")


if __name__ == "__main__":
    main()
