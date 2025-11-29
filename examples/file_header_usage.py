#!/usr/bin/env python3
"""
Purpose: File header linter usage examples

Scope: Demonstrates CLI and library usage for file header validation

Overview: Shows multiple ways to use the file header linter including high-level Linter API,
    direct file_header lint convenience function, and custom configuration. Helps users
    understand different usage patterns for integrating file header checks into their workflows,
    editors, or automation scripts. Includes examples for both single files and directories with
    custom mandatory fields and language-specific configurations.

Dependencies: src.Linter, src.linters.file_header.lint for file header validation

Exports: Example script for documentation

Interfaces: Command-line example script

Implementation: Multiple usage patterns demonstrating flexibility of the API
"""

from pathlib import Path

from src import Linter
from src.linters.file_header import lint as file_header_lint


def example_high_level_api():
    """Example 1: High-level Linter API with config file."""
    print("=== Example 1: High-level API ===\n")

    # Initialize linter with config file
    linter = Linter(config_file='.thailint.yaml')

    # Lint directory with file-header rule
    violations = linter.lint('src/', rules=['file-header'])

    # Process violations
    if violations:
        print(f"Found {len(violations)} file header violations:\n")
        for v in violations[:5]:  # Show first 5
            print(f"  {v.file_path}:{v.line_number or '?'}")
            print(f"  {v.message}\n")
        if len(violations) > 5:
            print(f"  ... and {len(violations) - 5} more violations\n")
    else:
        print("No file header violations found!\n")


def example_direct_file_header_lint():
    """Example 2: Direct file_header_lint function."""
    print("=== Example 2: Direct file_header_lint() ===\n")

    # Lint specific file with default config
    violations = file_header_lint('src/cli.py')

    if violations:
        print(f"Found {len(violations)} violations in src/cli.py:\n")
        for v in violations:
            print(f"  Line {v.line_number or '?'}: {v.message}\n")
    else:
        print("src/cli.py passes file header check\n")


def example_custom_configuration():
    """Example 3: Custom configuration without config file."""
    print("=== Example 3: Custom Configuration ===\n")

    # Lint with custom mandatory fields
    violations = file_header_lint(
        'src/linters/',
        config={
            'mandatory_fields': ['Purpose', 'Scope', 'Overview'],
            'recommended_fields': ['Dependencies', 'Exports'],
            'check_atemporal': True
        }
    )

    print("Checking src/linters/ with custom config:")
    print("  Mandatory fields: [Purpose, Scope, Overview]")
    print("  Recommended fields: [Dependencies, Exports]")
    print(f"  Violations: {len(violations)}\n")


def example_strict_configuration():
    """Example 4: Strict configuration (all fields mandatory)."""
    print("=== Example 4: Strict Configuration ===\n")

    # Strict mode - all fields mandatory
    violations = file_header_lint(
        'src/config.py',
        config={
            'mandatory_fields': [
                'Purpose', 'Scope', 'Overview',
                'Dependencies', 'Exports', 'Interfaces', 'Implementation'
            ],
            'check_atemporal': True
        }
    )

    print("Strict mode: All fields mandatory")
    if violations:
        print(f"  Found {len(violations)} violations (more strict)\n")
        for v in violations[:3]:  # Show first 3
            print(f"    {v.message}")
    else:
        print("  No violations\n")


def example_process_multiple_files():
    """Example 5: Process multiple files."""
    print("=== Example 5: Multiple Files ===\n")

    files_to_check = [
        'src/cli.py',
        'src/config.py',
        'src/api.py',
    ]

    all_violations = []
    for file_path in files_to_check:
        if Path(file_path).exists():
            violations = file_header_lint(file_path)
            all_violations.extend(violations)
            status = "OK" if not violations else "FAIL"
            print(f"  {status} {file_path}: {len(violations)} violations")

    print(f"\nTotal violations: {len(all_violations)}\n")


