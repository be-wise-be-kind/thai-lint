"""
Purpose: Generate markdown validation report from classified trial results

Scope: Read classified result JSON files and produce docs/rust-trials-report.md

Overview: Reads all classified trial result JSON files from the results directory on the
    external SSD and generates a comprehensive markdown report documenting the validation
    trial outcomes. Produces a summary table with per-rule false positive rates, per-repository
    breakdowns, lists of true positives (proof of value) and false positives (issues to fix),
    and an overall pass/fail assessment based on the 5% false positive threshold. The generated
    report is written to docs/rust-trials-report.md for inclusion in the project repository.

Dependencies: json for result file parsing, argparse for CLI, config module for paths and thresholds

Exports: main() entry point, load_all_results(), build_rule_summary(), build_repo_summary(),
    generate_markdown()

Interfaces: CLI with --results-dir and --output arguments

Implementation: Aggregation of per-file results into rule-level and repo-level summaries,
    markdown table generation with pass/fail status indicators
"""

import argparse
import json
from pathlib import Path
from typing import Any

from tests.integration.rust_trials.config import (
    DEFAULT_RESULTS_DIR,
    FP_THRESHOLD,
)

DEFAULT_OUTPUT = Path(__file__).resolve().parents[3] / "docs" / "rust-trials-report.md"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate markdown report from classified trial results"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory containing classified result JSON files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output markdown file path",
    )
    return parser.parse_args()


def load_all_results(results_dir: Path) -> list[dict[str, Any]]:
    """Load all JSON result files from the results directory.

    Args:
        results_dir: Path to directory containing result JSON files

    Returns:
        List of parsed result dicts sorted by repo then rule
    """
    results: list[dict[str, Any]] = []
    for json_file in sorted(results_dir.glob("*.json")):
        with json_file.open("r", encoding="utf-8") as f:
            results.append(dict(json.load(f)))
    return results


def count_by_classification(violations: list[dict[str, Any]], classification: str) -> int:
    """Count violations matching a specific classification.

    Args:
        violations: List of violation dicts with classification field
        classification: Classification value to count

    Returns:
        Number of violations matching the classification
    """
    return sum(1 for v in violations if v.get("classification") == classification)


def build_rule_summary(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build per-rule summary with false positive rates.

    Args:
        results: All trial results

    Returns:
        List of rule summary dicts with totals and FP rates
    """
    rule_map: dict[str, dict[str, Any]] = {}
    for result in results:
        rule = result["rule"]
        if rule not in rule_map:
            rule_map[rule] = {"rule": rule, "total": 0, "tp": 0, "fp": 0, "unclassified": 0}
        violations = result.get("violations", [])
        rule_map[rule]["total"] += len(violations)
        rule_map[rule]["tp"] += count_by_classification(violations, "true_positive")
        rule_map[rule]["fp"] += count_by_classification(violations, "false_positive")
        rule_map[rule]["unclassified"] += sum(
            1 for v in violations if v.get("classification") is None
        )
    return _compute_fp_rates(list(rule_map.values()))


def _compute_fp_rates(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute false positive rates and pass/fail status for each summary."""
    for summary in summaries:
        total = summary["total"]
        summary["fp_rate"] = summary["fp"] / total if total > 0 else 0.0
        summary["status"] = "PASS" if summary["fp_rate"] <= FP_THRESHOLD else "NEEDS TUNING"
    return summaries


def build_repo_summary(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group results by repository for per-repo breakdown.

    Args:
        results: All trial results

    Returns:
        Dict mapping repo name to list of rule results for that repo
    """
    repo_map: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        repo_name = result["repo"]
        if repo_name not in repo_map:
            repo_map[repo_name] = []
        repo_map[repo_name].append(result)
    return repo_map


def collect_violations_by_type(
    results: list[dict[str, Any]], classification: str
) -> list[dict[str, Any]]:
    """Collect all violations of a specific classification across all results.

    Args:
        results: All trial results
        classification: Classification value to collect

    Returns:
        List of violation dicts with added repo and rule context
    """
    collected: list[dict[str, Any]] = []
    for result in results:
        for violation in result.get("violations", []):
            if violation.get("classification") == classification:
                enriched = dict(violation)
                enriched["_repo"] = result["repo"]
                enriched["_rule"] = result["rule"]
                collected.append(enriched)
    return collected


def _format_summary_table(rule_summaries: list[dict[str, Any]]) -> str:
    """Format the rule summary as a markdown table."""
    lines = [
        "| Rule | Total | True Positives | False Positives | FP Rate | Status |",
        "|------|-------|---------------|-----------------|---------|--------|",
    ]
    for summary in rule_summaries:
        fp_pct = f"{summary['fp_rate']:.1%}"
        lines.append(
            f"| {summary['rule']} "
            f"| {summary['total']} "
            f"| {summary['tp']} "
            f"| {summary['fp']} "
            f"| {fp_pct} "
            f"| {summary['status']} |"
        )
    return "\n".join(lines)


def _format_repo_section(repo_name: str, repo_results: list[dict[str, Any]]) -> str:
    """Format a single repository's results as a markdown section."""
    lines = []
    tag = repo_results[0]["tag"] if repo_results else "unknown"
    rs_files = repo_results[0].get("total_rs_files", "?") if repo_results else "?"
    lines.append(f"### {repo_name} (@ {tag})")
    lines.append(f"- Total .rs files: {rs_files}")
    for result in repo_results:
        lines.append(f"- {result['rule']}: {result['total_violations']} violations")
    lines.append("")
    return "\n".join(lines)


def _format_violations_section(title: str, violations: list[dict[str, Any]]) -> str:
    """Format a list of classified violations as a markdown section."""
    lines = [f"## {title}", ""]
    if not violations:
        lines.append("None found.")
        lines.append("")
        return "\n".join(lines)
    for violation in violations:
        file_path = violation.get("file_path", "unknown")
        line = violation.get("line", "?")
        message = violation.get("message", "no message")
        rule = violation.get("_rule", "unknown")
        lines.append(f"- **{rule}**: `{file_path}:{line}` - {message}")
    lines.append("")
    return "\n".join(lines)


def generate_markdown(results: list[dict[str, Any]]) -> str:
    """Generate the full markdown report from trial results.

    Args:
        results: All trial results (classified)

    Returns:
        Complete markdown report string
    """
    rule_summaries = build_rule_summary(results)
    repo_groups = build_repo_summary(results)
    true_positives = collect_violations_by_type(results, "true_positive")
    false_positives = collect_violations_by_type(results, "false_positive")

    sections = [
        _build_header(),
        _format_summary_table(rule_summaries),
        "",
        "## Per-Repository Results",
        "",
    ]
    for repo_name, repo_results in repo_groups.items():
        sections.append(_format_repo_section(repo_name, repo_results))
    sections.append(_format_violations_section("True Positives (Proof of Value)", true_positives))
    sections.append(
        _format_violations_section("False Positives (Issues to Address)", false_positives)
    )
    return "\n".join(sections)


def _build_header() -> str:
    """Build the report header section."""
    return (
        "# Rust Linter Validation Trials Report\n\n"
        "Validation results from running all Rust linters against popular,\n"
        "well-maintained Rust repositories. Target: < 5% false positive rate per rule.\n\n"
        "## Summary\n\n"
    )


def main() -> None:
    """Entry point for the report generator."""
    args = parse_args()

    if not args.results_dir.exists():
        print(f"Error: Results directory not found: {args.results_dir}")
        return

    results = load_all_results(args.results_dir)
    if not results:
        print("No result files found.")
        return

    report = generate_markdown(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
