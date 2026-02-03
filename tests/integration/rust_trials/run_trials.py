"""
Purpose: Main trial runner for validating Rust linters against popular repositories

Scope: Clone repositories, execute linters, capture JSON results, print summary

Overview: Standalone script that validates Rust linter accuracy by running all Rust-aware
    linter rules against popular, well-maintained Rust repositories. Clones each repository
    at a pinned release tag for reproducibility, counts Rust source files, executes each
    linter via subprocess capturing JSON output, and writes structured result files to the
    external SSD. Prints a summary table of violation counts per repo/rule combination.
    Designed to run outside the normal pytest test suite due to network and time requirements.

Dependencies: subprocess for CLI invocation, json for result parsing, argparse for CLI,
    config module for repository/rule/path constants

Exports: main() entry point, clone_repo(), count_rs_files(), run_single_linter(),
    write_result(), print_summary()

Interfaces: CLI with --repo-dir, --repos, --rules, --output-dir arguments

Implementation: Subprocess-based linter invocation using python -m src.cli for accurate
    CLI interface testing. Small decomposed functions for Xenon A-grade compliance.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from tests.integration.rust_trials.config import (
    DEFAULT_REPO_DIR,
    DEFAULT_RESULTS_DIR,
    REPOS,
    RULES,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the trial runner."""
    parser = argparse.ArgumentParser(
        description="Run Rust linters against popular repositories to validate accuracy"
    )
    parser.add_argument(
        "--repo-dir",
        type=Path,
        default=DEFAULT_REPO_DIR,
        help="Directory to clone repositories into",
    )
    parser.add_argument(
        "--repos",
        type=str,
        default=None,
        help="Comma-separated subset of repo names to test",
    )
    parser.add_argument(
        "--rules",
        type=str,
        default=None,
        help="Comma-separated subset of rule names to run",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory to write result JSON files",
    )
    return parser.parse_args()


def get_selected_repos(repo_filter: str | None) -> list[dict[str, str]]:
    """Filter repositories based on comma-separated name list."""
    if repo_filter is None:
        return list(REPOS)
    selected_names = {name.strip() for name in repo_filter.split(",")}
    return [repo for repo in REPOS if repo["name"] in selected_names]


def get_selected_rules(rule_filter: str | None) -> list[str]:
    """Filter rules based on comma-separated name list."""
    if rule_filter is None:
        return list(RULES)
    return [rule.strip() for rule in rule_filter.split(",")]


def clone_repo(repo: dict[str, str], repo_dir: Path) -> Path:
    """Clone a repository at its pinned tag if not already present.

    Args:
        repo: Repository definition with name, url, and tag fields
        repo_dir: Parent directory for cloned repositories

    Returns:
        Path to the cloned repository directory
    """
    repo_path = repo_dir / repo["name"]
    if repo_path.exists():
        print(f"  Using cached: {repo_path}")
        return repo_path

    print(f"  Cloning {repo['url']} @ {repo['tag']}...")
    clone_result = subprocess.run(
        [
            "git",
            "clone",
            "--depth=1",
            "--branch",
            repo["tag"],
            repo["url"],
            str(repo_path),
        ],
        capture_output=True,
        text=True,
    )
    if clone_result.returncode != 0:
        print(f"  ERROR: Clone failed: {clone_result.stderr.strip()}")
        msg = f"Failed to clone {repo['name']}: {clone_result.stderr.strip()}"
        raise RuntimeError(msg)
    return repo_path


def count_rs_files(repo_path: Path) -> int:
    """Count .rs files in a repository, excluding the target directory."""
    count = 0
    for rs_file in repo_path.rglob("*.rs"):
        if "target" not in rs_file.parts:
            count += 1
    return count


def run_single_linter(rule: str, repo_path: Path) -> dict[str, Any]:
    """Run a single linter rule against a repository and return parsed JSON output.

    Args:
        rule: Linter rule name (e.g., "unwrap-abuse")
        repo_path: Path to the cloned repository

    Returns:
        Parsed JSON output dict with violations list and total count
    """
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            rule,
            "--format",
            "json",
            str(repo_path),
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[3]),
        timeout=300,
    )
    return _parse_linter_output(result.stdout)


