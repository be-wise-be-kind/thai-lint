#!/usr/bin/env python3
"""
Purpose: SARIF output format usage examples demonstrating CLI and Python API integration

Scope: SARIF generation, validation, file output, and CI/CD integration patterns

Overview: Demonstrates various methods for generating SARIF (Static Analysis Results Interchange
    Format) v2.1.0 output from thailint. Shows both CLI subprocess invocation and direct Python
    API usage with the SarifFormatter class. Includes examples for single linter analysis,
    combined multi-linter output, custom tool metadata, file saving, and CI/CD integration
    patterns with exit code handling.

Dependencies: src.api (Linter), src.formatters.sarif (SarifFormatter), json, subprocess, sys

Exports: Example functions for documentation and testing

Interfaces: Command-line example script with multiple demonstration functions

Implementation: Shows CLI subprocess patterns and Python API usage for SARIF generation
"""

import json
import subprocess
import sys
from pathlib import Path


def example_cli_sarif_output() -> None:
    """Demonstrate SARIF output via CLI subprocess.

    This is the simplest way to get SARIF output - just run the CLI
    with --format sarif and capture the output.
    """
    print("=" * 60)
    print("Example 1: CLI SARIF Output")
    print("=" * 60)

    # Run thailint with SARIF output
    result = subprocess.run(
        ["thailint", "nesting", "--format", "sarif", "src/"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("No violations found!")
        sarif = json.loads(result.stdout)
        print(f"SARIF version: {sarif['version']}")
        print(f"Tool: {sarif['runs'][0]['tool']['driver']['name']}")
    elif result.returncode == 1:
        print("Violations found!")
        sarif = json.loads(result.stdout)
        results = sarif["runs"][0]["results"]
        print(f"Found {len(results)} violations")
        for r in results[:3]:  # Show first 3
            print(f"  - {r['ruleId']}: {r['message']['text'][:50]}...")
    else:
        print(f"Error occurred: {result.stderr}")

    print()


def example_save_sarif_to_file() -> None:
    """Demonstrate saving SARIF output to a file.

    Save SARIF output to a file for later processing or
    upload to CI/CD systems.
    """
    print("=" * 60)
    print("Example 2: Save SARIF to File")
    print("=" * 60)

    output_path = Path("/tmp/thailint-results.sarif")

    # Run thailint and save to file
    result = subprocess.run(
        ["thailint", "nesting", "--format", "sarif", "src/"],
        capture_output=True,
        text=True,
    )

    # Always save the output, even if there are violations
    with open(output_path, "w") as f:
        f.write(result.stdout)

    print(f"SARIF saved to: {output_path}")
    print(f"Exit code: {result.returncode}")
    print(f"File size: {output_path.stat().st_size} bytes")

    # Parse and summarize
    sarif = json.loads(output_path.read_text())
    results = sarif["runs"][0]["results"]
    print(f"Total violations: {len(results)}")

    print()


def example_python_api_sarif() -> None:
    """Demonstrate SARIF generation via Python API.

    Use the Linter API and SarifFormatter class directly
    for more control over the analysis process.
    """
    print("=" * 60)
    print("Example 3: Python API SARIF Generation")
    print("=" * 60)

    try:
        from src.api import Linter
        from src.formatters.sarif import SarifFormatter

        # Initialize linter
        linter = Linter()

        # Run nesting analysis
        violations = linter.lint("src/", rules=["nesting"])

        # Create SARIF formatter
        formatter = SarifFormatter()

        # Generate SARIF document
        sarif_doc = formatter.format(violations)

        print(f"SARIF version: {sarif_doc['version']}")
        print(f"Tool name: {sarif_doc['runs'][0]['tool']['driver']['name']}")
        print(f"Tool version: {sarif_doc['runs'][0]['tool']['driver']['version']}")
        print(f"Results count: {len(sarif_doc['runs'][0]['results'])}")

        # Pretty-print first result if any
        results = sarif_doc["runs"][0]["results"]
        if results:
            print("\nFirst violation:")
            print(json.dumps(results[0], indent=2))

    except ImportError as e:
        print(f"Import error (run from project root): {e}")

    print()


def example_custom_tool_metadata() -> None:
    """Demonstrate customizing SARIF tool metadata.

    Customize tool name, version, and information URI
    for integration with custom tooling.
    """
    print("=" * 60)
    print("Example 4: Custom Tool Metadata")
    print("=" * 60)

    try:
        from src.api import Linter
        from src.formatters.sarif import SarifFormatter

        # Initialize with custom metadata
        formatter = SarifFormatter(
            tool_name="my-custom-linter",
            tool_version="2.0.0",
            information_uri="https://example.com/my-linter",
        )

        linter = Linter()
        violations = linter.lint("src/", rules=["nesting"])
        sarif_doc = formatter.format(violations)

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        print(f"Custom tool name: {driver['name']}")
        print(f"Custom version: {driver['version']}")
        print(f"Custom URI: {driver['informationUri']}")

    except ImportError as e:
        print(f"Import error (run from project root): {e}")

    print()


def example_multiple_linters_combined() -> None:
    """Demonstrate combining results from multiple linters.

    Run multiple linter rules and combine all violations
    into a single SARIF document.
    """
    print("=" * 60)
    print("Example 5: Multiple Linters Combined")
    print("=" * 60)

    try:
        from src.api import Linter
        from src.formatters.sarif import SarifFormatter

        linter = Linter()

        # Run multiple analyses
        all_violations = []

        rules_to_run = ["nesting", "srp", "magic-numbers"]
        for rule in rules_to_run:
            try:
                violations = linter.lint("src/", rules=[rule])
                all_violations.extend(violations)
                print(f"  {rule}: {len(violations)} violations")
            except Exception as e:
                print(f"  {rule}: skipped ({e})")

        # Generate combined SARIF
        formatter = SarifFormatter()
        sarif_doc = formatter.format(all_violations)

        print(f"\nTotal violations: {len(all_violations)}")
        print(f"SARIF results: {len(sarif_doc['runs'][0]['results'])}")

        # Show rule distribution
        rules = sarif_doc["runs"][0]["tool"]["driver"]["rules"]
        print(f"Unique rules: {len(rules)}")
        for rule in rules:
            print(f"  - {rule['id']}")

    except ImportError as e:
        print(f"Import error (run from project root): {e}")

    print()


def example_ci_exit_code_handling() -> None:
    """Demonstrate CI/CD exit code handling.

    Proper exit code handling for CI/CD pipelines:
    - Exit 0: No violations
    - Exit 1: Violations found
    - Exit 2: Error occurred
    """
    print("=" * 60)
    print("Example 6: CI/CD Exit Code Handling")
    print("=" * 60)

    result = subprocess.run(
        ["thailint", "nesting", "--format", "sarif", "src/"],
        capture_output=True,
        text=True,
    )

    exit_code = result.returncode
    print(f"Exit code: {exit_code}")

    if exit_code == 0:
        print("Status: SUCCESS - No violations found")
        print("CI/CD Action: Continue pipeline")
    elif exit_code == 1:
        print("Status: VIOLATIONS - Issues detected")
        sarif = json.loads(result.stdout)
        count = len(sarif["runs"][0]["results"])
        print(f"Violation count: {count}")
        print("CI/CD Action: Fail build or create alerts")
    else:
        print("Status: ERROR - Something went wrong")
        print(f"Stderr: {result.stderr}")
        print("CI/CD Action: Fail build, investigate error")

    print()


def example_sarif_validation() -> None:
    """Demonstrate SARIF output validation.

    Validate that SARIF output is well-formed and contains
    required fields for platform integration.
    """
    print("=" * 60)
    print("Example 7: SARIF Validation")
    print("=" * 60)

    result = subprocess.run(
        ["thailint", "nesting", "--format", "sarif", "src/"],
        capture_output=True,
        text=True,
    )

    # Parse JSON
    try:
        sarif = json.loads(result.stdout)
        print("✓ Valid JSON")
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return

    # Check required fields
    checks = [
        ("version", "version" in sarif and sarif["version"] == "2.1.0"),
        ("$schema", "$schema" in sarif),
        ("runs", "runs" in sarif and len(sarif["runs"]) > 0),
        ("tool.driver", "tool" in sarif["runs"][0]),
        ("tool.driver.name", sarif["runs"][0]["tool"]["driver"]["name"] == "thai-lint"),
        ("results", "results" in sarif["runs"][0]),
    ]

    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")

    all_passed = all(passed for _, passed in checks)
    print(f"\nValidation: {'PASSED' if all_passed else 'FAILED'}")

    print()


def main() -> None:
    """Run all SARIF usage examples."""
    print("\n" + "=" * 60)
    print("thailint SARIF Output Usage Examples")
    print("=" * 60 + "\n")

    # CLI examples (always work)
    example_cli_sarif_output()
    example_save_sarif_to_file()
    example_ci_exit_code_handling()
    example_sarif_validation()

    # Python API examples (require imports)
    example_python_api_sarif()
    example_custom_tool_metadata()
    example_multiple_linters_combined()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
