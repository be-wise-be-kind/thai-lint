#!/usr/bin/env python3
"""
Purpose: CI/CD integration example demonstrating automated linting in pipelines

Scope: Continuous integration and automated quality checks

Overview: Demonstrates integration of thailint into CI/CD pipelines with proper exit codes,
    violation reporting, and error handling. Shows how to use the library API in GitHub Actions,
    GitLab CI, Jenkins, and other automation systems. Provides patterns for failing builds on
    violations, generating reports, and integrating with code review tools.

Dependencies: src.Linter for linting operations, sys for exit codes

Exports: Example script for CI/CD documentation

Interfaces: Command-line CI/CD integration script with exit codes

Implementation: CI-friendly patterns with exit codes, JSON output, and error handling
"""

import json
import sys
from pathlib import Path

from src import Linter


def lint_for_ci(target_path: str, config_file: str | None = None) -> int:
    """Lint code for CI/CD pipeline with proper exit codes.

    Args:
        target_path: Path to lint (file or directory)
        config_file: Optional config file path

    Returns:
        Exit code: 0 for success, 1 for violations found, 2 for errors
    """
    try:
        # Initialize linter
        if config_file:
            linter = Linter(config_file=config_file)
        else:
            linter = Linter()

        # Run linting
        violations = linter.lint(target_path)

        # Report results
        if violations:
            print(f"❌ Found {len(violations)} violations")

            # JSON output for CI tools
            violations_data = [
                {
                    "file": str(v.file_path),
                    "rule": v.rule_id,
                    "message": v.message,
                    "severity": v.severity.name,
                    "line": v.line_number if hasattr(v, "line_number") else None,
                }
                for v in violations
            ]

            # Write JSON report
            report_file = Path("lint-report.json")
            report_file.write_text(json.dumps(violations_data, indent=2))
            print(f"Report written to {report_file}")

            # Print human-readable output
            for v in violations:
                print(f"  {v.file_path}:{v.rule_id} - {v.message}")

            return 1  # Exit code 1 for violations

        print("✅ No violations found")
        return 0  # Success

    except Exception as e:
        print(f"❌ Error during linting: {e}", file=sys.stderr)
        return 2  # Exit code 2 for errors


def main():
    """Run CI linting."""
    import argparse

    parser = argparse.ArgumentParser(description="Lint code for CI/CD")
    parser.add_argument("path", help="Path to lint")
    parser.add_argument("--config", help="Config file path", default=None)

    args = parser.parse_args()

    exit_code = lint_for_ci(args.path, args.config)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