def example_with_error_handling():
    """Example 6: Robust error handling."""
    print("=== Example 6: Error Handling ===\n")

    try:
        # Attempt to lint non-existent file
        violations = file_header_lint('nonexistent.py')
        print(f"Violations: {len(violations)}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"Error during linting: {e}")

    print()


def example_check_header_format():
    """Example 7: Checking header format compliance."""
    print("=== Example 7: Header Format Check ===\n")

    # Create temporary file with incomplete header
    test_file = Path('/tmp/test_header.py')
    test_file.write_text('''"""
Purpose: Test module for demonstration
"""
import os

def main():
    pass
''')

    violations = file_header_lint(str(test_file))

    print("Checking file with incomplete header:")
    if violations:
        print(f"  Found {len(violations)} violations:")
        for v in violations:
            print(f"    {v.message}")
    else:
        print("  Header format is valid")

    print()


def example_atemporal_language_detection():
    """Example 8: Detecting atemporal language violations."""
    print("=== Example 8: Atemporal Language Detection ===\n")

    # Create test file with temporal language
    test_file = Path('/tmp/test_atemporal.py')
    test_file.write_text('''"""
Purpose: Test module for temporal language detection

Scope: Demonstration of atemporal language rules

Overview: This module was recently updated to support new features.
    Currently handles authentication. Created: 2024-01-15.
    Will be extended in the future.

Dependencies: None

Exports: None
"""

def main():
    pass
''')

    violations = file_header_lint(str(test_file))

    print("File with temporal language:")
    print("  - 'recently updated'")
    print("  - 'Currently handles'")
    print("  - 'Created: 2024-01-15'")
    print("  - 'Will be extended'")
    print(f"\n  Violations detected: {len(violations)}")
    for v in violations:
        print(f"    {v.message}")

    print()


def example_typescript_header_check():
    """Example 9: Checking TypeScript file headers."""
    print("=== Example 9: TypeScript Header Check ===\n")

    # Create test TypeScript file
    test_file = Path('/tmp/test_header.ts')
    test_file.write_text('''/**
 * Purpose: User authentication component
 *
 * Scope: Authentication UI, login form
 *
 * Overview: Renders login form with email and password fields.
 *     Handles validation and submission to auth API.
 *
 * Dependencies: React, react-hook-form
 *
 * Exports: LoginForm component
 */
import React from 'react';

export const LoginForm = () => {
    return <form>Login</form>;
};
''')

    violations = file_header_lint(str(test_file))

    print("Checking TypeScript file with JSDoc header:")
    if violations:
        print(f"  Found {len(violations)} violations:")
        for v in violations:
            print(f"    {v.message}")
    else:
        print("  TypeScript header is valid")

    print()


def example_bash_header_check():
    """Example 10: Checking Bash script headers."""
    print("=== Example 10: Bash Script Header Check ===\n")

    # Create test Bash script
    test_file = Path('/tmp/test_script.sh')
    test_file.write_text('''#!/bin/bash
# Purpose: Database backup script
#
# Scope: Database operations, scheduled tasks
#
# Overview: Creates compressed database backups and uploads to S3.
#     Implements rotation policy keeping last 30 backups.
#
# Dependencies: pg_dump, aws-cli, gzip
#
# Exports: Creates backup files in /backups directory

set -euo pipefail

pg_dump mydb > backup.sql
''')

    violations = file_header_lint(str(test_file))

    print("Checking Bash script with comment header:")
    if violations:
        print(f"  Found {len(violations)} violations:")
        for v in violations:
            print(f"    {v.message}")
    else:
        print("  Bash header is valid")

    print()


def main():
    """Run all examples."""
    print("File Header Linter - Usage Examples")
    print("=" * 50)
    print()

    example_high_level_api()
    example_direct_file_header_lint()
    example_custom_configuration()
    example_strict_configuration()
    example_process_multiple_files()
    example_with_error_handling()
    example_check_header_format()
    example_atemporal_language_detection()
    example_typescript_header_check()
    example_bash_header_check()

    print("=" * 50)
    print("Examples complete!")
    print("\nFor more examples, see:")
    print("  - docs/file-header-linter.md (comprehensive guide)")
    print("  - docs/how-to-ignore-violations.md (ignore patterns)")
    print("  - docs/ai-doc-standard.md (AI-optimized header format)")


if __name__ == "__main__":
    main()
