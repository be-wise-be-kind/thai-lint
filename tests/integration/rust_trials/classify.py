"""
Purpose: Interactive classification helper for Rust linter validation trial results

Scope: Read trial result JSON files and prompt for violation classification

Overview: Reads a trial result JSON file produced by run_trials.py and interactively
    prompts the reviewer to classify each violation as a true positive, false positive,
    or intentional pattern. Updates the classification field in each violation and writes
    the classified result back to the same file. Supports resuming partially classified
    files by skipping violations that already have a classification. Provides context
    for each violation including file path, line number, rule ID, and message.

Dependencies: json for file I/O, argparse for CLI

Exports: main() entry point, classify_file(), classify_violation(), load_result(),
    save_result()

Interfaces: CLI with positional result_file argument

Implementation: Interactive stdin prompts with input validation and resume support
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_CLASSIFICATIONS = ("true_positive", "false_positive", "intentional")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactively classify violations in a trial result file"
    )
    parser.add_argument(
        "result_file",
        type=Path,
        help="Path to a trial result JSON file",
    )
    return parser.parse_args()


def load_result(result_path: Path) -> dict[str, Any]:
    """Load a trial result JSON file.

    Args:
        result_path: Path to the JSON result file

    Returns:
        Parsed result dict
    """
    with result_path.open("r", encoding="utf-8") as f:
        return dict(json.load(f))


def save_result(result: dict[str, Any], result_path: Path) -> None:
    """Save a classified trial result back to its JSON file.

    Args:
        result: The result dict with updated classifications
        result_path: Path to write the JSON file
    """
    with result_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


def print_violation_context(violation: dict[str, Any], index: int, total: int) -> None:
    """Print violation details for the reviewer.

    Args:
        violation: Violation dict with rule_id, file_path, line, message fields
        index: 1-based index of the violation
        total: Total number of violations
    """
    print(f"\n--- Violation {index}/{total} ---")
    print(f"  Rule:    {violation.get('rule_id', 'unknown')}")
    print(f"  File:    {violation.get('file_path', 'unknown')}")
    print(f"  Line:    {violation.get('line', '?')}")
    print(f"  Message: {violation.get('message', 'no message')}")


def prompt_classification() -> str:
    """Prompt the reviewer for a classification and validate input.

    Returns:
        One of: true_positive, false_positive, intentional
    """
    print("\nClassify as:")
    print("  [t] true_positive  - Legitimate issue, rule is correct")
    print("  [f] false_positive - Idiomatic code incorrectly flagged")
    print("  [i] intentional    - Valid pattern, acceptable in context")
    print("  [s] skip           - Skip this violation for now")

    shortcut_map = {"t": "true_positive", "f": "false_positive", "i": "intentional"}

    while True:
        choice = input("\n> ").strip().lower()
        if choice == "s":
            return ""
        if choice in shortcut_map:
            return shortcut_map[choice]
        if choice in VALID_CLASSIFICATIONS:
            return choice
        print(f"Invalid choice: '{choice}'. Use t/f/i/s or full name.")


def classify_violation(violation: dict[str, Any], index: int, total: int) -> bool:
    """Classify a single violation interactively.

    Args:
        violation: Violation dict to classify (modified in place)
        index: 1-based index of the violation
        total: Total number of violations

    Returns:
        True if classified, False if skipped
    """
    print_violation_context(violation, index, total)
    classification = prompt_classification()
    if classification:
        violation["classification"] = classification
        return True
    return False


def classify_file(result: dict[str, Any]) -> int:
    """Classify all unclassified violations in a result dict.

    Args:
        result: Trial result dict with violations list

    Returns:
        Number of violations classified in this session
    """
    violations = result.get("violations", [])
    unclassified = [v for v in violations if v.get("classification") is None]

    if not unclassified:
        print("All violations already classified.")
        return 0

    total = len(violations)
    classified_count = 0
    print(f"\n{len(unclassified)} unclassified violations (of {total} total)")

    for violation in violations:
        if violation.get("classification") is not None:
            continue
        index = violations.index(violation) + 1
        if classify_violation(violation, index, total):
            classified_count += 1

    return classified_count


def main() -> None:
    """Entry point for the classification helper."""
    args = parse_args()

    if not args.result_file.exists():
        print(f"Error: File not found: {args.result_file}", file=sys.stderr)
        sys.exit(1)

    result = load_result(args.result_file)
    print(f"Repo: {result.get('repo', '?')} | Rule: {result.get('rule', '?')}")
    print(f"Total violations: {result.get('total_violations', 0)}")

    classified = classify_file(result)
    save_result(result, args.result_file)
    print(f"\nClassified {classified} violations. Saved to {args.result_file}")


if __name__ == "__main__":
    main()
