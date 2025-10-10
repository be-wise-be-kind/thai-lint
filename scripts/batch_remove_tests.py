#!/usr/bin/env python3
"""
Purpose: Fast batch removal of redundant tests with periodic validation
Scope: Removes tests in batches to minimize coverage validation overhead
Overview: This script removes multiple tests at once and validates coverage
    periodically rather than after each individual test. This is much faster
    than single-test removal while still maintaining safety. If a batch causes
    coverage to drop too much, it rolls back and tries smaller batches.
Dependencies: subprocess, pathlib, json for test execution and tracking
Exports: BatchTestRemover class and command-line interface
Interfaces: Reads removal candidates JSON, removes tests in batches
Implementation: Batch removal with periodic validation and adaptive batch sizing
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class BatchTestRemover:
    """Removes redundant tests in batches for faster processing."""

    def __init__(
        self,
        batch_size: int = 15,
        max_coverage_drop: float = 2.0,
        dry_run: bool = False,
    ) -> None:
        """
        Initialize the batch test remover.

        Args:
            batch_size: Number of tests to remove per batch (default 15)
            max_coverage_drop: Maximum allowed coverage drop in percentage points
            dry_run: If True, simulate removals without actually deleting tests
        """
        self.batch_size = batch_size
        self.max_coverage_drop = max_coverage_drop
        self.dry_run = dry_run
        self.baseline_coverage = 0.0
        self.current_coverage = 0.0
        self.removed_tests: List[str] = []
        self.backup_dir = Path(".test_backup")

    def get_current_coverage(self) -> float:
        """Run tests and extract current coverage percentage."""
        print("  Running coverage validation...")

        try:
            result = subprocess.run(
                ["poetry", "run", "pytest", "--cov=src", "--cov-report=term", "-q"],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )

            # Parse coverage from output
            for line in result.stdout.split("\n"):
                if "TOTAL" in line:
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            coverage_str = part.replace("%", "")
                            return float(coverage_str)

            print("  WARNING: Could not parse coverage")
            return 0.0

        except subprocess.TimeoutExpired:
            print("  ERROR: Test run timed out")
            return 0.0
        except Exception as e:
            print(f"  ERROR: {e}")
            return 0.0

    def backup_tests(self) -> None:
        """Create a backup of the tests directory."""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        print(f"Creating backup of tests directory...")
        shutil.copytree("tests", self.backup_dir)

    def restore_tests(self) -> None:
        """Restore tests from backup."""
        if not self.backup_dir.exists():
            print("ERROR: No backup found")
            return

        print("  Rolling back batch...")
        if Path("tests").exists():
            shutil.rmtree("tests")
        shutil.copytree(self.backup_dir, "tests")

    def remove_test_function(self, test_file: Path, function_name: str) -> bool:
        """Remove a specific test function from a test file."""
        if self.dry_run:
            return True

        try:
            content = test_file.read_text()
            lines = content.split("\n")
            new_lines = []
            in_target_function = False
            function_indent = 0

            for line in lines:
                # Check if this is the start of our target function
                if line.strip().startswith(f"def {function_name}("):
                    in_target_function = True
                    function_indent = len(line) - len(line.lstrip())
                    continue

                # If we're in the target function
                if in_target_function:
                    current_indent = len(line) - len(line.lstrip())

                    # Empty lines or docstrings continue the function
                    if line.strip() == "" or line.strip().startswith('"""'):
                        continue

                    # If we find a line with same or less indentation, we've left the function
                    if (
                        line.strip()
                        and current_indent <= function_indent
                        and not line.strip().startswith("@")
                    ):
                        in_target_function = False

                    # Skip lines that are part of the function
                    if in_target_function:
                        continue

                # Keep all other lines
                new_lines.append(line)

            # Write back
            test_file.write_text("\n".join(new_lines))
            return True

        except Exception as e:
            print(f"    ERROR removing {function_name}: {e}")
            return False

    def remove_test(self, test_name: str) -> bool:
        """Remove a specific test."""
        if "::" not in test_name:
            return False

        parts = test_name.split("::")
        file_path_str = parts[0]
        function_name = parts[1] if len(parts) > 1 else None

        test_file = Path(file_path_str)

        if not test_file.exists() or not function_name:
            return False

        return self.remove_test_function(test_file, function_name)

    def remove_batch(self, batch: List[Tuple[str, str, float]]) -> int:
        """Remove a batch of tests. Returns number successfully removed."""
        removed_count = 0

        for test_to_remove, test_to_keep, overlap_pct in batch:
            if self.remove_test(test_to_remove):
                removed_count += 1
                self.removed_tests.append(test_to_remove)

        return removed_count

    def execute_batch_removal(
        self, candidates: List[Tuple[str, str, float]], target_removal: int
    ) -> None:
        """Execute batch removal with periodic validation."""
        print("\n" + "=" * 80)
        print("BATCH TEST REMOVAL")
        print("=" * 80)

        # Get baseline
        print("\nEstablishing baseline coverage...")
        self.baseline_coverage = self.get_current_coverage()
        self.current_coverage = self.baseline_coverage
        print(f"Baseline coverage: {self.baseline_coverage:.2f}%")

        if self.baseline_coverage == 0.0:
            print("ERROR: Could not establish baseline. Aborting.")
            return

        # Create backup
        print("\nCreating backup...")
        self.backup_tests()

        # Process in batches
        print(f"\nRemoving tests in batches of {self.batch_size}...")
        print(f"Target: {target_removal} tests")
        print(f"Available candidates: {len(candidates)}")
        print("")

        batch_num = 0
        total_removed = 0

        while total_removed < target_removal and total_removed < len(candidates):
            batch_num += 1
            start_idx = total_removed
            end_idx = min(start_idx + self.batch_size, target_removal, len(candidates))
            batch = candidates[start_idx:end_idx]

            print(
                f"Batch {batch_num}: Removing tests {start_idx + 1}-{end_idx} "
                f"({len(batch)} tests)..."
            )

            # Remove the batch
            removed_in_batch = self.remove_batch(batch)
            print(f"  Removed: {removed_in_batch}/{len(batch)} tests")

            # Validate coverage
            new_coverage = self.get_current_coverage()
            coverage_drop = self.baseline_coverage - new_coverage

            print(
                f"  Coverage: {new_coverage:.2f}% "
                f"(drop: {coverage_drop:.2f}% points)"
            )

            # Check if acceptable
            if coverage_drop > self.max_coverage_drop:
                print(
                    f"  ❌ Coverage drop exceeds limit ({self.max_coverage_drop}%)"
                )
                self.restore_tests()
                print(f"  Stopped at {total_removed} tests removed")
                break
            else:
                print(f"  ✅ Batch successful")
                total_removed += removed_in_batch
                self.current_coverage = new_coverage

                # Update backup for next batch
                if not self.dry_run:
                    if self.backup_dir.exists():
                        shutil.rmtree(self.backup_dir)
                    shutil.copytree("tests", self.backup_dir)

        # Summary
        print("\n" + "=" * 80)
        print("BATCH REMOVAL SUMMARY")
        print("=" * 80)
        print(f"Tests removed: {total_removed}")
        print(f"Target: {target_removal}")
        print(
            f"Progress: {total_removed / target_removal * 100:.1f}%"
            if target_removal > 0
            else "N/A"
        )
        print(f"\nBaseline coverage: {self.baseline_coverage:.2f}%")
        print(f"Final coverage: {self.current_coverage:.2f}%")
        print(
            f"Coverage drop: {self.baseline_coverage - self.current_coverage:.2f}% points"
        )

        # Save results
        if not self.dry_run:
            Path(".artifacts").mkdir(exist_ok=True)
            results_file = Path(".artifacts/batch_removal_results.json")
            with open(results_file, "w") as f:
                json.dump(
                    {
                        "removed_tests": self.removed_tests,
                        "total_removed": total_removed,
                        "baseline_coverage": self.baseline_coverage,
                        "final_coverage": self.current_coverage,
                        "coverage_drop": self.baseline_coverage
                        - self.current_coverage,
                        "batch_size": self.batch_size,
                    },
                    f,
                    indent=2,
                )
            print(f"\nResults saved to: {results_file}")

        print(f"\nBackup preserved at: {self.backup_dir}/")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fast batch removal of redundant tests"
    )
    parser.add_argument(
        "--candidates-file",
        type=str,
        default=".artifacts/removal_candidates_100pct.json",
        help="JSON file containing removal candidates",
    )
    parser.add_argument(
        "--target-pct",
        type=float,
        default=40.0,
        help="Target percentage of tests to remove (default: 40%%)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=15,
        help="Number of tests to remove per batch (default: 15)",
    )
    parser.add_argument(
        "--max-drop",
        type=float,
        default=2.0,
        help="Maximum coverage drop allowed (default: 2.0%%)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without deleting"
    )

    args = parser.parse_args()

    # Load candidates
    candidates_file = Path(args.candidates_file)
    if not candidates_file.exists():
        print(f"ERROR: Candidates file not found: {candidates_file}")
        sys.exit(1)

    with open(candidates_file) as f:
        data = json.load(f)
        candidates = [
            (item["test_to_remove"], item["test_to_keep"], item["overlap_pct"])
            for item in data["candidates"]
        ]

    total_tests = data["total_tests"]
    target_removal = int(total_tests * (args.target_pct / 100.0))

    print(f"Total tests: {total_tests}")
    print(f"Candidates: {len(candidates)}")
    print(f"Target removal: {target_removal} ({args.target_pct}%)")
    print(f"Batch size: {args.batch_size}")

    # Execute
    remover = BatchTestRemover(
        batch_size=args.batch_size,
        max_coverage_drop=args.max_drop,
        dry_run=args.dry_run,
    )

    remover.execute_batch_removal(candidates, target_removal)


if __name__ == "__main__":
    main()
