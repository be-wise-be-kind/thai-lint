#!/usr/bin/env python3
"""Mark duplicate tests as skipped instead of deleting them."""

import json
from pathlib import Path
import re

candidates_file = Path(".artifacts/removal_candidates_100pct.json")
with open(candidates_file) as f:
    data = json.load(f)

candidates = [(item["test_to_remove"], item["test_to_keep"], item["overlap_pct"])
              for item in data["candidates"]]

# Skip ALL 100% duplicates
total_tests = data["total_tests"]
candidates_to_skip = candidates  # No limit - skip all duplicates

print(f"Marking ALL {len(candidates_to_skip)} duplicate tests as skipped (from {total_tests} total)...")

skipped_count = 0

for test_to_remove, test_to_keep, overlap_pct in candidates_to_skip:
    # Convert dotted path to file path
    # Full: tests.unit.linters.dry.test_file.TestClass.test_method -> tests/unit/linters/dry/test_file.py
    # Short: dry.test_file.TestClass.test_method -> tests/unit/linters/dry/test_file.py
    parts = test_to_remove.split(".")

    # Check if it starts with "tests" or is a shortened path
    if not parts[0].startswith("test"):
        # Shortened path - need to prepend tests/unit/linters/
        # dry.test_file -> tests/unit/linters/dry/test_file
        # file_placement.test_file -> tests/unit/linters/file_placement/test_file
        # nesting.test_file -> tests/unit/linters/nesting/test_file
        parts = ["tests", "unit", "linters"] + parts

    # Find ALL parts up to and including the test file (last part starting with "test_")
    file_parts = []
    remaining_parts = []

    for i, part in enumerate(parts):
        if part.startswith("test_") and i < len(parts) - 1:  # It's a test file, not the final method
            file_parts.append(part)
            remaining_parts = parts[i+1:]
            break
        elif i == len(parts) - 1 and part.startswith("test_"):  # It's the test method
            remaining_parts = [part]
        else:
            file_parts.append(part)

    # Construct file path
    file_path = "/".join(file_parts) + ".py"
    test_file = Path(file_path)

    if not test_file.exists():
        print(f"  ⚠️  File not found: {file_path}")
        continue

    # Get the function name (last part)
    if not remaining_parts:
        print(f"  ⚠️  No function name found in: {test_to_remove}")
        continue

    function_name = remaining_parts[-1]

    # Read the file
    try:
        content = test_file.read_text()
        lines = content.split("\n")
        new_lines = []
        modified = False
        has_pytest_import = "import pytest" in content

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line defines our target function
            if re.match(rf'\s*def {re.escape(function_name)}\(', line):
                # Check if already has skip decorator
                has_skip = False
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if '@pytest.mark.skip' in prev_line:
                        has_skip = True

                if not has_skip:
                    # Get the indentation of the function
                    indent = len(line) - len(line.lstrip())
                    skip_decorator = ' ' * indent + '@pytest.mark.skip(reason="100% duplicate")'
                    new_lines.append(skip_decorator)
                    modified = True
                    skipped_count += 1

            new_lines.append(line)
            i += 1

        # Add pytest import if not present and we made modifications
        if modified and not has_pytest_import:
            # Find the last import line and add after it
            final_lines = []
            import_added = False
            for line in new_lines:
                final_lines.append(line)
                if not import_added and (line.startswith("import ") or line.startswith("from ")):
                    # Check if next line is also an import
                    idx = new_lines.index(line)
                    if idx + 1 < len(new_lines) and not (new_lines[idx + 1].startswith("import ") or new_lines[idx + 1].startswith("from ")):
                        final_lines.append("import pytest")
                        import_added = True

            if not import_added:
                # No imports found, add at top after any docstring
                final_lines = ["import pytest", ""] + new_lines

            new_lines = final_lines

        # Write back if modified
        if modified:
            test_file.write_text("\n".join(new_lines))

            if skipped_count % 10 == 0:
                print(f"  Marked {skipped_count}/{len(candidates_to_skip)} tests as skipped...")

    except Exception as e:
        print(f"  ERROR processing {function_name}: {e}")

print(f"\n✅ Marked {skipped_count} tests as skipped")
print(f"\nSaving results...")

# Save results
Path(".artifacts").mkdir(exist_ok=True)
with open(".artifacts/skipped_tests_list.json", "w") as f:
    json.dump({
        "skipped_tests": [c[0] for c in candidates_to_skip],
        "total_skipped": skipped_count,
        "total_candidates": len(candidates_to_skip),
        "already_skipped": len(candidates_to_skip) - skipped_count
    }, f, indent=2)

print(f"Results saved to .artifacts/skipped_tests_list.json")
print(f"\n📊 Next steps:")
print(f"  1. Run: poetry run pytest --cov=src --cov-report=term")
print(f"  2. Verify coverage is still ~90%")
print(f"  3. If good, commit the changes")
print(f"  4. Later: Use scripts/remove_skipped_tests.py to permanently delete")
