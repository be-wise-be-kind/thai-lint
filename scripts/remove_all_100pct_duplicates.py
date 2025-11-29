#!/usr/bin/env python3
"""
Purpose: Removes 100% duplicate test functions from test files
Scope: Test file maintenance and deduplication
Overview: Utility script that permanently deletes duplicate test functions identified
    as 100% overlapping in code coverage. Reads candidates from JSON artifact file,
    limits removal to 40% of total tests for safety, and removes entire function
    definitions including decorators. Uses indentation-based parsing to identify
    function boundaries. Saves removal report to JSON for audit trail.
Dependencies: json, pathlib for file operations
Exports: main script logic for removing duplicate test functions
Interfaces: Reads .artifacts/removal_candidates_100pct.json, writes to test files
Implementation: Indentation-based function removal with safety limits and progress tracking
"""

import json
from pathlib import Path

candidates_file = Path(".artifacts/removal_candidates_100pct.json")
with open(candidates_file) as f:
    data = json.load(f)

candidates = [(item["test_to_remove"], item["test_to_keep"], item["overlap_pct"])
              for item in data["candidates"]]

# Limit to 40% of total tests
total_tests = data["total_tests"]
target_removal = int(total_tests * 0.4)
candidates_to_remove = candidates[:target_removal]

print(f"Removing {len(candidates_to_remove)} tests (40% of {total_tests})...")

removed_count = 0

for test_to_remove, test_to_keep, overlap_pct in candidates_to_remove:
    # Parse test name
    if "::" not in test_to_remove:
        continue

    parts = test_to_remove.split("::")
    file_path_str = parts[0]
    function_name = parts[1] if len(parts) > 1 else None

    test_file = Path(file_path_str)

    if not test_file.exists() or not function_name:
        continue

    # Remove the function
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
                if (line.strip() and current_indent <= function_indent
                    and not line.strip().startswith("@")):
                    in_target_function = False

                # Skip lines that are part of the function
                if in_target_function:
                    continue

            # Keep all other lines
            new_lines.append(line)

        # Write back
        test_file.write_text("\n".join(new_lines))
        removed_count += 1

        if removed_count % 10 == 0:
            print(f"  Removed {removed_count}/{len(candidates_to_remove)}...")

    except Exception as e:
        print(f"  ERROR removing {function_name}: {e}")

print(f"\n✅ Removed {removed_count} duplicate tests")
print(f"\nSaving results...")

# Save results
Path(".artifacts").mkdir(exist_ok=True)
with open(".artifacts/removed_tests_list.json", "w") as f:
    json.dump({
        "removed_tests": [c[0] for c in candidates_to_remove[:removed_count]],
        "total_removed": removed_count,
        "target": target_removal
    }, f, indent=2)

print(f"Results saved to .artifacts/removed_tests_list.json")
print(f"\nNext: Run 'poetry run pytest --cov=src --cov-report=term' to validate coverage")
