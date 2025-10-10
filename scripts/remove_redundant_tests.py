#!/usr/bin/env python3
"""
Purpose: Remove redundant tests while maintaining coverage within acceptable limits
Scope: Automates safe removal of duplicate tests identified by coverage analysis
Overview: This script takes a list of redundant tests identified by the coverage
    analyzer and systematically removes them one at a time, validating after each
    removal that coverage has not dropped more than the allowed threshold (default 2%).
    It tracks which tests have been removed, maintains a backup of the original test
    suite, and can rollback if coverage drops too much. The script generates a detailed
    report of what was removed and the final coverage impact.
Dependencies: subprocess, pathlib, json for test execution and tracking
Exports: TestRemovalOrchestrator class and command-line interface
Interfaces: Reads removal candidates JSON, removes tests, validates coverage
Implementation: Iterative removal with validation and rollback capability
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TestRemovalOrchestrator:
    """Orchestrates the safe removal of redundant tests."""

    def __init__(
        self,
        target_removal_pct: float = 40.0,
        max_coverage_drop: float = 2.0,
        dry_run: bool = False,
    ) -> None:
        """
        Initialize the test removal orchestrator.

        Args:
            target_removal_pct: Target percentage of tests to remove (default 40%)
            max_coverage_drop: Maximum allowed coverage drop in percentage points (default 2.0%)
            dry_run: If True, simulate removals without actually deleting tests
        """
        self.target_removal_pct = target_removal_pct
        self.max_coverage_drop = max_coverage_drop
        self.dry_run = dry_run
        self.baseline_coverage = 0.0
        self.current_coverage = 0.0
        self.removed_tests: List[str] = []
        self.backup_dir = Path(".test_backup")

    def get_current_coverage(self) -> float:
        """
        Run tests and extract current coverage percentage.

        Returns:
            Coverage percentage as a float
        """
        print("Running tests to get current coverage...")

        try:
            # Run pytest with coverage (without verbose output for speed)
            result = subprocess.run(
                ["poetry", "run", "pytest", "--cov=src", "--cov-report=term", "-q"],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )

            # Parse coverage from output
            # Look for line like: "TOTAL    1234   123   90%"
            for line in result.stdout.split("\n"):
                if "TOTAL" in line:
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            coverage_str = part.replace("%", "")
                            return float(coverage_str)

            print("WARNING: Could not parse coverage from pytest output")
            print("Output:", result.stdout[-500:])  # Show last 500 chars
            return 0.0

        except subprocess.TimeoutExpired:
            print("ERROR: Test run timed out after 10 minutes")
            return 0.0
        except Exception as e:
            print(f"ERROR running tests: {e}")
            return 0.0

    def backup_tests(self) -> None:
        """Create a backup of the tests directory."""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        print(f"Creating backup of tests directory to {self.backup_dir}...")
        shutil.copytree("tests", self.backup_dir)

    def restore_tests(self) -> None:
        """Restore tests from backup."""
        if not self.backup_dir.exists():
            print("ERROR: No backup found to restore from")
            return

        print("Restoring tests from backup...")
        if Path("tests").exists():
            shutil.rmtree("tests")
        shutil.copytree(self.backup_dir, "tests")

    def find_test_file(self, test_name: str) -> Path | None:
        """
        Find the file containing a given test.

        Args:
            test_name: Full test name (e.g., "tests/unit/test_foo.py::test_bar")

        Returns:
            Path to the test file, or None if not found
        """
        # Extract file path from test name
        if "::" in test_name:
            file_path_str = test_name.split("::")[0]
            file_path = Path(file_path_str)

            if file_path.exists():
                return file_path

        return None

    def remove_test_function(self, test_file: Path, function_name: str) -> bool:
        """
        Remove a specific test function from a test file.

        Args:
            test_file: Path to the test file
            function_name: Name of the test function to remove

        Returns:
            True if successfully removed, False otherwise
        """
        if self.dry_run:
            print(f"  [DRY RUN] Would remove {function_name} from {test_file}")
            return True

        try:
            content = test_file.read_text()
            lines = content.split("\n")

            # Find the test function and remove it
            new_lines = []
            in_target_function = False
            function_indent = 0

            for i, line in enumerate(lines):
                # Check if this is the start of our target function
                if line.strip().startswith(f"def {function_name}("):
                    in_target_function = True
                    function_indent = len(line) - len(line.lstrip())
                    continue

                # If we're in the target function
                if in_target_function:
                    # Check if we've reached the next function or class
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

            # Write back the modified content
            test_file.write_text("\n".join(new_lines))
            return True

        except Exception as e:
            print(f"  ERROR removing function {function_name}: {e}")
            return False

    def remove_test(self, test_name: str) -> bool:
        """
        Remove a specific test.

        Args:
            test_name: Full test name (e.g., "tests/unit/test_foo.py::test_bar")

        Returns:
            True if successfully removed, False otherwise
        """
        # Parse test name to get file and function
        if "::" not in test_name:
            print(f"  WARNING: Invalid test name format: {test_name}")
            return False

        parts = test_name.split("::")
        file_path_str = parts[0]
        function_name = parts[1] if len(parts) > 1 else None

        test_file = Path(file_path_str)

        if not test_file.exists():
            print(f"  WARNING: Test file not found: {test_file}")
            return False

        if not function_name:
            print(f"  WARNING: Could not extract function name from: {test_name}")
            return False

        # Remove the test function
        return self.remove_test_function(test_file, function_name)

    def execute_removal_plan(
        self, removal_candidates: List[Tuple[str, str, float]]
    ) -> None:
        """
        Execute the test removal plan.

        Args:
            removal_candidates: List of (test_to_remove, test_to_keep, overlap_pct) tuples
        """
        print("\n" + "=" * 80)
        print("EXECUTING TEST REMOVAL PLAN")
        print("=" * 80)

        # Get baseline coverage
        print("\nStep 1: Establishing baseline coverage...")
        self.baseline_coverage = self.get_current_coverage()
        self.current_coverage = self.baseline_coverage
        print(f"Baseline coverage: {self.baseline_coverage:.2f}%")

        if self.baseline_coverage == 0.0:
            print("ERROR: Could not establish baseline coverage. Aborting.")
            return

        # Create backup
        print("\nStep 2: Creating backup...")
        self.backup_tests()

        # Calculate targets
        total_candidates = len(removal_candidates)
        target_removal_count = int(
            total_candidates * (self.target_removal_pct / 100.0)
        )

        print(f"\nStep 3: Removing tests...")
        print(f"Total candidates: {total_candidates}")
        print(f"Target removals: {target_removal_count}")
        print(f"Max coverage drop allowed: {self.max_coverage_drop}%")

        # Process each candidate
        for i, (test_to_remove, test_to_keep, overlap_pct) in enumerate(
            removal_candidates[:target_removal_count], 1
        ):
            print(f"\n[{i}/{target_removal_count}] Processing: {test_to_remove}")
            print(f"  Overlap: {overlap_pct:.1f}% with {test_to_keep}")

            # Remove the test
            if self.remove_test(test_to_remove):
                # Check coverage impact
                new_coverage = self.get_current_coverage()
                coverage_drop = self.baseline_coverage - new_coverage

                print(
                    f"  Coverage: {new_coverage:.2f}% (drop: {coverage_drop:.2f}% points)"
                )

                # Check if coverage drop is acceptable
                if coverage_drop > self.max_coverage_drop:
                    print(
                        f"  ❌ Coverage drop exceeds limit ({self.max_coverage_drop}%). Rolling back..."
                    )
                    self.restore_tests()
                    self.current_coverage = self.get_current_coverage()
                    print("  Rollback complete. Stopping removal process.")
                    break
                else:
                    print(f"  ✅ Removed successfully")
                    self.removed_tests.append(test_to_remove)
                    self.current_coverage = new_coverage
            else:
                print(f"  ⚠️  Failed to remove test")

        # Print summary
        print("\n" + "=" * 80)
        print("REMOVAL SUMMARY")
        print("=" * 80)
        print(f"Tests removed: {len(self.removed_tests)}")
        print(f"Target removals: {target_removal_count}")
        print(
            f"Completion: {len(self.removed_tests)/target_removal_count*100:.1f}%"
            if target_removal_count > 0
            else "N/A"
        )
        print(f"\nBaseline coverage: {self.baseline_coverage:.2f}%")
        print(f"Final coverage: {self.current_coverage:.2f}%")
        print(
            f"Coverage drop: {self.baseline_coverage - self.current_coverage:.2f}% points"
        )

        # Save removed tests list
        if not self.dry_run:
            Path(".artifacts").mkdir(exist_ok=True)
            removed_tests_file = Path(".artifacts/removed_tests.json")
            with open(removed_tests_file, "w") as f:
                json.dump(
                    {
                        "removed_tests": self.removed_tests,
                        "baseline_coverage": self.baseline_coverage,
                        "final_coverage": self.current_coverage,
                        "coverage_drop": self.baseline_coverage
                        - self.current_coverage,
                    },
                    f,
                    indent=2,
                )
            print(f"\nRemoved tests list saved to: {removed_tests_file}")

        print("\nBackup preserved at:", self.backup_dir)


def main() -> None:
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove redundant tests while maintaining coverage"
    )
    parser.add_argument(
        "--candidates-file",
        type=str,
        default=".artifacts/removal_candidates.json",
        help="JSON file containing removal candidates",
    )
    parser.add_argument(
        "--target-pct",
        type=float,
        default=40.0,
        help="Target percentage of tests to remove (default: 40%%)",
    )
    parser.add_argument(
        "--max-drop",
        type=float,
        default=2.0,
        help="Maximum coverage drop allowed in percentage points (default: 2.0%%)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate removal without actually deleting tests",
    )

    args = parser.parse_args()

    # Load removal candidates
    candidates_file = Path(args.candidates_file)
    if not candidates_file.exists():
        print(
            f"ERROR: Candidates file not found: {candidates_file}\n"
            "Run analyze_test_coverage.py first to generate candidates."
        )
        sys.exit(1)

    with open(candidates_file) as f:
        data = json.load(f)
        candidates = [
            (item["test_to_remove"], item["test_to_keep"], item["overlap_pct"])
            for item in data["candidates"]
        ]

    # Create orchestrator and execute plan
    orchestrator = TestRemovalOrchestrator(
        target_removal_pct=args.target_pct,
        max_coverage_drop=args.max_drop,
        dry_run=args.dry_run,
    )

    orchestrator.execute_removal_plan(candidates)


if __name__ == "__main__":
    main()
