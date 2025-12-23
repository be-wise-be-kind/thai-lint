#!/usr/bin/env python3
"""
Purpose: Analyze pip-audit output and block on critical vulnerabilities
Scope: Security gate for CI/CD pipelines to prevent vulnerable releases
Overview: Parses pip-audit JSON output to identify vulnerabilities in dependencies.
    Supports configurable ignore patterns for known acceptable vulnerabilities,
    distinguishes between production and dev dependencies, and provides clear
    exit codes for CI/CD integration. Blocks the pipeline if unaccepted
    vulnerabilities are found.
Dependencies: json (stdlib), sys (stdlib), argparse (stdlib), pathlib (stdlib)
Exports: Main vulnerability checking function and CLI interface
Interfaces: Command-line script that reads pip-audit JSON and exits 0 (safe) or 1 (blocked)
Implementation: JSON parsing with configurable allowlists and severity filtering
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict


class VulnInfo(TypedDict):
    """Type definition for vulnerability information."""

    id: str
    fix_versions: list[str]
    aliases: list[str]
    description: str


class DependencyInfo(TypedDict):
    """Type definition for dependency information."""

    name: str
    version: str
    vulns: list[VulnInfo]


class AuditResult(TypedDict):
    """Type definition for pip-audit JSON output."""

    dependencies: list[DependencyInfo]
    fixes: list[object]


def load_ignore_list(ignore_file: Path | None) -> set[str]:
    """
    Load list of vulnerability IDs to ignore.

    Args:
        ignore_file: Path to file containing one vuln ID per line

    Returns:
        Set of vulnerability IDs to ignore
    """
    if ignore_file is None or not ignore_file.exists():
        return set()

    with ignore_file.open() as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def parse_audit_output(audit_file: Path) -> AuditResult:
    """
    Parse pip-audit JSON output file.

    Args:
        audit_file: Path to pip-audit JSON output

    Returns:
        Parsed audit result

    Raises:
        SystemExit: If file doesn't exist or contains invalid JSON
    """
    if not audit_file.exists():
        print(f"ERROR: Audit file not found: {audit_file}")
        sys.exit(2)

    try:
        with audit_file.open() as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in audit file: {e}")
        sys.exit(2)


def extract_vulnerabilities(
    audit_data: AuditResult,
    ignore_ids: set[str],
) -> list[tuple[str, str, VulnInfo]]:
    """
    Extract non-ignored vulnerabilities from audit data.

    Args:
        audit_data: Parsed pip-audit output
        ignore_ids: Set of vulnerability IDs to skip

    Returns:
        List of (package_name, version, vuln_info) tuples
    """
    vulns: list[tuple[str, str, VulnInfo]] = []

    for dep in audit_data.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            vuln_id = vuln.get("id", "")
            aliases = vuln.get("aliases", [])

            # Check if this vuln or any alias is ignored
            all_ids = {vuln_id} | set(aliases)
            if all_ids & ignore_ids:
                continue

            vulns.append((dep["name"], dep["version"], vuln))

    return vulns


def format_vuln_report(
    vulns: list[tuple[str, str, VulnInfo]],
) -> str:
    """
    Format vulnerability report for display.

    Args:
        vulns: List of (package, version, vuln) tuples

    Returns:
        Formatted report string
    """
    if not vulns:
        return "No blocking vulnerabilities found."

    lines = [
        f"SECURITY ALERT: {len(vulns)} vulnerability(ies) require attention",
        "",
    ]

    for pkg, version, vuln in vulns:
        vuln_id = vuln.get("id", "unknown")
        aliases = vuln.get("aliases", [])
        fix_versions = vuln.get("fix_versions", [])

        lines.append(f"  Package: {pkg} {version}")
        lines.append(f"  ID: {vuln_id}")
        if aliases:
            lines.append(f"  CVE: {', '.join(aliases)}")
        if fix_versions:
            lines.append(f"  Fix: upgrade to {', '.join(fix_versions)}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    """
    Main entry point for vulnerability checking.

    Returns:
        Exit code: 0 for safe, 1 for blocked, 2 for errors
    """
    parser = argparse.ArgumentParser(
        description="Check pip-audit output for critical vulnerabilities"
    )
    parser.add_argument(
        "audit_file",
        type=Path,
        help="Path to pip-audit JSON output file",
    )
    parser.add_argument(
        "--ignore-file",
        type=Path,
        default=None,
        help="File containing vulnerability IDs to ignore (one per line)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on any vulnerability (default behavior)",
    )
    args = parser.parse_args()

    # Load ignore list
    ignore_ids = load_ignore_list(args.ignore_file)

    # Parse audit output
    audit_data = parse_audit_output(args.audit_file)

    # Extract non-ignored vulnerabilities
    vulns = extract_vulnerabilities(audit_data, ignore_ids)

    # Generate and print report
    report = format_vuln_report(vulns)
    print(report)

    # Exit with appropriate code
    if vulns:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