def _parse_linter_output(stdout: str) -> dict[str, Any]:
    """Parse JSON output from linter subprocess, handling empty or invalid output."""
    if not stdout.strip():
        return {"violations": [], "total": 0}
    try:
        return dict(json.loads(stdout))
    except json.JSONDecodeError:
        return {"violations": [], "total": 0}


def build_trial_result(
    repo: dict[str, str], rule: str, rs_file_count: int, linter_output: dict[str, Any]
) -> dict[str, Any]:
    """Build a structured trial result dict from linter output.

    Args:
        repo: Repository definition
        rule: Linter rule name
        rs_file_count: Number of .rs files in the repository
        linter_output: Parsed JSON from the linter

    Returns:
        Structured trial result with metadata and classified violation placeholders
    """
    violations = linter_output.get("violations", [])
    classified = _add_classification_field(violations)
    return {
        "repo": repo["name"],
        "rule": rule,
        "tag": repo["tag"],
        "total_rs_files": rs_file_count,
        "total_violations": len(classified),
        "violations": classified,
    }


def _add_classification_field(violations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add null classification field to each violation for later manual review."""
    for violation in violations:
        violation["classification"] = None
    return violations


def write_result(result: dict[str, Any], output_dir: Path) -> Path:
    """Write a trial result to a JSON file on the SSD.

    Args:
        result: Structured trial result dict
        output_dir: Directory to write the result file

    Returns:
        Path to the written result file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{result['repo']}-{result['rule']}.json"
    output_path = output_dir / filename
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return output_path


def print_summary(results: list[dict[str, Any]]) -> None:
    """Print a summary table of trial results to stdout."""
    print("\n" + "=" * 70)
    print("VALIDATION TRIAL SUMMARY")
    print("=" * 70)
    print(f"{'Repo':<15} {'Rule':<20} {'Files':<8} {'Violations':<12}")
    print("-" * 70)
    for result in results:
        print(
            f"{result['repo']:<15} "
            f"{result['rule']:<20} "
            f"{result['total_rs_files']:<8} "
            f"{result['total_violations']:<12}"
        )
    print("-" * 70)
    total_violations = sum(r["total_violations"] for r in results)
    print(f"{'TOTAL':<35} {'':<8} {total_violations:<12}")
    print("=" * 70)


def run_trial_for_repo(
    repo: dict[str, str], rules: list[str], repo_dir: Path, output_dir: Path
) -> list[dict[str, Any]]:
    """Run all selected rules against a single repository.

    Args:
        repo: Repository definition
        rules: List of rule names to run
        repo_dir: Directory containing cloned repos
        output_dir: Directory to write results

    Returns:
        List of trial result dicts for this repository
    """
    print(f"\n[{repo['name']}] {repo['description']}")
    repo_path = clone_repo(repo, repo_dir)
    rs_count = count_rs_files(repo_path)
    print(f"  Found {rs_count} .rs files")

    results: list[dict[str, Any]] = []
    for rule in rules:
        print(f"  Running {rule}...", end=" ", flush=True)
        linter_output = _run_linter_safely(rule, repo_path)
        result = build_trial_result(repo, rule, rs_count, linter_output)
        write_result(result, output_dir)
        print(f"{result['total_violations']} violations")
        results.append(result)
    return results


def _run_linter_safely(rule: str, repo_path: Path) -> dict[str, Any]:
    """Run a linter with timeout and error handling."""
    try:
        return run_single_linter(rule, repo_path)
    except subprocess.TimeoutExpired:
        print("TIMEOUT", end=" ")
        return {"violations": [], "total": 0}


def main() -> None:
    """Entry point for the trial runner."""
    args = parse_args()
    repos = get_selected_repos(args.repos)
    rules = get_selected_rules(args.rules)

    print(f"Running validation trials: {len(repos)} repos x {len(rules)} rules")
    print(f"Repo directory: {args.repo_dir}")
    print(f"Output directory: {args.output_dir}")

    args.repo_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    all_results: list[dict[str, Any]] = []
    for repo in repos:
        try:
            repo_results = run_trial_for_repo(repo, rules, args.repo_dir, args.output_dir)
            all_results.extend(repo_results)
        except RuntimeError as e:
            print(f"  Skipping {repo['name']}: {e}")

    print_summary(all_results)


if __name__ == "__main__":
    main()
